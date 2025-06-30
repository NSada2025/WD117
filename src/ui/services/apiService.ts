// API連携サービス
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// 歯牙移動APIレスポンス型
export interface ToothMovementResponse {
  patient_id: string;
  movements: {
    anterior_retraction?: {
      [toothName: string]: {
        後方移動量: number;
        舌側傾斜: number;
        圧下量: number;
      };
    };
    molar_movement?: {
      [toothName: string]: {
        遠心移動: number;
        回転: number;
      };
    };
    tooth_vectors: {
      [toothName: string]: [number, number, number];
    };
    total_movement_time: number;
  };
  calculated_at: string;
}

// ワイヤーシーケンスAPIレスポンス型
export interface WireSequenceResponse {
  patient_id: string;
  appliance_type: string;
  wire_sequence: Array<{
    size: string;
    duration_weeks: number;
    purpose: string;
    force_level: string;
    stage: string;
  }>;
  total_duration_weeks: number;
  generated_at: string;
}

// 顎間ゴム処方APIレスポンス型
export interface ElasticPrescriptionResponse {
  patient_id: string;
  prescription: {
    stage: string;
    elastics: Array<{
      type: string;
      attachment: {
        上顎: string;
        下顎: string;
      };
      force: string;
      wear_time: string;
      purpose: string;
    }>;
    duration_weeks: number;
    wear_instructions: string;
  };
  prescribed_at: string;
}

// APIサービスクラス
export class TreatmentPlanApiService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  // 歯牙移動データを取得
  async getToothMovements(patientId: string, patientAge: number): Promise<ApiResponse<ToothMovementResponse>> {
    try {
      const response = await fetch(
        `${this.baseUrl}/patients/${patientId}/tooth-movements?patient_age=${patientAge}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status
        };
      }

      return {
        data,
        status: response.status
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : '歯牙移動データの取得に失敗しました',
        status: 500
      };
    }
  }

  // ワイヤーシーケンスを取得
  async getWireSequence(patientId: string, patientAge: number): Promise<ApiResponse<WireSequenceResponse>> {
    try {
      const response = await fetch(
        `${this.baseUrl}/patients/${patientId}/wire-sequence?patient_age=${patientAge}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status
        };
      }

      return {
        data,
        status: response.status
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'ワイヤーシーケンスの取得に失敗しました',
        status: 500
      };
    }
  }

  // 顎間ゴム処方を取得
  async getElasticPrescription(
    patientId: string, 
    treatmentStage: string,
    occlusionAnalysis?: any
  ): Promise<ApiResponse<ElasticPrescriptionResponse>> {
    try {
      const response = await fetch(
        `${this.baseUrl}/patients/${patientId}/elastic-prescription?treatment_stage=${encodeURIComponent(treatmentStage)}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: occlusionAnalysis ? JSON.stringify(occlusionAnalysis) : undefined,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status
        };
      }

      return {
        data,
        status: response.status
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : '顎間ゴム処方の取得に失敗しました',
        status: 500
      };
    }
  }

  // APIサーバーの稼働状況をチェック
  async checkApiHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        timeout: 5000,
      } as any);
      return response.ok;
    } catch (error) {
      console.warn('API health check failed:', error);
      return false;
    }
  }
}

// シングルトンインスタンス
export const apiService = new TreatmentPlanApiService();