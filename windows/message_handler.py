"""
Handler for MQTT message parsing and processing.
"""
import json
import time
from datetime import datetime
import traceback
from threading import Thread

import nanoid  # To generate Identifier

import config
from logger import setup_logger

# Setup logger
log = setup_logger("msg_hdl")

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
            log.debug(f"ID {identifier} | Received message on {msg.topic}: {msg_text[:200]}...")

            # Parse JSON data
            data = json.loads(msg_text)

            if "logging" in topic:
                log.debug(f"ID {identifier} | ignore msg from `logging`")
                return

            if type(data) is not dict:
                log.debug(f"ID {identifier} | ignore data type {type(data)}")
                return

            if "action" not in data:
                log.debug(f"ID {identifier} | ignore msg without 'action' key")
                return

            # Enrich data with topic
            data.update({'topic': topic.split("/")[-1]})
            identifier += f" - {topic}"
            log.debug(f"ID {identifier} | Parsed message: topic={topic}, data={data}")

            # Compose message
            action, message = self._compose_message(data)
            
            # Skip adding to queue if it's just a background ping
            if action == "bg_ping":
                log.debug(f"ID {identifier} | Background check, still alive.")
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
            action (str): Possible value: "call", "cancel", "debug", "bg_ping", <other unknown action>
            msg (Optional[str]): Formatted message for LINE,
                if None, it means that is not an trigger event,
                it simply a background pinging ("bg_ping") automatically send.
        """
        action = data.get("action")
        actual_action = config.BUTTON_ACTION_BEHAVIOR.get(action)
        log.info(f"Get action: {action}, actual action: {actual_action}")
        battery = int(data.get('battery') or -1)
        voltage = int(data.get('voltage') or -1)
        linkquality = int(data.get('linkquality') or -1)

        if action is None:
            log.debug(f"Get msg without action, possibly a bg ping: {data}")
            return "bg_ping", None

        msg = ""

        if actual_action is None:
            msg += f"未定義的行為：{action}"

        if actual_action == "debug":
            msg = f"<測試> {data.get('topic')}\n\n"
            msg += f"- 電池電力： {battery}\n"
            msg += f"- 電池電壓： {voltage}\n"
            msg += f"- 連線品質： {linkquality}\n"
            msg += f"\n時間戳：{time.strftime('%Y-%m-%d %H:%M:%S')}"

        elif actual_action == "call":
            msg += f"現在時間 {time.strftime('%Y/%m/%d %H:%M')}，急救室呼叫急救案件\n"
        
        elif actual_action == "cancel":
            msg += f"現在時間 {time.strftime('%Y/%m/%d %H:%M')}，取消急救呼叫\n"

        # Add alerts for low values
        if battery >= 0 and battery < config.BATTERY_ALARM_THRESHOLD:
            msg += f'- 電池電力剩下 {battery} %，請盡快更換。\n'
        if voltage >= 0 and voltage < config.VOLTAGE_ALARM_THRESHOLD:
            msg += f'- 電池電壓剩下 {voltage} mV，可能需要更換。\n'
        if linkquality >= 0 and linkquality < config.LINK_ALARM_THRESHOLD:
            msg += f'- 連線品質不佳： {linkquality}。\n'

        return actual_action, msg