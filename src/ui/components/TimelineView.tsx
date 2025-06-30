import React, { useState } from 'react';
import { FacialPhoto, XRayImage, IntraoralPhoto, ModelPhoto } from '../types';
import { ImageViewer } from './ImageViewer';

interface TimelineViewProps {
  facialPhotos: FacialPhoto[];
  xrayImages: XRayImage[];
  intraoralPhotos: IntraoralPhoto[];
  modelPhotos: ModelPhoto[];
}

type TimelineItem = {
  date: Date;
  type: 'facial' | 'xray' | 'intraoral' | 'model';
  image: FacialPhoto | XRayImage | IntraoralPhoto | ModelPhoto;
};

export const TimelineView: React.FC<TimelineViewProps> = ({
  facialPhotos,
  xrayImages,
  intraoralPhotos,
  modelPhotos
}) => {
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(
    new Set(['facial', 'xray', 'intraoral', 'model'])
  );
  const [expandedDates, setExpandedDates] = useState<Set<string>>(new Set());

  // Combine all images with their types and sort by date
  const timelineItems: TimelineItem[] = [
    ...facialPhotos.map(img => ({ date: new Date(img.captureDate), type: 'facial' as const, image: img })),
    ...xrayImages.map(img => ({ date: new Date(img.captureDate), type: 'xray' as const, image: img })),
    ...intraoralPhotos.map(img => ({ date: new Date(img.captureDate), type: 'intraoral' as const, image: img })),
    ...modelPhotos.map(img => ({ date: new Date(img.captureDate), type: 'model' as const, image: img }))
  ].sort((a, b) => b.date.getTime() - a.date.getTime());

  // Group by date
  const groupedByDate = timelineItems.reduce((acc, item) => {
    const dateKey = item.date.toISOString().split('T')[0];
    if (!acc[dateKey]) {
      acc[dateKey] = [];
    }
    if (selectedTypes.has(item.type)) {
      acc[dateKey].push(item);
    }
    return acc;
  }, {} as Record<string, TimelineItem[]>);

  const toggleType = (type: string) => {
    const newTypes = new Set(selectedTypes);
    if (newTypes.has(type)) {
      newTypes.delete(type);
    } else {
      newTypes.add(type);
    }
    setSelectedTypes(newTypes);
  };

  const toggleDate = (date: string) => {
    const newExpanded = new Set(expandedDates);
    if (newExpanded.has(date)) {
      newExpanded.delete(date);
    } else {
      newExpanded.add(date);
    }
    setExpandedDates(newExpanded);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'facial': return '👤';
      case 'xray': return '📡';
      case 'intraoral': return '🦷';
      case 'model': return '🎭';
      default: return '📷';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'facial': return '顔面写真';
      case 'xray': return 'レントゲン';
      case 'intraoral': return '口腔内写真';
      case 'model': return '模型写真';
      default: return '写真';
    }
  };

  return (
    <div className="h-full flex">
      {/* Filter Sidebar */}
      <div className="w-64 bg-gray-50 p-4 border-r">
        <h3 className="font-semibold mb-4">表示フィルター</h3>
        <div className="space-y-2">
          {['facial', 'xray', 'intraoral', 'model'].map(type => (
            <label key={type} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedTypes.has(type)}
                onChange={() => toggleType(type)}
                className="w-4 h-4 text-blue-600"
              />
              <span className="text-sm">
                {getTypeIcon(type)} {getTypeLabel(type)}
              </span>
            </label>
          ))}
        </div>

        <div className="mt-6">
          <h3 className="font-semibold mb-2">統計</h3>
          <div className="text-sm space-y-1 text-gray-600">
            <div>総画像数: {timelineItems.length}</div>
            <div>期間: {Object.keys(groupedByDate).length}日</div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto">
          {Object.entries(groupedByDate).map(([date, items]) => (
            <div key={date} className="mb-8">
              <div
                className="flex items-center gap-3 mb-4 cursor-pointer hover:bg-gray-50 p-2 rounded"
                onClick={() => toggleDate(date)}
              >
                <div className="w-32 text-right text-sm text-gray-600">
                  {new Date(date).toLocaleDateString('ja-JP', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </div>
                <div className="w-4 h-4 bg-blue-500 rounded-full" />
                <div className="flex-1 h-0.5 bg-gray-300" />
                <div className="flex gap-2">
                  {items.map((item, idx) => (
                    <span key={idx} className="text-lg">
                      {getTypeIcon(item.type)}
                    </span>
                  ))}
                </div>
                <span className="text-gray-500">
                  {expandedDates.has(date) ? '▼' : '▶'}
                </span>
              </div>

              {expandedDates.has(date) && (
                <div className="ml-36 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {items.map((item, idx) => (
                    <div key={idx} className="bg-white rounded-lg shadow-md overflow-hidden">
                      <div className="bg-gray-100 px-3 py-2 flex items-center justify-between">
                        <span className="text-sm font-medium flex items-center gap-2">
                          {getTypeIcon(item.type)} {getTypeLabel(item.type)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {item.image.type}
                        </span>
                      </div>
                      <ImageViewer
                        image={item.image}
                        className="h-48"
                        showAnnotations={false}
                        showMeasurements={false}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};