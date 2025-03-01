import paho.mqtt.client as mqtt
import subprocess
import json
import time
import os
import sys
import logging
from threading import Thread

from send_message import send_message

############ Setup Logger       ############
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

############ MQTT Configuration ############
MQTT_BROKER = "192.168.232.128"
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/#"


############ MQTT Msg Response  ############
BATTERY_ALARM_THRESHOLD = 30    # %
VOLTAGE_ALARM_THRESHOLD = 2400  # mV
LINK_ALARM_THRESHOLD = 60

def compose_message(data):

    msg = f"===== 按鈕觸發：{data.get('topic')} =====\n\n"

    battery = int(data.get('battery') or -1)
    voltage = int(data.get('voltage') or -1)
    linkquality = int(data.get('linkquality') or -1)

    if battery < BATTERY_ALARM_THRESHOLD:
        msg += f'- 電池電力剩下 {battery} %，請盡快更換。\n'
    if voltage < VOLTAGE_ALARM_THRESHOLD:
        msg += f'- 電池電壓剩下 {voltage} mV，可能需要更換。\n'
    if linkquality < LINK_ALARM_THRESHOLD:
        msg += f'- 連線品質不佳： {linkquality}。\n'

    action = data.get('action') or 'error'

    if action == "error":
        msg += f"\n\nerror.\ndata = {data}"

    if action == "double":
        msg += f"- 電池電力： {battery}\n"
        msg += f"- 電池電壓： {voltage}\n"
        msg += f"- 連線品質： {linkquality}\n"

    return msg

############ MQTT Msg callback  ############
def on_message(client, msg):
    msg_text = msg.payload.decode()
    try:
        msg_json = json.loads(msg_text)
        if not "message" in msg_json:
            return
        msg_text = msg_json["message"]
        # z2m:mqtt: MQTT publish: topic 'zigbee2mqtt/btn1', payload '{"action":"single","battery":100,"linkquality":160,"voltage":3000}'
        topic = msg_text.split("zigbee2mqtt")[1].split(",")[0][1:-1]
        data = json.loads(msg_text.split(" ")[-1][1:-1])
        data.update({'topic': topic})
        log.info(f"解析消息: 主題={topic}, 數據={data}")

        send_message(compose_message(data))

    except json.JSONDecodeError:
        log.warning(f"消息不是有效的JSON格式: {msg_text[:100]}")
    except Exception as e:
        log.error(f"處理消息時發生錯誤: {e}")
        log.error(f"消息內容: {msg_text}")

# 主程序
def main():

    # 初始化MQTT客戶端 - 使用新版API避免警告
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    # 設置回調函數
    client.on_connect = lambda client, userdata, flags, rc, properties=None: \
        client.subscribe(MQTT_TOPIC) if rc == 0 else \
        log.error(f"連接MQTT代理失敗，代碼: {rc}")

    client.on_message = lambda client, userdata, msg: \
        on_message(client, msg)

    # 連接到MQTT代理
    try:
        log.info(f"連接到MQTT代理 {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        log.info(f"已訂閱主題: {MQTT_TOPIC}")
        log.info("程序已啟動，等待MQTT消息...")

        # 保持程序運行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("接收到停止信號，正在關閉...")
        finally:
            # 清理資源
            client.loop_stop()
            client.disconnect()
            log.info("程序已關閉")
    except Exception as e:
        log.error(f"連接MQTT代理失敗: {e}")

if __name__ == "__main__":

    main()