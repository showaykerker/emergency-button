import pyautogui
import pyperclip
import logging
import time

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level

# Create a handler that writes log messages to a file
handler = logging.StreamHandler()

# Create a formatter that includes milliseconds
formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

MOUSE_MOVE_DURATION = 0.1
SLEEP_AFTER_CLICK = 0.2

def save_locate_img(
        target,
        confidence,
        click=False,
        move_before_click=True,
        move_duration=MOUSE_MOVE_DURATION,
        sleep_after_click=SLEEP_AFTER_CLICK):
    try:
        found = pyautogui.locateOnScreen(target, confidence=confidence)
        if not click: return found
        if move_before_click:
            x = found.left + int(found.width // 2)
            y = found.top + int(found.height // 2)
            pyautogui.moveTo(x, y, duration=move_duration)
        pyautogui.click(found)
        time.sleep(sleep_after_click)
        return found
    except pyautogui.ImageNotFoundException:
        return None

def save_input(string, enter=True):
    pyperclip.copy(string)
    pyautogui.hotkey('ctrl', 'v')
    if not enter: return
    pyautogui.hotkey('enter')

def try_start_line_app():
    pyautogui.hotkey('win', 'd')  # show desktop
    pyautogui.hotkey('win')
    save_input('line', True)

def ensure_line_app_opened():
    icon1 = save_locate_img(r"images\line-left-bar-icon-1.png", confidence=0.95)
    if icon1 is not None: return icon1

    line_icon = save_locate_img(r"images\line-icon.png", confidence=0.8, click=True)
    if line_icon is None:
        try_start_line_app()
    while icon1 is None:
        time.sleep(2)
        icon1 = save_locate_img(r"images\line-left-bar-icon-1.png", confidence=0.95)
    return icon1

def wait_for_img(target, confidence=0.8, retry_n=10, retry_interval=2, **kwargs):
    found = save_locate_img(target=target, confidence=confidence, **kwargs)
    if found is not None:
        return found
    for i in range(retry_n):
        time.sleep(retry_interval)
        found = save_locate_img(target=target, confidence=confidence*0.99, **kwargs)
        if found:
            return found
    logger.error(f"Can't locate target {target} after {retry_n} tries in {retry_n * retry_interval} secs.")
    return None

def send_message(msg):
    ensure_line_app_opened()
    
    icon1 = wait_for_img(r"images\line-left-bar-icon-1.png", confidence=0.95)
    icon3 = wait_for_img(r"images\line-left-bar-icon-3.png", confidence=0.95)
    if icon1 is None or icon3 is None: return
    x = icon1.left + int(icon1.width // 2)
    y = int((icon1.top + icon3.top + icon3.height)//2)
    pyautogui.moveTo(x, y, duration=MOUSE_MOVE_DURATION)
    pyautogui.click(x, y)

    group_tab = wait_for_img(r"images\group-tab.png", confidence=0.95, click=True)
    target_group_name = wait_for_img(r"images\target-group-name.png", confidence=0.95, click=True)
    input_box = wait_for_img(r"images\input-box.png", confidence=0.95, click=True)

    if group_tab is None or target_group_name is None or input_box is None: return

    save_input(msg, True)


if __name__ == '__main__':
    send_message("測試一下\n第二行\npyautogui\n嘻嘻")