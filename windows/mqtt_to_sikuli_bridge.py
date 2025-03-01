import paho.mqtt.client as mqtt
import json
import time
import socket
import os
import sys
import logging
import traceback
from threading import Thread

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("mqtt-sikuli-bridge")

# 配置信息
MQTT_BROKER = "192.168.232.128"
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/#"
SIKULI_SERVER_HOST = "localhost"
SIKULI_SERVER_PORT = 5000

class SikuliClient:
    def __init__(self, host=SIKULI_SERVER_HOST, port=SIKULI_SERVER_PORT):
        """初始化Sikuli客戶端"""
        self.host = host
        self.port = port
        log.info(f"初始化Sikuli客戶端，連接到 {host}:{port}")
        # 檢查服務器是否運行
        self._check_server()
    
    def _check_server(self):
        """檢查Sikuli服務器是否運行"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((self.host, self.port))
                if result == 0:
                    log.info("Sikuli服務器已啟動並運行")
                else:
                    log.warning(f"無法連接到Sikuli服務器 {self.host}:{self.port}")
                    log.warning("請確保SikuliServer正在運行")
        except Exception as e:
            log.error(f"檢查Sikuli服務器時出錯: {e}")
    
    def execute_command(self, *args):
        """向Sikuli服務器發送命令"""
        try:
            # 將參數轉換為空格分隔的字符串
            command = " ".join([str(arg) for arg in args])
            log.info(f"向Sikuli服務器發送命令: {command}")
            
            # 創建套接字連接
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)  # 設置超時為10秒
                s.connect((self.host, self.port))
                
                # 發送命令
                s.sendall((command + "\n").encode())
                
                # 接收響應
                response = s.recv(4096).decode().strip()
                log.info(f"服務器響應: {response}")
                
                return response
        except socket.timeout:
            log.error("連接Sikuli服務器超時")
        except ConnectionRefusedError:
            log.error(f"無法連接到Sikuli服務器 {self.host}:{self.port}，連接被拒絕")
        except Exception as e:
            log.error(f"執行Sikuli命令時出錯: {e}")
            log.error(traceback.format_exc())
        
        return "ERROR: 執行命令失敗"

# MQTT消息處理函數
def on_message(client, sikuli_client, msg):
    msg_text = msg.payload.decode()
    try:
        msg_json = json.loads(msg_text)
        if not "message" in msg_json:
            return
        msg_text = msg_json["message"]
        
        # 解析消息
        # z2m:mqtt: MQTT publish: topic 'zigbee2mqtt/btn1', payload '{"action":"single","battery":100,"linkquality":160,"voltage":3000}' 
        topic = msg_text.split("zigbee2mqtt")[1].split(",")[0][1:-1]
        data = json.loads(msg_text.split(" ")[-1][1:-1])

        log.info(f"解析消息: 主題={topic}, 數據={data}")

        # 發送命令到Sikuli服務器
        # 在單獨的線程中執行，避免阻塞MQTT客戶端
        Thread(target=sikuli_client.execute_command, args=(
            topic,
            data.get("action", ""),
            data.get("battery", ""),
            data.get("voltage", ""),
            data.get("linkquality", "")
        )).start()

    except json.JSONDecodeError:
        log.warning(f"消息不是有效的JSON格式: {msg_text[:100]}")
    except Exception as e:
        log.error(f"處理消息時發生錯誤: {e}")
        log.error(f"消息內容: {msg_text}")
        log.error(traceback.format_exc())

# 主程序
def main():
    log.info("啟動MQTT到Sikuli橋接程序")
    
    # 初始化Sikuli客戶端
    sikuli_client = SikuliClient(SIKULI_SERVER_HOST, SIKULI_SERVER_PORT)
    
    # 初始化MQTT客戶端
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    # 設置回調函數
    client.on_connect = lambda client, userdata, flags, rc, properties=None: \
        client.subscribe(MQTT_TOPIC) if rc == 0 else \
        log.error(f"連接MQTT代理失敗，代碼: {rc}")
    
    # 使用部分應用將sikuli_client傳遞給on_message回調
    client.on_message = lambda client, userdata, msg: \
        on_message(client, sikuli_client, msg)
    
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
        log.error(traceback.format_exc())

if __name__ == "__main__":
    # 如果有命令行參數，可以覆蓋默認設置
    if len(sys.argv) > 1:
        MQTT_BROKER = sys.argv[1]
    if len(sys.argv) > 2:
        SIKULI_SERVER_HOST = sys.argv[2]
    if len(sys.argv) > 3:
        SIKULI_SERVER_PORT = int(sys.argv[3])
    
    main()