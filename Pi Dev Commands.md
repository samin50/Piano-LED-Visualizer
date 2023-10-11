## Connection
```bash
pi@172.26.0.2
```

## Setup
cd to
```bash
cd /home/Piano-LED-Visualizer
```

## List services
```bash
systemctl list-units --type=service --state=running
```
## List processes

```bash
ps aux
```

## Stop service
```bash
sudo systemctl stop visualizer.service
```

## Stop process
```bash
sudo pkill -f "/home/Piano-LED-Visualizer/visualizer.py"
```

## In WSL, sync file (make sure in Code directory)
```bash
cd ..
rsync -avz -e ssh Piano-LED-Visualizer/ pi@172.26.0.2:/home/Piano-LED-Visualizer
```

## Start service
```bash
sudo systemctl start visualizer.service
```
