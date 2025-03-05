from flask import Flask, render_template, Response
from flask_cors import CORS
from cvzone.HandTrackingModule import HandDetector
import cv2
from flask_socketio import SocketIO
import serial

port = "COM4"
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:63342", "http://127.0.0.1:5000"]}})
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:63342", "http://127.0.0.1:5000"], logger=True,
                    engineio_logger=True)
count = 0
uno = None
detection = HandDetector(detectionCon=0.8)
h = 480
w = 640
servoVal = {
    "s1": 0,
    "s2": 0,
    "s3": 0,
    "s4": 0
}

@app.route('/')
def index():
    return render_template('ControlServoUsingFingers.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


def drawSection(frame):
    global w, h
    for i in range(4):
        cv2.putText(img=frame, text=f"servo{i + 1}", org=((w // 4) * i + 10, 50), fontFace=1, fontScale=2,
                    color=(255, 255, 255), thickness=2)
        cv2.line(img=frame, pt1=((w // 4) * i, 0), pt2=((w // 4) * i, h), color=(255, 255, 255), thickness=3)
    return frame


def controlServo(x, distance):
    for i in range(4):
        if i * 160 < x < (i + 1) * 160:
            servoVal[f"s{i + 1}"] = int(distance)
    result = f"Q{servoVal['s1']}W{servoVal['s2']}E{servoVal['s3']}R{servoVal['s4']}"
    return result


def generate():
    global cx, cy, MODE
    uno = serial.Serial(port, 9600, timeout=1)
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()

        frame = cv2.flip(frame, 1)
        frame = drawSection(frame)

        hand, img = detection.findHands(frame)
        if hand:
            lmList = hand[0]["lmList"]
            cursor = lmList[8]
            modeTake = lmList[4]

            l, img_new, _ = detection.findDistance([cursor[0], cursor[1]], [modeTake[0], modeTake[1]], frame,
                                                   color=(255, 0, 0), scale=10)
            cv2.putText(frame, f"d: {int(l)}", (cursor[0], cursor[1]), 1, 2, (255, 255, 255), 2)
            res = controlServo(cursor[0], l)
            uno.write(res.encode("utf-8"))

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
