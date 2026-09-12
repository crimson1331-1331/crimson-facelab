#!/usr/bin/env python3

import os
import sys
import time
import signal
import threading
from datetime import datetime

import cv2

from flask import (
    Flask,
    render_template,
    Response,
    jsonify
)


# ============================================================
# CRIMSON FACE LAB
# Developed by crimson1331
# ============================================================

APP_NAME = "CRIMSON FACE LAB"
VERSION = "2.0.0"
DEVELOPER = "crimson1331"

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

PHOTO_DIR = os.path.join(
    DATA_DIR,
    "photos"
)

VIDEO_DIR = os.path.join(
    DATA_DIR,
    "videos"
)


# ============================================================
# SETTINGS
# ============================================================

HOST = "127.0.0.1"
PORT = 5000

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

FPS = 20.0

# Automatic photo interval
PHOTO_INTERVAL = 3.0

# Browser heartbeat timeout.
# If the webpage stops contacting the server,
# recording will stop after this many seconds.
SESSION_TIMEOUT = 6.0


# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs(
    PHOTO_DIR,
    exist_ok=True
)

os.makedirs(
    VIDEO_DIR,
    exist_ok=True
)


# ============================================================
# ANSI COLORS
# ============================================================

RESET = "\033[0m"

RED = "\033[91m"
CRIMSON = "\033[38;5;196m"
DARK_RED = "\033[38;5;124m"

WHITE = "\033[97m"
GRAY = "\033[90m"

GREEN = "\033[92m"
YELLOW = "\033[93m"

CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)


# ============================================================
# CAMERA STATE
# ============================================================

camera = None

camera_lock = threading.Lock()

latest_frame = None

latest_frame_lock = threading.Lock()


# ============================================================
# RECORDING STATE
# ============================================================

recording = False

recording_thread = None

video_writer = None

video_filename = None

video_filepath = None

last_photo_time = 0.0

last_heartbeat = 0.0

session_active = False

state_lock = threading.Lock()


# ============================================================
# BANNER
# ============================================================

def banner():

    print(f"{CRIMSON}")

    print(r"""
        ██████╗██████╗ ██╗███╗   ███╗███████╗ ██████╗ ███╗   ██╗
       ██╔════╝██╔══██╗██║████╗ ████║██╔════╝██╔══██╗████╗  ██║
       ██║     ██████╔╝██║██╔████╔██║███████╗██████╔╝██╔██╗ ██║
       ██║     ██╔══██╗██║██║╚██╔╝██║╚════██║██╔═══╝ ██║╚██╗██║
       ╚██████╗██║  ██║██║██║ ╚═╝ ██║███████║██║     ██║ ╚████║
        ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═══╝

                       F A C E   L A B

                 C R I M S O N   V I S I O N
    """)

    print(f"{WHITE}                    developed by{RESET}")
    print(f"{CRIMSON}                       {DEVELOPER}{RESET}")

    print()

    print(
        f"{DARK_RED}"
        "╔══════════════════════════════════════════════════════╗"
        f"{RESET}"
    )

    print(
        f"{DARK_RED}║"
        f"{YELLOW}          EDUCATIONAL / RESEARCH USE ONLY          "
        f"{DARK_RED}║{RESET}"
    )

    print(
        f"{DARK_RED}║"
        f"{GRAY}                                                      "
        f"{DARK_RED}║{RESET}"
    )

    print(
        f"{DARK_RED}║"
        f"{GRAY}  Use only on systems, cameras, and people for which "
        f"{DARK_RED}║{RESET}"
    )

    print(
        f"{DARK_RED}║"
        f"{GRAY}  you have appropriate authorization and consent.    "
        f"{DARK_RED}║{RESET}"
    )

    print(
        f"{DARK_RED}║"
        f"{GRAY}  The developer does not endorse unauthorized use or "
        f"{DARK_RED}║{RESET}"
    )

    print(
        f"{DARK_RED}║"
        f"{GRAY}  misuse of this software.                          "
        f"{DARK_RED}║{RESET}"
    )

    print(
        f"{DARK_RED}"
        "╚══════════════════════════════════════════════════════╝"
        f"{RESET}"
    )

    print()


# ============================================================
# BOOT ANIMATION
# ============================================================

def boot():

    os.system("clear")

    banner()

    print(
        f"{CRIMSON}"
        "╔══════════════════════════════════════════════════════╗"
        f"{RESET}"
    )

    print(
        f"{CRIMSON}║"
        f"{WHITE}              CRIMSON INITIALIZATION                "
        f"{CRIMSON}║{RESET}"
    )

    print(
        f"{CRIMSON}"
        "╚══════════════════════════════════════════════════════╝"
        f"{RESET}"
    )

    print()

    messages = [

        (
            "Establishing Crimson Core",
            CRIMSON
        ),

        (
            "Loading OpenCV vision engine",
            CYAN
        ),

        (
            "Loading Haar face detector",
            MAGENTA
        ),

        (
            "Verifying photo storage",
            YELLOW
        ),

        (
            "Verifying video storage",
            YELLOW
        ),

        (
            "Initializing webcam interface",
            GREEN
        ),

        (
            "Initializing automatic capture",
            BLUE
        ),

        (
            "Preparing Flask interface",
            CRIMSON
        ),

        (
            "Checking local research environment",
            CYAN
        )
    ]


    for message, color in messages:

        print(
            f"{GRAY}[ CRIMSON ]{RESET} "
            f"{color}{message:<40}{RESET}",
            end="",
            flush=True
        )

        for _ in range(3):

            time.sleep(0.13)

            print(
                ".",
                end="",
                flush=True
            )

        print(
            f" {GREEN}OK{RESET}"
        )


    print()

    print(
        f"{CRIMSON}[ SYSTEM ]{RESET} "
        "Booting runtime"
    )


    for i in range(31):

        percent = int(
            (i / 30) * 100
        )

        bar = (
            "█" * i
            +
            "░" * (30 - i)
        )

        print(
            f"\r{CRIMSON}"
            f"[{bar}]"
            f"{RESET} "
            f"{WHITE}{percent:3d}%{RESET}",
            end="",
            flush=True
        )

        time.sleep(0.035)


    print("\n")

    print(
        f"{GREEN}"
        "╔══════════════════════════════════════════════════════╗"
        f"{RESET}"
    )

    print(
        f"{GREEN}║"
        f"{WHITE}              CRIMSON SYSTEM READY                  "
        f"{GREEN}║{RESET}"
    )

    print(
        f"{GREEN}"
        "╚══════════════════════════════════════════════════════╝"
        f"{RESET}"
    )

    print()

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        f"Developer : {MAGENTA}{DEVELOPER}{RESET}"
    )

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        f"Version   : {WHITE}{VERSION}{RESET}"
    )

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        f"Purpose   : {CYAN}Educational / Research{RESET}"
    )

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        f"Photos    : {YELLOW}{PHOTO_DIR}{RESET}"
    )

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        f"Videos    : {YELLOW}{VIDEO_DIR}{RESET}"
    )

    print()


# ============================================================
# CAMERA INITIALIZATION
# ============================================================

def initialize_camera():

    global camera

    print(
        f"{CYAN}[CAMERA]{RESET} "
        "Searching for webcam..."
    )

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print(
            f"{RED}[ERROR]{RESET} "
            "Could not access webcam."
        )

        print(
            f"{YELLOW}[TIP]{RESET} "
            "Check available devices:"
        )

        print(
            "      ls /dev/video*"
        )

        return False


    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        FRAME_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        FRAME_HEIGHT
    )

    camera.set(
        cv2.CAP_PROP_FPS,
        FPS
    )


    actual_width = int(
        camera.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    actual_height = int(
        camera.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )


    print(
        f"{GREEN}[CAMERA]{RESET} "
        f"Webcam initialized: "
        f"{actual_width}x{actual_height}"
    )

    return True


# ============================================================
# FACE DETECTOR
# ============================================================

cascade_path = (
    cv2.data.haarcascades
    +
    "haarcascade_frontalface_default.xml"
)


face_detector = cv2.CascadeClassifier(
    cascade_path
)


if face_detector.empty():

    print(
        f"{RED}[FATAL]{RESET} "
        "Could not load face detector."
    )

    sys.exit(1)


# ============================================================
# FACE DETECTION
# ============================================================

def detect_faces(frame):

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    return faces


# ============================================================
# CREATE VIDEO FILE
# ============================================================

def create_video_writer():

    global video_writer
    global video_filename
    global video_filepath


    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )


    video_filename = (
        f"recording_{timestamp}.avi"
    )


    video_filepath = os.path.join(
        VIDEO_DIR,
        video_filename
    )


    fourcc = cv2.VideoWriter_fourcc(
        *"MJPG"
    )


    video_writer = cv2.VideoWriter(
        video_filepath,
        fourcc,
        FPS,
        (
            FRAME_WIDTH,
            FRAME_HEIGHT
        )
    )


    if not video_writer.isOpened():

        print(
            f"{RED}[VIDEO ERROR]{RESET} "
            "Could not create video file."
        )

        video_writer = None

        return False


    print(
        f"{GREEN}[VIDEO]{RESET} "
        "Recording initialized."
    )

    print(
        f"{GRAY}        File: {WHITE}"
        f"{video_filepath}{RESET}"
    )

    return True


# ============================================================
# SAVE PHOTO
# ============================================================

def save_photo(
    frame,
    faces
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S-%f"
    )[:-3]


    filename = (
        f"photo_{timestamp}.jpg"
    )


    filepath = os.path.join(
        PHOTO_DIR,
        filename
    )


    # Automatically crop the largest
    # detected face when a face exists.

    if len(faces) > 0:

        faces_sorted = sorted(
            faces,
            key=lambda face:
                face[2] * face[3],
            reverse=True
        )


        x, y, w, h = faces_sorted[0]


        padding = int(
            w * 0.30
        )


        x1 = max(
            0,
            x - padding
        )

        y1 = max(
            0,
            y - padding
        )

        x2 = min(
            frame.shape[1],
            x + w + padding
        )

        y2 = min(
            frame.shape[0],
            y + h + padding
        )


        image = frame[
            y1:y2,
            x1:x2
        ]

    else:

        image = frame


    success = cv2.imwrite(
        filepath,
        image
    )


    if success:

        print(
            f"{CYAN}[PHOTO]{RESET} "
            f"Saved {filename}"
        )


    return success


# ============================================================
# CAMERA LOOP
# ============================================================

def camera_loop():

    global latest_frame
    global recording
    global video_writer
    global last_photo_time


    print(
        f"{GREEN}[SYSTEM]{RESET} "
        "Automatic camera engine started."
    )


    while recording:

        # ----------------------------------------------------
        # Read camera
        # ----------------------------------------------------

        with camera_lock:

            if camera is None:
                break

            success, frame = camera.read()


        if not success:

            print(
                f"{RED}[CAMERA]{RESET} "
                "Frame read failed."
            )

            time.sleep(
                0.1
            )

            continue


        # Mirror image
        frame = cv2.flip(
            frame,
            1
        )


        # ----------------------------------------------------
        # Face detection
        # ----------------------------------------------------

        faces = detect_faces(
            frame
        )


        # ----------------------------------------------------
        # Draw detection boxes
        # ----------------------------------------------------

        for x, y, w, h in faces:

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                3
            )


            cv2.putText(
                frame,
                "FACE DETECTED",
                (
                    x,
                    max(
                        30,
                        y - 12
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )


        # ----------------------------------------------------
        # UI overlays
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "CRIMSON FACE LAB",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )


        cv2.putText(
            frame,
            f"Faces: {len(faces)}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            "AUTO RECORDING",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 255),
            2
        )


        # ----------------------------------------------------
        # Save latest frame
        # ----------------------------------------------------

        with latest_frame_lock:

            latest_frame = (
                frame.copy()
            )


        # ----------------------------------------------------
        # Write video
        # ----------------------------------------------------

        if video_writer is not None:

            video_writer.write(
                frame
            )


        # ----------------------------------------------------
        # Automatic photos
        # ----------------------------------------------------

        current_time = time.time()


        if (
            current_time
            -
            last_photo_time
            >=
            PHOTO_INTERVAL
        ):

            save_photo(
                frame,
                faces
            )

            last_photo_time = (
                current_time
            )


        # Small delay to avoid
        # unnecessary CPU usage.

        time.sleep(
            0.001
        )


    print(
        f"{YELLOW}[SYSTEM]{RESET} "
        "Automatic camera engine stopped."
    )


# ============================================================
# START RECORDING
# ============================================================

def start_recording():

    global recording
    global recording_thread
    global last_photo_time


    with state_lock:

        if recording:
            return True


        if not create_video_writer():

            return False


        recording = True

        last_photo_time = (
            time.time()
        )


        recording_thread = threading.Thread(
            target=camera_loop,
            daemon=True
        )


        recording_thread.start()


    print(
        f"{GREEN}[RECORDING]{RESET} "
        "Automatic recording ACTIVE."
    )

    return True


# ============================================================
# STOP RECORDING
# ============================================================

def stop_recording():

    global recording
    global video_writer
    global recording_thread


    with state_lock:

        if not recording:

            return


        print()

        print(
            f"{YELLOW}[RECORDING]{RESET} "
            "Finalizing recording..."
        )


        recording = False


    if (
        recording_thread is not None
        and recording_thread.is_alive()
    ):

        recording_thread.join(
            timeout=5
        )


    if video_writer is not None:

        video_writer.release()

        video_writer = None


        print(
            f"{GREEN}[VIDEO]{RESET} "
            "Video finalized."
        )

        if video_filepath:

            print(
                f"{GRAY}        Saved: "
                f"{WHITE}{video_filepath}{RESET}"
            )


# ============================================================
# BROWSER SESSION MONITOR
# ============================================================

def session_monitor():

    global session_active

    print(
        f"{GRAY}[SESSION]{RESET} "
        "Session monitor started."
    )


    while True:

        time.sleep(
            1
        )


        with state_lock:

            active = (
                session_active
            )

            heartbeat = (
                last_heartbeat
            )


        if not active:
            continue


        if heartbeat == 0:
            continue


        elapsed = (
            time.time()
            -
            heartbeat
        )


        if elapsed > SESSION_TIMEOUT:

            print()

            print(
                f"{YELLOW}[SESSION]{RESET} "
                "Browser heartbeat lost."
            )

            print(
                f"{GRAY}[SESSION]{RESET} "
                "Finalizing current video..."
            )


            with state_lock:

                session_active = False


            stop_recording()


# ============================================================
# STREAM FRAMES TO BROWSER
# ============================================================

def generate_frames():

    while True:

        with latest_frame_lock:

            if latest_frame is None:

                time.sleep(
                    0.05
                )

                continue


            frame = (
                latest_frame.copy()
            )


        success, buffer = cv2.imencode(
            ".jpg",
            frame
        )


        if not success:
            continue


        frame_bytes = (
            buffer.tobytes()
        )


        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            +
            frame_bytes
            +
            b"\r\n"
        )


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html",
        developer=DEVELOPER,
        version=VERSION
    )


@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        )
    )


# ============================================================
# START SESSION
# ============================================================

@app.route(
    "/session/start",
    methods=["POST"]
)
def session_start():

    global session_active
    global last_heartbeat


    with state_lock:

        session_active = True

        last_heartbeat = (
            time.time()
        )


    if not recording:

        started = start_recording()

        if not started:

            return jsonify({
                "success": False,
                "message":
                    "Could not start recording."
            }), 500


    print(
        f"{GREEN}[SESSION]{RESET} "
        "Browser session connected."
    )


    return jsonify({
        "success": True,
        "recording": True
    })


# ============================================================
# HEARTBEAT
# ============================================================

@app.route(
    "/session/heartbeat",
    methods=["POST"]
)
def heartbeat():

    global last_heartbeat
    global session_active


    with state_lock:

        last_heartbeat = (
            time.time()
        )

        session_active = True


    return jsonify({
        "success": True,
        "recording": recording
    })


# ============================================================
# SESSION STOP
# ============================================================

@app.route(
    "/session/stop",
    methods=["POST"]
)
def session_stop():

    global session_active


    with state_lock:

        session_active = False


    stop_recording()


    return jsonify({
        "success": True,
        "recording": False
    })


# ============================================================
# STATISTICS
# ============================================================

@app.route("/stats")
def stats():

    photos = [
        f
        for f in os.listdir(
            PHOTO_DIR
        )
        if f.lower().endswith(
            (
                ".jpg",
                ".jpeg",
                ".png"
            )
        )
    ]


    videos = [
        f
        for f in os.listdir(
            VIDEO_DIR
        )
        if f.lower().endswith(
            (
                ".avi",
                ".mp4",
                ".mkv"
            )
        )
    ]


    with state_lock:

        current_recording = (
            recording
        )


    return jsonify({

        "photos":
            len(photos),

        "videos":
            len(videos),

        "recording":
            current_recording

    })


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown():

    print()

    print(
        f"{YELLOW}[SYSTEM]{RESET} "
        "Shutting down Crimson Face Lab..."
    )


    stop_recording()


    global camera


    if camera is not None:

        camera.release()

        camera = None

        print(
            f"{GREEN}[CAMERA]{RESET} "
            "Camera released."
        )


    print(
        f"{CRIMSON}[CRIMSON]{RESET} "
        "Session terminated."
    )

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        "Goodbye, crimson1331."
    )


# ============================================================
# SIGNAL HANDLER
# ============================================================

def signal_handler(
    sig,
    frame
):

    shutdown()

    sys.exit(0)


signal.signal(
    signal.SIGINT,
    signal_handler
)

signal.signal(
    signal.SIGTERM,
    signal_handler
)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    boot()


    if not initialize_camera():

        print(
            f"{RED}[FATAL]{RESET} "
            "Camera initialization failed."
        )

        sys.exit(1)


    # Start the session monitor.
    monitor = threading.Thread(
        target=session_monitor,
        daemon=True
    )

    monitor.start()


    print()

    print(
        f"{CRIMSON}"
        "╔══════════════════════════════════════════════════════╗"
        f"{RESET}"
    )

    print(
        f"{CRIMSON}║"
        f"{WHITE}             CRIMSON FACE LAB ONLINE                "
        f"{CRIMSON}║{RESET}"
    )

    print(
        f"{CRIMSON}╠══════════════════════════════════════════════════════╣"
        f"{RESET}"
    )

    print(
        f"{CRIMSON}║{RESET} "
        f"Local URL : {CYAN}"
        f"http://{HOST}:{PORT}"
        f"{RESET}"
    )

    print(
        f"{CRIMSON}║{RESET} "
        f"Photos    : {YELLOW}"
        f"{PHOTO_DIR}"
        f"{RESET}"
    )

    print(
        f"{CRIMSON}║{RESET} "
        f"Videos    : {YELLOW}"
        f"{VIDEO_DIR}"
        f"{RESET}"
    )

    print(
        f"{CRIMSON}║{RESET} "
        f"Auto photo: {GREEN}"
        f"Every {PHOTO_INTERVAL:.0f} seconds"
        f"{RESET}"
    )

    print(
        f"{CRIMSON}║{RESET} "
        f"Session   : {CYAN}"
        "Browser heartbeat"
        f"{RESET}"
    )

    print(
        f"{CRIMSON}╚══════════════════════════════════════════════════════╝"
        f"{RESET}"
    )

    print()

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        "Open the URL in your browser."
    )

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        "The browser does not access the camera directly."
    )

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        "Recording begins when the web session starts."
    )

    print(
        f"{GRAY}[SYSTEM]{RESET} "
        "Use CTRL+C for emergency/manual shutdown."
    )

    print()


    try:

        app.run(
            host=HOST,
            port=PORT,
            debug=False,
            threaded=True,
            use_reloader=False
        )

    finally:

        shutdown()
