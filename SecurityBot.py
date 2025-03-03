from flask import Flask, render_template, Response, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import mediapipe as mp
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:63342", "http://127.0.0.1:5000"]}})
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:63342", "http://127.0.0.1:5000"], logger=True, engineio_logger=True)

def diffImg(f1, f2):
    d1 = cv2.absdiff(f1, f2)
    d3 = np.ravel(d1)
    d4 = np.count_nonzero(d3)
    return d4, d1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate():
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic()
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    frame = cap.read()[1]
    prev_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        nonzero, result = diffImg(prev_frame, current_frame_gray)
        results = holistic.process(rgb)
        state = 0
        faceM = False
        handL = False
        handR = False
        Body = False
        faceResult = results.face_landmarks
        leftResult = results.left_hand_landmarks
        rightResult = results.right_hand_landmarks
        poseResult = results.pose_landmarks
        if faceResult:
            mp_draw.draw_landmarks(frame, faceResult, mp_holistic.FACEMESH_TESSELATION)
            state += 1
            faceM = True
        if leftResult:
            mp_draw.draw_landmarks(frame, leftResult, mp_holistic.HAND_CONNECTIONS)
            state += 1
            handL = True
        if rightResult:
            mp_draw.draw_landmarks(frame, rightResult, mp_holistic.HAND_CONNECTIONS)
            state += 1
            handR = True
        if poseResult:
            mp_draw.draw_landmarks(frame, poseResult, mp_holistic.POSE_CONNECTIONS)
            state += 1
            Body = True
        if nonzero > 210000 and state > 2:
            cv2.imwrite("img/move.jpg", frame)
            itogFound = "Система безопасности нашла :"

            if faceM:
                itogFound += "Голову"
            if handR:
                itogFound += "Правую руку"
            if handL:
                itogFound += "Левую руку"
            if Body:
                itogFound += "Тело"


            socketio.emit('message', {'msg': itogFound})
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
