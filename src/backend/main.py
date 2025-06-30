import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from models import (
    OrthodonticRecord, PatientListResponse, 
    AnalysisRequest, AnalysisResponse,
    PhotoData, XRayData, ModelAnalysis
)
from treatment_planner import TreatmentPlannerEngine, TreatmentPlan

app = FastAPI(
    title="矯正治療データ管理基盤API",
    description="顔面写真・レントゲン・口腔内写真・模型写真・セファロ分析・模型分析の統合管理システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データストレージ（実際の実装ではデータベースを使用）
DATA_DIR = Path("/mnt/d/multiagent-system/data")
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# 既存データの読み込み
def load_existing_data():
    """既存のorthodontic_clinical_analysis.jsonからデータを読み込む"""
    json_path = Path("/mnt/d/multiagent-system/orthodontic_clinical_analysis.json")
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# メモリ内データストア（実際の実装ではデータベースを使用）
orthodontic_records: Dict[str, OrthodonticRecord] = {}

# 初期データのロード
initial_data = load_existing_data()
for record in initial_data:
    try:
        # 日時文字列をdatetimeオブジェクトに変換
        if isinstance(record.get("分析日時"), str):
            record["分析日時"] = datetime.fromisoformat(record["分析日時"])
        orthodontic_record = OrthodonticRecord(**record)
        orthodontic_records[orthodontic_record.patient_id] = orthodontic_record
    except Exception as e:
        print(f"データ読み込みエラー: {e}")


@app.get("/", response_model=Dict[str, str])
async def root():
    """APIルートエンドポイント"""
    return {
        "message": "矯正治療データ管理基盤API",
        "version": "1.0.0",
        "endpoints": {
            "patients": "/patients",
            "patient_detail": "/patients/{patient_id}",
            "upload_photo": "/patients/{patient_id}/photos",
            "upload_xray": "/patients/{patient_id}/xrays",
            "upload_model": "/patients/{patient_id}/models",
            "analyze": "/analyze"
        }
    }


@app.get("/patients", response_model=PatientListResponse)
async def get_patients(
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数")
):
    """患者リストを取得"""
    patients_list = list(orthodontic_records.values())
    total = len(patients_list)
    
    # ページネーション
    patients_list = patients_list[skip:skip + limit]
    
    return PatientListResponse(
        total=total,
        patients=patients_list
    )


@app.get("/patients/{patient_id}", response_model=OrthodonticRecord)
async def get_patient(patient_id: str):
    """特定の患者情報を取得"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    return orthodontic_records[patient_id]


@app.post("/patients", response_model=OrthodonticRecord)
async def create_patient(patient: OrthodonticRecord):
    """新規患者を登録"""
    if patient.patient_id in orthodontic_records:
        raise HTTPException(status_code=400, detail="患者IDが既に存在します")
    
    orthodontic_records[patient.patient_id] = patient
    return patient


@app.put("/patients/{patient_id}", response_model=OrthodonticRecord)
async def update_patient(patient_id: str, patient: OrthodonticRecord):
    """患者情報を更新"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    # patient_idの整合性チェック
    if patient.patient_id != patient_id:
        raise HTTPException(status_code=400, detail="患者IDが一致しません")
    
    orthodontic_records[patient_id] = patient
    return patient


@app.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str):
    """患者情報を削除"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    del orthodontic_records[patient_id]
    return {"message": "患者情報を削除しました"}


@app.post("/patients/{patient_id}/photos")
async def upload_photo(
    patient_id: str,
    photo_type: str = Query(..., description="写真タイプ（facial/intraoral/model）"),
    file: UploadFile = File(..., description="アップロードする写真ファイル")
):
    """写真をアップロード"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    # ファイルの保存
    patient_dir = UPLOADS_DIR / patient_id / "photos" / photo_type
    patient_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = patient_dir / file.filename
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 写真データの記録
    photo_data = PhotoData(
        photo_type=photo_type,
        file_path=str(file_path),
        upload_date=datetime.now()
    )
    
    patient = orthodontic_records[patient_id]
    
    if photo_type == "facial":
        patient.facial_photos.append(photo_data)
    elif photo_type == "intraoral":
        patient.intraoral_photos.append(photo_data)
    elif photo_type == "model":
        patient.model_photos.append(photo_data)
    else:
        raise HTTPException(status_code=400, detail="無効な写真タイプです")
    
    return {"message": "写真をアップロードしました", "file_path": str(file_path)}


@app.post("/patients/{patient_id}/xrays")
async def upload_xray(
    patient_id: str,
    xray_type: str = Query(..., description="レントゲンタイプ（panoramic/cephalometric）"),
    file: UploadFile = File(..., description="アップロードするレントゲンファイル")
):
    """レントゲン画像をアップロード"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    # ファイルの保存
    patient_dir = UPLOADS_DIR / patient_id / "xrays"
    patient_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = patient_dir / file.filename
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # レントゲンデータの記録
    xray_data = XRayData(
        xray_type=xray_type,
        file_path=str(file_path),
        upload_date=datetime.now()
    )
    
    patient = orthodontic_records[patient_id]
    patient.xray_images.append(xray_data)
    
    return {"message": "レントゲン画像をアップロードしました", "file_path": str(file_path)}


@app.post("/patients/{patient_id}/models")
async def upload_model(
    patient_id: str,
    model_type: str = Query(..., description="模型タイプ（upper/lower/occlusion）"),
    file: UploadFile = File(..., description="アップロードする模型データファイル")
):
    """模型データをアップロード"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    # ファイルの保存
    patient_dir = UPLOADS_DIR / patient_id / "models"
    patient_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = patient_dir / file.filename
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 模型データの記録
    model_data = ModelAnalysis(
        model_type=model_type,
        file_path=str(file_path),
        upload_date=datetime.now()
    )
    
    patient = orthodontic_records[patient_id]
    patient.model_analysis.append(model_data)
    
    return {"message": "模型データをアップロードしました", "file_path": str(file_path)}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    """データ分析を実行"""
    if request.patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    # 分析タイプに応じた処理（実際の実装では各種分析アルゴリズムを実行）
    analysis_result = {
        "status": "completed",
        "analysis_type": request.analysis_type,
        "summary": f"{request.analysis_type}の分析が完了しました"
    }
    
    if request.analysis_type == "cephalometric":
        analysis_result["measurements"] = {
            "SNA": 82.0,
            "SNB": 78.0,
            "ANB": 4.0,
            "FMA": 25.0,
            "IMPA": 95.0
        }
    elif request.analysis_type == "model":
        analysis_result["measurements"] = {
            "overjet": 4.5,
            "overbite": 3.0,
            "arch_length_discrepancy": -6.0,
            "bolton_ratio": 91.5
        }
    
    return AnalysisResponse(
        patient_id=request.patient_id,
        analysis_type=request.analysis_type,
        result=analysis_result
    )


@app.get("/patients/{patient_id}/summary")
async def get_patient_summary(patient_id: str):
    """患者の総合サマリーを取得"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    patient = orthodontic_records[patient_id]
    
    summary = {
        "patient_id": patient.patient_id,
        "patient_name": patient.patient_name,
        "analysis_date": patient.analysis_date.isoformat(),
        "diagnosis": {
            "skeletal_class": patient.cephalometric_analysis.skeletal.skeletal_classification,
            "dental_class": patient.occlusion_relation.posterior.molar_relation,
            "growth_pattern": patient.jaw_relation.vertical.growth_pattern,
            "complexity": patient.treatment_difficulty.complexity_score,
            "prognosis": patient.treatment_difficulty.prognosis
        },
        "data_completeness": {
            "clinical_analysis": True,
            "facial_photos": len(patient.facial_photos),
            "intraoral_photos": len(patient.intraoral_photos),
            "xray_images": len(patient.xray_images),
            "model_photos": len(patient.model_photos),
            "model_analysis": len(patient.model_analysis)
        }
    }
    
    return summary


@app.get("/stats")
async def get_statistics():
    """システム統計情報を取得"""
    total_patients = len(orthodontic_records)
    
    skeletal_classes = {}
    dental_classes = {}
    complexity_scores = {}
    
    for patient in orthodontic_records.values():
        # 骨格型分類の集計
        skeletal_class = patient.cephalometric_analysis.skeletal.skeletal_classification
        if skeletal_class:
            skeletal_classes[skeletal_class] = skeletal_classes.get(skeletal_class, 0) + 1
        
        # 歯列分類の集計
        dental_class = patient.occlusion_relation.posterior.molar_relation
        if dental_class:
            dental_classes[dental_class] = dental_classes.get(dental_class, 0) + 1
        
        # 複雑度の集計
        complexity = patient.treatment_difficulty.complexity_score
        if complexity:
            complexity_scores[complexity] = complexity_scores.get(complexity, 0) + 1
    
    return {
        "total_patients": total_patients,
        "skeletal_classification": skeletal_classes,
        "dental_classification": dental_classes,
        "complexity_distribution": complexity_scores,
        "last_updated": datetime.now().isoformat()
    }


@app.post("/patients/{patient_id}/treatment-plan")
async def generate_treatment_plan(
    patient_id: str,
    patient_age: int = Query(..., description="患者の年齢"),
    occlusion_analysis: Optional[Dict[str, Any]] = None,
    preferences: Optional[Dict[str, Any]] = None
):
    """治療計画を生成"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    patient = orthodontic_records[patient_id]
    
    # 咬合分析結果がない場合はデフォルト値を使用
    if not occlusion_analysis:
        occlusion_analysis = {
            "midline_deviation": 0,
            "occlusal_plane_cant": 0,
            "bite_depth": "normal"
        }
    
    # 治療計画生成エンジンを使用
    planner = TreatmentPlannerEngine()
    treatment_plan = planner.generate_treatment_plan(
        patient=patient,
        occlusion_analysis=occlusion_analysis,
        patient_age=patient_age,
        patient_preferences=preferences
    )
    
    # JSON形式で返却
    return JSONResponse(
        content=json.loads(planner.export_treatment_plan(treatment_plan, format="json"))
    )


@app.get("/patients/{patient_id}/treatment-plan-report")
async def get_treatment_plan_report(
    patient_id: str,
    patient_age: int = Query(..., description="患者の年齢")
):
    """治療計画レポートを取得"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    patient = orthodontic_records[patient_id]
    
    # 治療計画を生成
    planner = TreatmentPlannerEngine()
    treatment_plan = planner.generate_treatment_plan(
        patient=patient,
        occlusion_analysis={},
        patient_age=patient_age
    )
    
    # レポート形式で返却
    report = planner.generate_treatment_report(treatment_plan)
    
    return {
        "patient_id": patient_id,
        "report": report,
        "generated_at": datetime.now().isoformat()
    }


@app.post("/treatment-simulation")
async def simulate_treatment(
    simulation_request: Dict[str, Any]
):
    """治療シミュレーションを実行"""
    patient_id = simulation_request.get("patient_id")
    if not patient_id or patient_id not in orthodontic_records:
        raise HTTPException(status_code=400, detail="有効な患者IDが必要です")
    
    patient = orthodontic_records[patient_id]
    patient_age = simulation_request.get("patient_age", 20)
    
    # 複数の治療オプションを生成
    planner = TreatmentPlannerEngine()
    options = []
    
    # オプション1: 非抜歯治療
    non_extraction_plan = planner.generate_treatment_plan(
        patient=patient,
        occlusion_analysis={},
        patient_age=patient_age,
        patient_preferences={"extraction_avoidance": True}
    )
    options.append({
        "option_name": "非抜歯治療",
        "plan": json.loads(planner.export_treatment_plan(non_extraction_plan, format="json"))
    })
    
    # オプション2: 抜歯治療
    extraction_plan = planner.generate_treatment_plan(
        patient=patient,
        occlusion_analysis={},
        patient_age=patient_age,
        patient_preferences={"extraction_acceptable": True}
    )
    options.append({
        "option_name": "抜歯治療",
        "plan": json.loads(planner.export_treatment_plan(extraction_plan, format="json"))
    })
    
    # オプション3: 審美重視
    aesthetic_plan = planner.generate_treatment_plan(
        patient=patient,
        occlusion_analysis={},
        patient_age=patient_age,
        patient_preferences={"aesthetic_priority": True}
    )
    options.append({
        "option_name": "審美重視治療",
        "plan": json.loads(planner.export_treatment_plan(aesthetic_plan, format="json"))
    })
    
    return {
        "patient_id": patient_id,
        "simulation_date": datetime.now().isoformat(),
        "treatment_options": options
    }


@app.get("/patients/{patient_id}/tooth-movements")
async def get_tooth_movements(
    patient_id: str,
    patient_age: int = Query(..., description="患者の年齢")
):
    """歯牙移動量を計算"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    patient = orthodontic_records[patient_id]
    
    # 治療計画を生成
    planner = TreatmentPlannerEngine()
    treatment_plan = planner.generate_treatment_plan(
        patient=patient,
        occlusion_analysis={},
        patient_age=patient_age
    )
    
    # 歯牙移動量を計算
    movements = planner.calculate_tooth_movements(patient, treatment_plan)
    
    # numpy配列をリストに変換
    if "tooth_vectors" in movements:
        movements["tooth_vectors"] = {
            tooth: vector.tolist() 
            for tooth, vector in movements["tooth_vectors"].items()
        }
    
    return {
        "patient_id": patient_id,
        "movements": movements,
        "calculated_at": datetime.now().isoformat()
    }


@app.get("/patients/{patient_id}/wire-sequence")
async def get_wire_sequence(
    patient_id: str,
    patient_age: int = Query(..., description="患者の年齢")
):
    """ワイヤーシークエンスを取得"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    patient = orthodontic_records[patient_id]
    
    # 治療計画を生成
    planner = TreatmentPlannerEngine()
    treatment_plan = planner.generate_treatment_plan(
        patient=patient,
        occlusion_analysis={},
        patient_age=patient_age
    )
    
    # ワイヤーシークエンスを計画
    wire_sequence = planner.wire_sequence_planner(
        treatment_plan.stages,
        treatment_plan.primary_appliance
    )
    
    return {
        "patient_id": patient_id,
        "appliance_type": treatment_plan.primary_appliance.value,
        "wire_sequence": wire_sequence,
        "total_duration_weeks": sum(w["duration_weeks"] for w in wire_sequence),
        "generated_at": datetime.now().isoformat()
    }


@app.post("/patients/{patient_id}/elastic-prescription")
async def get_elastic_prescription(
    patient_id: str,
    treatment_stage: str = Query(..., description="治療ステージ"),
    occlusion_analysis: Optional[Dict[str, Any]] = None
):
    """顎間ゴム処方を取得"""
    if patient_id not in orthodontic_records:
        raise HTTPException(status_code=404, detail="患者が見つかりません")
    
    patient = orthodontic_records[patient_id]
    
    # 顎間ゴム処方を生成
    planner = TreatmentPlannerEngine()
    prescription = planner.elastic_prescription(
        patient=patient,
        treatment_stage=treatment_stage,
        occlusion_analysis=occlusion_analysis
    )
    
    return {
        "patient_id": patient_id,
        "prescription": prescription,
        "prescribed_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)