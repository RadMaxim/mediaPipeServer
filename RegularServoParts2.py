import time

from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO
import serial
port = "COM9"



app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:63342", "http://127.0.0.1:5000"], logger=True, engineio_logger=True)
count = 0
uno = None
@app.route('/handle_click', methods=['POST'])
def handle_click():

    global count,uno
    if count==0:
        uno = serial.Serial(port, 9600, timeout=1)
    count+=1
    # print(uno)
    # # time.sleep(2)
    # print("secwscwsc")

    data = request.json
    # print(data)
    r1 = data.get("r1")
    r2 = data.get("r2")
    r3 = data.get("r3")
    # print(r1)
    # print(r2)
    # print(r3)
    dataServo = "X"+str(r1)+"Y"+str(r2)+"Z"+str(r3)
    print(dataServo)
    # mode = data.get('angle')
    # modeFace = int(mode)
    uno.write(str(dataServo).encode("utf-8"))


    return jsonify(success=True, mode=dataServo)

@app.route('/')
def index():
    return render_template('indexRegularServoPart2.html')




if __name__ == '__main__':

    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)


