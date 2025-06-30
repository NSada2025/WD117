from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DentalOcclusion(BaseModel):
    """前歯部咬合データモデル"""
    overjet: Optional[str] = Field(None, description="オーバージェット")
    overbite: Optional[str] = Field(None, description="オーバーバイト")
    anterior_coverage: Optional[str] = Field(None, description="前歯部被蓋")
    edge_bite: Optional[str] = Field(None, description="切端咬合")


class MolarRelation(BaseModel):
    """臼歯部咬合データモデル"""
    molar_relation: Optional[str] = Field(None, description="大臼歯関係")
    canine_relation: Optional[str] = Field(None, description="犬歯関係")
    cusp_interdigitation: Optional[str] = Field(None, description="咬頭嵌合")
    crossbite: Optional[str] = Field(None, description="交叉咬合")


class FunctionalOcclusion(BaseModel):
    """機能的咬合データモデル"""
    centric_occlusion: Optional[str] = Field(None, description="中心咬合位")
    lateral_movement: Optional[str] = Field(None, description="側方運動")
    anterior_movement: Optional[str] = Field(None, description="前方運動")
    tmj_symptoms: Optional[str] = Field(None, description="顎関節症状")


class OcclusionRelation(BaseModel):
    """咬合関係データモデル"""
    anterior: DentalOcclusion = Field(..., description="前歯部")
    posterior: MolarRelation = Field(..., description="臼歯部")
    functional: FunctionalOcclusion = Field(..., description="機能的咬合")


class DentalArch(BaseModel):
    """歯列データモデル"""
    arch_form: Optional[str] = Field(None, description="歯列弓形態")
    arch_width: Optional[str] = Field(None, description="歯列幅径")
    crowding: Optional[str] = Field(None, description="叢生量")
    space_analysis: Optional[str] = Field(None, description="スペース分析")
    midline: Optional[str] = Field(None, description="正中線")


class DentalStatus(BaseModel):
    """歯列状態データモデル"""
    upper_arch: DentalArch = Field(..., description="上顎歯列")
    lower_arch: DentalArch = Field(..., description="下顎歯列")
    individual_findings: List[str] = Field(default_factory=list, description="個別歯牙所見")


class SagittalAnalysis(BaseModel):
    """矢状面分析データモデル"""
    anb_angle: Optional[str] = Field(None, description="ANB角")
    wits_analysis: Optional[str] = Field(None, description="Wits分析")
    facial_angle: Optional[str] = Field(None, description="顔面角")
    sna_angle: Optional[str] = Field(None, description="SNA角")
    snb_angle: Optional[str] = Field(None, description="SNB角")


class VerticalAnalysis(BaseModel):
    """垂直面分析データモデル"""
    lower_facial_height: Optional[str] = Field(None, description="下顔面高")
    mandibular_plane_angle: Optional[str] = Field(None, description="下顎下縁平面角")
    y_axis: Optional[str] = Field(None, description="Y軸角")
    growth_pattern: Optional[str] = Field(None, description="成長パターン")


class JawRelation(BaseModel):
    """顎骨位置関係データモデル"""
    sagittal: SagittalAnalysis = Field(..., description="矢状面")
    vertical: VerticalAnalysis = Field(..., description="垂直面")
    maxillary_mandibular: Optional[str] = Field(None, description="上下顎関係")
    jaw_deviation: Optional[str] = Field(None, description="顎偏位")
    asymmetry: Optional[str] = Field(None, description="非対称性")


class SkeletalAnalysis(BaseModel):
    """骨格系分析データモデル"""
    skeletal_classification: Optional[str] = Field(None, description="骨格型分類")
    growth_prediction: Optional[str] = Field(None, description="成長予測")
    airway_evaluation: Optional[str] = Field(None, description="気道評価")


class DentalAnalysis(BaseModel):
    """歯系分析データモデル"""
    upper_incisor_inclination: Optional[str] = Field(None, description="上顎前歯傾斜")
    lower_incisor_inclination: Optional[str] = Field(None, description="下顎前歯傾斜")
    interincisal_angle: Optional[str] = Field(None, description="前歯軸角")


class SoftTissueAnalysis(BaseModel):
    """軟組織分析データモデル"""
    e_line: Optional[str] = Field(None, description="E-line")
    nasolabial_angle: Optional[str] = Field(None, description="鼻唇角")
    lip_position: Optional[str] = Field(None, description="口唇位置")


class CephalometricAnalysis(BaseModel):
    """セファロ分析データモデル"""
    skeletal: SkeletalAnalysis = Field(..., description="骨格系")
    dental: DentalAnalysis = Field(..., description="歯系")
    soft_tissue: SoftTissueAnalysis = Field(..., description="軟組織")


class TreatmentDifficulty(BaseModel):
    """治療難易度評価データモデル"""
    par_index: Optional[str] = Field(None, description="PAR指数")
    iotn: Optional[str] = Field(None, description="IOTN")
    complexity_score: Optional[str] = Field(None, description="複雑度スコア")
    prognosis: Optional[str] = Field(None, description="予後予測")


class PhotoData(BaseModel):
    """写真データモデル"""
    photo_type: str = Field(..., description="写真タイプ")
    file_path: Optional[str] = Field(None, description="ファイルパス")
    upload_date: datetime = Field(default_factory=datetime.now, description="アップロード日時")
    analysis_data: Optional[Dict[str, Any]] = Field(None, description="分析データ")


class XRayData(BaseModel):
    """レントゲンデータモデル"""
    xray_type: str = Field(..., description="レントゲンタイプ")
    file_path: Optional[str] = Field(None, description="ファイルパス")
    upload_date: datetime = Field(default_factory=datetime.now, description="アップロード日時")
    cephalometric_tracing: Optional[Dict[str, Any]] = Field(None, description="セファロトレース")


class ModelAnalysis(BaseModel):
    """模型分析データモデル"""
    model_type: str = Field(..., description="模型タイプ")
    file_path: Optional[str] = Field(None, description="ファイルパス")
    upload_date: datetime = Field(default_factory=datetime.now, description="アップロード日時")
    measurements: Optional[Dict[str, Any]] = Field(None, description="計測値")


class OrthodonticRecord(BaseModel):
    """矯正治療記録統合データモデル"""
    patient_id: str = Field(..., alias="患者ID", description="患者ID")
    patient_name: str = Field(..., alias="患者氏名", description="患者氏名")
    analysis_date: datetime = Field(..., alias="分析日時", description="分析日時")
    dental_status: DentalStatus = Field(..., alias="歯列状態", description="歯列状態")
    occlusion_relation: OcclusionRelation = Field(..., alias="咬合関係", description="咬合関係")
    jaw_relation: JawRelation = Field(..., alias="顎骨位置関係", description="顎骨位置関係")
    cephalometric_analysis: CephalometricAnalysis = Field(..., alias="セファロ分析", description="セファロ分析")
    treatment_difficulty: TreatmentDifficulty = Field(..., alias="治療難易度評価", description="治療難易度評価")
    
    # 追加の統合データ
    facial_photos: List[PhotoData] = Field(default_factory=list, description="顔面写真")
    intraoral_photos: List[PhotoData] = Field(default_factory=list, description="口腔内写真")
    xray_images: List[XRayData] = Field(default_factory=list, description="レントゲン画像")
    model_photos: List[PhotoData] = Field(default_factory=list, description="模型写真")
    model_analysis: List[ModelAnalysis] = Field(default_factory=list, description="模型分析")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PatientListResponse(BaseModel):
    """患者リスト応答モデル"""
    total: int = Field(..., description="総患者数")
    patients: List[OrthodonticRecord] = Field(..., description="患者リスト")


class AnalysisRequest(BaseModel):
    """分析リクエストモデル"""
    patient_id: str = Field(..., description="患者ID")
    analysis_type: str = Field(..., description="分析タイプ")
    data: Dict[str, Any] = Field(..., description="分析データ")


class AnalysisResponse(BaseModel):
    """分析応答モデル"""
    patient_id: str = Field(..., description="患者ID")
    analysis_type: str = Field(..., description="分析タイプ")
    result: Dict[str, Any] = Field(..., description="分析結果")
    timestamp: datetime = Field(default_factory=datetime.now, description="分析タイムスタンプ")