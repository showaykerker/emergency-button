# MQTT to LINE Messaging Bridge

這個專案實現了一個橋接系統，將 MQTT 訊息轉發到 LINE 聊天群組。
系統使用 PyAutoGUI 實現自動化 UI 交互，模擬使用者操作 LINE 桌面應用程式，從而發送訊息。

## 功能

- 訂閱 MQTT 主題並解析來自 Zigbee2MQTT 的訊息
- 自動化開啟 LINE 應用程式並導航到目標聊天群組
- 根據 MQTT 訊息內容
	- 單擊自動生成內容並發送訊息
	- 雙擊自動生成詳細內容並發送訊息
	- 長按發送通話
- 監控設備電池電量、電壓和連線品質
- 提供自動重連機制、錯誤處理和日誌記錄
- 支援命令行配置參數

## 系統需求

- Python 3.6+
- LINE 桌面應用程式
- Windows 作業系統（因為使用 PyAutoGUI 自動化 Windows 應用程式）

## 安裝步驟

1. Clone 本專案或下載源碼：

2. 安裝所需套件：

```bash
pip install -r requirements.txt
```

3. 視需要設置 LINE 聊天群組截圖：

- 在 `images` 目錄中放置必要的截圖：
  - `call-icon.png`
  - `call-selection.png`
  - `start-call.png`
  - `cancel-call.png`
  - `group-tab-activated.png` - 群組標籤已被選中的圖示
  - `group-tab.png` - 群組標籤
  - `input-box.png` - 訊息輸入框
  - `line-icon.png` - LINE 應用程式圖示
  - `line-left-bar-icon-1.png` - LINE 左側導航列的第一個圖示
  - `line-left-bar-icon-3.png` - LINE 左側導航列的第三個圖示
  - `target-group-name.png` - **目標群組名稱** (應該只需要設定這個)

## 使用方法

1. 啟動程式：

```bash
python mqtt_client.py
```

2. 使用命令行參數自定義設置：

```bash
python mqtt_client.py --broker 192.168.1.100 --port 1883 --topic "zigbee2mqtt/#" --battery-threshold 25
```

可用命令行參數：
- `--broker` - MQTT 代理伺服器地址
- `--port` - MQTT 代理伺服器端口
- `--topic` - 訂閱的 MQTT 主題
- `--battery-threshold` - 電池電量警告閾值 (%)
- `--voltage-threshold` - 電池電壓警告閾值 (mV)
- `--link-threshold` - 連線品質警告閾值

## 檔案結構

```
hch-emergency-button/
│
├── config.py              # 配置文件
├── mqtt_client.py         # 主MQTT客戶端
├── line_messenger.py      # LINE消息發送模塊
├── logger.py
├── images/                # 圖像文件夾
│   ├── call-icon.png
│   ├── ...
│   ├── ...
│   └── target-group-name.png
└── README.md              # 說明文件
```

## 測試

執行單獨的 LINE 訊息發送測試：

```bash
python line_messenger.py
```

這將嘗試打開 LINE 並發送測試訊息。

## 注意事項

1. 使用此程式時，請確保：
   - LINE 桌面應用程式已安裝
   - 已登入 LINE 帳號
   - 截圖適合當前顯示器解析度和 LINE 界面
   
2. 由於使用圖像識別自動化 UI，請避免：
   - 在程式運行時干擾滑鼠操作
   - 更改 LINE 界面主題或樣式
   - 縮放或調整 LINE 窗口大小

## 錯誤排除

如果消息發送失敗，請檢查：

1. 所有截圖是否仍然匹配當前界面
2. 檢查日誌文件，位於 `logs` 目錄
3. 確保 LINE 應用程式正常運行且未更新界面
