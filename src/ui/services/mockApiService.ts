// モックAPIサービス - dev2のAPIが利用できない場合のフォールバック
import { 
  ApiResponse, 
  ToothMovementResponse, 
  WireSequenceResponse, 
  ElasticPrescriptionResponse 
} from './apiService';

export class MockApiService {
  private delay: number;

  constructor(delay: number = 1000) {
    this.delay = delay;
  }

  private async mockDelay(): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, this.delay));
  }

  async getToothMovements(patientId: string, patientAge: number): Promise<ApiResponse<ToothMovementResponse>> {
    await this.mockDelay();

    const mockData: ToothMovementResponse = {
      patient_id: patientId,
      movements: {
        anterior_retraction: {
          "上顎中切歯": {
            後方移動量: 3.5,
            舌側傾斜: 10.0,
            圧下量: 0.5
          },
          "下顎中切歯": {
            後方移動量: 2.0,
            舌側傾斜: 5.0,
            圧下量: 0.2
          }
        },
        molar_movement: {
          "上顎第一大臼歯": {
            遠心移動: 3.0,
            回転: -5.0
          },
          "下顎第一大臼歯": {
            遠心移動: 2.5,
            回転: -3.0
          }
        },
        tooth_vectors: {
          "上顎中切歯": [-3.5, 0, -0.5],
          "下顎中切歯": [-2.0, 0, -0.2],
          "上顎側切歯": [-2.8, 0.5, -0.3],
          "下顎側切歯": [-1.5, 0.3, -0.1],
          "上顎犬歯": [-2.2, 1.0, 0],
          "下顎犬歯": [-1.8, 0.8, 0],
          "上顎第一小臼歯": [-1.5, 0.5, 0.2],
          "下顎第一小臼歯": [-1.2, 0.4, 0.1]
        },
        total_movement_time: 18
      },
      calculated_at: new Date().toISOString()
    };

    return {
      data: mockData,
      status: 200
    };
  }

  async getWireSequence(patientId: string, patientAge: number): Promise<ApiResponse<WireSequenceResponse>> {
    await this.mockDelay();

    const mockData: WireSequenceResponse = {
      patient_id: patientId,
      appliance_type: "メタルブラケット",
      wire_sequence: [
        {
          size: "0.012\" NiTi",
          duration_weeks: 4,
          purpose: "初期配列",
          force_level: "軽度（25-50g）",
          stage: "初期治療"
        },
        {
          size: "0.014\" NiTi",
          duration_weeks: 6,
          purpose: "レベリング",
          force_level: "軽度（50-75g）",
          stage: "配列期"
        },
        {
          size: "0.016\" NiTi",
          duration_weeks: 8,
          purpose: "歯列弓の拡大",
          force_level: "中等度（75-125g）",
          stage: "配列期"
        },
        {
          size: "0.016×0.022\" NiTi",
          duration_weeks: 12,
          purpose: "トルクコントロール",
          force_level: "中等度（100-150g）",
          stage: "仕上げ期前期"
        },
        {
          size: "0.019×0.025\" SS",
          duration_weeks: 16,
          purpose: "最終的な歯の位置決め",
          force_level: "中等度（125-175g）",
          stage: "仕上げ期"
        },
        {
          size: "0.017×0.025\" TMA",
          duration_weeks: 8,
          purpose: "ディテーリング",
          force_level: "軽度（75-100g）",
          stage: "最終調整"
        }
      ],
      total_duration_weeks: 54,
      generated_at: new Date().toISOString()
    };

    return {
      data: mockData,
      status: 200
    };
  }

  async getElasticPrescription(
    patientId: string, 
    treatmentStage: string,
    occlusionAnalysis?: any
  ): Promise<ApiResponse<ElasticPrescriptionResponse>> {
    await this.mockDelay();

    const mockData: ElasticPrescriptionResponse = {
      patient_id: patientId,
      prescription: {
        stage: treatmentStage,
        elastics: [
          {
            type: "II級ゴム",
            attachment: {
              上顎: "犬歯フック",
              下顎: "第一大臼歯フック"
            },
            force: "3.5oz (中等度)",
            wear_time: "20時間/日（食事時以外）",
            purpose: "上顎前突の改善・臼歯関係の改善"
          },
          {
            type: "垂直ゴム",
            attachment: {
              上顎: "前歯部ブラケット",
              下顎: "前歯部ブラケット"
            },
            force: "2.5oz (軽度)",
            wear_time: "夜間のみ（12時間/日）",
            purpose: "前歯部の圧下・開咬の改善"
          }
        ],
        duration_weeks: 16,
        wear_instructions: `
1. 指定された装着位置に正確に装着してください
2. 食事と歯磨き時以外は必ず装着してください
3. ゴムが切れたらすぐに新しいものに交換してください
4. 痛みや不快感が強い場合は無理をせず、次回の来院時にご相談ください
5. 効果を最大化するため、指示された装着時間を必ず守ってください
        `.trim()
      },
      prescribed_at: new Date().toISOString()
    };

    return {
      data: mockData,
      status: 200
    };
  }

  async checkApiHealth(): Promise<boolean> {
    await this.mockDelay();
    return true; // モックAPIは常に利用可能
  }
}

export const mockApiService = new MockApiService(800); // 800msの遅延でリアルなAPIコールをシミュレート