# 部署與技術細節

## 系統架構

整個系統由兩部分組成：

1. **Ubuntu VM** - 連接Zigbee USB Dongle (Coordinator) 並運行MQTT broker
   - 運行 mosquitto MQTT Server
   - 運行 [zigbee2mqtt](https://www.zigbee2mqtt.io/)，可以在 host 上以網頁介面進行 Zigbee 設備的連接設定。
   - 處理無線按鈕訊號
   - 透過MQTT協議發佈按鈕事件
   - 需有對 Zigbee USB Dongle 的控制權

2. **Windows 應用程式** - 訂閱MQTT消息並操作LINE
   - 接收來自 zigbee2mqtt 的按鈕觸發事件
   - 以 PyAutoGUI 自動化操作LINE桌面應用程式
   - 在特定的群組發送Line訊息或撥打Line語音
   - Line 操作失敗時發送 Discord 訊息通知

- 選用 Ubuntu 是因為 Zigbee USB Dongle 在 Windows 上的驅動支援不佳，因此以虛擬機的方式處理，並使用 systemd 與 docker compose 自動開啟 Zigbee2MQTT 及 Mosquitto Server。
- 選用 Windows 作為 Host 則是因為 Line APP 原生支援 Windows ，擁有較高的穩定性。
- 選用 Line 是因為大部分台灣人手機都有安裝，使用上阻力較小，只有在 Line 發送失敗時傳送通知到 Discord 頻道，只有管理人員需要額外安裝 Discord。若可以全部使用 Discord ，整個系統能夠更精簡穩定，使用一片約4000元內的 Raspberry Pi 且不需要 Windows 系統即可。


## 快速開始

### 準備工作

需要準備：
- 一台Windows電腦，安裝LINE桌面版
- VMware虛擬機，運行Ubuntu
- Zigbee無線按鈕
   - 本專案以 `Sonoff SNZB-01` 開發
- Zigbee協調器
   - 本專案以 `Sonoff 3.0 USB Dongle Plus ZBDongle-E` 開發
   - 產品序號為 `4410700XX` (與Driver和zigbee2mqtt模式設定(`serial:adpter`)有關)

### 設置步驟

1. **Ubuntu虛擬機設置**
   - 請參照 [ubuntu/README.md](ubuntu/README.md) 設置MQTT和Zigbee2MQTT
   - 配對無線按鈕到系統中 (可在 Windows 上執行)

2. **Windows應用程式設置**
   - 請參照 [windows/README.md](windows/README.md) 設置LINE自動化應用
   - 依需求變更圖片以達到更好的辨識效果

3. **測試系統**
   - 按下無線按鈕
   - 確認LINE群組收到相應消息或來電

## 專案架構

```
hch-emergency-button/
│
├── ubuntu/                         # Ubuntu VM 端相關設定和文件
│   ├── docker-compose.yaml         # Docker 組合設定
│   ├── mosquitto/                  # Mosquitto 設定與 runtime 資料儲存
│   ├── zigbee2mqtt/                # Zigbee2MQTT 設定與 runtime 資料儲存
│   ├── docker-compose.yaml/        # Zigbee2MQTT 設定與 runtime 資料儲存
│   ├── mosquitto-zigbee2mqtt-docker-compose.service
│   └── README.md                   # Ubuntu 端設定說明
│
├── windows/                        # Windows 端應用程式
│   ├── config.py                   # 配置文件
│   ├── main.py                     # 主應用程式入口
│   ├── mqtt_connection.py          # MQTT 連接處理
│   ├── message_handler.py          # 消息解析和處理
│   ├── message_processor.py        # 消息隊列處理
│   ├── line_messenger.py           # LINE 操作自動化
│   ├── logger/                     # 日誌系統
│   |   ├── discord_bot_handler.py  # Discord bot handler 實作
│   |   ├── commands.py             # Discord slash commands 實作
│   |   ├── setup_logger.py         # Logger 實作
│   |   └── README.md               # Logger 設定說明
│   ├── images/                     # LINE 界面截圖
│   ├── start.bat                   # 啟動腳本
│   └── README.md                   # Windows 端應用程式設定說明
│
└── README.md                       # 本說明文件
```

## 故障排除

### Ubuntu 端問題

- 檢查Zigbee協調器是否被正確識別 (`ls -l /dev/ttyACM*`)
- 檢查Docker服務是否正常運行 (`sudo systemctl status docker`)
- 查看系統日誌 (`sudo journalctl -f`)

### Windows 端問題

- 確認可以ping通Ubuntu VM (`ping [Ubuntu IP]`)
- 檢查MQTT端口是否開放 (`telnet [Ubuntu IP] 1883`)
- 檢查LINE應用是否正常啟動
- 檢查`images`目錄中的截圖是否與當前LINE界面匹配
- 查看日誌文件位於 `logs` 目錄

## Reference 
- [How to Flash Firmware on SONOFF ZBDongle-E: Step-by-Step Tutorial](https://sonoff.tech/product-review/tutorial/how-to-flash-firmware-on-sonoff-zbdongle-e-step-by-step-tutorial/)
