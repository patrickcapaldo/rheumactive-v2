"""The main application file for the RheumActive v2 web app."""

import reflex as rx
import asyncio
import os
import json
import time
from datetime import datetime
import cv2
import numpy as np
import base64
from picamera2 import Picamera2

# --- Constants & Global Objects ---
LOGS_DIR = "logs"
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Global camera object to avoid re-initialization
picam2 = None

def initialize_camera():
    """Initializes the global camera object."""
    global picam2
    if picam2 is None:
        print("--- Initializing Camera ---")
        try:
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT)})
            picam2.configure(config)
            picam2.start()
            time.sleep(2) # Allow camera to warm up
            print("Camera initialized successfully.")
            return True
        except Exception as e:
            print(f"FATAL: Could not initialize camera: {e}")
            return False
    return True

# --- Helper Functions (outside State) ---
def get_angle(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_product == 0: return 0.0
    cosine_angle = np.clip(dot_product / norm_product, -1.0, 1.0)
    return np.degrees(np.arccos(cosine_angle))

def draw_pose(frame, keypoints, confidence_threshold=0.5):
    for i, point in enumerate(keypoints):
        if point[2] > confidence_threshold:
            cv2.circle(frame, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)

# --- State Management ---

class State(rx.State):
    """The base state for the app."""
    pass

class MeasureState(State):
    """State for the measurement setup page."""
    joint: str = "Elbow"
    exercise: str = "Flexion"
    duration: int = 30

    # Status variables
    is_measuring: bool = False
    camera_ok: bool = False
    joint_found: bool = False
    camera_error: str = ""
    joint_error: str = ""
    countdown: int = 0
    current_angle: float = 0.0
    show_results: bool = False
    results: dict = {"min": 0, "max": 0, "avg": 0}
    live_frame: str = ""

    def set_joint(self, joint: str):
        self.joint = joint

    def set_exercise(self, exercise: str):
        self.exercise = exercise

    @rx.var
    def formatted_current_angle(self) -> str:
        return f"{self.current_angle:.1f}"

    def set_duration_str(self, duration_str):
        self.duration = int(duration_str.replace("s", ""))

    @rx.var
    def begin_disabled(self) -> bool:
        return not self.camera_ok or not self.joint_found

    def _process_frame(self, frame):
        # MOCK HAIlo INFERENCE
        mock_keypoints = np.zeros((17, 3), dtype=np.float32)
        mock_keypoints[5] = [CAMERA_WIDTH * 0.3, CAMERA_HEIGHT * 0.4, 0.95] # L-Shoulder
        mock_keypoints[7] = [CAMERA_WIDTH * 0.5, CAMERA_HEIGHT * 0.5, 0.95] # L-Elbow
        mock_keypoints[9] = [CAMERA_WIDTH * 0.4, CAMERA_HEIGHT * 0.7, 0.95] # L-Wrist

        p1, p2, p3 = mock_keypoints[5, :2], mock_keypoints[7, :2], mock_keypoints[9, :2]
        self.current_angle = get_angle(p1, p2, p3)
        self.joint_found = True

        draw_pose(frame, mock_keypoints)
        cv2.putText(frame, f"Angle: {self.current_angle:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        self.live_frame = base64.b64encode(buffer).decode('utf-8')

    async def on_page_load(self):
        """Run hardware checks and start the live preview loop."""
        self.camera_ok = initialize_camera()
        if not self.camera_ok:
            self.camera_error = "Camera not detected."
            return
        self.camera_error = ""

        # Start the preview loop directly
        while not self.is_measuring:
            if picam2 is None: break
            frame = picam2.capture_array()
            self._process_frame(frame)
            await asyncio.sleep(0.05) # ~20 FPS

    async def start_measurement(self):
        self.is_measuring = True
        self.show_results = False
        self.countdown = self.duration
        yield self.measurement_loop

    async def measurement_loop(self):
        raw_data = []
        start_time = rx.moment.utcnow()
        while True:
            if picam2 is None: break
            if rx.moment.utcnow().diff(start_time, "seconds") > self.duration: break
            self.countdown = self.duration - rx.moment.utcnow().diff(start_time, "seconds")
            frame = picam2.capture_array()
            self._process_frame(frame)
            raw_data.append(self.current_angle)
            await asyncio.sleep(0.05)
        self.is_measuring = False
        if raw_data:
            self.results = {"min": round(min(raw_data), 1), "max": round(max(raw_data), 1), "avg": round(sum(raw_data) / len(raw_data), 1)}
        self.show_results = True

    def save_log(self):
        os.makedirs(LOGS_DIR, exist_ok=True)
        now = datetime.now()
        timestamp_unix = int(now.timestamp() * 1000)
        log_data = {
            "id": timestamp_unix,
            "timestamp_unix": timestamp_unix,
            "timestamp_human": now.strftime("%H:%M:%S, %d %B, %Y"),
            "joint": self.joint, "exercise": self.exercise, "duration": self.duration, "results": self.results,
        }
        file_path = os.path.join(LOGS_DIR, f"{timestamp_unix}.json")
        with open(file_path, "w") as f:
            json.dump(log_data, f, indent=4)
        self.show_results = False

    def close_results_dialog(self):
        self.show_results = False

class HistoryState(State):
    pass

class LogDetailState(State):
    pass

# --- Reusable Components ---
def stat_card(title, value):
    return rx.card(rx.vstack(rx.text(title, size="2", color_scheme="gray"), rx.heading(value, size="7"), spacing="1", align="center"), width="100%")

# --- Pages ---
def index() -> rx.Component:
    return rx.flex(
        rx.vstack(
            rx.heading("RheumActive", size="9", weight="bold", trim="both"),
            rx.text("Your personal joint mobility measurement tool.", size="5", color_scheme="gray"),
            rx.spacer(height="48px"),
            rx.hstack(
                rx.link(rx.button(rx.hstack(rx.icon("ruler"), rx.text("Measure")), size="4", high_contrast=True), href="/measure"),
                rx.link(rx.button(rx.hstack(rx.icon("history"), rx.text("History")), size="4", high_contrast=True), href="/history"),
                spacing="4",
            ),
            align="center",
        ),
        align="center", justify="center", height="100vh",
    )

def measure_page() -> rx.Component:
    return rx.container(
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Measurement Complete"),
                rx.dialog.description(rx.hstack(stat_card("Min Angle", f"{MeasureState.results['min']}°"), stat_card("Max Angle", f"{MeasureState.results['max']}°"), stat_card("Avg Angle", f"{MeasureState.results['avg']}°"), spacing="4", padding_y="1em")),
                rx.flex(rx.dialog.close(rx.button("Discard", size="3", variant="soft", color_scheme="gray")), rx.spacer(), rx.link(rx.button("Save & Return", size="3", on_click=MeasureState.save_log), href="/"), justify="between", width="100%"),
            ),
            open=MeasureState.show_results,
        ),
        rx.cond(
            MeasureState.is_measuring,
            rx.vstack(
                rx.heading("Measuring...", size="8"),
                rx.text(f"{MeasureState.joint}: {MeasureState.exercise}", size="5", color_scheme="gray"),
                rx.image(src=f"data:image/jpeg;base64,{MeasureState.live_frame}", width="640px", height="480px"),
                rx.hstack(stat_card("Time Left", f"{MeasureState.countdown}s"), stat_card("Current Angle", f"{MeasureState.formatted_current_angle}°"), spacing="4", width="100%"),
                align="center", justify="center", height="100vh",
            ),
            rx.vstack(
                rx.heading("New Measurement", size="8"),
                rx.card(
                    rx.vstack(
                        rx.text("Joint"),
                        rx.select.root(rx.select.trigger(), rx.select.content(rx.select.item("Elbow"), rx.select.item("Knee"), rx.select.item("Shoulder"), rx.select.item("Hip")), default_value=MeasureState.joint, on_change=MeasureState.set_joint),
                        rx.text("Exercise"),
                        rx.select.root(rx.select.trigger(), rx.select.content(rx.select.item("Flexion"), rx.select.item("Extension")), default_value=MeasureState.exercise, on_change=MeasureState.set_exercise),
                        rx.text("Duration"),
                        rx.segmented_control.root(rx.segmented_control.item("15s"), rx.segmented_control.item("30s"), rx.segmented_control.item("45s"), rx.segmented_control.item("60s"), value="30s", on_change=MeasureState.set_duration_str),
                        spacing="4",
                    ),
                    width="100%", max_width="500px",
                ),
                # Live angle and status checks
                rx.vstack(
                    rx.cond(
                        MeasureState.camera_ok,
                        rx.vstack(
                            rx.image(src=f"data:image/jpeg;base64,{MeasureState.live_frame}", width="100%", height="auto"),
                            stat_card("Live Angle", f"{MeasureState.formatted_current_angle}°"),
                        ),
                        rx.callout(MeasureState.camera_error, icon="triangle_alert", color_scheme="orange", variant="soft"),
                    ),
                    padding_top="1em", width="100%", max_width="500px",
                ),
                rx.hstack(
                    rx.link(rx.button("Back", variant="soft"), href="/"),
                    rx.button(rx.hstack(rx.text("Begin"), rx.icon("play")), on_click=MeasureState.start_measurement, disabled=MeasureState.begin_disabled),
                    spacing="4", padding_top="1em",
                ),
                align="center", justify="center", height="100vh",
            ),
        ),
        on_mount=MeasureState.on_page_load
    )

def history_page() -> rx.Component:
    return rx.vstack(
        rx.heading("History", size="8"),
        # UI Simplified until foreach is resolved
        rx.link(rx.button("Back", variant="soft"), href="/"),
        align="center", spacing="4", padding_top="2em", height="100vh",
    )

def log_detail_page() -> rx.Component:
    return rx.vstack(
        rx.heading(f"Log #{LogDetailState.log_id}", size="8"),
        rx.link(rx.button("Back to History"), href="/history"),
        align="center", spacing="4", padding_top="2em", height="100vh",
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="cyan", radius="large"))
app.add_page(index, route="/")
app.add_page(measure_page, route="/measure")
app.add_page(history_page, route="/history")
app.add_page(log_detail_page, route="/history/[log_id]")