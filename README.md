# 🔴 Crimson Face Lab

### Webcam Phishing-Awareness & Security Research Tool

**Developed by crimson1331**

Educational cybersecurity project demonstrating webcam privacy risks, automatic image/video capture, face detection, and a local Flask interface.

## ⚠️ Disclaimer

**Authorized use only.** Use this project only on systems and cameras you own or have explicit permission to test. Do not use it for unauthorized surveillance or privacy violations.

## 🛠️ Requirements

* Kali Linux
* Python 3
* Git
* Webcam

## 🚀 Installation

```bash
git clone https://github.com/crimson1331-1331/crimson-facelab.git
cd crimson-facelab

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

mkdir -p data/photos data/videos
```

## ▶️ Run

```bash
python3 app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 📁 Storage

Photos:

```text
data/photos/
```

Videos:

```text
data/videos/
```

## 📷 Camera Troubleshooting

Check cameras:

```bash
ls /dev/video*
```

Or:

```bash
v4l2-ctl --list-devices
```

Change the camera in `app.py`:

```python
CAMERA_INDEX = 0
```

## 🔴 Features

* Automatic image capture
* Video recording
* OpenCV face detection
* Flask web interface
* Local media storage
* Kali Linux support

**Use responsibly and only in authorized security-research environments.**
# crimson-facelab
