# MQTT to LINE Messaging Bridge

這個專案實作了一個將 MQTT 訊息轉發到 LINE 聊天群組橋接系統。
系統使用 PyAutoGUI 實現 UI 自動化，模擬使用者操作 LINE 桌面應用程式，並發送訊息。

## 功能

- 訂閱 MQTT 主題並解析來自 Zigbee2MQTT 的訊息
- 自動化開啟 LINE 應用程式並點選到目標聊天群組
- 根據 MQTT 訊息內容 (可在[config](config.py)中設置)
	- 單擊自動生成內容並發送訊息
	- 雙擊發送通話
	- 長按自動生成除錯資訊並發送訊息
- 監控設備電池電量、電壓和連線品質
- 提供自動重連機制、錯誤處理和日誌記錄

## 系統需求

- 僅在 Python 3.13 測試
- LINE 桌面應用程式
- Windows 作業系統

## 安裝步驟

1. Clone 本專案或下載原始碼：

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

### 檢查 Ubuntu VM 、 MQTT 及 Line，並啟動程式

點擊 `start_mqtt_client.bat`


## 檔案結構

```
hch-emergency-button/
│
├── main.py                    # 主程式
│
├── config.py                  # 設定檔
│
├── mqtt_connection_handler.py # MQTT連線相關實作
├── message_queue_processor.py # Thread Worker 處理訊息佇列，避免高併發造成影響
├── message_handler.py         # 解讀 MQTT msg，並產生要傳出的訊息
├── line_messenger.py          # LINE消息發送模塊
│
├── logger.py
│
├── images/                    # 圖像文件夾
│   ├── call-icon.png
│   ├── ...
│   ├── ...
│   └── target-group-name.png
├── start.bat
├── requirements.txt
└── README.md                  # 說明文件
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
   - 截圖適合所使用顯示器的**解析度**和 LINE 界面
   
2. 由於使用圖像識別自動化 UI，請避免：
   - 在程式運行時干擾滑鼠操作
   - 更改 LINE 界面主題或樣式
   - 縮放或調整 LINE 窗口大小

3. Ubuntu 虛擬機配置請參考 [../ubuntu/README.md](../ubuntu/README.md)

## 錯誤排除

如果消息發送失敗，請檢查：

1. 所有截圖是否仍然與現在的介面類似
2. 檢查日誌文件，位於 `logs` 目錄
3. 確保 LINE 應用程式正常運行且未更新界面
4. 確保 Ubuntu VM 被開啟 (使用者不須登入)
5. 從 Zigbee2MQTT 的 [Web GUI](http://192.168.108.128:8080) 確認連線狀況
