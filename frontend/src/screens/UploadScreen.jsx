import { useRef, useState } from "react";
import Card from "../components/Card.jsx";

export default function UploadScreen({ onAnalyze, loading, error }) {
  const inputRef = useRef(null);
  const [preview, setPreview] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = (file) => {
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    onAnalyze(file);
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <div className="mb-8">
        <p className="eyebrow mb-2">Screen 01 — Image Intake</p>
        <h1 className="font-display text-3xl font-semibold text-textprimary">
          Upload Traffic Image
        </h1>
        <p className="text-textmuted mt-2">
          Drop a traffic-camera frame. VisionGuard scans it for vehicle,
          helmet, triple-riding and number-plate signals.
        </p>
      </div>

      <Card>
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFile(e.dataTransfer.files?.[0]);
          }}
          onClick={() => inputRef.current?.click()}
          className={`relative rounded-lg border-2 border-dashed cursor-pointer transition-colors flex flex-col items-center justify-center text-center px-6 py-16 ${
            dragOver ? "border-cyan bg-cyan/5" : "border-border hover:border-cyan/50"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />

          {preview ? (
            <div className="relative w-full max-w-md">
              <span className="viewfinder-corner border-t-2 border-l-2 top-0 left-0 rounded-tl-lg" />
              <span className="viewfinder-corner border-t-2 border-r-2 top-0 right-0 rounded-tr-lg" />
              <span className="viewfinder-corner border-b-2 border-l-2 bottom-0 left-0 rounded-bl-lg" />
              <span className="viewfinder-corner border-b-2 border-r-2 bottom-0 right-0 rounded-br-lg" />
              <img src={preview} alt="preview" className="rounded-lg w-full" />
              {loading && (
                <div className="absolute inset-0 overflow-hidden rounded-lg">
                  <div className="absolute left-0 w-full h-1 bg-cyan/80 shadow-[0_0_12px_2px_rgba(45,212,191,0.8)] animate-scan" />
                </div>
              )}
            </div>
          ) : (
            <>
              <div className="w-12 h-12 rounded-full border-2 border-cyan/60 flex items-center justify-center mb-4 text-cyan font-display text-xl">
                +
              </div>
              <p className="font-medium text-textprimary">
                Click to upload, or drag a JPG / PNG here
              </p>
              <p className="text-sm text-textmuted mt-1 font-mono">bike.jpg</p>
            </>
          )}
        </div>

        {loading && (
          <p className="text-center text-cyan font-mono text-sm mt-4 animate-pulse">
            Running detection pipeline…
          </p>
        )}
        {error && (
          <p className="text-center text-red font-mono text-sm mt-4">{error}</p>
        )}
      </Card>
    </div>
  );
}
