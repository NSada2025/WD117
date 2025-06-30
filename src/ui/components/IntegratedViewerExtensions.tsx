import React, { useState, useRef, useEffect } from 'react';
import { ImageViewer } from './ImageViewer';

interface SliderComparisonProps {
  leftImage: any;
  rightImage: any;
  className?: string;
}

export const SliderComparison: React.FC<SliderComparisonProps> = ({
  leftImage,
  rightImage,
  className = ''
}) => {
  const [sliderPosition, setSliderPosition] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    setSliderPosition(Math.max(0, Math.min(100, percentage)));
  };

  useEffect(() => {
    const handleGlobalMouseUp = () => setIsDragging(false);
    const handleGlobalMouseMove = (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = (x / rect.width) * 100;
      setSliderPosition(Math.max(0, Math.min(100, percentage)));
    };

    if (isDragging) {
      document.addEventListener('mouseup', handleGlobalMouseUp);
      document.addEventListener('mousemove', handleGlobalMouseMove);
    }

    return () => {
      document.removeEventListener('mouseup', handleGlobalMouseUp);
      document.removeEventListener('mousemove', handleGlobalMouseMove);
    };
  }, [isDragging]);

  return (
    <div
      ref={containerRef}
      className={`relative overflow-hidden ${className}`}
      onMouseMove={handleMouseMove}
    >
      {/* 左側画像 */}
      <div className="absolute inset-0">
        <ImageViewer
          image={leftImage}
          showAnnotations={true}
          showMeasurements={true}
          className="h-full"
        />
      </div>

      {/* 右側画像（クリップされる） */}
      <div
        className="absolute inset-0"
        style={{
          clipPath: `inset(0 0 0 ${sliderPosition}%)`
        }}
      >
        <ImageViewer
          image={rightImage}
          showAnnotations={true}
          showMeasurements={true}
          className="h-full"
        />
      </div>

      {/* スライダーハンドル */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize"
        style={{ left: `${sliderPosition}%` }}
        onMouseDown={handleMouseDown}
      >
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-full w-8 h-8 shadow-lg flex items-center justify-center">
          <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8 5v10l-3-3m0 0l3-3m8-2v10l3-3m0 0l-3-3" />
          </svg>
        </div>
      </div>

      {/* ラベル */}
      <div className="absolute top-4 left-4 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
        Before
      </div>
      <div className="absolute top-4 right-4 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
        After
      </div>
    </div>
  );
};

interface OverlayComparisonProps {
  baseImage: any;
  overlayImage: any;
  opacity?: number;
  blendMode?: string;
  className?: string;
}

export const OverlayComparison: React.FC<OverlayComparisonProps> = ({
  baseImage,
  overlayImage,
  opacity = 0.5,
  blendMode = 'normal',
  className = ''
}) => {
  const [overlayOpacity, setOverlayOpacity] = useState(opacity);
  const [currentBlendMode, setCurrentBlendMode] = useState(blendMode);

  const blendModes = [
    'normal',
    'multiply',
    'screen',
    'overlay',
    'difference',
    'exclusion',
    'color-dodge',
    'color-burn'
  ];

  return (
    <div className={`relative ${className}`}>
      {/* コントロールパネル */}
      <div className="absolute top-4 right-4 z-20 bg-black bg-opacity-75 rounded p-3 space-y-2">
        <div>
          <label className="text-white text-xs block mb-1">透明度</label>
          <input
            type="range"
            min="0"
            max="100"
            value={overlayOpacity * 100}
            onChange={(e) => setOverlayOpacity(parseInt(e.target.value) / 100)}
            className="w-32"
          />
        </div>
        <div>
          <label className="text-white text-xs block mb-1">ブレンドモード</label>
          <select
            value={currentBlendMode}
            onChange={(e) => setCurrentBlendMode(e.target.value)}
            className="bg-gray-700 text-white text-xs rounded px-2 py-1"
          >
            {blendModes.map(mode => (
              <option key={mode} value={mode}>{mode}</option>
            ))}
          </select>
        </div>
      </div>

      {/* ベース画像 */}
      <div className="absolute inset-0">
        <ImageViewer
          image={baseImage}
          showAnnotations={true}
          showMeasurements={true}
          className="h-full"
        />
      </div>

      {/* オーバーレイ画像 */}
      <div
        className="absolute inset-0"
        style={{
          opacity: overlayOpacity,
          mixBlendMode: currentBlendMode as any
        }}
      >
        <ImageViewer
          image={overlayImage}
          showAnnotations={false}
          showMeasurements={false}
          className="h-full"
        />
      </div>

      {/* ラベル */}
      <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
        Base: {baseImage.type} | Overlay: {overlayImage.type} ({Math.round(overlayOpacity * 100)}%)
      </div>
    </div>
  );
};

interface SynchronizedViewerProps {
  images: any[];
  onSyncUpdate?: (state: SyncState) => void;
  className?: string;
}

interface SyncState {
  zoom: number;
  pan: { x: number; y: number };
  brightness: number;
  contrast: number;
}

export const SynchronizedViewer: React.FC<SynchronizedViewerProps> = ({
  images,
  onSyncUpdate,
  className = ''
}) => {
  const [syncState, setSyncState] = useState<SyncState>({
    zoom: 1,
    pan: { x: 0, y: 0 },
    brightness: 100,
    contrast: 100
  });

  const handleViewerUpdate = (index: number, update: Partial<SyncState>) => {
    setSyncState(prev => {
      const newState = { ...prev, ...update };
      if (onSyncUpdate) {
        onSyncUpdate(newState);
      }
      return newState;
    });
  };

  const gridCols = images.length <= 2 ? 'grid-cols-2' : 
                   images.length <= 4 ? 'grid-cols-2' : 
                   'grid-cols-3';

  return (
    <div className={`grid ${gridCols} gap-2 ${className}`}>
      {images.map((image, index) => (
        <div key={image.id} className="relative">
          <ImageViewer
            image={image}
            showAnnotations={true}
            showMeasurements={true}
            className="h-full"
            // 同期された値を渡す
            // TODO: ImageViewerコンポーネントに同期プロパティを追加する必要がある
          />
          <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
            {image.type} - {new Date(image.captureDate || image.analysisDate).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
};

interface MeasurementToolsProps {
  onMeasurementComplete?: (measurement: Measurement) => void;
}

interface Measurement {
  type: 'distance' | 'angle' | 'area';
  points: { x: number; y: number }[];
  value: number;
  unit: string;
}

export const MeasurementTools: React.FC<MeasurementToolsProps> = ({
  onMeasurementComplete
}) => {
  const [activeTool, setActiveTool] = useState<'distance' | 'angle' | 'area' | null>(null);
  const [points, setPoints] = useState<{ x: number; y: number }[]>([]);

  const calculateDistance = (p1: { x: number; y: number }, p2: { x: number; y: number }) => {
    return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
  };

  const calculateAngle = (p1: { x: number; y: number }, p2: { x: number; y: number }, p3: { x: number; y: number }) => {
    const a = calculateDistance(p2, p3);
    const b = calculateDistance(p1, p3);
    const c = calculateDistance(p1, p2);
    const angle = Math.acos((a * a + c * c - b * b) / (2 * a * c));
    return (angle * 180) / Math.PI;
  };

  const calculateArea = (points: { x: number; y: number }[]) => {
    let area = 0;
    for (let i = 0; i < points.length; i++) {
      const j = (i + 1) % points.length;
      area += points[i].x * points[j].y;
      area -= points[j].x * points[i].y;
    }
    return Math.abs(area / 2);
  };

  const handlePointAdd = (point: { x: number; y: number }) => {
    const newPoints = [...points, point];
    setPoints(newPoints);

    if (activeTool === 'distance' && newPoints.length === 2) {
      const distance = calculateDistance(newPoints[0], newPoints[1]);
      if (onMeasurementComplete) {
        onMeasurementComplete({
          type: 'distance',
          points: newPoints,
          value: distance,
          unit: 'px'
        });
      }
      setPoints([]);
    } else if (activeTool === 'angle' && newPoints.length === 3) {
      const angle = calculateAngle(newPoints[0], newPoints[1], newPoints[2]);
      if (onMeasurementComplete) {
        onMeasurementComplete({
          type: 'angle',
          points: newPoints,
          value: angle,
          unit: '°'
        });
      }
      setPoints([]);
    } else if (activeTool === 'area' && newPoints.length >= 3) {
      // エリア測定は右クリックで完了
    }
  };

  return (
    <div className="flex gap-2 p-2 bg-white rounded shadow">
      <button
        onClick={() => setActiveTool('distance')}
        className={`px-3 py-1 rounded text-sm ${
          activeTool === 'distance' ? 'bg-blue-500 text-white' : 'bg-gray-200'
        }`}
      >
        距離
      </button>
      <button
        onClick={() => setActiveTool('angle')}
        className={`px-3 py-1 rounded text-sm ${
          activeTool === 'angle' ? 'bg-blue-500 text-white' : 'bg-gray-200'
        }`}
      >
        角度
      </button>
      <button
        onClick={() => setActiveTool('area')}
        className={`px-3 py-1 rounded text-sm ${
          activeTool === 'area' ? 'bg-blue-500 text-white' : 'bg-gray-200'
        }`}
      >
        面積
      </button>
      {points.length > 0 && (
        <span className="text-sm text-gray-600 ml-2">
          {points.length}点選択中
        </span>
      )}
    </div>
  );
};