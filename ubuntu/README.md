# 在 Ubuntu 上部署 Mosquitto Server 和 Zigbee2Mqtt

**機翻自[README-en.md](README-en.md)**

## 前置需求
- docker 
- docker compose

這兩個可透過 `sudo snap install docker` 安裝。若您以其他方式安裝，請確認修改 [systemd 服務檔案](mosquitto-zigbee2mqtt-docker-compose.service) 中的 `ExecStart` 和 `ExecStop`。

## 安裝步驟
1. 確保 [zigbee2mqtt 設定](zigbee2mqtt/data/configuration.yaml) 內容正確，尤其是序列埠部分。
2. 檢查 [`docker-compose.yaml`](docker-compose.yaml)，修改裝置部分。容器中的協調器 (coordinator) 裝置應與 [zigbee2mqtt 配置](zigbee2mqtt/data/configuration.yaml) 中的 `serial` > `port` 相同。
3. 試著用 `docker compose up` 啟動。
4. 若一切正常，檢查 [systemd 服務檔案](mosquitto-zigbee2mqtt-docker-compose.service) 並進行設定。確保 `[Service]` 配置中的路徑、使用者、群組都正確。此處的使用者應具有執行 docker 指令的權限。
5. 複製服務檔案到 `/etc/systemd/system`，或建立符號連結(Symbolic Link)。
6. 重新載入 systemd 並啟用服務：`sudo systemctl daemon-reload && sudo systemctl enable mosquitto-zigbee2mqtt-docker-compose.service`
7. 啟動服務：`sudo systemctl start mosquitto-zigbee2mqtt-docker-compose.service`

## 檢查狀態
- `sudo systemctl status mosquitto-zigbee2mqtt-docker-compose.service`
- 重新啟動系統並確認服務能否自動啟動。

## 配對無線按鈕
1. 開啟瀏覽器，前往 `http://localhost:8080/`，點擊頂部的 `Permit join (All)`。協調器將進入配對模式。
2. 讓您的無線按鈕進入配對模式，它將顯示在網頁上。
   - 通常需要按下 `rst` 按鈕幾秒鐘。請查閱按鈕的使用手冊了解詳細資訊。

## 確認 Ubuntu 端一切正常運作
透過 `sudo journalctl --all -f` 檢查系統日誌，螢幕上應該會顯示一些記錄。

如果您按下按鈕，應該會顯示如下記錄：

```
Mar 01 18:39:46 user-VMware-Virtual-Platform docker-compose[11426]: zigbee2mqtt  | [2025-03-01 18:39:46] info: 	z2m:mqtt: MQTT publish: topic 'zigbee2mqtt/btn1', payload '{"action":"single","battery":100,"linkquality":212,"voltage":3000}'
```