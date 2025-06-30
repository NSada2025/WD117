import React, { useState } from 'react';
import { CephalometricAnalysis, ModelAnalysis } from '../types';

interface AnalysisPanelProps {
  cephalometricAnalyses: CephalometricAnalysis[];
  modelAnalyses: ModelAnalysis[];
}

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  cephalometricAnalyses,
  modelAnalyses
}) => {
  const [selectedAnalysisType, setSelectedAnalysisType] = useState<'cephalometric' | 'model'>('cephalometric');
  const [selectedAnalysis, setSelectedAnalysis] = useState<CephalometricAnalysis | ModelAnalysis | null>(
    cephalometricAnalyses[0] || null
  );

  const renderCephalometricMeasurements = (analysis: CephalometricAnalysis) => {
    return Object.entries(analysis.measurements).map(([key, measurement]) => {
      const isOutOfRange = measurement.deviation && Math.abs(measurement.deviation) > 2;
      
      return (
        <div
          key={key}
          className={`p-3 rounded-lg ${
            isOutOfRange ? 'bg-red-50 border border-red-200' : 'bg-gray-50'
          }`}
        >
          <div className="flex justify-between items-center">
            <span className="font-medium text-gray-700">{key}</span>
            <div className="text-right">
              <span className={`text-lg font-semibold ${isOutOfRange ? 'text-red-600' : 'text-gray-900'}`}>
                {measurement.value} {measurement.unit}
              </span>
              {measurement.deviation && (
                <span className={`block text-sm ${isOutOfRange ? 'text-red-500' : 'text-gray-500'}`}>
                  偏差: {measurement.deviation > 0 ? '+' : ''}{measurement.deviation.toFixed(1)} SD
                </span>
              )}
            </div>
          </div>
          <div className="mt-2">
            <div className="text-xs text-gray-500">
              正常範囲: {measurement.normalRange.min} - {measurement.normalRange.max} {measurement.unit}
            </div>
            <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${isOutOfRange ? 'bg-red-500' : 'bg-green-500'}`}
                style={{
                  width: `${Math.max(0, Math.min(100, 
                    ((measurement.value - measurement.normalRange.min) / 
                    (measurement.normalRange.max - measurement.normalRange.min)) * 100
                  ))}%`
                }}
              />
            </div>
          </div>
        </div>
      );
    });
  };

  const renderModelAnalysis = (analysis: ModelAnalysis) => {
    return (
      <div className="space-y-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-3">アーチ長分析</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-gray-600">上顎:</span>
              <span className="ml-2 font-semibold">{analysis.archLength.upper} mm</span>
            </div>
            <div>
              <span className="text-gray-600">下顎:</span>
              <span className="ml-2 font-semibold">{analysis.archLength.lower} mm</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-3">スペース分析</h3>
          {['upper', 'lower'].map(arch => {
            const data = analysis.spaceAnalysis[arch as 'upper' | 'lower'];
            const hasDiscrepancy = data.discrepancy < -2;
            
            return (
              <div key={arch} className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">
                  {arch === 'upper' ? '上顎' : '下顎'}
                </h4>
                <div className={`grid grid-cols-2 gap-3 p-3 rounded ${
                  hasDiscrepancy ? 'bg-yellow-50' : 'bg-gray-50'
                }`}>
                  <div>
                    <span className="text-sm text-gray-600">利用可能スペース:</span>
                    <span className="ml-2 font-medium">{data.availableSpace} mm</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">必要スペース:</span>
                    <span className="ml-2 font-medium">{data.requiredSpace} mm</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">不足量:</span>
                    <span className={`ml-2 font-medium ${
                      hasDiscrepancy ? 'text-orange-600' : 'text-green-600'
                    }`}>
                      {data.discrepancy} mm
                    </span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">叢生量:</span>
                    <span className="ml-2 font-medium">{data.crowding} mm</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-3">咬合関係</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">臼歯関係:</span>
              <span className="font-medium">
                {analysis.occlusalRelationship.molarRelationship.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">オーバージェット:</span>
              <span className="font-medium">{analysis.occlusalRelationship.overjet} mm</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">オーバーバイト:</span>
              <span className="font-medium">{analysis.occlusalRelationship.overbite} mm</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">交叉咬合:</span>
              <span className="font-medium">
                {analysis.occlusalRelationship.crossbite ? 'あり' : 'なし'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">正中偏位:</span>
              <span className="font-medium">{analysis.occlusalRelationship.midlineDeviation} mm</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex">
      {/* Analysis List */}
      <div className="w-64 bg-gray-50 p-4 border-r overflow-y-auto">
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">セファロ分析</h3>
            {cephalometricAnalyses.map(analysis => (
              <button
                key={analysis.id}
                onClick={() => {
                  setSelectedAnalysisType('cephalometric');
                  setSelectedAnalysis(analysis);
                }}
                className={`w-full text-left p-2 rounded mb-1 ${
                  selectedAnalysis?.id === analysis.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="font-medium">{analysis.analysisType.toUpperCase()}</div>
                <div className="text-sm text-gray-500">
                  {new Date(analysis.analysisDate).toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>

          <div>
            <h3 className="font-semibold mb-2">模型分析</h3>
            {modelAnalyses.map(analysis => (
              <button
                key={analysis.id}
                onClick={() => {
                  setSelectedAnalysisType('model');
                  setSelectedAnalysis(analysis);
                }}
                className={`w-full text-left p-2 rounded mb-1 ${
                  selectedAnalysis?.id === analysis.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="font-medium">模型分析</div>
                <div className="text-sm text-gray-500">
                  {new Date(analysis.analysisDate).toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Analysis Details */}
      <div className="flex-1 p-6 overflow-y-auto bg-gray-100">
        {selectedAnalysis && (
          <div>
            <h2 className="text-2xl font-bold mb-4">
              {selectedAnalysisType === 'cephalometric'
                ? `セファロ分析 - ${(selectedAnalysis as CephalometricAnalysis).analysisType.toUpperCase()}`
                : '模型分析'}
            </h2>
            <div className="text-gray-600 mb-6">
              分析日: {new Date(selectedAnalysis.analysisDate).toLocaleDateString()}
            </div>

            {selectedAnalysisType === 'cephalometric' && 'measurements' in selectedAnalysis && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {renderCephalometricMeasurements(selectedAnalysis as CephalometricAnalysis)}
              </div>
            )}

            {selectedAnalysisType === 'model' && 'archLength' in selectedAnalysis && (
              renderModelAnalysis(selectedAnalysis as ModelAnalysis)
            )}
          </div>
        )}
      </div>
    </div>
  );
};