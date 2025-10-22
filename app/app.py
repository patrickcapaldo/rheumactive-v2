import os
import json
import time
import socket
import threading
import base64 # Added import

from flask import Flask, render_template, Response

# --- Configuration ---
TCP_IP = '127.0.0.1'
TCP_PORT = 5001
LOGS_DIR = "logs"

# --- Global Data ---
latest_frame_data = {"image": "", "angle": 0.0}

# --- Flask App Setup ---
app = Flask(__name__)

# --- Inter-Process Communication (IPC) ---

def socket_listener():
    global latest_frame_data
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((TCP_IP, TCP_PORT))
    server_socket.listen(1)
    print(f"Flask app listening for camera streamer on {TCP_IP}:{TCP_PORT}")

    conn = None
    try:
        conn, addr = server_socket.accept()
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
        server_socket.close()
        print("Socket listener stopped.")

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    print("Video feed requested!") # DEBUG
    def generate():
        while True:
            if latest_frame_data["image"]:
                print("Sending frame to browser!") # DEBUG
                frame = base64.b64decode(latest_frame_data["image"])
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + f'{len(frame)}'.encode() + b'\r\n\r\n' +
                       frame + b'\r\n')
            else:
                print("No frame data available yet.") # DEBUG
            time.sleep(0.05) # ~20 FPS
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/angle_feed')
def angle_feed():
    return json.dumps({"angle": latest_frame_data["angle"]})

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