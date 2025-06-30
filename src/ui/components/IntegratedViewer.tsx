import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { ImageViewer } from './ImageViewer';
import {
  FacialPhoto,
  XRayImage,
  IntraoralPhoto,
  ModelPhoto,
  CephalometricAnalysis,
  ModelAnalysis,
  PhotoAnnotation
} from '../types';

interface IntegratedViewerProps {
  facialPhotos: FacialPhoto[];
  xrayImages: XRayImage[];
  intraoralPhotos: IntraoralPhoto[];
  modelPhotos: ModelPhoto[];
  cephalometricAnalyses: CephalometricAnalysis[];
  modelAnalyses: ModelAnalysis[];
  onDataUpdate?: (type: string, id: string, data: any) => void;
}

type ViewLayout = 'single' | 'side-by-side' | 'quad' | 'grid' | 'timeline-compare';
type DataType = 'facial' | 'xray' | 'intraoral' | 'model' | 'cephalo' | 'model-analysis';

interface ViewerState {
  layout: ViewLayout;
  activeViewports: ViewportState[];
  syncSettings: {
    zoom: boolean;
    pan: boolean;
    brightness: boolean;
    annotations: boolean;
  };
  comparisonMode: 'overlay' | 'side-by-side' | 'slider';
  globalZoom: number;
  globalPan: { x: number; y: number };
  globalBrightness: number;
  globalContrast: number;
}

interface ViewportState {
  id: string;
  dataType: DataType;
  dataId: string | null;
  isActive: boolean;
  localZoom?: number;
  localPan?: { x: number; y: number };
  localBrightness?: number;
  localContrast?: number;
}

export const IntegratedViewer: React.FC<IntegratedViewerProps> = ({
  facialPhotos,
  xrayImages,
  intraoralPhotos,
  modelPhotos,
  cephalometricAnalyses,
  modelAnalyses,
  onDataUpdate
}) => {
  const [viewerState, setViewerState] = useState<ViewerState>({
    layout: 'side-by-side',
    activeViewports: [
      { id: 'vp1', dataType: 'facial', dataId: null, isActive: true },
      { id: 'vp2', dataType: 'xray', dataId: null, isActive: true },
      { id: 'vp3', dataType: 'intraoral', dataId: null, isActive: false },
      { id: 'vp4', dataType: 'model', dataId: null, isActive: false }
    ],
    syncSettings: {
      zoom: true,
      pan: true,
      brightness: true,
      annotations: false
    },
    comparisonMode: 'side-by-side',
    globalZoom: 1,
    globalPan: { x: 0, y: 0 },
    globalBrightness: 100,
    globalContrast: 100
  });

  const [selectedDataItems, setSelectedDataItems] = useState<Map<string, string>>(new Map());
  const [annotationMode, setAnnotationMode] = useState<'view' | 'edit' | 'measure'>('view');
  const [measurementPoints, setMeasurementPoints] = useState<Array<{ x: number; y: number }>>([]);

  // データマッピング
  const allImageData = useMemo(() => {
    const dataMap = new Map<string, any>();
    
    facialPhotos.forEach(photo => dataMap.set(`facial-${photo.id}`, photo));
    xrayImages.forEach(image => dataMap.set(`xray-${image.id}`, image));
    intraoralPhotos.forEach(photo => dataMap.set(`intraoral-${photo.id}`, photo));
    modelPhotos.forEach(photo => dataMap.set(`model-${photo.id}`, photo));
    cephalometricAnalyses.forEach(analysis => dataMap.set(`cephalo-${analysis.id}`, analysis));
    modelAnalyses.forEach(analysis => dataMap.set(`model-analysis-${analysis.id}`, analysis));
    
    return dataMap;
  }, [facialPhotos, xrayImages, intraoralPhotos, modelPhotos, cephalometricAnalyses, modelAnalyses]);

  // レイアウト変更
  const changeLayout = useCallback((layout: ViewLayout) => {
    setViewerState(prev => {
      const newViewports = [...prev.activeViewports];
      
      switch (layout) {
        case 'single':
          newViewports.forEach((vp, idx) => vp.isActive = idx === 0);
          break;
        case 'side-by-side':
          newViewports.forEach((vp, idx) => vp.isActive = idx < 2);
          break;
        case 'quad':
          newViewports.forEach(vp => vp.isActive = true);
          break;
        case 'grid':
          newViewports.forEach(vp => vp.isActive = true);
          break;
        case 'timeline-compare':
          newViewports.forEach((vp, idx) => vp.isActive = idx < 2);
          break;
      }
      
      return { ...prev, layout, activeViewports: newViewports };
    });
  }, []);

  // 同期設定の切り替え
  const toggleSync = useCallback((syncType: keyof ViewerState['syncSettings']) => {
    setViewerState(prev => ({
      ...prev,
      syncSettings: {
        ...prev.syncSettings,
        [syncType]: !prev.syncSettings[syncType]
      }
    }));
  }, []);

  // グローバル操作のハンドラー
  const handleGlobalZoom = useCallback((zoom: number) => {
    if (viewerState.syncSettings.zoom) {
      setViewerState(prev => ({ ...prev, globalZoom: zoom }));
    }
  }, [viewerState.syncSettings.zoom]);

  const handleGlobalPan = useCallback((pan: { x: number; y: number }) => {
    if (viewerState.syncSettings.pan) {
      setViewerState(prev => ({ ...prev, globalPan: pan }));
    }
  }, [viewerState.syncSettings.pan]);

  // ビューポートへのデータ割り当て
  const assignDataToViewport = useCallback((viewportId: string, dataType: DataType, dataId: string) => {
    setViewerState(prev => ({
      ...prev,
      activeViewports: prev.activeViewports.map(vp =>
        vp.id === viewportId ? { ...vp, dataType, dataId } : vp
      )
    }));
    setSelectedDataItems(prev => new Map(prev).set(viewportId, `${dataType}-${dataId}`));
  }, []);

  // 測定機能
  const handleMeasurement = useCallback((viewport: ViewportState, point: { x: number; y: number }) => {
    if (annotationMode === 'measure') {
      setMeasurementPoints(prev => {
        const newPoints = [...prev, point];
        if (newPoints.length === 2) {
          const distance = Math.sqrt(
            Math.pow(newPoints[1].x - newPoints[0].x, 2) +
            Math.pow(newPoints[1].y - newPoints[0].y, 2)
          );
          console.log(`測定距離: ${distance.toFixed(2)}px`);
          return [];
        }
        return newPoints;
      });
    }
  }, [annotationMode]);

  // アノテーション追加
  const handleAnnotationAdd = useCallback((viewportId: string, annotation: PhotoAnnotation) => {
    const viewport = viewerState.activeViewports.find(vp => vp.id === viewportId);
    if (viewport && viewport.dataId && onDataUpdate) {
      onDataUpdate(viewport.dataType, viewport.dataId, { annotation });
    }
  }, [viewerState.activeViewports, onDataUpdate]);

  // レイアウトのレンダリング
  const renderViewportGrid = () => {
    const activeViewports = viewerState.activeViewports.filter(vp => vp.isActive);
    
    let gridClassName = '';
    switch (viewerState.layout) {
      case 'single':
        gridClassName = 'grid-cols-1';
        break;
      case 'side-by-side':
        gridClassName = 'grid-cols-2';
        break;
      case 'quad':
        gridClassName = 'grid-cols-2 grid-rows-2';
        break;
      case 'grid':
        gridClassName = 'grid-cols-3';
        break;
      default:
        gridClassName = 'grid-cols-2';
    }

    return (
      <div className={`grid ${gridClassName} gap-2 h-full p-2`}>
        {activeViewports.map(viewport => {
          const dataKey = viewport.dataId ? `${viewport.dataType}-${viewport.dataId}` : null;
          const imageData = dataKey ? allImageData.get(dataKey) : null;
          
          return (
            <div key={viewport.id} className="relative bg-gray-900 rounded-lg overflow-hidden">
              {imageData && 'url' in imageData ? (
                <ImageViewer
                  image={imageData}
                  showAnnotations={true}
                  showMeasurements={annotationMode === 'measure'}
                  onAnnotationAdd={(annotation) => handleAnnotationAdd(viewport.id, annotation)}
                  onImageClick={(coords) => handleMeasurement(viewport, coords)}
                  className="h-full"
                />
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-400">
                  <div className="mb-4">
                    <svg className="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p className="text-sm mb-4">画像を選択してください</p>
                  <DataSelector
                    dataType={viewport.dataType}
                    onSelect={(dataId) => assignDataToViewport(viewport.id, viewport.dataType, dataId)}
                    availableData={getAvailableDataForType(viewport.dataType)}
                  />
                </div>
              )}
              
              {/* ビューポートラベル */}
              <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                {getDataTypeLabel(viewport.dataType)}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // データタイプごとの利用可能データ取得
  const getAvailableDataForType = (dataType: DataType) => {
    switch (dataType) {
      case 'facial': return facialPhotos;
      case 'xray': return xrayImages;
      case 'intraoral': return intraoralPhotos;
      case 'model': return modelPhotos;
      case 'cephalo': return cephalometricAnalyses;
      case 'model-analysis': return modelAnalyses;
      default: return [];
    }
  };

  // データタイプのラベル取得
  const getDataTypeLabel = (dataType: DataType) => {
    switch (dataType) {
      case 'facial': return '顔面写真';
      case 'xray': return 'レントゲン';
      case 'intraoral': return '口腔内写真';
      case 'model': return '模型写真';
      case 'cephalo': return 'セファロ分析';
      case 'model-analysis': return '模型分析';
      default: return '';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-100">
      {/* ツールバー */}
      <div className="bg-white border-b p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* レイアウト選択 */}
            <div className="flex gap-2">
              <button
                onClick={() => changeLayout('single')}
                className={`p-2 rounded ${viewerState.layout === 'single' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                title="シングルビュー"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 3h14v14H3V3z"/>
                </svg>
              </button>
              <button
                onClick={() => changeLayout('side-by-side')}
                className={`p-2 rounded ${viewerState.layout === 'side-by-side' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                title="サイドバイサイド"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 3h6v14H3V3zm8 0h6v14h-6V3z"/>
                </svg>
              </button>
              <button
                onClick={() => changeLayout('quad')}
                className={`p-2 rounded ${viewerState.layout === 'quad' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                title="4分割"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 3h6v6H3V3zm8 0h6v6h-6V3zM3 11h6v6H3v-6zm8 0h6v6h-6v-6z"/>
                </svg>
              </button>
              <button
                onClick={() => changeLayout('grid')}
                className={`p-2 rounded ${viewerState.layout === 'grid' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                title="グリッド"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 3h4v4H3V3zm6 0h4v4H9V3zm6 0h4v4h-4V3zM3 9h4v4H3V9zm6 0h4v4H9V9zm6 0h4v4h-4V9zM3 15h4v4H3v-4zm6 0h4v4H9v-4z"/>
                </svg>
              </button>
            </div>

            {/* 同期設定 */}
            <div className="flex items-center gap-3 border-l pl-4">
              <span className="text-sm font-medium">同期:</span>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={viewerState.syncSettings.zoom}
                  onChange={() => toggleSync('zoom')}
                  className="w-4 h-4"
                />
                <span className="text-sm">ズーム</span>
              </label>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={viewerState.syncSettings.pan}
                  onChange={() => toggleSync('pan')}
                  className="w-4 h-4"
                />
                <span className="text-sm">パン</span>
              </label>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={viewerState.syncSettings.brightness}
                  onChange={() => toggleSync('brightness')}
                  className="w-4 h-4"
                />
                <span className="text-sm">明度</span>
              </label>
            </div>

            {/* アノテーションモード */}
            <div className="flex gap-2 border-l pl-4">
              <button
                onClick={() => setAnnotationMode('view')}
                className={`px-3 py-1 rounded text-sm ${annotationMode === 'view' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
              >
                表示
              </button>
              <button
                onClick={() => setAnnotationMode('edit')}
                className={`px-3 py-1 rounded text-sm ${annotationMode === 'edit' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
              >
                編集
              </button>
              <button
                onClick={() => setAnnotationMode('measure')}
                className={`px-3 py-1 rounded text-sm ${annotationMode === 'measure' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
              >
                測定
              </button>
            </div>
          </div>

          {/* グローバルコントロール */}
          {viewerState.syncSettings.zoom && (
            <div className="flex items-center gap-2">
              <span className="text-sm">全体ズーム:</span>
              <input
                type="range"
                min="50"
                max="500"
                value={viewerState.globalZoom * 100}
                onChange={(e) => handleGlobalZoom(parseInt(e.target.value) / 100)}
                className="w-32"
              />
              <span className="text-sm w-12">{Math.round(viewerState.globalZoom * 100)}%</span>
            </div>
          )}
        </div>
      </div>

      {/* メインビューエリア */}
      <div className="flex-1 overflow-hidden">
        {renderViewportGrid()}
      </div>

      {/* ステータスバー */}
      <div className="bg-white border-t px-4 py-2">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex gap-4">
            <span>レイアウト: {viewerState.layout}</span>
            <span>アクティブビューポート: {viewerState.activeViewports.filter(vp => vp.isActive).length}</span>
            {annotationMode === 'measure' && measurementPoints.length > 0 && (
              <span>測定中... ({measurementPoints.length}/2点)</span>
            )}
          </div>
          <div className="flex gap-4">
            <span>総画像数: {facialPhotos.length + xrayImages.length + intraoralPhotos.length + modelPhotos.length}</span>
            <span>分析数: {cephalometricAnalyses.length + modelAnalyses.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// データセレクターコンポーネント
interface DataSelectorProps {
  dataType: DataType;
  onSelect: (dataId: string) => void;
  availableData: any[];
}

const DataSelector: React.FC<DataSelectorProps> = ({ dataType, onSelect, availableData }) => {
  return (
    <select
      onChange={(e) => onSelect(e.target.value)}
      className="px-3 py-1 bg-gray-700 text-white rounded text-sm"
      defaultValue=""
    >
      <option value="" disabled>選択...</option>
      {availableData.map((item: any) => (
        <option key={item.id} value={item.id}>
          {item.type || item.analysisType || item.id} - {new Date(item.captureDate || item.analysisDate).toLocaleDateString()}
        </option>
      ))}
    </select>
  );
};