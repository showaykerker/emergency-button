"""
Handler for MQTT message parsing and processing.
"""
import json
import time
import traceback
from threading import Thread

import nanoid  # To generate Identifier

import config
from logger import setup_logger

# Setup logger
log = setup_logger("message_handler")

class MessageHandler:
    """
    Handles MQTT message parsing and processing logic.
    """
    
    def __init__(self, message_queue_processor):
        """
        Initialize the message handler.
        
        Args:
            message_queue_processor: The processor to handle queued messages
        """
        self.processor = message_queue_processor
    
    def handle_message(self, msg):
        """
        Parse and process an MQTT message.
        
        Args:
            msg: MQTT message object from paho-mqtt
        """
        # Start parsing in a separate thread to avoid blocking MQTT client
        Thread(target=self._parse_message, args=(msg,), daemon=True).start()
    
    def _parse_message(self, msg):
        """
        Parse an MQTT message and add it to the processing queue.
        """
        identifier = nanoid.generate(size=8)

        try:
            msg_text = msg.payload.decode()
            topic = msg.topic
            log.info(f"ID {identifier} | Received message on {msg.topic}: {msg_text[:200]}...")

            # Parse JSON data
            data = json.loads(msg_text)

            if "logging" in topic:
                log.info(f"ID {identifier} | ignore msg from `logging`")
                return

            if type(data) is not dict:
                log.info(f"ID {identifier} | ignore data type {type(data)}")
                return

            if "action" not in data:
                log.info(f"ID {identifier} | ignore msg without 'action' key")
                return

            # Enrich data with topic
            data.update({'topic': topic.split("/")[-1]})
            identifier += f" - {topic}"
            log.info(f"ID {identifier} | Parsed message: topic={topic}, data={data}")

            # Compose message
            action, message = self._compose_message(data)
            
            # Skip adding to queue if it's just a background ping
            if action == "bg_ping":
                log.info(f"ID {identifier} | Background check, still alive.")
                return
                
            success = self.processor.enqueue_message(identifier, action, message)
            if success:
                log.info(f"ID {identifier} | Added to processing queue")

        except json.JSONDecodeError:
            log.warning(f"ID {identifier} | Message is not valid JSON: {msg.payload.decode()[:100]}")
        except Exception as e:
            log.error(f"ID {identifier} | Error parsing message: {e}")
            log.error(f"ID {identifier} | {traceback.format_exc()}")
    
    def _compose_message(self, data):
        """
        Compose a message for LINE based on MQTT data.

        Args:
            data (dict): Message data

        Returns:
            action (str): Possible value: "send", "call", "debug", "bg_ping", <other unknown action>
            msg (Optional[str]): Formatted message for LINE,
                if None, it means that is not an trigger event,
                it simply a background pinging ("bg_ping") automatically send.
        """
        action = data.get("action")
        battery = int(data.get('battery') or -1)
        voltage = int(data.get('voltage') or -1)
        linkquality = int(data.get('linkquality') or -1)

        if action is None:
            log.info(f"Get msg without action, possibly a bg ping: {data}")
            return "bg_ping", None

        if config.BUTTON_ACTION_BEHAVIOR.get(action) == "call":
            log.info(f"Get call action")
            return "call", None

        msg = f"===== 按鈕觸發：{data.get('topic')} =====\n\n"

        if config.BUTTON_ACTION_BEHAVIOR.get(action) is None:
            msg += f"未定義的行為：{action}"

        if config.BUTTON_ACTION_BEHAVIOR.get(action) == "debug":
            msg = "<這只是一個觸發測試>\n\n" + msg
            msg += f"- 電池電力： {battery}\n"
            msg += f"- 電池電壓： {voltage}\n"
            msg += f"- 連線品質： {linkquality}\n"

        # Add alerts for low values
        if battery >= 0 and battery < config.BATTERY_ALARM_THRESHOLD:
            msg += f'- 電池電力剩下 {battery} %，請盡快更換。\n'
        if voltage >= 0 and voltage < config.VOLTAGE_ALARM_THRESHOLD:
            msg += f'- 電池電壓剩下 {voltage} mV，可能需要更換。\n'
        if linkquality >= 0 and linkquality < config.LINK_ALARM_THRESHOLD:
            msg += f'- 連線品質不佳： {linkquality}。\n'

        # Add timestamp
        msg += f"\n時間戳：{time.strftime('%Y-%m-%d %H:%M:%S')}"

        return action, msg