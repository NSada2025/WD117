import React, { useState, useCallback } from 'react';
import { ImageViewer } from './ImageViewer';
import { AnalysisPanel } from './AnalysisPanel';
import { TreatmentPlanPanel } from './TreatmentPlanPanel';
import { TimelineView } from './TimelineView';
import {
  PatientData,
  FacialPhoto,
  XRayImage,
  IntraoralPhoto,
  ModelPhoto,
  CephalometricAnalysis,
  ModelAnalysis,
  TreatmentPlan,
  ViewMode
} from '../types';

interface OrthodonticDashboardProps {
  patient: PatientData;
  facialPhotos: FacialPhoto[];
  xrayImages: XRayImage[];
  intraoralPhotos: IntraoralPhoto[];
  modelPhotos: ModelPhoto[];
  cephalometricAnalyses: CephalometricAnalysis[];
  modelAnalyses: ModelAnalysis[];
  treatmentPlan?: TreatmentPlan;
  onTreatmentPlanUpdate?: (plan: TreatmentPlan) => void;
}

export const OrthodonticDashboard: React.FC<OrthodonticDashboardProps> = ({
  patient,
  facialPhotos,
  xrayImages,
  intraoralPhotos,
  modelPhotos,
  cephalometricAnalyses,
  modelAnalyses,
  treatmentPlan,
  onTreatmentPlanUpdate
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>({
    type: 'grid',
    activeImages: [],
    syncMode: false,
    annotations: true,
    measurements: true
  });
  const [selectedTab, setSelectedTab] = useState<'images' | 'analysis' | 'plan' | 'timeline'>('images');
  const [selectedImageType, setSelectedImageType] = useState<'facial' | 'xray' | 'intraoral' | 'model'>('facial');
  const [selectedImages, setSelectedImages] = useState<string[]>([]);

  const handleImageSelect = useCallback((imageId: string) => {
    setSelectedImages(prev => {
      if (prev.includes(imageId)) {
        return prev.filter(id => id !== imageId);
      }
      if (viewMode.type === 'comparison' && prev.length >= 2) {
        return [prev[1], imageId];
      }
      return [...prev, imageId];
    });
  }, [viewMode.type]);

  const renderImageGrid = () => {
    let images: any[] = [];
    switch (selectedImageType) {
      case 'facial':
        images = facialPhotos;
        break;
      case 'xray':
        images = xrayImages;
        break;
      case 'intraoral':
        images = intraoralPhotos;
        break;
      case 'model':
        images = modelPhotos;
        break;
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4">
        {images.map(image => (
          <div
            key={image.id}
            className={`relative cursor-pointer border-2 rounded-lg overflow-hidden ${
              selectedImages.includes(image.id) ? 'border-blue-500' : 'border-gray-300'
            }`}
            onClick={() => handleImageSelect(image.id)}
          >
            <ImageViewer
              image={image}
              showAnnotations={viewMode.annotations}
              showMeasurements={viewMode.measurements}
              className="h-64"
            />
            <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
              {image.type}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderComparisonView = () => {
    const allImages = [...facialPhotos, ...xrayImages, ...intraoralPhotos, ...modelPhotos];
    const imagesToCompare = allImages.filter(img => selectedImages.includes(img.id));

    return (
      <div className="grid grid-cols-2 gap-2 h-full p-4">
        {imagesToCompare.map(image => (
          <div key={image.id} className="relative h-full">
            <ImageViewer
              image={image}
              showAnnotations={viewMode.annotations}
              showMeasurements={viewMode.measurements}
              className="h-full"
            />
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-md p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              矯正治療計画立案・評価システム
            </h1>
            <p className="text-gray-600">
              患者: {patient.name} | 年齢: {patient.age}歳 | ID: {patient.id}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode(prev => ({ ...prev, type: 'grid' }))}
              className={`px-4 py-2 rounded ${
                viewMode.type === 'grid' ? 'bg-blue-500 text-white' : 'bg-gray-200'
              }`}
            >
              グリッド表示
            </button>
            <button
              onClick={() => setViewMode(prev => ({ ...prev, type: 'comparison' }))}
              className={`px-4 py-2 rounded ${
                viewMode.type === 'comparison' ? 'bg-blue-500 text-white' : 'bg-gray-200'
              }`}
            >
              比較表示
            </button>
            <button
              onClick={() => setViewMode(prev => ({ ...prev, type: 'timeline' }))}
              className={`px-4 py-2 rounded ${
                viewMode.type === 'timeline' ? 'bg-blue-500 text-white' : 'bg-gray-200'
              }`}
            >
              タイムライン
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <div className="flex">
          <button
            onClick={() => setSelectedTab('images')}
            className={`px-6 py-3 font-medium ${
              selectedTab === 'images'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            画像
          </button>
          <button
            onClick={() => setSelectedTab('analysis')}
            className={`px-6 py-3 font-medium ${
              selectedTab === 'analysis'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            分析結果
          </button>
          <button
            onClick={() => setSelectedTab('plan')}
            className={`px-6 py-3 font-medium ${
              selectedTab === 'plan'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            治療計画
          </button>
          <button
            onClick={() => setSelectedTab('timeline')}
            className={`px-6 py-3 font-medium ${
              selectedTab === 'timeline'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            経過観察
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {selectedTab === 'images' && (
          <div className="h-full flex">
            {/* Image Type Selector */}
            <div className="w-48 bg-gray-50 p-4 border-r">
              <h3 className="font-semibold mb-3">画像タイプ</h3>
              <div className="space-y-2">
                <button
                  onClick={() => setSelectedImageType('facial')}
                  className={`w-full text-left px-3 py-2 rounded ${
                    selectedImageType === 'facial' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
                  }`}
                >
                  顔面写真 ({facialPhotos.length})
                </button>
                <button
                  onClick={() => setSelectedImageType('xray')}
                  className={`w-full text-left px-3 py-2 rounded ${
                    selectedImageType === 'xray' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
                  }`}
                >
                  レントゲン ({xrayImages.length})
                </button>
                <button
                  onClick={() => setSelectedImageType('intraoral')}
                  className={`w-full text-left px-3 py-2 rounded ${
                    selectedImageType === 'intraoral' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
                  }`}
                >
                  口腔内写真 ({intraoralPhotos.length})
                </button>
                <button
                  onClick={() => setSelectedImageType('model')}
                  className={`w-full text-left px-3 py-2 rounded ${
                    selectedImageType === 'model' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
                  }`}
                >
                  模型写真 ({modelPhotos.length})
                </button>
              </div>

              <div className="mt-6">
                <h3 className="font-semibold mb-3">表示設定</h3>
                <label className="flex items-center gap-2 mb-2">
                  <input
                    type="checkbox"
                    checked={viewMode.annotations}
                    onChange={(e) => setViewMode(prev => ({ ...prev, annotations: e.target.checked }))}
                  />
                  <span className="text-sm">注釈を表示</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={viewMode.measurements}
                    onChange={(e) => setViewMode(prev => ({ ...prev, measurements: e.target.checked }))}
                  />
                  <span className="text-sm">計測値を表示</span>
                </label>
              </div>
            </div>

            {/* Image Display Area */}
            <div className="flex-1 overflow-auto">
              {viewMode.type === 'grid' && renderImageGrid()}
              {viewMode.type === 'comparison' && renderComparisonView()}
              {viewMode.type === 'timeline' && (
                <TimelineView
                  facialPhotos={facialPhotos}
                  xrayImages={xrayImages}
                  intraoralPhotos={intraoralPhotos}
                  modelPhotos={modelPhotos}
                />
              )}
            </div>
          </div>
        )}

        {selectedTab === 'analysis' && (
          <AnalysisPanel
            cephalometricAnalyses={cephalometricAnalyses}
            modelAnalyses={modelAnalyses}
          />
        )}

        {selectedTab === 'plan' && treatmentPlan && (
          <TreatmentPlanPanel
            treatmentPlan={treatmentPlan}
            onUpdate={onTreatmentPlanUpdate}
          />
        )}

        {selectedTab === 'timeline' && (
          <TimelineView
            facialPhotos={facialPhotos}
            xrayImages={xrayImages}
            intraoralPhotos={intraoralPhotos}
            modelPhotos={modelPhotos}
          />
        )}
      </div>
    </div>
  );
};