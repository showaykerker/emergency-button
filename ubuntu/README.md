# Deploy Mosquitto Server and Zigbee2Mqtt on Ubuntu

## Prerequisition
- docker 
- docker compose

These 2 can be installed by `sudo snap install docker`. If you install it otherwise, make sure to modify `ExecStart` and `ExecStop` in [systemd service file](mosquitto-zigbee2mqtt-docker-compose.service).

## Installation
1. Make sure content in [zigbee2mqtt configuration](zigbee2mqtt/data/configuration.yaml) is correct, especially serial part.
2. Check [`docker-compose.yaml`](docker-compose.yaml), modify the device part. The coordinator device in the container should be the same as `serial` > `port` in [zigbee2mqtt configuration](zigbee2mqtt/data/configuration.yaml).
3. Try to launch with `docker compose up`.
4. If everything is alright, check [systemd service file](mosquitto-zigbee2mqtt-docker-compose.service) and configure it. Make sure paths, user, group in `[Service]` configurations are all correct. The user here should have the permission to run docker commands.
5. Copy the service file to `/etc/systemd/system`, or symbolically link it.
6. Reload systemd and enable the service: `sudo systemctl daemon-reload && sudo systemctl enable mosquitto-zigbee2mqtt-docker-compose.service`
7. Start the service: `sudo systemctl start mosquitto-zigbee2mqtt-docker-compose.service`

## Check Status
- `sudo systemctl status mosquitto-zigbee2mqtt-docker-compose.service`
- Reboot and see if it can start automatically.

## Pair Wireless Button
1. Open a browser, go to `http://localhost:8080/` and click on `Permit join (All)` at top. The coordinator will enter pairing mode.
2. Have your wireless button go into pairing mode, it will then be shown on the web page.
	- Typically, it requires to press `rst` for a few seconds. Check the button's manual for details.

## Make Sure Everything Works on Ubuntu Side
Check system journal by `sudo journalctl --all -f`, this should show a few logs on the screen.

If you click on the button, a log should be shown.

```
Mar 01 18:39:46 user-VMware-Virtual-Platform docker-compose[11426]: zigbee2mqtt  | [2025-03-01 18:39:46] info: 	z2m:mqtt: MQTT publish: topic 'zigbee2mqtt/btn1', payload '{"action":"single","battery":100,"linkquality":212,"voltage":3000}'
```
