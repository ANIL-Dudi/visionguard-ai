import { useRef, useState, useEffect } from "react";

const KIND_COLOR = {
  detection: "#2DD4BF",
  violation: "#F5A623",
  critical: "#EF4444",
};

/**
 * Renders an <img> with absolutely-positioned bounding boxes scaled from
 * the original image's natural pixel coordinates to however the image is
 * actually displayed (responsive-safe).
 */
export default function BoundingBoxOverlay({ src, boxes = [], alt = "" }) {
  const imgRef = useRef(null);
  const [scale, setScale] = useState(null);

  const recompute = () => {
    const img = imgRef.current;
    if (!img || !img.naturalWidth) return;
    setScale({
      sx: img.clientWidth / img.naturalWidth,
      sy: img.clientHeight / img.naturalHeight,
    });
  };

  useEffect(() => {
    window.addEventListener("resize", recompute);
    return () => window.removeEventListener("resize", recompute);
  }, []);

  return (
    <div className="relative inline-block w-full">
      {/* corner brackets — the viewfinder signature */}
      <span className="viewfinder-corner border-t-2 border-l-2 top-0 left-0 rounded-tl-lg" />
      <span className="viewfinder-corner border-t-2 border-r-2 top-0 right-0 rounded-tr-lg" />
      <span className="viewfinder-corner border-b-2 border-l-2 bottom-0 left-0 rounded-bl-lg" />
      <span className="viewfinder-corner border-b-2 border-r-2 bottom-0 right-0 rounded-br-lg" />

      <img
        ref={imgRef}
        src={src}
        alt={alt}
        onLoad={recompute}
        className="w-full h-auto rounded-lg block"
      />
      {scale &&
        boxes.map((b, i) => {
          const color = KIND_COLOR[b.kind] || KIND_COLOR.detection;
          return (
            <div
              key={i}
              className="absolute border-2 pointer-events-none"
              style={{
                borderColor: color,
                left: b.x1 * scale.sx,
                top: b.y1 * scale.sy,
                width: (b.x2 - b.x1) * scale.sx,
                height: (b.y2 - b.y1) * scale.sy,
              }}
            >
              <span
                className="absolute -top-5 left-0 text-[10px] font-mono px-1 rounded-sm whitespace-nowrap"
                style={{ background: color, color: "#0D1117" }}
              >
                {b.label} {(b.confidence * 100).toFixed(0)}%
              </span>
            </div>
          );
        })}
    </div>
  );
}
