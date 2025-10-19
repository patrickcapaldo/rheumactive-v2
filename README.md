# RheumActive v2

This is the second version of RheumActive, this time taking a computer vision-based approach to helping people with rheumatoid arthritis monitor and improve their mobility.

## Features

- Real-time joint angle measurement using a webcam.
- Persistent data logging to LocalStorage.
- History view with filtering options.
- Modern and responsive UI.

## Technology Stack

- **Frontend:**
  - React
  - Tailwind CSS
  - Vite
- **Pose Detection:**
  - TensorFlow.js
  - Posenet
- **Data Storage:**
  - Local

### Running the Application

```bash
cd app
npm run dev
```

This will start the development server at `http://localhost:5173`.