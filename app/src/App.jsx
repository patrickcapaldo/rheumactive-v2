import React, { useState, useEffect, useRef, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import * as tf from '@tensorflow/tfjs';
import * as posedetection from '@tensorflow-models/posenet';
import { Scan, History, Save, Trash, ChevronsLeft, ChevronsRight, PlusCircle } from 'lucide-react';


// --- Main App Component ---
const App = () => {
  return (
    <Router>
      <div className="bg-gray-900 text-white min-h-screen">
        <Routes>
          <Route path="/" element={<NavigationView />} />
          <Route path="/measure" element={<MeasurementView />} />
          <Route path="/history" element={<HistoryView />} />
        </Routes>
      </div>
    </Router>
  );
};

// --- Views ---
const NavigationView = () => (
  <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
    <div className="text-center">
      <h1 className="text-6xl font-bold text-white mb-4">RheumActive</h1>
      <p className="text-xl text-gray-400 mb-12">Your personal joint mobility measurement tool.</p>
    </div>
    <div className="space-y-6">
      <Link to="/measure" className="flex items-center justify-center bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-4 px-12 rounded-full text-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
        <Scan className="mr-4" /> Measure Mobility
      </Link>
      <Link to="/history" className="flex items-center justify-center bg-gray-700 hover:bg-gray-600 text-white font-bold py-4 px-12 rounded-full text-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
        <History className="mr-4" /> View History
      </Link>
    </div>
  </div>
);

const MeasurementView = () => {
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
    if (!summary) return;
    const log = {
      id: Date.now(),
      timestamp: Date.now(),
      joint,
      exercise,
      durationSeconds: duration,
      minAngle: summary.min,
      maxAngle: summary.max,
      avgAngle: summary.avg,
      rawLogData: JSON.stringify(rawLogData),
    };
    const logs = JSON.parse(localStorage.getItem('mobility_logs') || '[]');
    logs.push(log);
    localStorage.setItem('mobility_logs', JSON.stringify(logs));
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

const HistoryView = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [jointFilter, setJointFilter] = useState('All');
  const [exerciseFilter, setExerciseFilter] = useState('All');
  const [selectedLog, setSelectedLog] = useState(null);

  useEffect(() => {
    const logsData = JSON.parse(localStorage.getItem('mobility_logs') || '[]');
    setLogs(logsData.sort((a, b) => b.timestamp - a.timestamp));
    setFilteredLogs(logsData);
  }, []);

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
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-white">History</h1>
        <Link to="/" className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-full transition-colors duration-300">Home</Link>
      </div>
      <div className="flex space-x-4 mb-8">
        <select value={jointFilter} onChange={e => setJointFilter(e.target.value)} className="w-full px-4 py-3 text-white bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500">
          <option>All</option>
          <option>Elbow</option>
          <option>Knee</option>
          <option>Shoulder</option>
          <option>Hip</option>
        </select>
        <select value={exerciseFilter} onChange={e => setExerciseFilter(e.target.value)} className="w-full px-4 py-3 text-white bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500">
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

const LogList = ({ logs, onSelectLog }) => (
  <div className="space-y-4">
    {logs.map(log => (
      <div key={log.id} onClick={() => onSelectLog(log)} className="bg-gray-800 p-6 rounded-xl shadow-lg cursor-pointer hover:bg-gray-700 transition-colors duration-300">
        <div className="flex justify-between items-center">
          <div>
            <div className="text-xl font-bold text-white">{log.joint}: {log.exercise}</div>
            <div className="text-sm text-gray-400">{new Date(log.timestamp).toLocaleString()}</div>
          </div>
          <div className="text-right">
            <div className="text-lg text-gray-300">Duration: {log.durationSeconds}s</div>
            <div className="text-lg text-gray-300">Min/Max: {Math.round(log.minAngle)}° / {Math.round(log.maxAngle)}°</div>
          </div>
        </div>
      </div>
    ))
  }
  </div>
);


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
  <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900">
    <div className="w-full max-w-2xl p-8 space-y-8 bg-gray-800 rounded-2xl shadow-2xl text-center">
      <h2 className="text-4xl font-bold text-white">Measurement Complete</h2>
      <div className="grid grid-cols-3 gap-8 text-white">
        <div>
          <div className="text-5xl font-bold text-cyan-400">{Math.round(summary.min)}°</div>
          <div className="text-xl text-gray-400">Min Angle</div>
        </div>
        <div>
          <div className="text-5xl font-bold text-cyan-400">{Math.round(summary.max)}°</div>
          <div className="text-xl text-gray-400">Max Angle</div>
        </div>
        <div>
          <div className="text-5xl font-bold text-cyan-400">{Math.round(summary.avg)}°</div>
          <div className="text-xl text-gray-400">Avg Angle</div>
        </div>
      </div>
      <div className="space-y-4 pt-8">
        <button onClick={handleSaveAndMeasureAgain} className="w-full flex items-center justify-center bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-4 rounded-full transition-colors duration-300">
          <Save className="mr-2" /> Save & Measure Same
        </button>
        <button onClick={handleSaveAndMeasureAnother} className="w-full flex items-center justify-center bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-3 px-4 rounded-full transition-colors duration-300">
          <PlusCircle className="mr-2" /> Save & Measure Another
        </button>
        <button onClick={handleSaveAndViewHistory} className="w-full flex items-center justify-center bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-4 rounded-full transition-colors duration-300">
          <History className="mr-2" /> Save & View History
        </button>
        <button onClick={handleDiscard} className="w-full flex items-center justify-center bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-4 rounded-full transition-colors duration-300">
          <Trash className="mr-2" /> Discard
        </button>
      </div>
    </div>
  </div>
);



const Modal = ({ log, onClose }) => (
  <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4">
    <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl max-w-2xl w-full">
      <h3 className="text-3xl font-bold text-white mb-6">Log Details</h3>
      <pre className="bg-gray-900 p-6 rounded-lg text-sm text-gray-300 overflow-auto max-h-96">
        {JSON.stringify(JSON.parse(log.rawLogData), null, 2)}
      </pre>
      <button onClick={onClose} className="mt-6 w-full bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-4 rounded-full transition-colors duration-300">
        Close
      </button>
    </div>
  </div>
);

export default App;