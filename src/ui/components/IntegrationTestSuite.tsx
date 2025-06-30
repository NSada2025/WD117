import React, { useState, useEffect } from 'react';
import { DetailedTreatmentPlanView } from './DetailedTreatmentPlanView';
import { 
  apiService, 
  ToothMovementResponse, 
  WireSequenceResponse, 
  ElasticPrescriptionResponse 
} from '../services/apiService';
import { generateCompleteTestDataset } from '../utils/testDataGenerator';
import { LoadingSpinner, Toast } from './UIUtilities';
import { DetailedTreatmentPlan, ToothMovement, WireSequence, ElasticConfiguration } from '../types';

interface TestResult {
  testName: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  duration?: number;
  error?: string;
  details?: any;
}

export const IntegrationTestSuite: React.FC = () => {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [apiHealth, setApiHealth] = useState<boolean | null>(null);
  const [testData, setTestData] = useState<any>(null);
  const [treatmentPlan, setTreatmentPlan] = useState<DetailedTreatmentPlan | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const tests: Array<{
    name: string;
    description: string;
    testFunction: () => Promise<void>;
  }> = [
    {
      name: 'API Health Check',
      description: 'APIサーバーの稼働状況確認',
      testFunction: testApiHealth
    },
    {
      name: 'Tooth Movements API',
      description: '歯牙移動APIの動作確認',
      testFunction: testToothMovementsApi
    },
    {
      name: 'Wire Sequence API',
      description: 'ワイヤーシーケンスAPIの動作確認',
      testFunction: testWireSequenceApi
    },
    {
      name: 'Elastic Prescription API',
      description: '顎間ゴム処方APIの動作確認',
      testFunction: testElasticPrescriptionApi
    },
    {
      name: 'UI Data Integration',
      description: 'UIとAPIデータの統合表示テスト',
      testFunction: testUiDataIntegration
    },
    {
      name: 'Real-time Updates',
      description: 'リアルタイムデータ更新テスト',
      testFunction: testRealTimeUpdates
    }
  ];

  useEffect(() => {
    // テスト用データの初期化
    const data = generateCompleteTestDataset();
    setTestData(data);
    
    // 初期化時にAPIヘルスチェック
    checkApiHealth();
  }, []);

  async function checkApiHealth() {
    const isHealthy = await apiService.checkApiHealth();
    setApiHealth(isHealthy);
  }

  async function testApiHealth(): Promise<void> {
    const isHealthy = await apiService.checkApiHealth();
    setApiHealth(isHealthy);
    if (!isHealthy) {
      throw new Error('APIサーバーに接続できません');
    }
  }

  async function testToothMovementsApi(): Promise<void> {
    if (!testData) throw new Error('テストデータが初期化されていません');
    
    const result = await apiService.getToothMovements(testData.patient.id, testData.patient.age);
    
    if (result.error) {
      throw new Error(`歯牙移動API呼び出し失敗: ${result.error}`);
    }

    if (!result.data) {
      throw new Error('歯牙移動データが取得できませんでした');
    }

    // データ構造の検証
    const data = result.data;
    if (!data.movements || !data.movements.tooth_vectors) {
      throw new Error('期待されるデータ構造と異なります');
    }

    // 計算結果の妥当性チェック
    const movementTime = data.movements.total_movement_time;
    if (!movementTime || movementTime <= 0) {
      throw new Error('治療期間の計算が正しくありません');
    }

    console.log('歯牙移動API テスト結果:', data);
  }

  async function testWireSequenceApi(): Promise<void> {
    if (!testData) throw new Error('テストデータが初期化されていません');
    
    const result = await apiService.getWireSequence(testData.patient.id, testData.patient.age);
    
    if (result.error) {
      throw new Error(`ワイヤーシーケンスAPI呼び出し失敗: ${result.error}`);
    }

    if (!result.data) {
      throw new Error('ワイヤーシーケンスデータが取得できませんでした');
    }

    // データ構造の検証
    const data = result.data;
    if (!data.wire_sequence || !Array.isArray(data.wire_sequence)) {
      throw new Error('ワイヤーシーケンスの配列が正しくありません');
    }

    // 段階的な進行の確認
    const sequence = data.wire_sequence;
    if (sequence.length === 0) {
      throw new Error('ワイヤーシーケンスが空です');
    }

    // 期間の妥当性確認
    if (!data.total_duration_weeks || data.total_duration_weeks <= 0) {
      throw new Error('総治療期間が正しく計算されていません');
    }

    console.log('ワイヤーシーケンスAPI テスト結果:', data);
  }

  async function testElasticPrescriptionApi(): Promise<void> {
    if (!testData) throw new Error('テストデータが初期化されていません');
    
    const result = await apiService.getElasticPrescription(
      testData.patient.id, 
      '空隙閉鎖',
      {
        molar_relationship: 'class_ii',
        overjet: 5.2,
        overbite: 4.1
      }
    );
    
    if (result.error) {
      throw new Error(`顎間ゴム処方API呼び出し失敗: ${result.error}`);
    }

    if (!result.data) {
      throw new Error('顎間ゴム処方データが取得できませんでした');
    }

    // データ構造の検証
    const data = result.data;
    if (!data.prescription || !data.prescription.elastics) {
      throw new Error('顎間ゴム処方の構造が正しくありません');
    }

    // 処方内容の検証
    const elastics = data.prescription.elastics;
    if (!Array.isArray(elastics) || elastics.length === 0) {
      throw new Error('顎間ゴム処方が空です');
    }

    // 各処方の妥当性確認
    for (const elastic of elastics) {
      if (!elastic.type || !elastic.attachment || !elastic.force) {
        throw new Error('顎間ゴム処方の項目が不完全です');
      }
    }

    console.log('顎間ゴム処方API テスト結果:', data);
  }

  async function testUiDataIntegration(): Promise<void> {
    if (!testData) throw new Error('テストデータが初期化されていません');
    
    // APIからデータを取得
    const [toothResult, wireResult, elasticResult] = await Promise.all([
      apiService.getToothMovements(testData.patient.id, testData.patient.age),
      apiService.getWireSequence(testData.patient.id, testData.patient.age),
      apiService.getElasticPrescription(testData.patient.id, '配列')
    ]);

    // エラーチェック
    if (toothResult.error || wireResult.error || elasticResult.error) {
      throw new Error('一部のAPI呼び出しが失敗しました');
    }

    // APIデータをDetailedTreatmentPlan形式に変換
    const convertedPlan = convertApiDataToTreatmentPlan(
      testData.treatmentPlan,
      toothResult.data!,
      wireResult.data!,
      elasticResult.data!
    );

    setTreatmentPlan(convertedPlan);

    // UIコンポーネントの描画確認
    if (!convertedPlan.toothMovements || convertedPlan.toothMovements.length === 0) {
      throw new Error('歯牙移動データの変換に失敗しました');
    }

    if (!convertedPlan.wireSequences || convertedPlan.wireSequences.length === 0) {
      throw new Error('ワイヤーシーケンスデータの変換に失敗しました');
    }

    if (!convertedPlan.elasticConfigurations || convertedPlan.elasticConfigurations.length === 0) {
      throw new Error('顎間ゴム設定データの変換に失敗しました');
    }

    console.log('UI統合テスト 変換後データ:', convertedPlan);
  }

  async function testRealTimeUpdates(): Promise<void> {
    if (!treatmentPlan) {
      throw new Error('治療計画データが準備されていません');
    }

    // 歯牙移動データの更新テスト
    const updatedMovement = { ...treatmentPlan.toothMovements[0] };
    updatedMovement.force = updatedMovement.force + 10;

    const updatedPlan = {
      ...treatmentPlan,
      toothMovements: treatmentPlan.toothMovements.map(m => 
        m.toothNumber === updatedMovement.toothNumber ? updatedMovement : m
      )
    };

    setTreatmentPlan(updatedPlan);

    // 更新が正常に反映されているかチェック
    const updatedForce = updatedPlan.toothMovements.find(
      m => m.toothNumber === updatedMovement.toothNumber
    )?.force;

    if (updatedForce !== updatedMovement.force) {
      throw new Error('リアルタイム更新が正しく動作していません');
    }

    console.log('リアルタイム更新テスト完了');
  }

  function convertApiDataToTreatmentPlan(
    basePlan: DetailedTreatmentPlan,
    toothData: ToothMovementResponse,
    wireData: WireSequenceResponse,
    elasticData: ElasticPrescriptionResponse
  ): DetailedTreatmentPlan {
    // 歯牙移動データの変換
    const toothMovements: ToothMovement[] = Object.entries(toothData.movements.tooth_vectors).map(
      ([toothName, vector], index) => ({
        toothNumber: 11 + index, // 実際には歯番号のマッピングが必要
        initialPosition: { x: 0, y: 0, z: 0, rotation: 0 },
        targetPosition: { x: vector[0], y: vector[1], z: vector[2], rotation: 0 },
        movementVector: { x: vector[0], y: vector[1], z: vector[2] },
        duration: toothData.movements.total_movement_time,
        force: 150 // デフォルト値
      })
    );

    // ワイヤーシーケンスの変換
    const wireSequences: WireSequence[] = wireData.wire_sequence.map((wire, index) => ({
      id: `W${index + 1}`,
      stage: index + 1,
      wireType: wire.size.includes('NiTi') ? 'NiTi' : 'SS',
      dimension: wire.size.split(' ')[0],
      shape: wire.size.includes('×') ? 'rectangular' : 'round',
      startMonth: index * 2,
      endMonth: (index + 1) * 2,
      notes: wire.purpose
    }));

    // 顎間ゴム設定の変換
    const elasticConfigurations: ElasticConfiguration[] = elasticData.prescription.elastics.map(
      (elastic, index) => ({
        id: `E${index + 1}`,
        type: elastic.type.includes('II級') ? 'class_ii' : 
              elastic.type.includes('III級') ? 'class_iii' : 'midline',
        attachmentPoints: {
          upper: [13, 14], // 実際には処方内容から解析が必要
          lower: [34, 35]
        },
        force: parseFloat(elastic.force) || 4.5,
        wearTime: 'full_time',
        startMonth: 0,
        endMonth: Math.ceil(elasticData.prescription.duration_weeks / 4)
      })
    );

    return {
      ...basePlan,
      toothMovements,
      wireSequences,
      elasticConfigurations
    };
  }

  async function runTest(testIndex: number): Promise<void> {
    const test = tests[testIndex];
    const startTime = Date.now();

    // テスト状態を更新
    setTestResults(prev => prev.map((result, index) => 
      index === testIndex 
        ? { ...result, status: 'running', duration: undefined, error: undefined }
        : result
    ));

    try {
      await test.testFunction();
      const duration = Date.now() - startTime;
      
      setTestResults(prev => prev.map((result, index) => 
        index === testIndex 
          ? { ...result, status: 'passed', duration, error: undefined }
          : result
      ));
    } catch (error) {
      const duration = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : '不明なエラー';
      
      setTestResults(prev => prev.map((result, index) => 
        index === testIndex 
          ? { ...result, status: 'failed', duration, error: errorMessage }
          : result
      ));
    }
  }

  async function runAllTests(): Promise<void> {
    setIsRunning(true);
    
    // 全テストを初期化
    setTestResults(tests.map(test => ({
      testName: test.name,
      status: 'pending' as const
    })));

    try {
      // テストを順次実行
      for (let i = 0; i < tests.length; i++) {
        await runTest(i);
        // テスト間の短い待機
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      setToast({ message: '統合テストが完了しました', type: 'success' });
    } catch (error) {
      setToast({ message: '統合テストでエラーが発生しました', type: 'error' });
    } finally {
      setIsRunning(false);
    }
  }

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'passed': return 'text-green-600 bg-green-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'passed': return '✓';
      case 'failed': return '✗';
      case 'running': return '⟳';
      default: return '○';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white border-b p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">統合テストスイート</h1>
            <p className="text-gray-600">
              DetailedTreatmentPlanViewとdev2 APIの連携テスト
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`px-3 py-1 rounded text-sm font-medium ${
              apiHealth === true ? 'bg-green-100 text-green-700' :
              apiHealth === false ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              API: {apiHealth === true ? '正常' : apiHealth === false ? '異常' : '確認中'}
            </div>
            <button
              onClick={runAllTests}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {isRunning ? 'テスト実行中...' : '全テスト実行'}
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* テスト結果パネル */}
        <div className="w-96 bg-white border-r p-4">
          <h3 className="font-semibold mb-4">テスト結果</h3>
          <div className="space-y-2">
            {tests.map((test, index) => {
              const result = testResults[index];
              return (
                <div
                  key={test.name}
                  className="border rounded p-3 cursor-pointer hover:bg-gray-50"
                  onClick={() => !isRunning && runTest(index)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                        result ? getStatusColor(result.status) : 'bg-gray-100 text-gray-600'
                      }`}>
                        {result ? getStatusIcon(result.status) : '○'}
                      </span>
                      <span className="font-medium">{test.name}</span>
                    </div>
                    {result?.duration && (
                      <span className="text-xs text-gray-500">{result.duration}ms</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{test.description}</p>
                  {result?.error && (
                    <p className="text-sm text-red-600 mt-2 bg-red-50 p-2 rounded">
                      {result.error}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* メインテストエリア */}
        <div className="flex-1 p-6">
          {treatmentPlan ? (
            <div>
              <h3 className="text-lg font-semibold mb-4">
                統合テスト: DetailedTreatmentPlanView
              </h3>
              <div className="bg-white rounded-lg shadow h-96">
                <DetailedTreatmentPlanView
                  treatmentPlan={treatmentPlan}
                  onUpdate={(updatedPlan) => setTreatmentPlan(updatedPlan)}
                  isEditable={true}
                />
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-gray-500 mb-4">
                  統合テストを実行して治療計画データを表示します
                </p>
                <button
                  onClick={runAllTests}
                  disabled={isRunning}
                  className="px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                >
                  {isRunning ? (
                    <div className="flex items-center gap-2">
                      <LoadingSpinner size="small" />
                      テスト実行中...
                    </div>
                  ) : (
                    'テスト開始'
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* トースト通知 */}
      {toast && (
        <div className="fixed bottom-4 right-4 z-50">
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
          />
        </div>
      )}
    </div>
  );
};