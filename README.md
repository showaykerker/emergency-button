# 無線按鈕轉LINE通知系統

本專案實作了一個將Zigbee無線按鈕的動作轉換為LINE群組的通知或通話的系統。

## 功能特色

- **多種觸發模式** (可由[config](windows/config.py)改變行為)
  - 單擊：發送普通通知訊息
  - 雙擊：撥打LINE群組電話
  - 長按：發送包含詳細診斷資訊的測試訊息

- **設備健康監控**
  - 電池電量監測與低電量警告
  - 訊號品質監測
  - 電池電壓監測

- **系統可靠性設計**
  - 消息隊列確保並發處理
  - 自動重連機制
  - 完整的錯誤處理
  - 詳細日誌記錄


## 開始使用
1. 開啟桌面上的 `VMware Workstation 17 Player` 並點選 Ubuntu，然後縮到最小放著不管。注意，如果沒有縮到最小，有一點可能會影響到自動化操作。
2. 打開 `Line`並且登入。請一定要確認登入，不然後續什麼都沒辦法傳出去。
3. 點選 `start.bat` ，這個執行檔會檢查 Ubuntu VM 以及 Line 是否被開啟。但是它無法檢查 Line 是否登入，因此請人工確保。若依竊沒問題，畫面上會出現 Log 的資訊，如果沒有什麼 Error 的話，應該就是一切正常。
4. 可以把 `Line` 的程式打開，不要有任何東西遮擋，這樣可以加快收到按鈕訊息到傳送訊息之間的時間。

## 設定
- USB Dongle 有兩種模式，外觀一樣但用途不同
  - Coordinator 需插在電腦上
  - 訊號延伸器可以使用一般 5V 充電器供電,建議放在連線品質 60~100 的地方作為訊號延伸。
- 裝置配對、設定、檢查：點選桌面上 `Zigbee2MQTT` 的網頁捷徑，如果 Ubuntu VM 已經被開啟的話，這個網頁點開會是設定的頁面。
  - **配對**：點選上方「允許裝置加入(全部)」，並將裝置進入配對模式
    - 按鈕的配對模式通常是(用pin針)按著`RST`一段時間，以 `Sonoff SNZB-01` 來說，需要按到紅燈閃爍一下，再多一下下，接著會看到畫面上跳出配對成功通知。
    - `訊號延伸器`只要在範圍內且沒有被加入其他 zigbee 網路，就可以直接被找到並加入。
  - **設定**：「裝置」頁面中，每個裝置右邊有四個圖標
    - 重新命名裝置：在按鈕上的話，會改變 Line 訊息的標題 `===== 按鈕觸發：[按鈕名稱] =====`
    - interview：會重新確認裝置是否存在
  - **檢查**：在「網路圖」頁面中，點選「載入網路拓樸圖」，會開始檢查網路中的每個節點，通常可以用這個判斷`訊號延伸器`位置是否OK以及按鈕距離是否過遠。

## 已知問題
- 有提供送出通話的功能，預設是雙擊的行為，在通話中的情況下再次雙擊則會取消通話，但是如果兩次雙擊的時間間格太短，有可能會失敗，需要再一次雙擊並等待前一次的 timeout 結束。
- 如果 Line 沒有登入的話會沒辦法送出任何東西，可以另外架一個 discord bot 處理，但目前還沒有。
- 連線品質跟距離不是線性的，會跟地形、室內格局還有障礙物等有關。

## 客製化設定

### 按鈕行為設定

在 `windows/config.py` 中，可以修改 `BUTTON_ACTION_BEHAVIOR` 字典來自定義單擊、雙擊和長按的行為：

```python
BUTTON_ACTION_BEHAVIOR = {  # "send", "call", "debug"
    "single": "send",  # 單擊發送消息
    "double": "call",  # 雙擊撥打電話
    "long"  : "debug"  # 長按發送診斷消息
}
```

### 警報閾值設定

可以調整以下閾值來控制何時發出設備狀態警告：

```python
BATTERY_ALARM_THRESHOLD = 30    # 電池電量(%)
VOLTAGE_ALARM_THRESHOLD = 2400  # 電池電壓(mV)
LINK_ALARM_THRESHOLD = 60       # 連接品質
```

由於測試時間還沒有到讓電池下降的程度，因此這個部分可能需要依據情況修改。

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
- [Zigbee network optimization: a how-to guide for avoiding radio frequency interference + adding Zigbee Router devices (repeaters/extenders) to get a stable Zigbee network mesh with best possible range and coverage by fully utilizing Zigbee mesh networking](https://community.home-assistant.io/t/zigbee-network-optimization-a-how-to-guide-for-avoiding-radio-frequency-interference-adding-zigbee-router-devices-repeaters-extenders-to-get-a-stable-zigbee-network-mesh-with-best-possible-range-and-coverage-by-fully-utilizing-zigbee-mesh-networking/515752)