import React, { useState, useRef, useEffect } from 'react';
import { FacialPhoto, XRayImage, IntraoralPhoto, ModelPhoto, PhotoAnnotation } from '../types';

interface ImageViewerProps {
  image: FacialPhoto | XRayImage | IntraoralPhoto | ModelPhoto;
  showAnnotations?: boolean;
  showMeasurements?: boolean;
  onAnnotationAdd?: (annotation: PhotoAnnotation) => void;
  onImageClick?: (coordinates: { x: number; y: number }) => void;
  className?: string;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  image,
  showAnnotations = true,
  showMeasurements = true,
  onAnnotationAdd,
  onImageClick,
  className = ''
}) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDrawing, setIsDrawing] = useState(false);
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const imageRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(prev => Math.max(0.5, Math.min(5, prev * delta)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.shiftKey) {
      setIsDrawing(true);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (e.buttons === 1 && !e.shiftKey) {
      setPan(prev => ({
        x: prev.x + e.movementX,
        y: prev.y + e.movementY
      }));
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    if (!imageRef.current || !onImageClick) return;
    
    const rect = imageRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - pan.x) / zoom;
    const y = (e.clientY - rect.top - pan.y) / zoom;
    
    onImageClick({ x, y });
  };

  const renderAnnotations = () => {
    if (!showAnnotations || !('annotations' in image) || !image.annotations) return null;

    return image.annotations.map(annotation => (
      <div
        key={annotation.id}
        className="absolute pointer-events-none"
        style={{
          left: `${annotation.coordinates[0] * zoom + pan.x}px`,
          top: `${annotation.coordinates[1] * zoom + pan.y}px`,
          transform: `scale(${zoom})`
        }}
      >
        <div className="bg-blue-500 text-white px-2 py-1 rounded text-xs">
          {annotation.label}
        </div>
      </div>
    ));
  };

  return (
    <div className={`relative overflow-hidden bg-gray-900 ${className}`}>
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        <div className="bg-black bg-opacity-50 rounded p-2">
          <label className="text-white text-xs">Zoom: {Math.round(zoom * 100)}%</label>
          <input
            type="range"
            min="50"
            max="500"
            value={zoom * 100}
            onChange={(e) => setZoom(parseInt(e.target.value) / 100)}
            className="w-24 ml-2"
          />
        </div>
        <div className="bg-black bg-opacity-50 rounded p-2">
          <label className="text-white text-xs">Brightness</label>
          <input
            type="range"
            min="0"
            max="200"
            value={brightness}
            onChange={(e) => setBrightness(parseInt(e.target.value))}
            className="w-24 ml-2"
          />
        </div>
        <div className="bg-black bg-opacity-50 rounded p-2">
          <label className="text-white text-xs">Contrast</label>
          <input
            type="range"
            min="0"
            max="200"
            value={contrast}
            onChange={(e) => setContrast(parseInt(e.target.value))}
            className="w-24 ml-2"
          />
        </div>
      </div>

      <div
        ref={imageRef}
        className="relative w-full h-full cursor-move"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onClick={handleClick}
      >
        <img
          src={image.url}
          alt={`${image.type} image`}
          className="absolute"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'top left',
            filter: `brightness(${brightness}%) contrast(${contrast}%)`,
            maxWidth: 'none'
          }}
          draggable={false}
        />
        {renderAnnotations()}
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 pointer-events-none"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'top left'
          }}
        />
      </div>

      <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 rounded p-2">
        <p className="text-white text-sm">
          Type: {image.type} | Date: {new Date(image.captureDate).toLocaleDateString()}
        </p>
        <p className="text-white text-xs mt-1">
          Shift+Click to annotate | Scroll to zoom | Drag to pan
        </p>
      </div>
    </div>
  );
};