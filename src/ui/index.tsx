import React from 'react';
import ReactDOM from 'react-dom/client';
import { OrthodonticDashboard } from './components/OrthodonticDashboard';
import { IntegratedViewer } from './components/IntegratedViewer';
import { IntegrationTestSuite } from './components/IntegrationTestSuite';
import {
  PatientData,
  FacialPhoto,
  XRayImage,
  IntraoralPhoto,
  ModelPhoto,
  CephalometricAnalysis,
  ModelAnalysis,
  TreatmentPlan
} from './types';

// サンプルデータ（実際のアプリケーションではAPIから取得）
const samplePatient: PatientData = {
  id: 'P001',
  name: '山田太郎',
  age: 16,
  gender: 'male',
  registrationDate: new Date('2024-01-15'),
  treatmentStatus: 'active'
};

const sampleFacialPhotos: FacialPhoto[] = [
  {
    id: 'F001',
    type: 'frontal',
    url: '/api/images/facial/f001.jpg',
    captureDate: new Date('2024-01-20'),
    annotations: []
  },
  {
    id: 'F002',
    type: 'profile',
    url: '/api/images/facial/f002.jpg',
    captureDate: new Date('2024-01-20'),
    annotations: []
  }
];

const sampleXRayImages: XRayImage[] = [
  {
    id: 'X001',
    type: 'lateral',
    url: '/api/images/xray/x001.jpg',
    captureDate: new Date('2024-01-22'),
    measurements: []
  }
];

const sampleIntraoralPhotos: IntraoralPhoto[] = [
  {
    id: 'I001',
    type: 'frontal',
    url: '/api/images/intraoral/i001.jpg',
    captureDate: new Date('2024-01-25'),
    annotations: []
  }
];

const sampleModelPhotos: ModelPhoto[] = [
  {
    id: 'M001',
    type: 'upper',
    url: '/api/images/model/m001.jpg',
    captureDate: new Date('2024-01-28'),
    modelType: 'digital'
  }
];

const sampleCephalometricAnalysis: CephalometricAnalysis = {
  id: 'CA001',
  analysisType: 'downs',
  measurements: {
    'SNA': {
      value: 82.5,
      unit: '°',
      normalRange: { min: 80, max: 84 },
      deviation: 0.5
    },
    'SNB': {
      value: 78.2,
      unit: '°',
      normalRange: { min: 78, max: 82 },
      deviation: -0.8
    },
    'ANB': {
      value: 4.3,
      unit: '°',
      normalRange: { min: 2, max: 4 },
      deviation: 1.2
    }
  },
  analysisDate: new Date('2024-01-30')
};

const sampleModelAnalysis: ModelAnalysis = {
  id: 'MA001',
  archLength: {
    upper: 72.5,
    lower: 68.3
  },
  spaceAnalysis: {
    upper: {
      availableSpace: 72.5,
      requiredSpace: 75.8,
      discrepancy: -3.3,
      crowding: 3.3
    },
    lower: {
      availableSpace: 68.3,
      requiredSpace: 71.2,
      discrepancy: -2.9,
      crowding: 2.9
    }
  },
  occlusalRelationship: {
    molarRelationship: 'class_ii',
    overjet: 5.2,
    overbite: 4.1,
    crossbite: false,
    midlineDeviation: 1.5
  },
  analysisDate: new Date('2024-02-01')
};

const sampleTreatmentPlan: TreatmentPlan = {
  id: 'TP001',
  patientId: 'P001',
  createdDate: new Date('2024-02-05'),
  modifiedDate: new Date('2024-02-05'),
  status: 'approved',
  orthodontist: 'Dr. 佐藤',
  objectives: [
    '上下顎前歯の叢生改善',
    'II級咬合関係の改善',
    '適切なオーバージェット・オーバーバイトの確立'
  ],
  procedures: [
    {
      id: 'PR001',
      type: 'extraction',
      description: '上顎第一小臼歯の抜歯',
      sequence: 1,
      duration: 1,
      completed: false
    },
    {
      id: 'PR002',
      type: 'alignment',
      description: 'レベリング・アライメント',
      sequence: 2,
      duration: 6,
      completed: false
    }
  ],
  estimatedDuration: 24,
  notes: '患者の協力度は良好。定期的な調整が必要。'
};

// アプリケーションのマウント
const App: React.FC = () => {
  const [viewMode, setViewMode] = React.useState<'dashboard' | 'integrated' | 'test'>('dashboard');

  const handleTreatmentPlanUpdate = (updatedPlan: TreatmentPlan) => {
    console.log('Treatment plan updated:', updatedPlan);
    // ここでAPIを呼び出して更新を保存
  };

  const handleDataUpdate = (type: string, id: string, data: any) => {
    console.log('Data updated:', { type, id, data });
    // ここでAPIを呼び出してデータを更新
  };

  return (
    <div className="h-screen flex flex-col">
      {/* ビューモード切り替えボタン */}
      <div className="bg-gray-800 text-white p-2 flex gap-2">
        <button
          onClick={() => setViewMode('dashboard')}
          className={`px-4 py-2 rounded ${
            viewMode === 'dashboard' ? 'bg-blue-600' : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          ダッシュボード
        </button>
        <button
          onClick={() => setViewMode('integrated')}
          className={`px-4 py-2 rounded ${
            viewMode === 'integrated' ? 'bg-blue-600' : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          統合ビューアー
        </button>
        <button
          onClick={() => setViewMode('test')}
          className={`px-4 py-2 rounded ${
            viewMode === 'test' ? 'bg-blue-600' : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          統合テスト
        </button>
      </div>

      {/* メインコンテンツ */}
      <div className="flex-1">
        {viewMode === 'dashboard' ? (
          <OrthodonticDashboard
            patient={samplePatient}
            facialPhotos={sampleFacialPhotos}
            xrayImages={sampleXRayImages}
            intraoralPhotos={sampleIntraoralPhotos}
            modelPhotos={sampleModelPhotos}
            cephalometricAnalyses={[sampleCephalometricAnalysis]}
            modelAnalyses={[sampleModelAnalysis]}
            treatmentPlan={sampleTreatmentPlan}
            onTreatmentPlanUpdate={handleTreatmentPlanUpdate}
          />
        ) : viewMode === 'integrated' ? (
          <IntegratedViewer
            facialPhotos={sampleFacialPhotos}
            xrayImages={sampleXRayImages}
            intraoralPhotos={sampleIntraoralPhotos}
            modelPhotos={sampleModelPhotos}
            cephalometricAnalyses={[sampleCephalometricAnalysis]}
            modelAnalyses={[sampleModelAnalysis]}
            onDataUpdate={handleDataUpdate}
          />
        ) : (
          <IntegrationTestSuite />
        )}
      </div>
    </div>
  );
};

// ルート要素を取得してアプリケーションをレンダリング
const rootElement = document.getElementById('root');
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  console.error('Root element not found');
}