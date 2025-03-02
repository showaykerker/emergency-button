"""
MQTT client for handling Zigbee2MQTT messages and sending them to LINE.
Uses separate modules for connection management, message processing and handling.
"""
import sys

import config
from logger import setup_logger
from mqtt_connection import MQTTConnection
from message_queue_processor import MessageQueueProcessor
from message_handler import MessageHandler

# Setup logger
log = setup_logger("mqtt_client")

def main():
    """
    Main entry point of the application.
    """
    log.info("Starting MQTT to LINE messaging bridge")

    try:
        # Create message processor
        processor = MessageQueueProcessor()
        processor.start()
        
        # Create message handler
        handler = MessageHandler(processor)
        
        # Create MQTT connection with the message handler
        connection = MQTTConnection(
            broker=config.MQTT_BROKER, 
            port=config.MQTT_PORT, 
            topic=config.MQTT_TOPIC,
            message_callback=handler.handle_message
        )
        
        # Connect to MQTT broker
        if connection.connect():
            # Wait for messages
            connection.wait_for_messages()
        else:
            log.error("Failed to connect to MQTT broker. Exiting.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        log.info("Received interrupt signal, shutting down...")
    except Exception as e:
        log.error(f"Error: {e}")
        sys.exit(1)
    finally:
        # Clean shutdown
        if 'connection' in locals():
            connection.disconnect()
        if 'processor' in locals():
            processor.stop()
            processor.wait_completion()
        
    log.info("Program terminated")


if __name__ == "__main__":
    main()