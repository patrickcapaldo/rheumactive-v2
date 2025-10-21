# RheumActive v2 - Design and Architecture Decisions (The "Whys")

This document outlines the key decisions made during the development of the RheumActive v2 web application, explaining the rationale behind each choice, especially in light of the challenges encountered.

## 1. Initial Project Goals & Web Application Framework Selection

*   **Original Goal:** Develop a pose detection system on Raspberry Pi 5 with a Hailo AI HAT+, including a web-based user interface.
*   **Existing Web App:** A React + Vite application was initially present in the `app/` directory.
*   **User Request:** Switch to a Python-only web application framework (Reflex) to simplify the technology stack and leverage Python's strengths, while maintaining a modern, aesthetically pleasing UI.

*   **Decision:** Abandon React/Vite and adopt **Reflex (version 0.8.15)**.
    *   **Why:** User preference for a Python-only stack, promising modern UI capabilities from Reflex, and the desire for a unified development experience.

## 2. UI/UX Design Principles

*   **User Requirement:** The web app must have a modern style, be aesthetically pleasing, and feature a dark theme, inspired by Material-UI templates.

*   **Decision:** Implement a **dark-themed UI with a focus on clean design and responsiveness**.
    *   **Why (Reflex):** Reflex's built-in component libraries (Chakra/Radix) were expected to provide a modern foundation. Custom styling would be applied to achieve the dark theme and specific aesthetic.
    *   **Why (Flask):** With the pivot to Flask, **Bootstrap 5 (dark theme)** was chosen for its ease of integration via CDN, responsive design capabilities, and extensive component library, allowing for a modern look with minimal custom CSS.

## 3. Hardware Integration & The `picamera2` Challenge

This was the most significant technical hurdle, leading to a major architectural pivot.

*   **Hardware:** Raspberry Pi 5 with Camera Module 3 and Hailo AI HAT+.
*   **Key Library:** `picamera2` for camera control.

*   **Initial Approach (Reflex):** Attempted to integrate `picamera2` directly into the Reflex backend.
    *   **Problem 1 (`ModuleNotFoundError: No module named 'libcamera'`):** `picamera2` relies on system-level Python bindings for `libcamera`. By default, isolated Python virtual environments (`venv`) do not have access to these system packages.
    *   **Attempted Fix 1.1 (Lazy Imports):** Moved `picamera2` imports inside functions to delay loading.
        *   **Outcome:** Only delayed the error; it still occurred at runtime when the camera was initialized.
    *   **Attempted Fix 1.2 (Recreate `venv` with `--system-site-packages`):** This was the recommended solution to allow the `venv` to see system packages.
        *   **Problem 1.2.1 (`numpy` conflicts):** This led to `numpy` version conflicts between `picamera2` (system) and `opencv-python` (installed in `venv`).
        *   **Problem 1.2.2 (`python-prctl` build failure):** `python-prctl` (a dependency of `picamera2`) failed to build from source in the isolated `venv`, even with `libcap-dev` installed on the system.
    *   **Conclusion:** `picamera2` proved fundamentally incompatible with being installed into an isolated Python virtual environment due to its deep system dependencies and build requirements.

*   **Problem 2 (Reflex Event Loop Limitations - `TypeError: functools.partial`):** Even when `picamera2` was theoretically accessible, any attempt to run a long-running background task (like a continuous video stream) from within Reflex's event handlers (using `on_mount`, `yield`, `asyncio.create_task`) resulted in persistent `TypeError`s. This indicated a fundamental incompatibility with the asynchronous event handling patterns required for live streaming in Reflex version `0.8.15`.

## 4. Architectural Pivot: Abandoning Reflex for Flask + Separate Camera Process

*   **Decision:** Abandon Reflex and switch to **Flask** for the web backend, implementing a **two-process architecture**.
    *   **Why:** This was the only viable solution to overcome the insurmountable `picamera2` build issues within an isolated `venv` and the `reflex==0.8.15` event loop's inability to handle continuous background tasks for streaming.
    *   **Architecture:**
        1.  **Flask Backend (`app.py`):** Runs in an isolated `venv`, handles web serving, API endpoints, and communicates with the camera process.
        2.  **Camera Streamer (`camera_streamer.py`):** Runs as a separate process using the **system's Python interpreter** (where `picamera2` is natively installed). It captures frames, processes them, and sends data to the Flask app via a TCP socket.
    *   **Outcome:** Successfully achieved a live camera preview in the web application.

## 5. Frontend Implementation (HTML/CSS/JS with Bootstrap)

*   **Decision:** Use **HTML/CSS/JavaScript with Bootstrap 5** for the frontend.
    *   **Why:** To meet the user's requirement for a modern, dark, and aesthetically pleasing UI. Bootstrap provides a robust, responsive foundation that is easy to integrate and customize. JavaScript handles dynamic updates (MJPEG stream display, angle polling, view switching).

## 6. History Page Functionality

*   **Decision:** Implement the History page as a **static placeholder for now**.
    *   **Why:** The `rx.foreach` component in `reflex==0.8.15` proved incompatible with dynamic list rendering, leading to `ForeachVarError`s. While the architecture has shifted to Flask, re-implementing dynamic filtering and display for the history page was deferred to prioritize getting the core camera functionality working. This will be a future enhancement.

## 7. Log Storage

*   **Decision:** Implement **file-based JSON storage** for measurement logs.
    *   **Why:** Simple, portable, and easy to implement. Each log is stored as a JSON file in an `app/logs/` directory, which is added to `.gitignore` for privacy. This format supports future filtering requirements.
    *   **Format:** Each log includes both a Unix epoch timestamp and a human-readable timestamp.

## Conclusion

The development of the RheumActive v2 web application involved significant architectural pivots to overcome specific technical challenges related to hardware integration and framework limitations. The current architecture provides a stable, functional web application with a live camera preview, a modern UI, and a robust logging mechanism, laying a solid foundation for future enhancements.
