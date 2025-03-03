"""
LINE messaging module for automated UI interactions.
"""
import pyautogui
import pyperclip
import time
import os

from logger import setup_logger
import config

# Setup logger
logger = setup_logger("line_msngr")

class LineUIException(Exception):
    """Exception raised for errors in LINE UI interactions."""
    pass

class LineMessenger:
    """
    Handles automated interactions with LINE desktop application.
    Uses image recognition to navigate the interface and send messages.
    """

    def __init__(self):
        # Cache for UI element locations
        self.ui_cache = {}
        self.cache_lifetime = config.IMAGE_CACHE_LIFETIME  # seconds
        self.cache_timestamps = {}
        self.ensure_line_app_opened()

    def locate_on_screen(self, target, confidence=None, click=False,
                        move_before_click=True, cache_key=None):
        """
        Locate an image on screen, optionally click it, and cache the result.

        Args:
            target (str): Path to the target image
            confidence (float): Recognition confidence (0-1)
            click (bool): Whether to click the found location
            move_before_click (bool): Whether to move mouse before clicking
            cache_key (str): Key to cache the result under

        Returns:
            Box: Found location box or None if not found
        """
        confidence = confidence or config.IMAGE_SEARCH_CONFIDENCE

        # Check cache if a cache key is provided
        if cache_key is not None:
            current_time = time.time()
            if (cache_key in self.ui_cache and
                current_time - self.cache_timestamps.get(cache_key, 0) < self.cache_lifetime):
                found = self.ui_cache[cache_key]
                logger.debug(f"Using cached location for {target} ({cache_key})")

                if click:
                    self._click_location(found, move_before_click)
                return found

        try:
            logger.debug(f"Looking for {target} with confidence {confidence}")
            found = pyautogui.locateOnScreen(target, confidence=confidence)

            if found:
                logger.debug(f"Found {target} at {found}")

                # Cache the result if a cache key is provided
                if cache_key is not None:
                    self.ui_cache[cache_key] = found
                    self.cache_timestamps[cache_key] = time.time()

                if click:
                    self._click_location(found, move_before_click)

                return found
            return None
        except pyautogui.ImageNotFoundException:
            logger.debug(f"Image not found: {target}")
            return None
        except Exception as e:
            logger.error(f"Error locating image {target}: {e}")
            return None

    def _click_location(self, location, move_before_click=True):
        """
        Click at the specified location.

        Args:
            location: PyAutoGUI box location
            move_before_click: Whether to move mouse before clicking
        """
        try:
            if move_before_click:
                x = location.left + int(location.width // 2)
                y = location.top + int(location.height // 2)
                logger.debug(f"Moving to {x}, {y}")
                pyautogui.moveTo(x, y, duration=config.MOUSE_MOVE_DURATION)

            pyautogui.click(location)
            logger.debug(f"Clicked at {location}")
            time.sleep(config.SLEEP_AFTER_CLICK)
        except Exception as e:
            logger.error(f"Error clicking location {location}: {e}")

    def wait_for_image(self, target, confidence=None, retry_n=None, retry_interval=None,
                      timeout=None, click=False, move_before_click=True, cache_key=None):
        """
        Wait for an image to appear on screen with timeout and retry logic.

        Args:
            target (str): Path to the target image
            confidence (float): Recognition confidence (0-1)
            retry_n (int): Number of retries
            retry_interval (float): Seconds between retries
            timeout (float): Maximum seconds to wait
            click (bool): Whether to click the found location
            move_before_click (bool): Whether to move mouse before clicking
            cache_key (str): Key to cache the result under

        Returns:
            Box: Found location box or None if not found
        """
        confidence = confidence or config.IMAGE_SEARCH_CONFIDENCE
        retry_n = retry_n or config.IMAGE_RETRY_COUNT
        retry_interval = retry_interval or config.IMAGE_RETRY_INTERVAL
        timeout = timeout or config.IMAGE_SEARCH_TIMEOUT

        start_time = time.time()

        # First attempt
        found = self.locate_on_screen(target, confidence, click, move_before_click, cache_key)
        if found is not None:
            return found

        # Retry logic
        for i in range(retry_n):
            if time.time() - start_time > timeout:
                logger.warning(f"Timeout waiting for {target} after {timeout} seconds")
                return None

            logger.debug(f"Waiting for {target}, attempt {i+1}/{retry_n}")
            time.sleep(retry_interval)

            # Gradually decrease confidence for more flexibility
            adjusted_confidence = max(0.6, confidence * (0.99 ** i))

            found = self.locate_on_screen(target, adjusted_confidence, click,
                                         move_before_click, cache_key)
            if found:
                return found

        logger.warning(f"Failed to find {target} after {retry_n} attempts")
        return None

    def input_text(self, text, enter=True):
        """
        Input text using clipboard to support special characters.

        Args:
            text (str): Text to input
            enter (bool): Whether to press Enter after inputting
        """
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            logger.debug(f"Input text (length: {len(text)})")

            if enter:
                time.sleep(0.1)  # Small delay before pressing Enter
                pyautogui.press('enter')
                logger.debug("Pressed Enter")
        except Exception as e:
            logger.error(f"Error inputting text: {e}")

    def start_line_app(self):
        """
        Start the LINE application if it's not already running.
        """
        try:
            logger.info("Attempting to start LINE application")
            pyautogui.hotkey('win', 'd')  # Show desktop
            time.sleep(0.2)
            pyautogui.press('win')        # Open start menu
            time.sleep(0.2)
            self.input_text('line', True) # Search for LINE and press Enter
            logger.info("\tLINE app start command sent")
        except Exception as e:
            logger.critical(f"\tError starting LINE app: {e}")
            raise LineUIException("Failed to start LINE application") from e

    def shutdown_if_line_not_logged_in(self):
        line_login = self.locate_on_screen(config.LINE_LOGIN, confidence=0.5)
        if line_login is not None:
            logger.critical("LINE IS NOT LOGGED IN !!! PLEASE LOG IN AND MANUALLY RESTART.")
            input("\nPress Enter to Stop....\n\n")
            exit(0)

    def found_line_logged_in_and_started(self):
        self.shutdown_if_line_not_logged_in()
        icon1 = self.locate_on_screen(config.LINE_LEFT_BAR_ICON_1)
        icon3 = self.locate_on_screen(config.LINE_LEFT_BAR_ICON_3)
        group_tab = self.locate_on_screen(config.GROUP_TAB, cache_key="group_tab", confidence=0.9993)
        group_tab_activated = self.locate_on_screen(config.GROUP_TAB_ACTIVATED, cache_key="group_tab_activated", confidence=0.9993)
        logger.debug(f"group_tab: {bool(group_tab)}, group_tab_activated: {bool(group_tab_activated)}")
        return (icon1 or icon3) and (group_tab or group_tab_activated)
        # return icon1 is not None or group_tab is not None or group_tab_activated is not None

    def ensure_line_app_opened(self, max_attempts=3):
        """
        Ensure the LINE application is open and visible.

        Args:
            max_attempts (int): Maximum number of attempts to start LINE

        Returns:
            bool: True if LINE is open, False otherwise

        Raises:
            LineUIException: If LINE cannot be opened after max attempts
        """
        logger.info("Checking if LINE app is open")

        # Try to find the LINE app window
        for attempt in range(max_attempts):
            if self.found_line_logged_in_and_started():
                logger.info("\tLINE app is already open. ")
                return True

            # Try to find and click LINE icon on desktop/taskbar
            line_icon = self.locate_on_screen(config.LINE_ICON, confidence=0.9, click=True)
            if line_icon is None and attempt < max_attempts - 1:
                logger.warning(f"\tLINE icon not found, attempting to start LINE (attempt {attempt+1}/{max_attempts})")
                self.start_line_app()

            # Wait for LINE to open
            wait_start = time.time()
            while time.time() - wait_start < 30:  # 15-second timeout for app to open
                if self.found_line_logged_in_and_started():
                    logger.info(f"\tLINE app opened successfully after attempt {attempt+1}.")
                    return True
                logger.info(f"\tSleep for 0.5 seconds to wait for line to open")
                time.sleep(0.5)

            if self.found_line_logged_in_and_started():
                logger.info(f"\tLINE app opened successfully after attempt {attempt+1}.")
                return True

        logger.critical("Failed to open LINE app after multiple attempts.")
        raise LineUIException("Could not open LINE application after multiple attempts")

    def navigate_to_target_group(self):
        """
        Navigate to the target chat group in LINE.

        Returns:
            bool: True if successfully navigated, False otherwise
        """
        logger.info("\tNavigating to target chat group")

        try:
            group_tab = self.locate_on_screen(config.GROUP_TAB, cache_key="group_tab", confidence=0.9993)
            group_tab_activated = self.locate_on_screen(config.GROUP_TAB_ACTIVATED, cache_key="group_tab_activated", confidence=0.9993)
            if bool(group_tab) == bool(group_tab_activated):
                logger.warning("\t\tGroup Tab activate status not clear here.")

            if group_tab is None and group_tab_activated is None:
                logger.info("\t\tgroup tabs not found, click on left bar first!")
                # Find the chat navigation area in the left sidebar
                icon1 = self.wait_for_image(config.LINE_LEFT_BAR_ICON_1, cache_key="left_bar_icon_1")
                icon3 = self.wait_for_image(config.LINE_LEFT_BAR_ICON_3, cache_key="left_bar_icon_3")

                if icon1 is None or icon3 is None:
                    logger.error("\t\tCould not find LINE navigation icons")
                    return False

                # Click in the middle of the chat area to focus
                x = icon1.left + int(icon1.width // 2)
                y = int((icon1.top + icon3.top + icon3.height)//2)
                logger.debug(f"\t\tClicking chat area at {x}, {y}")
                pyautogui.moveTo(x, y, duration=config.MOUSE_MOVE_DURATION)
                pyautogui.click(x, y)
                time.sleep(config.SLEEP_AFTER_CLICK)
            else:
                logger.debug(f"\t\tAlready found group tabs, skip. "\
                    f"group_tab: {bool(group_tab)}, group_tab_activated: {bool(group_tab_activated)}")

            if group_tab_activated is None:
                # Click group tab and select target group
                logger.debug("\t\tgroup tab not activated, click on group tab first.")
                if not self.wait_for_image(config.GROUP_TAB, click=True, cache_key="group_tab", confidence=0.8):
                    logger.error("\t\tCould not find groups tab")
                    return False
            else:
                logger.debug("\t\tgroup tab already activated, skip clicking on group tab")

            logger.debug("\t\twait for group name")

            if not self.wait_for_image(config.TARGET_GROUP_NAME, click=True):
                logger.error("\t\tCould not find target group")
                return False

            logger.debug("\t\twait for input box")

            if not self.wait_for_image(config.INPUT_BOX, click=True):
                logger.error("\t\tCould not find message input box")
                return False

            logger.info("\t\tSuccessfully navigated to target group")
            return True

        except Exception as e:
            logger.error(f"\t\tError navigating to target group: {e}", exc_info=True)
            return False

    def send_message(self, message="", max_retries=2, call_instead=False):
        """
        Send a message to the target chat group in LINE.

        Args:
            message (str): Message text to send
            max_retries (int): Maximum number of retry attempts
            call_instead (bool): Call the group instead of messaging

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if message is None:
            logger.debug(f"send_message Get empty message.")
        else:
            logger.debug(f"send_message length: {len(message)}")

        for attempt in range(max_retries + 1):
            try:

                # If the Cancel call icon exists and get another call_instead
                # We will cancel the call
                if call_instead:
                    if self.locate_on_screen(config.CANCEL_CALL, click=True):
                        logger.info("Cancel Call")
                        return True

                # Ensure LINE is open
                self.ensure_line_app_opened()

                # Navigate to target group
                if not self.navigate_to_target_group():
                    if attempt == max_retries:
                        logger.error("Failed to navigate to target group")
                        return False
                    logger.warning(f"Retrying navigation (attempt {attempt+1}/{max_retries+1})")
                    continue

                if not call_instead:
                    # Input and send message
                    self.input_text(message, True)
                    logger.info("Message sent successfully")
                    return True

                # Call INSTEAD
                logger.info("CALL")
                if not self.wait_for_image(config.CALL_ICON, click=True):
                    logger.error("Could not find call icon.")
                    return False
                if not self.wait_for_image(config.CALL_SELECTION, click=True):
                    logger.error("Could not find call selection.")
                    return False
                if not self.wait_for_image(config.START_CALL, click=True):
                    logger.error("Could not find start call.")
                    return False
                return True

            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Failed to send message after {max_retries+1} attempts: {e}")
                    return False
                logger.warning(f"Error sending message (attempt {attempt+1}/{max_retries+1}): {e}")
                # Clear cache to force fresh UI detection
                self.ui_cache.clear()
                self.cache_timestamps.clear()
                logger.debug(f"Sleep for 2 second before retry")
                time.sleep(2)  # Wait before retry

        return False


# Singleton instance for use throughout the application
messenger = LineMessenger()

def send_message(msg="", call_instead=False):
    """
    Public function to send a message using the LineMessenger.

    Args:
        msg (str): Message to send
        call_instead (bool): Call the group instead of messaging

    Returns:
        bool: True if successful, False otherwise
    """
    return messenger.send_message(message=msg, call_instead=call_instead)


if __name__ == '__main__':
    # Test the messenger
    send_message("Test message\nfrom LineMessenger\n\nTimestamp: " + str(time.time()), call_instead=False)
    # send_message("Test message\nfrom LineMessenger\n\nTimestamp: " + str(time.time()), call_instead=True)