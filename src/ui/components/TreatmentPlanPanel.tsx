import React, { useState } from 'react';
import { TreatmentPlan, TreatmentProcedure, DetailedTreatmentPlan } from '../types';
import { DetailedTreatmentPlanView } from './DetailedTreatmentPlanView';

interface TreatmentPlanPanelProps {
  treatmentPlan: TreatmentPlan;
  onUpdate?: (plan: TreatmentPlan) => void;
}

export const TreatmentPlanPanel: React.FC<TreatmentPlanPanelProps> = ({
  treatmentPlan,
  onUpdate
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedPlan, setEditedPlan] = useState(treatmentPlan);
  const [showDetailedView, setShowDetailedView] = useState(false);

  // 詳細治療計画データがあるかチェック
  const isDetailedPlan = (plan: any): plan is DetailedTreatmentPlan => {
    return 'toothMovements' in plan && 'wireSequences' in plan && 'elasticConfigurations' in plan;
  };

  const handleProcedureToggle = (procedureId: string) => {
    const updatedProcedures = editedPlan.procedures.map(proc =>
      proc.id === procedureId ? { ...proc, completed: !proc.completed } : proc
    );
    
    const updatedPlan = { ...editedPlan, procedures: updatedProcedures };
    setEditedPlan(updatedPlan);
    
    if (!isEditing && onUpdate) {
      onUpdate(updatedPlan);
    }
  };

  const handleSave = () => {
    if (onUpdate) {
      onUpdate(editedPlan);
    }
    setIsEditing(false);
  };

  const getProgressPercentage = () => {
    const completedProcedures = treatmentPlan.procedures.filter(p => p.completed).length;
    return (completedProcedures / treatmentPlan.procedures.length) * 100;
  };

  const getStatusColor = (status: TreatmentPlan['status']) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-700';
      case 'approved': return 'bg-green-100 text-green-700';
      case 'in_progress': return 'bg-blue-100 text-blue-700';
      case 'completed': return 'bg-purple-100 text-purple-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* ビューモード切り替え */}
      {isDetailedPlan(treatmentPlan) && (
        <div className="bg-white border-b p-3">
          <div className="flex gap-2">
            <button
              onClick={() => setShowDetailedView(false)}
              className={`px-4 py-2 rounded ${
                !showDetailedView ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              概要ビュー
            </button>
            <button
              onClick={() => setShowDetailedView(true)}
              className={`px-4 py-2 rounded ${
                showDetailedView ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              詳細ビュー
            </button>
          </div>
        </div>
      )}

      {/* メインコンテンツ */}
      {showDetailedView && isDetailedPlan(treatmentPlan) ? (
        <div className="flex-1">
          <DetailedTreatmentPlanView
            treatmentPlan={treatmentPlan}
            onUpdate={onUpdate as ((plan: DetailedTreatmentPlan) => void)}
            isEditable={!isEditing}
          />
        </div>
      ) : (
        <div className="flex-1 flex">
          {/* Plan Overview */}
          <div className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold mb-2">治療計画</h2>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>作成日: {new Date(treatmentPlan.createdDate).toLocaleDateString()}</span>
                  <span>最終更新: {new Date(treatmentPlan.modifiedDate).toLocaleDateString()}</span>
                  <span>担当医: {treatmentPlan.orthodontist}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(treatmentPlan.status)}`}>
                  {treatmentPlan.status === 'draft' && '下書き'}
                  {treatmentPlan.status === 'approved' && '承認済み'}
                  {treatmentPlan.status === 'in_progress' && '進行中'}
                  {treatmentPlan.status === 'completed' && '完了'}
                </span>
                {!isEditing && (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    編集
                  </button>
                )}
                {isEditing && (
                  <>
                    <button
                      onClick={handleSave}
                      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      保存
                    </button>
                    <button
                      onClick={() => {
                        setEditedPlan(treatmentPlan);
                        setIsEditing(false);
                      }}
                      className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                    >
                      キャンセル
                    </button>
                  </>
                )}
              </div>
            </div>

            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">進捗状況</span>
                <span className="text-sm text-gray-600">{Math.round(getProgressPercentage())}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-500 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${getProgressPercentage()}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <h3 className="font-semibold mb-2">推定治療期間</h3>
                <p className="text-2xl font-bold text-blue-600">{treatmentPlan.estimatedDuration}ヶ月</p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">治療目標</h3>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {(isEditing ? editedPlan : treatmentPlan).objectives.map((objective, index) => (
                    <li key={index}>{objective}</li>
                  ))}
                </ul>
              </div>
            </div>

            {treatmentPlan.notes && (
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-semibold mb-2">備考</h3>
                <p className="text-gray-700">{treatmentPlan.notes}</p>
              </div>
            )}
          </div>

          {/* Treatment Procedures */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">治療手順</h3>
            <div className="space-y-3">
              {(isEditing ? editedPlan : treatmentPlan).procedures
                .sort((a, b) => a.sequence - b.sequence)
                .map(procedure => (
                  <div
                    key={procedure.id}
                    className={`border rounded-lg p-4 ${
                      procedure.completed ? 'bg-green-50 border-green-300' : 'bg-white border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <input
                          type="checkbox"
                          checked={procedure.completed}
                          onChange={() => handleProcedureToggle(procedure.id)}
                          className="mt-1 w-5 h-5 text-blue-600 rounded"
                        />
                        <div>
                          <h4 className="font-semibold">
                            {procedure.sequence}. {procedure.type === 'extraction' && '抜歯'}
                            {procedure.type === 'expansion' && '拡大'}
                            {procedure.type === 'alignment' && '配列'}
                            {procedure.type === 'retention' && '保定'}
                          </h4>
                          <p className="text-gray-700 mt-1">{procedure.description}</p>
                          <p className="text-sm text-gray-500 mt-2">
                            推定期間: {procedure.duration}ヶ月
                          </p>
                        </div>
                      </div>
                      {procedure.completed && (
                        <span className="text-green-600 text-sm font-medium">完了</span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>

      {/* Side Panel - Quick Actions */}
      <div className="w-80 bg-gray-50 p-6 border-l">
        <h3 className="font-semibold mb-4">クイックアクション</h3>
        <div className="space-y-3">
          <button className="w-full px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 text-left">
            📄 治療計画書をPDF出力
          </button>
          <button className="w-full px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 text-left">
            📧 患者に送信
          </button>
          <button className="w-full px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 text-left">
            📋 コピーを作成
          </button>
          <button className="w-full px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 text-left">
            🗓️ 予約スケジュール確認
          </button>
          {isDetailedPlan(treatmentPlan) && !showDetailedView && (
            <button 
              onClick={() => setShowDetailedView(true)}
              className="w-full px-4 py-2 bg-blue-100 border border-blue-300 rounded hover:bg-blue-200 text-left text-blue-700"
            >
              🔬 詳細分析ビューを開く
            </button>
          )}
        </div>

        <div className="mt-8">
          <h3 className="font-semibold mb-4">治療経過メモ</h3>
          <div className="bg-white rounded p-4 h-64 overflow-y-auto">
            <p className="text-gray-500 text-sm">最新のメモがここに表示されます</p>
          </div>
        </div>
      </div>
        </div>
      )}
    </div>
  );
};