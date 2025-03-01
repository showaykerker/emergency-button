"""
MQTT client for handling Zigbee2MQTT messages and sending them to LINE.
"""
import paho.mqtt.client as mqtt
import json
import time
import sys
import traceback
from threading import Thread, Event

import config
from line_messenger import send_message
from logger import setup_logger

# Load configuration
config.parse_args()

# Setup logger
log = setup_logger("mqtt_client")

class MQTTHandler:
    """
    Handles MQTT connection, message parsing, and dispatching.
    """
    
    def __init__(self, broker=None, port=None, topic=None):
        """
        Initialize the MQTT handler.
        
        Args:
            broker (str): MQTT broker address
            port (int): MQTT broker port
            topic (str): MQTT topic to subscribe to
        """
        self.broker = broker or config.MQTT_BROKER
        self.port = port or config.MQTT_PORT
        self.topic = topic or config.MQTT_TOPIC
        self.client = None
        self.connected = Event()
        self.should_stop = Event()
        self.reconnect_count = 0
    
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """
        Callback for when the client connects to the broker.
        """
        if rc == 0:
            log.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
            self.client.subscribe(self.topic)
            log.info(f"Subscribed to topic: {self.topic}")
            self.connected.set()
            self.reconnect_count = 0
        else:
            log.error(f"Failed to connect to MQTT broker, code: {rc}")
            self.connected.clear()
    
    def _on_disconnect(self, client, userdata, rc, properties=None):
        """
        Callback for when the client disconnects from the broker.
        """
        log.warning(f"Disconnected from MQTT broker with code: {rc}")
        self.connected.clear()
        
        # Attempt reconnection if not stopping
        if not self.should_stop.is_set():
            self._schedule_reconnect()
    
    def _schedule_reconnect(self):
        """
        Schedule a reconnection attempt.
        """
        if self.reconnect_count < config.MQTT_MAX_RECONNECT_ATTEMPTS:
            self.reconnect_count += 1
            delay = config.MQTT_RECONNECT_DELAY * self.reconnect_count
            log.info(f"Scheduling reconnection attempt {self.reconnect_count} in {delay} seconds")
            
            Thread(target=self._delayed_reconnect, args=(delay,), daemon=True).start()
        else:
            log.error(f"Maximum reconnection attempts ({config.MQTT_MAX_RECONNECT_ATTEMPTS}) reached")
    
    def _delayed_reconnect(self, delay):
        """
        Attempt to reconnect after a delay.
        """
        time.sleep(delay)
        if not self.should_stop.is_set():
            try:
                log.info(f"Attempting to reconnect to MQTT broker")
                self.client.reconnect()
            except Exception as e:
                log.error(f"Reconnection attempt failed: {e}")
                self._schedule_reconnect()
    
    def _on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker.
        """
        try:
            Thread(target=self._process_message, args=(msg,), daemon=True).start()
        except Exception as e:
            log.error(f"Error starting message processing thread: {e}")
    
    def _process_message(self, msg):
        """
        Process an MQTT message.
        """
        try:
            msg_text = msg.payload.decode()
            log.debug(f"Received message on {msg.topic}: {msg_text[:100]}...")
            
            msg_json = json.loads(msg_text)
            if "message" not in msg_json:
                return
                
            msg_text = msg_json["message"]
            
            # Extract data from message
            # z2m:mqtt: MQTT publish: topic 'zigbee2mqtt/btn1', payload '{"action":"single","battery":100,"linkquality":160,"voltage":3000}'
            try:
                topic = msg_text.split("zigbee2mqtt")[1].split(",")[0][1:-1]
                data_json = msg_text.split(" ")[-1][1:-1]
                data = json.loads(data_json)
                data.update({'topic': topic})
                
                log.info(f"Parsed message: topic={topic}, data={data}")
                
                # Compose and send message
                message = self._compose_message(data)
                result = send_message(message)
                
                if result:
                    log.info("Message sent successfully to LINE")
                else:
                    log.error("Failed to send message to LINE")
                
            except IndexError:
                log.error(f"Failed to parse message format: {msg_text}")
            except json.JSONDecodeError:
                log.error(f"Failed to parse JSON data from message: {msg_text}")
                
        except json.JSONDecodeError:
            log.warning(f"Message is not valid JSON: {msg.payload.decode()[:100]}")
        except Exception as e:
            log.error(f"Error processing message: {e}")
            log.error(traceback.format_exc())
    
    def _compose_message(self, data):
        """
        Compose a message for LINE based on MQTT data.
        
        Args:
            data (dict): Message data
            
        Returns:
            str: Formatted message for LINE
        """
        msg = f"===== 按鈕觸發：{data.get('topic')} =====\n\n"
        
        battery = int(data.get('battery') or -1)
        voltage = int(data.get('voltage') or -1)
        linkquality = int(data.get('linkquality') or -1)
        
        # Add alerts for low values
        if battery >= 0 and battery < config.BATTERY_ALARM_THRESHOLD:
            msg += f'- 電池電力剩下 {battery} %，請盡快更換。\n'
        if voltage >= 0 and voltage < config.VOLTAGE_ALARM_THRESHOLD:
            msg += f'- 電池電壓剩下 {voltage} mV，可能需要更換。\n'
        if linkquality >= 0 and linkquality < config.LINK_ALARM_THRESHOLD:
            msg += f'- 連線品質不佳： {linkquality}。\n'
        
        action = data.get('action') or 'error'
        
        if action == "error":
            msg += f"\n\nerror.\ndata = {data}"
        
        if action == "double":
            msg += f"- 電池電力： {battery}\n"
            msg += f"- 電池電壓： {voltage}\n"
            msg += f"- 連線品質： {linkquality}\n"
        
        # Add timestamp
        msg += f"\n\n時間戳：{time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return msg
    
    def connect(self):
        """
        Connect to the MQTT broker.
        """
        try:
            # Setup MQTT client
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Connect to broker
            log.info(f"Connecting to MQTT broker at {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, 60)
            
            # Start the network loop
            self.client.loop_start()
            
            # Wait for connection
            if not self.connected.wait(timeout=10):
                log.warning("Timed out waiting for initial connection")
                
            return True
            
        except Exception as e:
            log.error(f"Error connecting to MQTT broker: {e}")
            log.error(traceback.format_exc())
            return False
    
    def disconnect(self):
        """
        Disconnect from the MQTT broker.
        """
        if self.client:
            log.info("Disconnecting from MQTT broker")
            self.should_stop.set()
            self.client.loop_stop()
            self.client.disconnect()
            log.info("Disconnected from MQTT broker")
    
    def wait_for_messages(self):
        """
        Wait for messages until interrupted.
        """
        try:
            log.info("Waiting for MQTT messages. Press Ctrl+C to exit.")
            while not self.should_stop.is_set():
                time.sleep(1)
        except KeyboardInterrupt