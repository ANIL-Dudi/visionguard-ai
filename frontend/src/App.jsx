import { useState } from "react";
import StepperNav, { STEPS } from "./components/StepperNav.jsx";
import UploadScreen from "./screens/UploadScreen.jsx";
import DetectionScreen from "./screens/DetectionScreen.jsx";
import PlateScreen from "./screens/PlateScreen.jsx";
import EvidenceScreen from "./screens/EvidenceScreen.jsx";
import RiskScreen from "./screens/RiskScreen.jsx";
import DashboardScreen from "./screens/DashboardScreen.jsx";
import { detectViolation } from "./api/client.js";

const ORDER = STEPS.map((s) => s.key);

export default function App() {
  const [screen, setScreen] = useState("upload");
  const [maxReached, setMaxReached] = useState("upload");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const goTo = (key) => setScreen(key);

  const advanceMax = (key) => {
    if (ORDER.indexOf(key) > ORDER.indexOf(maxReached)) setMaxReached(key);
  };

  const handleAnalyze = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const data = await detectViolation(file);
      setResult(data);
      setScreen("detection");
      advanceMax("detection");
    } catch (e) {
      setError(e.message || "Detection failed. Please try another image.");
    } finally {
      setLoading(false);
    }
  };

  const next = (key) => {
    setScreen(key);
    advanceMax(key);
  };

  const restart = () => {
    setResult(null);
    setScreen("upload");
    setMaxReached("upload");
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-border px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-md bg-cyan/10 border border-cyan flex items-center justify-center text-cyan font-display text-sm">
            VG
          </div>
          <div>
            <p className="font-display font-semibold text-textprimary leading-tight">
              VisionGuard AI
            </p>
            <p className="text-xs text-textmuted leading-tight">
              Intelligent Traffic Violation Enforcement
            </p>
          </div>
        </div>
        <span className="font-mono text-xs text-textmuted hidden sm:inline">
          v1.0 · YOLOv8 + EasyOCR
        </span>
      </header>

      <StepperNav current={screen} onJump={goTo} maxReached={maxReached} />

      <main className="flex-1">
        {screen === "upload" && (
          <UploadScreen onAnalyze={handleAnalyze} loading={loading} error={error} />
        )}
        {screen === "detection" && (
          <DetectionScreen result={result} onNext={() => next("plate")} />
        )}
        {screen === "plate" && (
          <PlateScreen result={result} onNext={() => next("evidence")} />
        )}
        {screen === "evidence" && (
          <EvidenceScreen result={result} onNext={() => next("risk")} />
        )}
        {screen === "risk" && (
          <RiskScreen result={result} onNext={() => next("dashboard")} />
        )}
        {screen === "dashboard" && <DashboardScreen onRestart={restart} />}
      </main>
    </div>
  );
}
