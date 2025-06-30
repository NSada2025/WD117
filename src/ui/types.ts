// 矯正治療計画立案・評価システムの型定義

export interface PatientData {
  id: string;
  name: string;
  age: number;
  gender: 'male' | 'female';
  registrationDate: Date;
  treatmentStatus: 'planning' | 'active' | 'completed';
}

export interface FacialPhoto {
  id: string;
  type: 'frontal' | 'profile' | 'smile';
  url: string;
  captureDate: Date;
  annotations?: PhotoAnnotation[];
}

export interface XRayImage {
  id: string;
  type: 'panoramic' | 'lateral' | 'frontal';
  url: string;
  captureDate: Date;
  measurements?: XRayMeasurement[];
}

export interface IntraoralPhoto {
  id: string;
  type: 'frontal' | 'lateral_right' | 'lateral_left' | 'upper_occlusal' | 'lower_occlusal';
  url: string;
  captureDate: Date;
  annotations?: PhotoAnnotation[];
}

export interface ModelPhoto {
  id: string;
  type: 'upper' | 'lower' | 'frontal' | 'lateral';
  url: string;
  captureDate: Date;
  modelType: 'physical' | 'digital';
}

export interface CephalometricAnalysis {
  id: string;
  analysisType: 'downs' | 'steiner' | 'tweed' | 'ricketts';
  measurements: {
    [key: string]: {
      value: number;
      unit: string;
      normalRange: {
        min: number;
        max: number;
      };
      deviation?: number;
    };
  };
  analysisDate: Date;
}

export interface ModelAnalysis {
  id: string;
  archLength: {
    upper: number;
    lower: number;
  };
  spaceAnalysis: {
    upper: SpaceAnalysisData;
    lower: SpaceAnalysisData;
  };
  occlusalRelationship: OcclusalData;
  analysisDate: Date;
}

export interface SpaceAnalysisData {
  availableSpace: number;
  requiredSpace: number;
  discrepancy: number;
  crowding: number;
}

export interface OcclusalData {
  molarRelationship: 'class_i' | 'class_ii' | 'class_iii';
  overjet: number;
  overbite: number;
  crossbite: boolean;
  midlineDeviation: number;
}

export interface PhotoAnnotation {
  id: string;
  type: 'point' | 'line' | 'angle' | 'area';
  coordinates: number[];
  label: string;
  color?: string;
}

export interface XRayMeasurement {
  id: string;
  type: 'angle' | 'distance';
  points: number[][];
  value: number;
  unit: string;
  label: string;
}

export interface TreatmentPlan {
  id: string;
  patientId: string;
  createdDate: Date;
  modifiedDate: Date;
  status: 'draft' | 'approved' | 'in_progress' | 'completed';
  orthodontist: string;
  objectives: string[];
  procedures: TreatmentProcedure[];
  estimatedDuration: number; // months
  notes: string;
}

export interface TreatmentProcedure {
  id: string;
  type: 'extraction' | 'expansion' | 'alignment' | 'retention';
  description: string;
  sequence: number;
  duration: number; // months
  completed: boolean;
}

export interface ViewMode {
  type: 'single' | 'comparison' | 'timeline' | 'grid';
  activeImages: string[];
  syncMode: boolean;
  annotations: boolean;
  measurements: boolean;
}

// 詳細治療計画の型定義
export interface ToothMovement {
  toothNumber: number;
  initialPosition: { x: number; y: number; z: number; rotation: number };
  targetPosition: { x: number; y: number; z: number; rotation: number };
  movementVector: { x: number; y: number; z: number };
  duration: number; // months
  force: number; // grams
}

export interface WireSequence {
  id: string;
  stage: number;
  wireType: 'NiTi' | 'SS' | 'TMA' | 'CuNiTi';
  dimension: string; // e.g., "0.014", "0.016x0.022"
  shape: 'round' | 'rectangular';
  startMonth: number;
  endMonth: number;
  notes?: string;
}

export interface ElasticConfiguration {
  id: string;
  type: 'class_ii' | 'class_iii' | 'midline' | 'triangle' | 'box';
  attachmentPoints: {
    upper: number[]; // tooth numbers
    lower: number[]; // tooth numbers
  };
  force: number; // ounces
  wearTime: 'full_time' | 'night_only' | 'custom';
  customHours?: number;
  startMonth: number;
  endMonth: number;
}

export interface TreatmentSimulation {
  currentMonth: number;
  totalMonths: number;
  stages: SimulationStage[];
  activeMovements: ToothMovement[];
  currentWire: WireSequence | null;
  activeElastics: ElasticConfiguration[];
}

export interface SimulationStage {
  month: number;
  description: string;
  movements: ToothMovement[];
  wire: WireSequence | null;
  elastics: ElasticConfiguration[];
  milestones: string[];
}

export interface DetailedTreatmentPlan extends TreatmentPlan {
  toothMovements: ToothMovement[];
  wireSequences: WireSequence[];
  elasticConfigurations: ElasticConfiguration[];
  simulationData?: TreatmentSimulation;
}