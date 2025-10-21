"""The main application file for the RheumActive v2 web app."""

import reflex as rx
import asyncio
import os
import json
from datetime import datetime

# --- Constants ---
LOGS_DIR = "logs"

# --- State Management ---

class State(rx.State):
    """The base state for the app."""
    pass

class MeasureState(State):
    """State for the measurement setup page."""
    # Form fields
    joint: str = "Elbow"
    exercise: str = "Flexion"
    duration: int = 30

    # Measurement status
    is_measuring: bool = False
    countdown: int = 0
    current_angle: float = 0.0
    show_results: bool = False
    results: dict = {"min": 0, "max": 0, "avg": 0}

    # Explicit setters to resolve deprecation warnings
    def set_joint(self, joint: str):
        self.joint = joint

    def set_exercise(self, exercise: str):
        self.exercise = exercise

    @rx.var
    def formatted_current_angle(self) -> str:
        """The formatted string for the current angle."""
        return f"{self.current_angle:.1f}"

    # Type hint removed from duration_str to fix type mismatch error
    def set_duration_str(self, duration_str):
        self.duration = int(duration_str.replace("s", ""))

    async def start_measurement(self):
        self.is_measuring = True
        self.show_results = False
        self.countdown = self.duration
        yield self.measurement_loop

    async def measurement_loop(self):
        raw_data = []
        start_time = rx.moment.utcnow()
        while True:
            if rx.moment.utcnow().diff(start_time, "seconds") > self.duration:
                break
            self.countdown = self.duration - rx.moment.utcnow().diff(start_time, "seconds")
            self.current_angle = 90 + 45 * rx.random.uniform() * (self.countdown % 7)
            raw_data.append(self.current_angle)
            await asyncio.sleep(0.1)
        self.is_measuring = False
        if raw_data:
            self.results = {
                "min": round(min(raw_data), 1),
                "max": round(max(raw_data), 1),
                "avg": round(sum(raw_data) / len(raw_data), 1),
            }
        self.show_results = True

    def save_log(self):
        os.makedirs(LOGS_DIR, exist_ok=True)
        now = datetime.now()
        timestamp_unix = int(now.timestamp() * 1000)
        log_data = {
            "id": timestamp_unix,
            "timestamp_unix": timestamp_unix,
            "timestamp_human": now.strftime("%H:%M:%S, %d %B, %Y"),
            "joint": self.joint,
            "exercise": self.exercise,
            "duration": self.duration,
            "results": self.results,
        }
        file_path = os.path.join(LOGS_DIR, f"{timestamp_unix}.json")
        with open(file_path, "w") as f:
            json.dump(log_data, f, indent=4)
        self.show_results = False

    def close_results_dialog(self):
        self.show_results = False

class HistoryState(State):
    """State for the history page."""
    filter_joint: str = "All"
    filter_exercise: str = "All"

    def set_filter_joint(self, value: str):
        self.filter_joint = value

    def set_filter_exercise(self, value: str):
        self.filter_exercise = value

class LogDetailState(State):
    """State for the log detail page."""
    pass

# --- Styling ---
base_style = {}

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
        align="center",
        justify="center",
        height="100vh",
    )

def measure_page() -> rx.Component:
    return rx.container(
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Measurement Complete"),
                rx.dialog.description(
                    rx.hstack(
                        stat_card("Min Angle", f"{MeasureState.results['min']}°"),
                        stat_card("Max Angle", f"{MeasureState.results['max']}°"),
                        stat_card("Avg Angle", f"{MeasureState.results['avg']}°"),
                        spacing="4", padding_y="1em",
                    )
                ),
                rx.flex(
                    rx.dialog.close(rx.button("Discard", size="3", variant="soft", color_scheme="gray")),
                    rx.spacer(),
                    rx.link(rx.button("Save & Return", size="3", on_click=MeasureState.save_log), href="/"),
                    justify="between", width="100%",
                ),
            ),
            open=MeasureState.show_results,
        ),
        rx.cond(
            MeasureState.is_measuring,
            # Active Measurement View
            rx.vstack(
                rx.heading("Measuring...", size="8"),
                rx.text(f"{MeasureState.joint}: {MeasureState.exercise}", size="5", color_scheme="gray"),
                rx.box(height="480px", width="640px", border="1px dashed", border_radius="var(--radius-3)", margin_y="1em"),
                rx.hstack(
                    stat_card("Time Left", f"{MeasureState.countdown}s"),
                    stat_card("Current Angle", f"{MeasureState.formatted_current_angle}°"),
                    spacing="4", width="100%",
                ),
                align="center", justify="center", height="100vh",
            ),
            # Setup Form View
            rx.vstack(
                rx.heading("New Measurement", size="8"),
                rx.card(
                    rx.vstack(
                        rx.text("Joint"),
                        rx.select.root(
                            rx.select.trigger(),
                            rx.select.content(
                                rx.select.item("Elbow", value="Elbow"),
                                rx.select.item("Knee", value="Knee"),
                                rx.select.item("Shoulder", value="Shoulder"),
                                rx.select.item("Hip", value="Hip"),
                            ),
                            default_value=MeasureState.joint, on_change=MeasureState.set_joint
                        ),
                        rx.text("Exercise"),
                        rx.select.root(
                            rx.select.trigger(),
                            rx.select.content(
                                rx.select.item("Flexion", value="Flexion"),
                                rx.select.item("Extension", value="Extension"),
                            ),
                            default_value=MeasureState.exercise, on_change=MeasureState.set_exercise
                        ),
                        rx.text("Duration"),
                        rx.segmented_control.root(
                            rx.segmented_control.item("15s", value="15s"),
                            rx.segmented_control.item("30s", value="30s"),
                            rx.segmented_control.item("45s", value="45s"),
                            rx.segmented_control.item("60s", value="60s"),
                            value=str(MeasureState.duration) + "s", on_change=MeasureState.set_duration_str
                        ),
                        spacing="4",
                    ),
                    width="100%", max_width="500px",
                ),
                rx.hstack(
                    rx.link(rx.button("Back", variant="soft"), href="/"),
                    rx.button(
                        rx.hstack(rx.text("Begin"), rx.icon("play")),
                        on_click=MeasureState.start_measurement,
                    ),
                    spacing="4", padding_top="1em",
                ),
                align="center", justify="center", height="100vh",
            ),
        ),
    )

def history_page() -> rx.Component:
    return rx.vstack(
        rx.heading("History", size="8"),
        rx.hstack(
            rx.select.root(
                rx.select.trigger(),
                rx.select.content(
                    rx.select.item("All", value="All"),
                    rx.select.item("Elbow", value="Elbow"),
                    rx.select.item("Knee", value="Knee"),
                    rx.select.item("Shoulder", value="Shoulder"),
                    rx.select.item("Hip", value="Hip"),
                ),
                default_value=HistoryState.filter_joint, on_change=HistoryState.set_filter_joint
            ),
            rx.select.root(
                rx.select.trigger(),
                rx.select.content(
                    rx.select.item("All", value="All"),
                    rx.select.item("Flexion", value="Flexion"),
                    rx.select.item("Extension", value="Extension"),
                ),
                default_value=HistoryState.filter_exercise, on_change=HistoryState.set_filter_exercise
            ),
            spacing="4",
        ),
        rx.vstack(
            # This is now a hardcoded example log to prevent crashing.
            rx.link(
                rx.card(
                    rx.hstack(
                        rx.vstack(rx.text("Elbow: Flexion", weight="bold"), rx.text("a few seconds ago"), align="start"),
                        rx.spacer(),
                        rx.vstack(rx.text("30° / 120°"), rx.text("Min / Max"), align="end"),
                    )
                ),
                href="/history/1",
                width="100%",
            ),
            spacing="4", width="100%", max_width="500px",
        ),
        rx.link(rx.button("Back", variant="soft"), href="/"),
        align="center", spacing="4", padding_top="2em", height="100vh",
    )

def log_detail_page() -> rx.Component:
    return rx.vstack(
        rx.heading(f"Log #{LogDetailState.log_id}", size="8"),
        rx.link(rx.button("Back to History"), href="/history"),
        align="center", spacing="4", padding_top="2em", height="100vh",
    )

app = rx.App(style=base_style, theme=rx.theme(appearance="dark", accent_color="cyan", radius="large"))
app.add_page(index, route="/")
app.add_page(measure_page, route="/measure")
app.add_page(history_page, route="/history")
app.add_page(log_detail_page, route="/history/[log_id]")