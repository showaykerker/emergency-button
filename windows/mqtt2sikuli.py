import paho.mqtt.client as mqtt
import json
import time
import os
import sys
import logging
import subprocess
from threading import Thread
import traceback
from concurrent.futures import ThreadPoolExecutor

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("mqtt-sikuli")

# 配置信息
MQTT_BROKER = "192.168.232.128"
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/#"
SIKULI_JAR = r".\sikulixapi-2.0.5-win.jar"
SIKULI_SCRIPT_FOLDER = r".\execution.sikuli"

# 使用線程池和單一Java進程的Sikuli執行器
class SikuliRunner:
    def __init__(self, max_workers=2):
        log.info(f"初始化Sikuli執行器，使用JAR: {SIKULI_JAR}, 最大並行工作數: {max_workers}")
        
        if not os.path.exists(SIKULI_JAR):
            log.error(f"找不到Sikuli JAR文件: {SIKULI_JAR}")
            return
            
        # 創建Python線程池
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        log.info(f"Python線程池初始化成功，大小: {max_workers}")
        
        # 啟動單一Java進程來保持JVM運行（可選）
        # 這個方法不是必須的，但可以預熱JVM
        self._warmup_jvm()
    
    def _warmup_jvm(self):
        """預熱JVM以減少首次運行的延遲"""
        try:
            log.info("預熱JVM...")
            cmd = ['java', '-version']
            subprocess.run(cmd, capture_output=True, text=True)
            log.info("JVM預熱完成")
        except Exception as e:
            log.error(f"預熱JVM時發生錯誤: {e}")
    
    def run_script(self, *args):
        """使用線程池執行Sikuli腳本，傳入參數"""
        return self.executor.submit(self._execute_script, *args)
    
    def _execute_script(self, *args):
        """實際執行Sikuli腳本的方法"""
        try:
            # 準備命令行參數
            cmd = ['java', '-jar', SIKULI_JAR, '-r', SIKULI_SCRIPT_FOLDER, '--']
            for arg in args:
                cmd.append(str(arg))
            
            log.info(f"執行Sikuli腳本: {' '.join(cmd)}")
            
            # 使用subprocess執行命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 捕獲輸出
            for line in process.stdout:
                log.info(f"Sikuli輸出: {line.strip()}")
            
            # 等待進程結束
            exit_code = process.wait()
            log.info(f"腳本執行完成，返回值: {exit_code}")
            
            return exit_code
        except Exception as e:
            log.error(f"執行腳本時發生錯誤: {e}")
            log.error(traceback.format_exc())
            return -1

# MQTT消息處理函數
def on_message(client, sikuli_runner, msg):
    msg_text = msg.payload.decode()
    try:
        msg_json = json.loads(msg_text)
        if not "message" in msg_json:
            return
        msg_text = msg_json["message"]
        # z2m:mqtt: MQTT publish: topic 'zigbee2mqtt/btn1', payload '{"action":"single","battery":100,"linkquality":160,"voltage":3000}' 
        topic = msg_text.split("zigbee2mqtt")[1].split(",")[0][1:-1]
        data = json.loads(msg_text.split(" ")[-1][1:-1])

        log.info(f"解析消息: 主題={topic}, 數據={data}")

        # 執行Sikuli腳本（不等待結果）
        sikuli_runner.run_script(
            topic,
            data.get("action"),
            data.get("battery"),
            data.get("voltage"),
            data.get("linkquality")
        )

    except json.JSONDecodeError:
        log.warning(f"消息不是有效的JSON格式: {msg_text[:100]}")
    except Exception as e:
        log.error(f"處理消息時發生錯誤: {e}")
        log.error(f"消息內容: {msg_text}")
        log.error(traceback.format_exc())

# 主程序
def main():
    log.info("啟動MQTT到Sikuli橋接程序 (使用Python線程池)")
    
    # 初始化Sikuli執行器，設置最大並行工作數
    sikuli_runner = SikuliRunner(max_workers=2)
    
    # 初始化MQTT客戶端
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    # 設置回調函數
    client.on_connect = lambda client, userdata, flags, rc, properties=None: \
        client.subscribe(MQTT_TOPIC) if rc == 0 else \
        log.error(f"連接MQTT代理失敗，代碼: {rc}")
    
    # 使用部分應用將sikuli_runner傳遞給on_message回調
    client.on_message = lambda client, userdata, msg: \
        on_message(client, sikuli_runner, msg)
    
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
            
            # 關閉Python線程池
            log.info("關閉線程池...")
            sikuli_runner.executor.shutdown()
            
            log.info("程序已關閉")
    except Exception as e:
        log.error(f"連接MQTT代理失敗: {e}")
        log.error(traceback.format_exc())

if __name__ == "__main__":
    # 如果有命令行參數，可以覆蓋默認設置
    if len(sys.argv) > 1:
        MQTT_BROKER = sys.argv[1]
    if len(sys.argv) > 2:
        SIKULI_JAR = sys.argv[2]
    
    main()