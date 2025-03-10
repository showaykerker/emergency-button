# 無線按鈕轉LINE通知系統

本專案實作了一個將Zigbee無線按鈕的動作轉換為LINE群組的通知或通話的系統。

## 功能特色

- **多種觸發模式** (可由 [config](windows/config.py) 改變行為)
    - 單擊：發送通知訊息並撥打Line群組電話，在30秒後若沒有手動取消則自動取消(可在[config](windows/config.py)中修改秒數)
    - 雙擊：取消撥打電話
    - 長按：發送包含詳細診斷資訊的測試訊息
- **設備健康監控**
    - 電池電量監測與低電量警告
    - 訊號品質監測
    - 電池電壓監測
- **系統可靠性設計**
    - 消息隊列確保並發處理：一個訊息傳送完才會傳送下一個
    - 自動重連機制
    - 完整的錯誤處理
    - 詳細日誌記錄
    - Discord Bot 錯誤通知 - 在 Line 無法使用的時候


## 開始使用
1. 開啟桌面上的 `VMware Workstation 17 Player` 並點選 Ubuntu，然後縮到最小放著不管。注意，如果沒有縮到最小，有一點可能會影響到自動化操作。
2. 打開 `Line`並且登入。
3. 點選 `start.bat` ，這個執行檔會檢查 `Ubuntu VM` 以及 `Line` 的 App 是否啟動。
4. 檢查結束後 `Line` 會被至於最頂，盡量保持不要有任何東西遮擋，這樣可以加快收到按鈕訊息到傳送訊息之間的時間。若 `Line` 沒登入的話，畫面會顯示「**LINE IS NOT LOGGED IN !!! PLEASE LOG IN AND MANUALLY RESTART.**」。 須關閉視窗後登入 `Line` 並且重新執行 `start.bat` 。若一切沒問題，畫面上會出現 Log 的資訊，如果沒有什麼 Error 的話，應該就是都正常。
5. 已經設定讓電腦不休眠，請**把螢幕關閉就好**，不要讓它自動鎖定。

## 必要設定
- USB Dongle 有兩種模式，外觀一樣但用途不同
    - `Coordinator` 需插在電腦上
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
- 在通話中的情況下如果手動取消通話的間隔太短，有可能會失敗，需要再一次手動取消或是等前一次的撥打時間結束。
- 如果 `Line` 沒有登入的話會沒辦法送出任何東西，目前可以透過 `Discord Bot` 通知失敗情形。
- 連線品質跟距離不是線性的，會跟地形、室內格局還有障礙物等有關。
- 在 `VM` 開啟的情況下，自動化的快捷鍵會是在 `VM` 裡面執行，造成沒辦法點選到 `Line` 的情況，因此建議打開後最小化。

## 客製化設定

### 按鈕行為設定

在 `windows/config.py` 中，可以修改 `BUTTON_ACTION_BEHAVIOR` 字典來自定義單擊、雙擊和長按的行為：

```python
BUTTON_ACTION_BEHAVIOR = {  # "call", "cancel", "debug"
    "single": "call",    # 單擊撥打電話並發送緊急呼叫訊息
    "double": "cancel",  # 雙擊取消撥打電話並發送取消呼叫訊息
    "long"  : "debug"    # 長按發送診斷消息
}
```

### 警報閾值設定

可以調整以下閾值來控制何時發出設備狀態警告：

```python
BATTERY_ALARM_THRESHOLD = 30    # 電池電量(%)
VOLTAGE_ALARM_THRESHOLD = 2400  # 電池電壓(mV)
LINK_ALARM_THRESHOLD = 60       # 連接品質
```

由於測試時間還沒有長到讓電池下降的程度，因此這個部分可能需要依據情況修改。

### Discord Bot 開啟 / 關閉

```python
ENABLE_DISOCRD_BOT_LOGGING = True
```

## 故障排除

1. 檢查LINE應用是否正常啟動
2. 檢查運行主程式的介面中有沒有 ERROR
    - 這邊待遇到後補充
3. 關閉 `start.bat` 的執行頁面並重新開啟，確認沒有跳出 Error
4. 重新開啟 Ubuntu VM：
    1. `VMware Workstation 17 Player` -> 左上角 `Player` -> `Power` -> `Restart Guest`
    2. 關閉 `start.bat` 的執行頁面並重新開啟，確認沒有跳出 Error
5. 重新開機，所有系統重新開一次。

## Reference
- [Zigbee network optimization: a how-to guide for avoiding radio frequency interference + adding Zigbee Router devices (repeaters/extenders) to get a stable Zigbee network mesh with best possible range and coverage by fully utilizing Zigbee mesh networking](https://community.home-assistant.io/t/zigbee-network-optimization-a-how-to-guide-for-avoiding-radio-frequency-interference-adding-zigbee-router-devices-repeaters-extenders-to-get-a-stable-zigbee-network-mesh-with-best-possible-range-and-coverage-by-fully-utilizing-zigbee-mesh-networking/515752)