import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import {
  DetailedTreatmentPlan,
  ToothMovement,
  WireSequence,
  ElasticConfiguration,
  TreatmentSimulation,
  SimulationStage
} from '../types';
import { LoadingSpinner, Toast, ProgressBar } from './UIUtilities';

interface DetailedTreatmentPlanViewProps {
  treatmentPlan: DetailedTreatmentPlan;
  onUpdate?: (updatedPlan: DetailedTreatmentPlan) => void;
  isEditable?: boolean;
}

export const DetailedTreatmentPlanView: React.FC<DetailedTreatmentPlanViewProps> = ({
  treatmentPlan,
  onUpdate,
  isEditable = true
}) => {
  const [activeTab, setActiveTab] = useState<'3d' | 'wire' | 'elastic' | 'simulation'>('3d');
  const [selectedTooth, setSelectedTooth] = useState<number | null>(null);
  const [editingMovement, setEditingMovement] = useState<ToothMovement | null>(null);
  const [simulationMonth, setSimulationMonth] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showToast, setShowToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  // 3Dビジュアライゼーション用の歯牙配置
  const teethPositions = useMemo(() => {
    const positions: Map<number, { x: number; y: number; quadrant: number }> = new Map();
    
    // 上顎（11-18, 21-28）
    for (let i = 1; i <= 8; i++) {
      positions.set(10 + i, { x: 150 - (i - 1) * 35, y: 100, quadrant: 1 });
      positions.set(20 + i, { x: 150 + (i - 1) * 35, y: 100, quadrant: 2 });
    }
    
    // 下顎（31-38, 41-48）
    for (let i = 1; i <= 8; i++) {
      positions.set(40 + i, { x: 150 + (i - 1) * 35, y: 300, quadrant: 4 });
      positions.set(30 + i, { x: 150 - (i - 1) * 35, y: 300, quadrant: 3 });
    }
    
    return positions;
  }, []);

  // 歯牙移動の3D描画
  const draw3DVisualization = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 背景グリッド
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= canvas.width; i += 50) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, canvas.height);
      ctx.stroke();
    }
    for (let i = 0; i <= canvas.height; i += 50) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(canvas.width, i);
      ctx.stroke();
    }
    
    // 歯牙の描画
    teethPositions.forEach((pos, toothNumber) => {
      const movement = treatmentPlan.toothMovements.find(m => m.toothNumber === toothNumber);
      const isSelected = selectedTooth === toothNumber;
      
      // 初期位置
      ctx.fillStyle = '#f0f0f0';
      ctx.strokeStyle = '#999';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 15, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      
      // 歯番号
      ctx.fillStyle = '#333';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(toothNumber.toString(), pos.x, pos.y);
      
      if (movement) {
        // 目標位置
        const targetX = pos.x + movement.movementVector.x * 10;
        const targetY = pos.y + movement.movementVector.y * 10;
        
        ctx.strokeStyle = '#4CAF50';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.arc(targetX, targetY, 15, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // 移動ベクトル
        ctx.strokeStyle = isSelected ? '#FF5722' : '#2196F3';
        ctx.lineWidth = isSelected ? 3 : 2;
        ctx.beginPath();
        ctx.moveTo(pos.x, pos.y);
        ctx.lineTo(targetX, targetY);
        ctx.stroke();
        
        // 矢印
        const angle = Math.atan2(targetY - pos.y, targetX - pos.x);
        ctx.beginPath();
        ctx.moveTo(targetX, targetY);
        ctx.lineTo(
          targetX - 10 * Math.cos(angle - Math.PI / 6),
          targetY - 10 * Math.sin(angle - Math.PI / 6)
        );
        ctx.moveTo(targetX, targetY);
        ctx.lineTo(
          targetX - 10 * Math.cos(angle + Math.PI / 6),
          targetY - 10 * Math.sin(angle + Math.PI / 6)
        );
        ctx.stroke();
        
        // 力の表示
        if (isSelected) {
          ctx.fillStyle = '#FF5722';
          ctx.font = '14px Arial';
          ctx.fillText(`${movement.force}g`, (pos.x + targetX) / 2, (pos.y + targetY) / 2 - 10);
        }
      }
    });
    
    // 顎間ゴムの描画
    const activeElastics = getActiveElastics(simulationMonth);
    activeElastics.forEach(elastic => {
      ctx.strokeStyle = '#FF9800';
      ctx.lineWidth = 2;
      ctx.setLineDash([3, 3]);
      
      elastic.attachmentPoints.upper.forEach(upperTooth => {
        elastic.attachmentPoints.lower.forEach(lowerTooth => {
          const upperPos = teethPositions.get(upperTooth);
          const lowerPos = teethPositions.get(lowerTooth);
          
          if (upperPos && lowerPos) {
            ctx.beginPath();
            ctx.moveTo(upperPos.x, upperPos.y);
            ctx.lineTo(lowerPos.x, lowerPos.y);
            ctx.stroke();
          }
        });
      });
      
      ctx.setLineDash([]);
    });
  }, [treatmentPlan, teethPositions, selectedTooth, simulationMonth]);

  // アニメーションループ
  useEffect(() => {
    draw3DVisualization();
  }, [draw3DVisualization]);

  // シミュレーション再生
  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setSimulationMonth(prev => {
          if (prev >= treatmentPlan.estimatedDuration) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 1;
        });
      }, 500);
      
      return () => clearInterval(interval);
    }
  }, [isPlaying, treatmentPlan.estimatedDuration]);

  // 現在アクティブなワイヤーを取得
  const getActiveWire = (month: number): WireSequence | null => {
    return treatmentPlan.wireSequences.find(
      wire => wire.startMonth <= month && wire.endMonth >= month
    ) || null;
  };

  // 現在アクティブな顎間ゴムを取得
  const getActiveElastics = (month: number): ElasticConfiguration[] => {
    return treatmentPlan.elasticConfigurations.filter(
      elastic => elastic.startMonth <= month && elastic.endMonth >= month
    );
  };

  // 歯牙移動の編集
  const handleMovementEdit = (movement: ToothMovement, field: keyof ToothMovement, value: any) => {
    if (!isEditable || !onUpdate) return;
    
    const updatedMovements = treatmentPlan.toothMovements.map(m =>
      m.toothNumber === movement.toothNumber
        ? { ...m, [field]: value }
        : m
    );
    
    onUpdate({
      ...treatmentPlan,
      toothMovements: updatedMovements
    });
    
    setShowToast({ message: '歯牙移動データを更新しました', type: 'success' });
  };

  // ワイヤーシーケンスの編集
  const handleWireEdit = (wire: WireSequence, field: keyof WireSequence, value: any) => {
    if (!isEditable || !onUpdate) return;
    
    const updatedWires = treatmentPlan.wireSequences.map(w =>
      w.id === wire.id ? { ...w, [field]: value } : w
    );
    
    onUpdate({
      ...treatmentPlan,
      wireSequences: updatedWires
    });
    
    setShowToast({ message: 'ワイヤーシーケンスを更新しました', type: 'success' });
  };

  // 顎間ゴムの編集
  const handleElasticEdit = (elastic: ElasticConfiguration, field: keyof ElasticConfiguration, value: any) => {
    if (!isEditable || !onUpdate) return;
    
    const updatedElastics = treatmentPlan.elasticConfigurations.map(e =>
      e.id === elastic.id ? { ...e, [field]: value } : e
    );
    
    onUpdate({
      ...treatmentPlan,
      elasticConfigurations: updatedElastics
    });
    
    setShowToast({ message: '顎間ゴム設定を更新しました', type: 'success' });
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* タブナビゲーション */}
      <div className="bg-white border-b">
        <div className="flex">
          <button
            onClick={() => setActiveTab('3d')}
            className={`px-6 py-3 font-medium ${
              activeTab === '3d'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            3D歯牙移動
          </button>
          <button
            onClick={() => setActiveTab('wire')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'wire'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            ワイヤーシーケンス
          </button>
          <button
            onClick={() => setActiveTab('elastic')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'elastic'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            顎間ゴム
          </button>
          <button
            onClick={() => setActiveTab('simulation')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'simulation'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            進捗シミュレーション
          </button>
        </div>
      </div>

      {/* コンテンツエリア */}
      <div className="flex-1 overflow-hidden">
        {activeTab === '3d' && (
          <div className="h-full flex">
            <div className="flex-1 p-6">
              <h3 className="text-lg font-semibold mb-4">歯牙移動ビジュアライゼーション</h3>
              <div className="bg-white rounded-lg shadow p-4">
                <canvas
                  ref={canvasRef}
                  width={600}
                  height={400}
                  className="border border-gray-200 rounded cursor-pointer"
                  onClick={(e) => {
                    const rect = canvasRef.current?.getBoundingClientRect();
                    if (!rect) return;
                    
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    // クリックした歯牙を検出
                    teethPositions.forEach((pos, toothNumber) => {
                      const distance = Math.sqrt(
                        Math.pow(x - pos.x, 2) + Math.pow(y - pos.y, 2)
                      );
                      if (distance < 20) {
                        setSelectedTooth(toothNumber);
                        const movement = treatmentPlan.toothMovements.find(
                          m => m.toothNumber === toothNumber
                        );
                        if (movement) {
                          setEditingMovement(movement);
                        }
                      }
                    });
                  }}
                />
              </div>
            </div>

            {/* 編集パネル */}
            {editingMovement && (
              <div className="w-80 bg-white border-l p-6">
                <h4 className="font-semibold mb-4">
                  歯牙 {editingMovement.toothNumber} の移動設定
                </h4>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      移動量 X (mm)
                    </label>
                    <input
                      type="number"
                      value={editingMovement.movementVector.x}
                      onChange={(e) => handleMovementEdit(editingMovement, 'movementVector', {
                        ...editingMovement.movementVector,
                        x: parseFloat(e.target.value)
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      step="0.1"
                      disabled={!isEditable}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      移動量 Y (mm)
                    </label>
                    <input
                      type="number"
                      value={editingMovement.movementVector.y}
                      onChange={(e) => handleMovementEdit(editingMovement, 'movementVector', {
                        ...editingMovement.movementVector,
                        y: parseFloat(e.target.value)
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      step="0.1"
                      disabled={!isEditable}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      力 (g)
                    </label>
                    <input
                      type="number"
                      value={editingMovement.force}
                      onChange={(e) => handleMovementEdit(editingMovement, 'force', parseFloat(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      step="5"
                      disabled={!isEditable}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      期間 (月)
                    </label>
                    <input
                      type="number"
                      value={editingMovement.duration}
                      onChange={(e) => handleMovementEdit(editingMovement, 'duration', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      min="1"
                      disabled={!isEditable}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'wire' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">ワイヤーシーケンスタイムライン</h3>
            
            <div className="bg-white rounded-lg shadow">
              <div className="p-4">
                {/* タイムラインヘッダー */}
                <div className="flex items-center mb-4">
                  <div className="w-32 font-medium">ステージ</div>
                  <div className="flex-1 relative h-8 bg-gray-100 rounded">
                    {Array.from({ length: treatmentPlan.estimatedDuration }, (_, i) => (
                      <div
                        key={i}
                        className="absolute top-0 bottom-0 border-l border-gray-300"
                        style={{ left: `${(i / treatmentPlan.estimatedDuration) * 100}%` }}
                      >
                        <span className="absolute top-full text-xs text-gray-500 -translate-x-1/2">
                          {i + 1}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* ワイヤーシーケンス */}
                <div className="space-y-3">
                  {treatmentPlan.wireSequences.map(wire => (
                    <div key={wire.id} className="flex items-center">
                      <div className="w-32">
                        <div className="text-sm font-medium">
                          {wire.wireType} {wire.dimension}
                        </div>
                        <div className="text-xs text-gray-500">
                          {wire.shape === 'round' ? '丸型' : '角型'}
                        </div>
                      </div>
                      <div className="flex-1 relative h-12">
                        <div
                          className="absolute top-2 bottom-2 bg-blue-500 rounded cursor-pointer hover:bg-blue-600"
                          style={{
                            left: `${(wire.startMonth / treatmentPlan.estimatedDuration) * 100}%`,
                            width: `${((wire.endMonth - wire.startMonth) / treatmentPlan.estimatedDuration) * 100}%`
                          }}
                          onClick={() => {
                            // 編集モーダルを開く
                          }}
                        >
                          <div className="text-white text-xs px-2 py-1 truncate">
                            {wire.notes || `${wire.endMonth - wire.startMonth}ヶ月`}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'elastic' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">顎間ゴム装着計画</h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* ゴム配置図 */}
              <div className="bg-white rounded-lg shadow p-4">
                <h4 className="font-medium mb-3">装着部位</h4>
                <div className="relative h-96">
                  {/* 簡易的な歯列図 */}
                  <svg viewBox="0 0 400 400" className="w-full h-full">
                    {/* 上顎歯列 */}
                    <g>
                      {[...Array(16)].map((_, i) => {
                        const toothNumber = i < 8 ? 18 - i : 21 + (i - 8);
                        const x = i < 8 ? 50 + i * 40 : 50 + i * 40;
                        const y = 100;
                        
                        return (
                          <g key={toothNumber}>
                            <rect
                              x={x}
                              y={y}
                              width="30"
                              height="30"
                              fill="#f0f0f0"
                              stroke="#999"
                              strokeWidth="2"
                              rx="5"
                            />
                            <text
                              x={x + 15}
                              y={y + 20}
                              textAnchor="middle"
                              fontSize="12"
                              fill="#333"
                            >
                              {toothNumber}
                            </text>
                          </g>
                        );
                      })}
                    </g>

                    {/* 下顎歯列 */}
                    <g>
                      {[...Array(16)].map((_, i) => {
                        const toothNumber = i < 8 ? 48 - i : 31 + (i - 8);
                        const x = i < 8 ? 50 + i * 40 : 50 + i * 40;
                        const y = 300;
                        
                        return (
                          <g key={toothNumber}>
                            <rect
                              x={x}
                              y={y}
                              width="30"
                              height="30"
                              fill="#f0f0f0"
                              stroke="#999"
                              strokeWidth="2"
                              rx="5"
                            />
                            <text
                              x={x + 15}
                              y={y + 20}
                              textAnchor="middle"
                              fontSize="12"
                              fill="#333"
                            >
                              {toothNumber}
                            </text>
                          </g>
                        );
                      })}
                    </g>

                    {/* 顎間ゴムの描画 */}
                    {getActiveElastics(simulationMonth).map(elastic => (
                      <g key={elastic.id}>
                        {elastic.attachmentPoints.upper.map(upperTooth =>
                          elastic.attachmentPoints.lower.map(lowerTooth => {
                            // 歯の位置を計算
                            const upperIndex = upperTooth > 20 ? upperTooth - 21 + 8 : 18 - upperTooth;
                            const lowerIndex = lowerTooth > 40 ? 48 - lowerTooth : lowerTooth - 31 + 8;
                            
                            const x1 = 65 + upperIndex * 40;
                            const y1 = 130;
                            const x2 = 65 + lowerIndex * 40;
                            const y2 = 300;
                            
                            return (
                              <line
                                key={`${upperTooth}-${lowerTooth}`}
                                x1={x1}
                                y1={y1}
                                x2={x2}
                                y2={y2}
                                stroke="#FF9800"
                                strokeWidth="3"
                                strokeDasharray="5,5"
                              />
                            );
                          })
                        )}
                      </g>
                    ))}
                  </svg>
                </div>
              </div>

              {/* ゴム設定リスト */}
              <div className="bg-white rounded-lg shadow p-4">
                <h4 className="font-medium mb-3">顎間ゴム設定</h4>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {treatmentPlan.elasticConfigurations.map(elastic => (
                    <div key={elastic.id} className="border rounded p-3">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <span className="font-medium">
                            {elastic.type.replace('_', ' ').toUpperCase()}
                          </span>
                          <span className="ml-2 text-sm text-gray-500">
                            {elastic.force} oz
                          </span>
                        </div>
                        <span className="text-sm text-gray-500">
                          {elastic.startMonth} - {elastic.endMonth}ヶ月
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        <div>
                          上顎: {elastic.attachmentPoints.upper.join(', ')}
                        </div>
                        <div>
                          下顎: {elastic.attachmentPoints.lower.join(', ')}
                        </div>
                        <div className="mt-1">
                          装着時間: {elastic.wearTime === 'full_time' ? '終日' : 
                                   elastic.wearTime === 'night_only' ? '夜間のみ' : 
                                   `${elastic.customHours}時間/日`}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'simulation' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">治療進捗シミュレーション</h3>
            
            <div className="bg-white rounded-lg shadow p-6">
              {/* シミュレーションコントロール */}
              <div className="mb-6">
                <div className="flex items-center gap-4 mb-4">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className={`px-4 py-2 rounded ${
                      isPlaying ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
                    } text-white`}
                  >
                    {isPlaying ? '停止' : '再生'}
                  </button>
                  <button
                    onClick={() => setSimulationMonth(0)}
                    className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded"
                  >
                    リセット
                  </button>
                  <div className="flex-1">
                    <input
                      type="range"
                      min="0"
                      max={treatmentPlan.estimatedDuration}
                      value={simulationMonth}
                      onChange={(e) => setSimulationMonth(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <span className="text-lg font-medium">
                    {simulationMonth} / {treatmentPlan.estimatedDuration} ヶ月
                  </span>
                </div>
              </div>

              {/* 現在の状態 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded p-4">
                  <h5 className="font-medium mb-2">現在のワイヤー</h5>
                  {(() => {
                    const wire = getActiveWire(simulationMonth);
                    return wire ? (
                      <div>
                        <div className="text-lg">{wire.wireType} {wire.dimension}</div>
                        <div className="text-sm text-gray-600">{wire.shape === 'round' ? '丸型' : '角型'}</div>
                      </div>
                    ) : (
                      <div className="text-gray-500">なし</div>
                    );
                  })()}
                </div>

                <div className="bg-gray-50 rounded p-4">
                  <h5 className="font-medium mb-2">アクティブな顎間ゴム</h5>
                  {(() => {
                    const elastics = getActiveElastics(simulationMonth);
                    return elastics.length > 0 ? (
                      <div className="space-y-1">
                        {elastics.map(elastic => (
                          <div key={elastic.id} className="text-sm">
                            {elastic.type.replace('_', ' ')} ({elastic.force}oz)
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-gray-500">なし</div>
                    );
                  })()}
                </div>

                <div className="bg-gray-50 rounded p-4">
                  <h5 className="font-medium mb-2">進行中の歯牙移動</h5>
                  {(() => {
                    const movements = treatmentPlan.toothMovements.filter(
                      m => simulationMonth <= m.duration
                    );
                    return movements.length > 0 ? (
                      <div className="text-sm">
                        {movements.length}本の歯が移動中
                      </div>
                    ) : (
                      <div className="text-gray-500">完了</div>
                    );
                  })()}
                </div>
              </div>

              {/* 進捗グラフ */}
              <div className="mt-6">
                <h5 className="font-medium mb-3">治療進捗</h5>
                <div className="space-y-2">
                  <ProgressBar
                    value={simulationMonth}
                    max={treatmentPlan.estimatedDuration}
                    label="全体進捗"
                  />
                  
                  {treatmentPlan.procedures.map(procedure => {
                    const startMonth = treatmentPlan.procedures
                      .slice(0, procedure.sequence - 1)
                      .reduce((sum, p) => sum + p.duration, 0);
                    const endMonth = startMonth + procedure.duration;
                    const isActive = simulationMonth >= startMonth && simulationMonth < endMonth;
                    const isCompleted = simulationMonth >= endMonth;
                    
                    return (
                      <div key={procedure.id} className="flex items-center gap-3">
                        <div className="w-32 text-sm truncate">{procedure.description}</div>
                        <div className="flex-1">
                          <div className="h-6 bg-gray-200 rounded relative">
                            <div
                              className={`h-full rounded transition-all ${
                                isCompleted ? 'bg-green-500' :
                                isActive ? 'bg-blue-500' : 'bg-gray-300'
                              }`}
                              style={{
                                width: isCompleted ? '100%' :
                                       isActive ? `${((simulationMonth - startMonth) / procedure.duration) * 100}%` :
                                       '0%'
                              }}
                            />
                          </div>
                        </div>
                        {isCompleted && <span className="text-green-600">✓</span>}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* トースト通知 */}
      {showToast && (
        <div className="fixed bottom-4 right-4 z-50">
          <Toast
            message={showToast.message}
            type={showToast.type}
            onClose={() => setShowToast(null)}
          />
        </div>
      )}
    </div>
  );
};