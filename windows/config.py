"""
Configuration settings for the MQTT to LINE messaging system.
"""
import os
import argparse

# MQTT Settings
MQTT_BROKER = "192.168.232.128"
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/#"
MQTT_QOS = 0
MQTT_RECONNECT_DELAY = 5  # seconds
MQTT_MAX_RECONNECT_ATTEMPTS = 10

# Button Behavior
BUTTON_ACTION_BEHAVIOR = {
    "single": "send",
    "double": "call",
    "long"  : "debug"
}
SINGLE_CLICK_ACTION = "send"
DOUBLE_CLICK_ACTION = "call"
LONG_CLICK_ACTION = "debug"

# Button Alert Thresholds
BATTERY_ALARM_THRESHOLD = 30    # %
VOLTAGE_ALARM_THRESHOLD = 2400  # mV
LINK_ALARM_THRESHOLD = 60       # quality

# LINE Automation Settings
MOUSE_MOVE_DURATION = 0.0       # seconds
SLEEP_AFTER_CLICK = 0.0         # seconds
IMAGE_SEARCH_CONFIDENCE = 0.95  # 0.0-1.0
IMAGE_RETRY_COUNT = 10
IMAGE_RETRY_INTERVAL = 0.25     # seconds
IMAGE_SEARCH_TIMEOUT = 60       # seconds

# Image paths
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
LINE_ICON = os.path.join(IMAGE_DIR, "line-icon.png")
LINE_LEFT_BAR_ICON_1 = os.path.join(IMAGE_DIR, "line-left-bar-icon-1.png")
LINE_LEFT_BAR_ICON_3 = os.path.join(IMAGE_DIR, "line-left-bar-icon-3.png")
GROUP_TAB = os.path.join(IMAGE_DIR, "group-tab.png")
GROUP_TAB_ACTIVATED = os.path.join(IMAGE_DIR, "group-tab-activated.png")
TARGET_GROUP_NAME = os.path.join(IMAGE_DIR, "target-group-name.png")
INPUT_BOX = os.path.join(IMAGE_DIR, "input-box.png")
CALL_ICON = os.path.join(IMAGE_DIR, "call-icon.png")
CALL_SELECTION = os.path.join(IMAGE_DIR, "call-selection.png")
START_CALL = os.path.join(IMAGE_DIR, "start-call.png")
CANCEL_CALL = os.path.join(IMAGE_DIR, "cancel-call.png")

def parse_args():
    """Parse command line arguments and update configuration."""
    parser = argparse.ArgumentParser(description='MQTT to LINE Messaging Bridge')
    parser.add_argument('--broker', type=str, help='MQTT broker address')
    parser.add_argument('--port', type=int, help='MQTT broker port')
    parser.add_argument('--topic', type=str, help='MQTT topic to subscribe')
    parser.add_argument('--battery-threshold', type=int, help='Battery alarm threshold (%)')
    parser.add_argument('--voltage-threshold', type=int, help='Voltage alarm threshold (mV)')
    parser.add_argument('--link-threshold', type=int, help='Link quality alarm threshold')
    
    args = parser.parse_args()
    
    # Update global variables based on arguments
    global MQTT_BROKER, MQTT_PORT, MQTT_TOPIC
    global BATTERY_ALARM_THRESHOLD, VOLTAGE_ALARM_THRESHOLD, LINK_ALARM_THRESHOLD
    
    if args.broker:
        MQTT_BROKER = args.broker
    if args.port:
        MQTT_PORT = args.port
    if args.topic:
        MQTT_TOPIC = args.topic
    if args.battery_threshold:
        BATTERY_ALARM_THRESHOLD = args.battery_threshold
    if args.voltage_threshold:
        VOLTAGE_ALARM_THRESHOLD = args.voltage_threshold
    if args.link_threshold:
        LINK_ALARM_THRESHOLD = args.link_threshold
        
    return args