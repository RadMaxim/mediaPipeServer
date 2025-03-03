import serial
from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO
import time



app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=[ "http://127.0.0.1:5000"], logger=True, engineio_logger=True)



@app.route('/')
def index():
    return render_template('indexRegularServo.html')
@app.route('/handle_click', methods=['POST'])
def handle_click():


    global modeFace
    data = request.json
    mode = data.get('angle')
    modeFace = int(mode)
    arduino.write(str(modeFace).encode("utf-8"))

    print(f"Mode clicked: {mode}")
    # time.sleep(1)
    # cameBack = arduino.readline()
    # print(cameBack.decode("utf-8"))
    return jsonify(success=True, mode=mode)
def generate():
    arduino = serial.Serial('COM9', 9600, timeout=1)
    while True:
        val = input("Value: ")
        arduino.write(val.encode())
        time.sleep(1)
        cameBack = arduino.readline()
        print(cameBack.decode("utf-8"))


# if __name__ == '__main__':
    # arduino = serial.Serial('COM9', 9600, timeout=1)

if __name__ == '__main__':
    app.run(debug=True)

arduino = serial.Serial('COM9', 9600, timeout=1)

# arduino.write('Hello Arduino!'.encode("utf-8"))
# time.sleep(0.2)
# arduino.close()