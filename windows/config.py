"""
Configuration settings for the MQTT to LINE messaging system.
"""
import os
import argparse
from pathlib import Path
import logging

############# MQTT Settings #############
MQTT_BROKER = "192.168.108.128"
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/#"
MQTT_QOS = 0
MQTT_RECONNECT_DELAY = 5  # seconds
MQTT_MAX_RECONNECT_ATTEMPTS = 10

############# Button Behavior ############
BUTTON_ACTION_BEHAVIOR = {  # "send", "call", "debug"
    "single": "send",
    "double": "call",
    "long"  : "debug"
}

############ Button Alert Thresholds ############
BATTERY_ALARM_THRESHOLD = 30    # %
VOLTAGE_ALARM_THRESHOLD = 2400  # mV
LINK_ALARM_THRESHOLD = 60       # quality

############ LINE Automation Settings ############
MOUSE_MOVE_DURATION = 0.0       # seconds
SLEEP_AFTER_CLICK = 0.0         # seconds
IMAGE_SEARCH_CONFIDENCE = 0.95  # 0.0-1.0
IMAGE_RETRY_COUNT = 10
IMAGE_RETRY_INTERVAL = 0.25     # seconds
IMAGE_SEARCH_TIMEOUT = 60       # seconds
IMAGE_CACHE_LIFETIME = 3        # seconds, won't search again if cached

############ Image Paths ############
# using pathlib for cross-platform compatibility
IMAGE_DIR = Path(__file__).parent / "images"
LINE_ICON            = str(IMAGE_DIR / "line-icon.png")
LINE_LEFT_BAR_ICON_1 = str(IMAGE_DIR / "line-left-bar-icon-1.png")
LINE_LEFT_BAR_ICON_3 = str(IMAGE_DIR / "line-left-bar-icon-3.png")
GROUP_TAB            = str(IMAGE_DIR / "group-tab.png")
GROUP_TAB_ACTIVATED  = str(IMAGE_DIR / "group-tab-activated.png")
TARGET_GROUP_NAME    = str(IMAGE_DIR / "target-group-name.png")
INPUT_BOX            = str(IMAGE_DIR / "input-box.png")
CALL_ICON            = str(IMAGE_DIR / "call-icon.png")
CALL_SELECTION       = str(IMAGE_DIR / "call-selection.png")
START_CALL           = str(IMAGE_DIR / "start-call.png")
CANCEL_CALL          = str(IMAGE_DIR / "cancel-call.png")

############ Log Configs ############
LOG_ROTATE_WHEN = "W0"             # When to trigger check, 'H', "M", "S", "D", "W0-W6", "midnight"
LOG_ROTATE_INTERVAL = 7            # How many 'when' in one file
LOG_ROTATE_BACKUPCOUNT = 8         # Preserve how many files
ENABLE_DISOCRD_BOT_LOGGING = True  #
BOT_LOG_LEVEL = logging.CRITICAL   #


############ Validation ################################################

def validate_config():
    """Validate configuration settings."""
    if not IMAGE_DIR.exists():
        raise FileNotFoundError(f"Image directory not found: {IMAGE_DIR}")

    # Validate thresholds
    if not 0 <= BATTERY_ALARM_THRESHOLD <= 100:
        raise ValueError(f"Battery threshold must be between 0-100%: {BATTERY_ALARM_THRESHOLD}")

    if not 0 <= VOLTAGE_ALARM_THRESHOLD <= 3300:
        raise ValueError(f"Voltage threshold must be between 0-3300mV: {VOLTAGE_ALARM_THRESHOLD}")

    if not 0 <= LINK_ALARM_THRESHOLD <= 100:
        raise ValueError(f"Link quality threshold must be between 0-100: {LINK_ALARM_THRESHOLD}")

    # Validate image files exist
    image_files = [
        LINE_ICON, LINE_LEFT_BAR_ICON_1, LINE_LEFT_BAR_ICON_3,
        GROUP_TAB, GROUP_TAB_ACTIVATED, TARGET_GROUP_NAME,
        INPUT_BOX, CALL_ICON, CALL_SELECTION, START_CALL, CANCEL_CALL
    ]

    missing_files = [img for img in image_files if not Path(img).exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing image files: {', '.join(missing_files)}")

validate_config()