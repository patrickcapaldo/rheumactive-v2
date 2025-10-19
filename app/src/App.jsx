import React, { useState, useEffect, useRef, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, addDoc, onSnapshot, query, where, orderBy } from 'firebase/firestore';
import * as tf from '@tensorflow/tfjs';
import * as posedetection from '@tensorflow-models/posenet';
import { Scan, History, Save, Trash, ChevronsLeft, ChevronsRight, PlusCircle } from 'lucide-react';

// --- DO NOT EDIT THESE GLOBAL VARIABLES ---
const __app_id = "rheumactive-v2";
const __firebase_config = JSON.stringify({
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
});
const __initial_auth_token = "YOUR_INITIAL_AUTH_TOKEN";
// ---

// --- Firebase Initialization ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// --- Main App Component ---
const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setUser(user);
        setLoading(false);
      } else {
        signInWithCustomToken(auth, __initial_auth_token)
          .catch((error) => {
            console.error("Error signing in with custom token:", error);
            setLoading(false);
          });
      }
    });
    return () => unsubscribe();
  }, []);

  if (loading) {
    return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <Router>
      <div className="bg-gray-900 text-white min-h-screen">
        <Routes>
          <Route path="/" element={<NavigationView />} />
          <Route path="/measure" element={<MeasurementView user={user} />} />
          <Route path="/history" element={<HistoryView user={user} />} />
        </Routes>
      </div>
    </Router>
  );
};

// --- Views ---
const NavigationView = () => (
  <div className="flex flex-col items-center justify-center min-h-screen">
    <h1 className="text-5xl font-bold mb-8">RheumActive</h1>
    <div className="space-y-4">
      <Link to="/measure" className="flex items-center justify-center bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-4 px-8 rounded-lg text-2xl">
        <Scan className="mr-4" /> Measure Mobility
      </Link>
      <Link to="/history" className="flex items-center justify-center bg-gray-700 hover:bg-gray-800 text-white font-bold py-4 px-8 rounded-lg text-2xl">
        <History className="mr-4" /> View History
      </Link>
    </div>
  </div>
);

const MeasurementView = ({ user }) => {
  const navigate = useNavigate();
  const [measurementState, setMeasurementState] = useState('selection'); // selection, measuring, complete
  const [joint, setJoint] = useState('Elbow');
  const [exercise, setExercise] = useState('Flexion');
  const [duration, setDuration] = useState(15);
  const [model, setModel] = useState(null);
  const [rawLogData, setRawLogData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [cameraOk, setCameraOk] = useState(false);
  const [aiHatOk, setAiHatOk] = useState(false);
  const [checkingHardware, setCheckingHardware] = useState(true);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Placeholder for AI HAT check
  const checkAiHat = async () => {
    // This is a placeholder. In a real scenario, this would
    // involve a call to a local server on the Raspberry Pi
    // to check for the AI HAT.
    return true;
  };

  useEffect(() => {
    const checkHardware = async () => {
      // Check for camera
      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasCamera = devices.some(device => device.kind === 'videoinput');
      setCameraOk(hasCamera);

      // Check for AI HAT
      const hasAiHat = await checkAiHat();
      setAiHatOk(hasAiHat);

      setCheckingHardware(false);
    };

    checkHardware();

    posedetection.load({
      architecture: 'MobileNetV1',
      outputStride: 16,
      inputResolution: { width: 640, height: 480 },
      multiplier: 0.75
    }).then(setModel);
  }, []);

  const handleStart = () => {
    setMeasurementState('measuring');
    setRawLogData([]);
    setSummary(null);
  };

  const handleDiscard = () => {
    setMeasurementState('selection');
    setRawLogData([]);
    setSummary(null);
  };

  const handleSave = async () => {
    if (!user || !summary) return;
    const log = {
      userId: user.uid,
      timestamp: Date.now(),
      joint,
      exercise,
      durationSeconds: duration,
      minAngle: summary.min,
      maxAngle: summary.max,
      avgAngle: summary.avg,
      rawLogData: JSON.stringify(rawLogData),
    };
    await addDoc(collection(db, `/artifacts/${__app_id}/users/${user.uid}/mobility_logs`), log);
  };

  const handleSaveAndMeasureAgain = async () => {
    await handleSave();
    setMeasurementState('selection');
  };

  const handleSaveAndMeasureAnother = async () => {
    await handleSave();
    setJoint('Elbow');
    setExercise('Flexion');
    setDuration(15);
    setMeasurementState('selection');
  };

  const handleSaveAndViewHistory = async () => {
    await handleSave();
    navigate('/history');
  };

  if (!model || checkingHardware) {
    return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center">Loading Model and Checking Hardware...</div>;
  }

  return (
    <div className="p-4">
      {measurementState === 'selection' && (
        <SelectionForm {...{ joint, setJoint, exercise, setExercise, duration, setDuration, handleStart, cameraOk, aiHatOk }} />
      )}
      {measurementState === 'measuring' && (
        <MeasurementInterface {...{ videoRef, canvasRef, model, joint, exercise, duration, setRawLogData, setSummary, setMeasurementState }} />
      )}
      {measurementState === 'complete' && summary && (
        <ResultsScreen {...{ summary, handleDiscard, handleSaveAndMeasureAgain, handleSaveAndMeasureAnother, handleSaveAndViewHistory }} />
      )}
    </div>
  );
};

const HistoryView = ({ user }) => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [jointFilter, setJointFilter] = useState('All');
  const [exerciseFilter, setExerciseFilter] = useState('All');
  const [selectedLog, setSelectedLog] = useState(null);

  useEffect(() => {
    if (!user) return;
    const q = query(collection(db, `/artifacts/${__app_id}/users/${user.uid}/mobility_logs`), orderBy('timestamp', 'desc'));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const logsData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setLogs(logsData);
      setFilteredLogs(logsData);
    });
    return () => unsubscribe();
  }, [user]);

  useEffect(() => {
    let newFilteredLogs = logs;
    if (jointFilter !== 'All') {
      newFilteredLogs = newFilteredLogs.filter(log => log.joint === jointFilter);
    }
    if (exerciseFilter !== 'All') {
      newFilteredLogs = newFilteredLogs.filter(log => log.exercise === exerciseFilter);
    }
    setFilteredLogs(newFilteredLogs);
  }, [logs, jointFilter, exerciseFilter]);

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">History</h1>
        <Link to="/" className="bg-gray-700 hover:bg-gray-800 text-white font-bold py-2 px-4 rounded-lg">Home</Link>
      </div>
      <div className="flex space-x-4 mb-4">
        <select value={jointFilter} onChange={e => setJointFilter(e.target.value)} className="bg-gray-800 text-white p-2 rounded-lg">
          <option>All</option>
          <option>Elbow</option>
          <option>Knee</option>
          <option>Shoulder</option>
          <option>Hip</option>
        </select>
        <select value={exerciseFilter} onChange={e => setExerciseFilter(e.target.value)} className="bg-gray-800 text-white p-2 rounded-lg">
          <option>All</option>
          <option>Flexion</option>
          <option>Extension</option>
        </select>
      </div>
      <LogList logs={filteredLogs} onSelectLog={setSelectedLog} />
      {selectedLog && <Modal log={selectedLog} onClose={() => setSelectedLog(null)} />}
    </div>
  );
};

// --- Components ---
const SelectionForm = ({ joint, setJoint, exercise, setExercise, duration, setDuration, handleStart, cameraOk, aiHatOk }) => {
  const hardwareReady = cameraOk && aiHatOk;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-3xl font-bold mb-8">Measure Mobility</h2>
      {!hardwareReady && (
        <div className="bg-yellow-500 text-black p-4 rounded-lg mb-4 max-w-xs text-center">
          {!cameraOk && <p>Camera not detected. Please connect a camera.</p>}
          {!aiHatOk && <p>AI HAT not detected. Please ensure it is connected.</p>}
        </div>
      )}
      <div className="space-y-4 w-full max-w-xs">
        <div>
          <label className="text-lg">Joint</label>
          <select value={joint} onChange={e => setJoint(e.target.value)} className="w-full bg-gray-800 text-white p-2 rounded-lg">
            <option>Elbow</option>
            <option>Knee</option>
            <option>Shoulder</option>
            <option>Hip</option>
          </select>
        </div>
        <div>
          <label className="text-lg">Exercise</label>
          <select value={exercise} onChange={e => setExercise(e.target.value)} className="w-full bg-gray-800 text-white p-2 rounded-lg">
            <option>Flexion</option>
            <option>Extension</option>
          </select>
        </div>
        <div>
          <label className="text-lg">Duration (seconds)</label>
          <select value={duration} onChange={e => setDuration(parseInt(e.target.value))} className="w-full bg-gray-800 text-white p-2 rounded-lg">
            <option>15</option>
            <option>30</option>
            <option>45</option>
          </select>
        </div>
        <button onClick={handleStart} disabled={!hardwareReady} className={`w-full text-white font-bold py-3 px-4 rounded-lg text-xl ${hardwareReady ? 'bg-cyan-500 hover:bg-cyan-600' : 'bg-gray-600 cursor-not-allowed'}`}>
          Start Measurement
        </button>
      </div>
    </div>
  );
};

const MeasurementInterface = ({ videoRef, canvasRef, model, joint, exercise, duration, setRawLogData, setSummary, setMeasurementState }) => {
  const [timeLeft, setTimeLeft] = useState(duration);
  const [currentAngle, setCurrentAngle] = useState(0);
  const lastLogTime = useRef(0);

  const jointsMap = {
    'Elbow:Flexion': ['left_shoulder', 'left_elbow', 'left_wrist'],
    'Elbow:Extension': ['left_shoulder', 'left_elbow', 'left_wrist'],
    'Knee:Flexion': ['left_hip', 'left_knee', 'left_ankle'],
    'Knee:Extension': ['left_hip', 'left_knee', 'left_ankle'],
    'Shoulder:Flexion': ['left_hip', 'left_shoulder', 'left_elbow'],
    'Shoulder:Extension': ['left_hip', 'left_shoulder', 'left_elbow'],
    'Hip:Flexion': ['left_shoulder', 'left_hip', 'left_knee'],
    'Hip:Extension': ['left_shoulder', 'left_hip', 'left_knee'],
  };

  const calculateAngle = (p1, p2, p3) => {
    const a = Math.sqrt(Math.pow(p2.x - p3.x, 2) + Math.pow(p2.y - p3.y, 2));
    const b = Math.sqrt(Math.pow(p1.x - p3.x, 2) + Math.pow(p1.y - p3.y, 2));
    const c = Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
    return Math.acos((a * a + c * c - b * b) / (2 * a * c)) * 180 / Math.PI;
  };

  const detectPose = useCallback(async () => {
    if (videoRef.current && videoRef.current.readyState === 4) {
      const pose = await model.estimateSinglePose(videoRef.current);
      const ctx = canvasRef.current.getContext('2d');
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);

      if (pose) {
        const keypoints = pose.keypoints;
        const [p1Name, p2Name, p3Name] = jointsMap[`${joint}:${exercise}`];
        const p1 = keypoints.find(k => k.part === p1Name);
        const p2 = keypoints.find(k => k.part === p2Name);
        const p3 = keypoints.find(k => k.part === p3Name);

        if (p1 && p2 && p3 && p1.score > 0.5 && p2.score > 0.5 && p3.score > 0.5) {
          const angle = calculateAngle(p1.position, p2.position, p3.position);
          setCurrentAngle(angle);

          const now = Date.now();
          if (now - lastLogTime.current > 250) { // 4Hz
            setRawLogData(prev => [...prev, { timeMs: now, angle }]);
            lastLogTime.current = now;
          }

          // Draw keypoints and lines
          ctx.fillStyle = 'cyan';
          ctx.strokeStyle = 'cyan';
          ctx.lineWidth = 2;
          [p1, p2, p3].forEach(p => {
            ctx.beginPath();
            ctx.arc(p.position.x, p.position.y, 5, 0, 2 * Math.PI);
            ctx.fill();
          });
          ctx.beginPath();
          ctx.moveTo(p1.position.x, p1.position.y);
          ctx.lineTo(p2.position.x, p2.position.y);
          ctx.lineTo(p3.position.x, p3.position.y);
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(detectPose);
  }, [model, joint, exercise, setRawLogData]);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      });
    
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          setMeasurementState('complete');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    requestAnimationFrame(detectPose);

    return () => {
      clearInterval(timer);
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, [detectPose, setMeasurementState]);

  useEffect(() => {
    if (measurementState === 'complete') {
      const angles = rawLogData.map(d => d.angle);
      const min = Math.min(...angles);
      const max = Math.max(...angles);
      const avg = angles.reduce((a, b) => a + b, 0) / angles.length;
      setSummary({ min, max, avg });
    }
  }, [measurementState, rawLogData, setSummary]);

  return (
    <div className="relative">
      <video ref={videoRef} className="w-full h-full" style={{ transform: 'scaleX(-1)' }} />
      <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-full" />
      <div className="absolute top-4 left-4 bg-gray-900 bg-opacity-75 p-4 rounded-lg">
        <div className="text-6xl font-bold text-cyan-400">{Math.round(currentAngle)}°</div>
      </div>
      <div className="absolute top-4 right-4 bg-gray-900 bg-opacity-75 p-4 rounded-lg">
        <div className="text-6xl font-bold">{timeLeft}</div>
      </div>
    </div>
  );
};

const ResultsScreen = ({ summary, handleDiscard, handleSaveAndMeasureAgain, handleSaveAndMeasureAnother, handleSaveAndViewHistory }) => (
  <div className="flex flex-col items-center justify-center min-h-screen">
    <h2 className="text-3xl font-bold mb-8">Measurement Complete</h2>
    <div className="grid grid-cols-3 gap-4 text-center mb-8">
      <div>
        <div className="text-4xl font-bold text-cyan-400">{Math.round(summary.min)}°</div>
        <div className="text-lg">Min Angle</div>
      </div>
      <div>
        <div className="text-4xl font-bold text-cyan-400">{Math.round(summary.max)}°</div>
        <div className="text-lg">Max Angle</div>
      </div>
      <div>
        <div className="text-4xl font-bold text-cyan-400">{Math.round(summary.avg)}°</div>
        <div className="text-lg">Avg Angle</div>
      </div>
    </div>
    <div className="space-y-4 w-full max-w-sm">
      <button onClick={handleSaveAndMeasureAgain} className="w-full flex items-center justify-center bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-4 rounded-lg">
        <Save className="mr-2" /> Save & Measure Same
      </button>
      <button onClick={handleSaveAndMeasureAnother} className="w-full flex items-center justify-center bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-3 px-4 rounded-lg">
        <PlusCircle className="mr-2" /> Save & Measure Another
      </button>
      <button onClick={handleSaveAndViewHistory} className="w-full flex items-center justify-center bg-gray-700 hover:bg-gray-800 text-white font-bold py-3 px-4 rounded-lg">
        <History className="mr-2" /> Save & View History
      </button>
      <button onClick={handleDiscard} className="w-full flex items-center justify-center bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-4 rounded-lg">
        <Trash className="mr-2" /> Discard
      </button>
    </div>
  </div>
);

const LogList = ({ logs, onSelectLog }) => (
  <div className="space-y-2">
    {logs.map(log => (
      <div key={log.id} onClick={() => onSelectLog(log)} className="bg-gray-800 p-4 rounded-lg cursor-pointer hover:bg-gray-700">
        <div className="flex justify-between">
          <div>
            <div className="font-bold">{log.joint}: {log.exercise}</div>
            <div>{new Date(log.timestamp).toLocaleString()}</div>
          </div>
          <div className="text-right">
            <div>Duration: {log.durationSeconds}s</div>
            <div>Min/Max: {Math.round(log.minAngle)}° / {Math.round(log.maxAngle)}°</div>
          </div>
        </div>
      </div>
    ))}
  </div>
);

const Modal = ({ log, onClose }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
    <div className="bg-gray-800 p-8 rounded-lg max-w-2xl w-full">
      <h3 className="text-2xl font-bold mb-4">Log Details</h3>
      <pre className="bg-gray-900 p-4 rounded-lg text-sm overflow-auto max-h-96">
        {JSON.stringify(JSON.parse(log.rawLogData), null, 2)}
      </pre>
      <button onClick={onClose} className="mt-4 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded-lg">
        Close
      </button>
    </div>
  </div>
);

export default App;