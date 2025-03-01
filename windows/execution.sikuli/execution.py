# -*- coding: utf-8 -*-

import sys

TEST_HARDWARE_ALARM = True

action = "single"
topic = "N/A"
battery = "N/A"
voltage = "N/A"
linkquality = "N/A"

battery_alarm_threshold = 30  # 30%
voltage_alarm_threshold = 2400  # mV
linkquality_alarm_threshold = 100  #

print(sys.argv)

if len(sys.argv) == 6:
    try:
        topic = sys.argv[1]
        action = sys.argv[2]
        battery = int(sys.argv[3])
        voltage = int(sys.argv[4])        
        linkquality = int(sys.argv[5])

    except Exception as e:
        print(e)

firstIconImg = Pattern("1740397041503.png").similar(0.95)
groupLabel = Pattern("1740397860611.png").similar(0.84)
groupNameLabel = "1740397972095.png"


def compose_message():
    msg = u"[按鈕觸發 - " + topic + "]\n"
    if battery != "N/A" and battery < battery_alarm_threshold:
        msg += u"- 偵測到電池電力不足：" + str(battery) + u", 請盡速更換。\n"
    if voltage != "N/A" and voltage < voltage_alarm_threshold:
        msg += u"- 偵測到電池電壓不足：" + str(voltage) + u", 請盡速更換。\n"    
    if linkquality != "N/A" and linkquality < linkquality_alarm_threshold:
        msg += u"- 偵測到連線品質不佳：" + str(linkquality) + u"。\n"

    if action == "double":  # Debug Mode
        msg += u"===== 按鈕資訊 =====\n"
        msg += u"- 電池　　：" + str(battery) + " %\n"
        msg += u"- 電壓　　：" + str(voltage) + " mA\n"
        msg += u"- 連線品質：" + str(linkquality) + "\n"

    return msg 

def key_press(target):
    keyDown(target)
    keyUp(target)

def confirm_line_started():
    if not exists(firstIconImg):
        print("Opening App")
        openApp("C:\\Users\\TZwayne\\AppData\\Local\\LINE\\bin\\LineLauncher.exe")
    wait(firstIconImg, 99)

def navigate_to_group_chat():
    # Step 1: Select Chat Page
    # There might be notification indicator on the chat page icon
    # so we use the middle of the first and the third icon here.
    firstIcon = find(firstIconImg)
    thirdIcon = find( Pattern("thirdIcon.png").similar(0.95))
    targetX = firstIcon.getX()
    firstIconY = firstIcon.getY()
    thirdIconY = thirdIcon.getY()
    targetY = (firstIconY + thirdIconY) // 2

    click(Location(targetX + 18, targetY + 8))

    # Step 2: Sequentially select group label -> group name
    # and the input area.
    wait(groupLabel, 99)
    click(groupLabel)
    click(groupNameLabel)
    textInputRegion = "1740398567221.png"
    wait(textInputRegion, 99)
    click(textInputRegion)

def send_message():
    # Step 3: Enter message and send
    paste(unicode(compose_message(), "utf8"))
    key_press(Key.ENTER)


confirm_line_started()
navigate_to_group_chat()
send_message()