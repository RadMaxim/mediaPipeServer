from flask import Flask, render_template, Response
from flask_cors import CORS
from cvzone.HandTrackingModule import HandDetector
import cv2
from flask_socketio import SocketIO
import serial
faces_cascad = cv2.CascadeClassifier("./cascadeH/haarcascade_frontalface_default.xml")

port = "COM6"
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






def generate():
    global cx, cy, MODE
    uno = serial.Serial(port, 9600, timeout=1)
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faces_cascad.detectMultiScale(gray, 1.3, 3, 0, (10, 10))
        if len(faces)>0:
            [x, y, w, h] = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
            centerFX,centerFY = (x+w)//2, (y+h)//2
            res = f"X{centerFX}Y{centerFY}"
            print(res)
            uno.write(res.encode("utf-8"))

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
