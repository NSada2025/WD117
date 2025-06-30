#!/usr/bin/env python3
"""
統合API
全モジュールを統合した統一APIインターフェース
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

# プロジェクトのルートパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

# コネクタのインポート
from integration.connectors.backend_connector import BackendConnector
from integration.connectors.analysis_connector import AnalysisConnector


# リクエスト/レスポンスモデル
class AnalysisRequest(BaseModel):
    """統合分析リクエスト"""
    patient_id: str
    age: int
    gender: str = "不明"
    chief_complaint: str
    measurements: Dict[str, Any]
    preferences: Optional[Dict[str, Any]] = None
    medical_history: Optional[List[str]] = []
    dental_history: Optional[List[str]] = []


class SystemStatus(BaseModel):
    """システムステータス"""
    status: str
    timestamp: str
    services: Dict[str, bool]
    version: str = "1.0.0"


# FastAPIアプリケーションの初期化
app = FastAPI(
    title="矯正治療統合システムAPI",
    description="咬合分析と治療計画を統合した包括的な矯正治療支援システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバルコネクタ
backend_connector = BackendConnector()
analysis_connector = AnalysisConnector()

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """起動時の初期化"""
    logger.info("統合APIサーバーを起動しています...")
    
    # 各サービスの接続確認
    connection_status = analysis_connector.validate_connection()
    logger.info(f"サービス接続状態: {connection_status}")


@app.on_event("shutdown")
async def shutdown_event():
    """シャットダウン時のクリーンアップ"""
    logger.info("統合APIサーバーをシャットダウンしています...")
    backend_connector.close()


# ヘルスチェックエンドポイント
@app.get("/", response_model=SystemStatus)
async def root():
    """システムステータスを返す"""
    services = {
        "backend": backend_connector.health_check(),
        "occlusion_analyzer": True,
        "treatment_planner": True,
        "integration": True
    }
    
    return SystemStatus(
        status="operational" if all(services.values()) else "degraded",
        timestamp=datetime.now().isoformat(),
        services=services
    )


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


# 統合分析エンドポイント
@app.post("/api/v1/integrated-analysis")
async def integrated_analysis(request: AnalysisRequest):
    """
    統合分析を実行
    咬合分析と治療計画を一括で生成
    """
    try:
        logger.info(f"統合分析を開始: 患者ID {request.patient_id}")
        
        # 患者データの準備
        patient_data = request.dict()
        
        # 統合分析の実行
        result = analysis_connector.analyze_and_plan(patient_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info(f"統合分析完了: 患者ID {request.patient_id}")
        return result
        
    except Exception as e:
        logger.error(f"統合分析エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 患者管理エンドポイント（バックエンドへのプロキシ）
@app.get("/api/v1/patients")
async def get_patients(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    """患者リストを取得"""
    result = backend_connector.get_patients(skip, limit)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@app.get("/api/v1/patients/{patient_id}")
async def get_patient(patient_id: str):
    """特定患者の詳細情報を取得"""
    result = backend_connector.get_patient(patient_id)
    if "error" in result:
        if result.get("status_code") == 404:
            raise HTTPException(status_code=404, detail="患者が見つかりません")
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@app.post("/api/v1/patients")
async def create_patient(patient_data: Dict[str, Any]):
    """新規患者を登録"""
    result = backend_connector.create_patient(patient_data)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@app.put("/api/v1/patients/{patient_id}")
async def update_patient(patient_id: str, patient_data: Dict[str, Any]):
    """患者情報を更新"""
    result = backend_connector.update_patient(patient_id, patient_data)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


# ファイルアップロードエンドポイント
@app.post("/api/v1/patients/{patient_id}/photos")
async def upload_photo(patient_id: str, photo_type: str, file: UploadFile = File(...)):
    """写真をアップロード"""
    try:
        # 一時ファイルに保存
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # バックエンドにアップロード
        result = backend_connector.upload_photo(patient_id, photo_type, temp_path)
        
        # 一時ファイルを削除
        os.remove(temp_path)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
        
    except Exception as e:
        logger.error(f"写真アップロードエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/patients/{patient_id}/xrays")
async def upload_xray(patient_id: str, xray_type: str, file: UploadFile = File(...)):
    """レントゲン画像をアップロード"""
    try:
        # 一時ファイルに保存
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # バックエンドにアップロード
        result = backend_connector.upload_xray(patient_id, xray_type, temp_path)
        
        # 一時ファイルを削除
        os.remove(temp_path)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
        
    except Exception as e:
        logger.error(f"レントゲンアップロードエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 個別分析エンドポイント
@app.post("/api/v1/analyze")
async def analyze_data(analysis_request: Dict[str, Any]):
    """データ分析を実行"""
    patient_id = analysis_request.get("patient_id")
    analysis_type = analysis_request.get("analysis_type")
    data = analysis_request.get("data", {})
    
    result = backend_connector.analyze_data(patient_id, analysis_type, data)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@app.get("/api/v1/patients/{patient_id}/summary")
async def get_patient_summary(patient_id: str):
    """患者の総合サマリーを取得"""
    result = backend_connector.get_patient_summary(patient_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


# 治療計画エンドポイント
@app.post("/api/v1/patients/{patient_id}/treatment-plan")
async def generate_treatment_plan(
    patient_id: str,
    patient_age: int = Query(..., description="患者の年齢"),
    occlusion_analysis: Optional[str] = Query(None, description="咬合分析結果（JSON形式）"),
    preferences: Optional[str] = Query(None, description="患者の希望（JSON形式）")
):
    """治療計画を生成"""
    import json
    
    # JSON文字列をパース
    occlusion_data = json.loads(occlusion_analysis) if occlusion_analysis else None
    preferences_data = json.loads(preferences) if preferences else None
    
    result = backend_connector.generate_treatment_plan(
        patient_id, patient_age, occlusion_data, preferences_data
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


# 統合システム情報
@app.get("/api/v1/system/info")
async def get_system_info():
    """システム情報を取得"""
    return {
        "name": "矯正治療統合システム",
        "version": "1.0.0",
        "components": {
            "ui": "React/TypeScript",
            "backend": "FastAPI/Python",
            "occlusion_analyzer": "Python/NumPy",
            "treatment_planner": "Python",
            "integration": "Python/FastAPI"
        },
        "features": [
            "咬合分析",
            "治療計画生成",
            "患者管理",
            "画像管理",
            "統合分析"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)