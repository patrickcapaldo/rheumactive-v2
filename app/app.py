import os
import json
import time
import socket
import threading
import base64

from flask import Flask, render_template, Response, request, jsonify
import database as db

# --- Configuration ---
TCP_IP = '127.0.0.1'
TCP_PORT = 5001
LOGS_DIR = "logs"

# --- Global Data ---
latest_frame_data = {"image": "", "angle": 0.0}
client_socket_conn = None # To hold the connection to the streamer

# --- Flask App Setup ---
app = Flask(__name__)

# --- Database Initialisation ---
with app.app_context():
    db.init_db()

# --- Inter-Process Communication (IPC) ---

def socket_listener():
    global latest_frame_data, client_socket_conn
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((TCP_IP, TCP_PORT))
    server_socket.listen(1)
    print(f"Flask app listening for camera streamer on {TCP_IP}:{TCP_PORT}")

    conn = None
    try:
        conn, addr = server_socket.accept()
        client_socket_conn = conn # Store the connection globally
        print(f"Camera streamer connected from {addr}")

        buffer = b""
        payload_size = 4  # Size of message length field

        while True:
            while len(buffer) < payload_size:
                data = conn.recv(4096)
                if not data: break
                buffer += data
            
            if not data: break # Connection closed

            packed_msg_size = buffer[:payload_size]
            buffer = buffer[payload_size:]
            msg_size = int.from_bytes(packed_msg_size, 'big')

            while len(buffer) < msg_size:
                data = conn.recv(4096)
                if not data: break
                buffer += data
            
            if not data: break # Connection closed

            frame_data = buffer[:msg_size]
            buffer = buffer[msg_size:]

            data = json.loads(frame_data.decode('utf-8'))
            latest_frame_data["image"] = data["image"]
            latest_frame_data["angle"] = data["angle"]

        print("Camera streamer disconnected.")
    except Exception as e:
        print(f"Error in socket listener: {e}")
    finally:
        if conn: conn.close()
        client_socket_conn = None # Clear the global connection
        server_socket.close()
        print("Socket listener stopped.")

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    """Renders the history page."""
    return render_template('history.html')

@app.route('/measurement/<measurement_id>')
def measurement_detail(measurement_id):
    """Renders the measurement detail page."""
    return render_template('measurement_detail.html', measurement_id=measurement_id)

@app.route('/start_video', methods=['POST'])
def start_video():
    global client_socket_conn
    data = request.get_json()
    joint = data.get('joint')

    if not joint:
        return json.dumps({'status': 'error', 'message': 'No joint specified'})

    if client_socket_conn:
        try:
            command = f"start_video:{joint}"
            client_socket_conn.sendall(command.encode('utf-8'))
            print(f"Sent '{command}' command to streamer.")
            return json.dumps({'status': 'success'})
        except Exception as e:
            print(f"Error sending start_video command: {e}")
            return json.dumps({'status': 'error', 'message': str(e)})
    else:
        print("Cannot start video: No camera streamer connected.")
        return json.dumps({'status': 'error', 'message': 'No streamer connected'})

@app.route('/video_feed')
def video_feed():

    def generate():
        while True:
            if latest_frame_data["image"]:

                frame = base64.b64decode(latest_frame_data["image"])
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + f'{len(frame)}'.encode() + b'\r\n\r\n' +
                       frame + b'\r\n')

            time.sleep(0.05) # ~20 FPS
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/angle_feed')
def angle_feed():
    return json.dumps({"angle": latest_frame_data["angle"]})

# --- API Routes ---

@app.route('/api/measurements', methods=['POST'])
def api_save_measurement():
    """API endpoint to save a new measurement."""
    data = request.get_json()
    joint = data.get('joint')
    exercise = data.get('exercise')
    measure_data = data.get('data')

    if not all([joint, exercise, measure_data]):
        return jsonify({'status': 'error', 'message': 'Missing required data'}), 400

    try:
        db.save_measurement(joint, exercise, measure_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/measurements', methods=['GET'])
def api_get_measurements():
    """API endpoint to get measurements with pagination and filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    joint = request.args.get('joint')
    exercise = request.args.get('exercise')
    date = request.args.get('date')

    try:
        result = db.get_measurements(page, per_page, joint, exercise, date)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/measurements/<measurement_id>', methods=['GET'])
def api_get_measurement(measurement_id):
    """API endpoint to get a single measurement by its ID."""
    try:
        measurement = db.get_measurement_by_id(measurement_id)
        if measurement:
            return jsonify(measurement)
        return jsonify({'status': 'error', 'message': 'Measurement not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- App Lifecycle ---

@app.teardown_appcontext
def teardown_appcontext(exception=None):
    # No subprocess to terminate here
    pass

if __name__ == '__main__':
    # Ensure logs directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Start the socket listener in a separate thread
    listener_thread = threading.Thread(target=socket_listener, daemon=True)
    listener_thread.start()
    # Give the listener a moment to bind
    time.sleep(1)
    
    app.run(host='0.0.0.0', port=5000, debug=False)