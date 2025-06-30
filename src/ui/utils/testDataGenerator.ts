import {
  PatientData,
  FacialPhoto,
  XRayImage,
  IntraoralPhoto,
  ModelPhoto,
  CephalometricAnalysis,
  ModelAnalysis,
  TreatmentPlan,
  TreatmentProcedure,
  DetailedTreatmentPlan,
  ToothMovement,
  WireSequence,
  ElasticConfiguration
} from '../types';

// テスト用データ生成関数
export const generateTestPatient = (id: string = 'TEST001'): PatientData => ({
  id,
  name: `テスト患者 ${id}`,
  age: Math.floor(Math.random() * 30) + 10,
  gender: Math.random() > 0.5 ? 'male' : 'female',
  registrationDate: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
  treatmentStatus: ['planning', 'active', 'completed'][Math.floor(Math.random() * 3)] as any
});

export const generateFacialPhotos = (count: number = 3): FacialPhoto[] => {
  const types: Array<FacialPhoto['type']> = ['frontal', 'profile', 'smile'];
  return Array.from({ length: count }, (_, i) => ({
    id: `F${String(i + 1).padStart(3, '0')}`,
    type: types[i % types.length],
    url: `/api/test/facial/${i + 1}.jpg`,
    captureDate: new Date(Date.now() - i * 7 * 24 * 60 * 60 * 1000),
    annotations: []
  }));
};

export const generateXRayImages = (count: number = 2): XRayImage[] => {
  const types: Array<XRayImage['type']> = ['panoramic', 'lateral', 'frontal'];
  return Array.from({ length: count }, (_, i) => ({
    id: `X${String(i + 1).padStart(3, '0')}`,
    type: types[i % types.length],
    url: `/api/test/xray/${i + 1}.jpg`,
    captureDate: new Date(Date.now() - i * 14 * 24 * 60 * 60 * 1000),
    measurements: []
  }));
};

export const generateIntraoralPhotos = (count: number = 5): IntraoralPhoto[] => {
  const types: Array<IntraoralPhoto['type']> = [
    'frontal', 'lateral_right', 'lateral_left', 'upper_occlusal', 'lower_occlusal'
  ];
  return Array.from({ length: count }, (_, i) => ({
    id: `I${String(i + 1).padStart(3, '0')}`,
    type: types[i % types.length],
    url: `/api/test/intraoral/${i + 1}.jpg`,
    captureDate: new Date(Date.now() - i * 3 * 24 * 60 * 60 * 1000),
    annotations: []
  }));
};

export const generateModelPhotos = (count: number = 4): ModelPhoto[] => {
  const types: Array<ModelPhoto['type']> = ['upper', 'lower', 'frontal', 'lateral'];
  return Array.from({ length: count }, (_, i) => ({
    id: `M${String(i + 1).padStart(3, '0')}`,
    type: types[i % types.length],
    url: `/api/test/model/${i + 1}.jpg`,
    captureDate: new Date(Date.now() - i * 10 * 24 * 60 * 60 * 1000),
    modelType: i % 2 === 0 ? 'physical' : 'digital'
  }));
};

export const generateCephalometricAnalysis = (): CephalometricAnalysis => {
  const analysisTypes = ['downs', 'steiner', 'tweed', 'ricketts'];
  const measurements = {
    'SNA': {
      value: 80 + Math.random() * 8,
      unit: '°',
      normalRange: { min: 80, max: 84 },
      deviation: (Math.random() - 0.5) * 4
    },
    'SNB': {
      value: 78 + Math.random() * 8,
      unit: '°',
      normalRange: { min: 78, max: 82 },
      deviation: (Math.random() - 0.5) * 4
    },
    'ANB': {
      value: 2 + Math.random() * 4,
      unit: '°',
      normalRange: { min: 2, max: 4 },
      deviation: (Math.random() - 0.5) * 3
    },
    'FMA': {
      value: 25 + Math.random() * 10,
      unit: '°',
      normalRange: { min: 22, max: 28 },
      deviation: (Math.random() - 0.5) * 5
    },
    'IMPA': {
      value: 90 + Math.random() * 20,
      unit: '°',
      normalRange: { min: 87, max: 95 },
      deviation: (Math.random() - 0.5) * 6
    }
  };

  return {
    id: `CA${Math.random().toString(36).substr(2, 9)}`,
    analysisType: analysisTypes[Math.floor(Math.random() * analysisTypes.length)] as any,
    measurements,
    analysisDate: new Date()
  };
};

export const generateModelAnalysis = (): ModelAnalysis => ({
  id: `MA${Math.random().toString(36).substr(2, 9)}`,
  archLength: {
    upper: 65 + Math.random() * 15,
    lower: 60 + Math.random() * 15
  },
  spaceAnalysis: {
    upper: {
      availableSpace: 70 + Math.random() * 10,
      requiredSpace: 72 + Math.random() * 8,
      discrepancy: -5 + Math.random() * 10,
      crowding: Math.random() * 8
    },
    lower: {
      availableSpace: 65 + Math.random() * 10,
      requiredSpace: 68 + Math.random() * 8,
      discrepancy: -4 + Math.random() * 8,
      crowding: Math.random() * 6
    }
  },
  occlusalRelationship: {
    molarRelationship: ['class_i', 'class_ii', 'class_iii'][Math.floor(Math.random() * 3)] as any,
    overjet: 2 + Math.random() * 6,
    overbite: 2 + Math.random() * 5,
    crossbite: Math.random() > 0.7,
    midlineDeviation: Math.random() * 3
  },
  analysisDate: new Date()
});

export const generateDetailedTreatmentPlan = (patientId: string): DetailedTreatmentPlan => {
  const procedures: TreatmentProcedure[] = [
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
    },
    {
      id: 'PR003',
      type: 'alignment',
      description: 'スペースクロージング',
      sequence: 3,
      duration: 8,
      completed: false
    },
    {
      id: 'PR004',
      type: 'retention',
      description: '保定装置の装着',
      sequence: 4,
      duration: 12,
      completed: false
    }
  ];

  // 歯牙移動データ生成
  const toothMovements: ToothMovement[] = [
    // 上顎前歯の配列
    { toothNumber: 11, initialPosition: { x: 0, y: 0, z: 0, rotation: 0 }, targetPosition: { x: -2, y: 1, z: 0, rotation: 5 }, movementVector: { x: -2, y: 1, z: 0 }, duration: 8, force: 150 },
    { toothNumber: 12, initialPosition: { x: 0, y: 0, z: 0, rotation: 0 }, targetPosition: { x: -1.5, y: 0.5, z: 0, rotation: 3 }, movementVector: { x: -1.5, y: 0.5, z: 0 }, duration: 6, force: 120 },
    { toothNumber: 21, initialPosition: { x: 0, y: 0, z: 0, rotation: 0 }, targetPosition: { x: 2, y: 1, z: 0, rotation: -5 }, movementVector: { x: 2, y: 1, z: 0 }, duration: 8, force: 150 },
    { toothNumber: 22, initialPosition: { x: 0, y: 0, z: 0, rotation: 0 }, targetPosition: { x: 1.5, y: 0.5, z: 0, rotation: -3 }, movementVector: { x: 1.5, y: 0.5, z: 0 }, duration: 6, force: 120 },
    // 下顎前歯の配列
    { toothNumber: 31, initialPosition: { x: 0, y: 0, z: 0, rotation: 0 }, targetPosition: { x: -1, y: -0.5, z: 0, rotation: 2 }, movementVector: { x: -1, y: -0.5, z: 0 }, duration: 10, force: 100 },
    { toothNumber: 32, initialPosition: { x: 0, y: 0, z: 0, rotation: 0 }, targetPosition: { x: -0.8, y: -0.3, z: 0, rotation: 1 }, movementVector: { x: -0.8, y: -0.3, z: 0 }, duration: 8, force: 80 },
    { toothNumber: 41, initialPosition: { x: 0, y: 0, z: 0, rotation: 0 }, targetPosition: { x: 1, y: -0.5, z: 0, rotation: -2 }, movementVector: { x: 1, y: -0.5, z: 0 }, duration: 10, force: 100 },
    { toothNumber: 42, initialPosition: { x: 0, y: 0, z: 0, rotation: 0 }, targetPosition: { x: 0.8, y: -0.3, z: 0, rotation: -1 }, movementVector: { x: 0.8, y: -0.3, z: 0 }, duration: 8, force: 80 }
  ];

  // ワイヤーシーケンス生成
  const wireSequences: WireSequence[] = [
    { id: 'W001', stage: 1, wireType: 'NiTi', dimension: '0.014', shape: 'round', startMonth: 0, endMonth: 3, notes: '初期配列用' },
    { id: 'W002', stage: 2, wireType: 'NiTi', dimension: '0.016', shape: 'round', startMonth: 3, endMonth: 6, notes: 'レベリング' },
    { id: 'W003', stage: 3, wireType: 'NiTi', dimension: '0.016x0.022', shape: 'rectangular', startMonth: 6, endMonth: 12, notes: 'トルクコントロール' },
    { id: 'W004', stage: 4, wireType: 'SS', dimension: '0.019x0.025', shape: 'rectangular', startMonth: 12, endMonth: 18, notes: 'フィニッシング' },
    { id: 'W005', stage: 5, wireType: 'TMA', dimension: '0.017x0.025', shape: 'rectangular', startMonth: 18, endMonth: 24, notes: '最終調整' }
  ];

  // 顎間ゴム設定生成
  const elasticConfigurations: ElasticConfiguration[] = [
    {
      id: 'E001',
      type: 'class_ii',
      attachmentPoints: { upper: [13, 14], lower: [34, 35] },
      force: 4.5,
      wearTime: 'full_time',
      startMonth: 6,
      endMonth: 16
    },
    {
      id: 'E002',
      type: 'class_ii',
      attachmentPoints: { upper: [23, 24], lower: [44, 45] },
      force: 4.5,
      wearTime: 'full_time',
      startMonth: 6,
      endMonth: 16
    },
    {
      id: 'E003',
      type: 'midline',
      attachmentPoints: { upper: [11], lower: [31] },
      force: 3.5,
      wearTime: 'night_only',
      startMonth: 18,
      endMonth: 24
    }
  ];

  return {
    id: `TP${Math.random().toString(36).substr(2, 9)}`,
    patientId,
    createdDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    modifiedDate: new Date(),
    status: 'approved',
    orthodontist: 'Dr. テスト医師',
    objectives: [
      '上下顎前歯の叢生改善',
      'II級咬合関係の改善',
      '適切なオーバージェット・オーバーバイトの確立',
      '審美的なスマイルラインの獲得'
    ],
    procedures,
    estimatedDuration: procedures.reduce((sum, p) => sum + p.duration, 0),
    notes: 'テスト用の詳細治療計画です。統合テストのために生成されました。',
    toothMovements,
    wireSequences,
    elasticConfigurations
  };
};

export const generateTreatmentPlan = (patientId: string): TreatmentPlan => {
  const procedures: TreatmentProcedure[] = [
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
    },
    {
      id: 'PR003',
      type: 'alignment',
      description: 'スペースクロージング',
      sequence: 3,
      duration: 8,
      completed: false
    },
    {
      id: 'PR004',
      type: 'retention',
      description: '保定装置の装着',
      sequence: 4,
      duration: 12,
      completed: false
    }
  ];

  return {
    id: `TP${Math.random().toString(36).substr(2, 9)}`,
    patientId,
    createdDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    modifiedDate: new Date(),
    status: 'approved',
    orthodontist: 'Dr. テスト医師',
    objectives: [
      '上下顎前歯の叢生改善',
      '適切な咬合関係の確立',
      '審美的なスマイルラインの獲得'
    ],
    procedures,
    estimatedDuration: procedures.reduce((sum, p) => sum + p.duration, 0),
    notes: 'テスト用の治療計画です。統合テストのために生成されました。'
  };
};

// 完全なテストデータセットを生成
export const generateCompleteTestDataset = () => {
  const patient = generateTestPatient();
  
  return {
    patient,
    facialPhotos: generateFacialPhotos(6),
    xrayImages: generateXRayImages(4),
    intraoralPhotos: generateIntraoralPhotos(10),
    modelPhotos: generateModelPhotos(8),
    cephalometricAnalyses: [
      generateCephalometricAnalysis(),
      generateCephalometricAnalysis(),
      generateCephalometricAnalysis()
    ],
    modelAnalyses: [
      generateModelAnalysis(),
      generateModelAnalysis()
    ],
    treatmentPlan: generateDetailedTreatmentPlan(patient.id)
  };
};

// エラーケーステスト用のデータ生成
export const generateErrorTestData = () => {
  return {
    emptyDataset: {
      patient: generateTestPatient(),
      facialPhotos: [],
      xrayImages: [],
      intraoralPhotos: [],
      modelPhotos: [],
      cephalometricAnalyses: [],
      modelAnalyses: [],
      treatmentPlan: undefined
    },
    invalidImageUrls: {
      facialPhotos: generateFacialPhotos(2).map(photo => ({
        ...photo,
        url: 'invalid://url'
      }))
    },
    missingAnalysisData: {
      cephalometricAnalyses: [{
        id: 'CA_ERROR',
        analysisType: 'downs' as const,
        measurements: {},
        analysisDate: new Date()
      }]
    }
  };
};

// パフォーマンステスト用の大量データ生成
export const generateLargeTestDataset = () => {
  return {
    patient: generateTestPatient(),
    facialPhotos: generateFacialPhotos(50),
    xrayImages: generateXRayImages(30),
    intraoralPhotos: generateIntraoralPhotos(100),
    modelPhotos: generateModelPhotos(40),
    cephalometricAnalyses: Array.from({ length: 20 }, () => generateCephalometricAnalysis()),
    modelAnalyses: Array.from({ length: 15 }, () => generateModelAnalysis()),
    treatmentPlan: generateTreatmentPlan('TEST001')
  };
};