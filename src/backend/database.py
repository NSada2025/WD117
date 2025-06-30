from typing import Optional, Dict, List
import json
from pathlib import Path
from datetime import datetime
import sqlite3
from contextlib import contextmanager

from models import OrthodonticRecord


class DatabaseManager:
    """データベース管理クラス"""
    
    def __init__(self, db_path: str = "/mnt/d/multiagent-system/data/orthodontic.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """データベース接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """データベースを初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 患者テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    patient_name TEXT NOT NULL,
                    analysis_date TIMESTAMP NOT NULL,
                    data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 写真テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    photo_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_date TIMESTAMP NOT NULL,
                    analysis_data JSON,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                )
            """)
            
            # レントゲンテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS xrays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    xray_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_date TIMESTAMP NOT NULL,
                    cephalometric_tracing JSON,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                )
            """)
            
            # 模型分析テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    file_path TEXT,
                    upload_date TIMESTAMP NOT NULL,
                    measurements JSON,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                )
            """)
            
            # インデックスの作成
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_photos_patient ON photos(patient_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_xrays_patient ON xrays(patient_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_patient ON model_analysis(patient_id)")
            
            conn.commit()
    
    def import_existing_data(self, json_path: str = "/mnt/d/multiagent-system/orthodontic_clinical_analysis.json"):
        """既存のJSONデータをインポート"""
        json_file = Path(json_path)
        if not json_file.exists():
            return
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for record in data:
                # 既存データの確認
                cursor.execute("SELECT patient_id FROM patients WHERE patient_id = ?", (record["患者ID"],))
                if cursor.fetchone():
                    continue
                
                # データの挿入
                cursor.execute("""
                    INSERT INTO patients (patient_id, patient_name, analysis_date, data)
                    VALUES (?, ?, ?, ?)
                """, (
                    record["患者ID"],
                    record["患者氏名"],
                    record["分析日時"],
                    json.dumps(record, ensure_ascii=False)
                ))
            
            conn.commit()
    
    def save_patient(self, patient: OrthodonticRecord):
        """患者データを保存"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 患者データをJSON形式で保存
            patient_data = patient.model_dump(by_alias=True)
            patient_json = json.dumps(patient_data, ensure_ascii=False, default=str)
            
            cursor.execute("""
                INSERT OR REPLACE INTO patients (patient_id, patient_name, analysis_date, data, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                patient.patient_id,
                patient.patient_name,
                patient.analysis_date,
                patient_json
            ))
            
            conn.commit()
    
    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """患者データを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT data FROM patients WHERE patient_id = ?", (patient_id,))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row["data"])
            return None
    
    def get_all_patients(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """全患者データを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data FROM patients
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """, (limit, skip))
            
            rows = cursor.fetchall()
            return [json.loads(row["data"]) for row in rows]
    
    def delete_patient(self, patient_id: str):
        """患者データを削除"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 関連データの削除
            cursor.execute("DELETE FROM photos WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM xrays WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM model_analysis WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
            
            conn.commit()
    
    def save_photo(self, patient_id: str, photo_type: str, file_path: str, analysis_data: Optional[Dict] = None):
        """写真データを保存"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO photos (patient_id, photo_type, file_path, upload_date, analysis_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                patient_id,
                photo_type,
                file_path,
                datetime.now(),
                json.dumps(analysis_data) if analysis_data else None
            ))
            
            conn.commit()
    
    def save_xray(self, patient_id: str, xray_type: str, file_path: str, cephalometric_tracing: Optional[Dict] = None):
        """レントゲンデータを保存"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO xrays (patient_id, xray_type, file_path, upload_date, cephalometric_tracing)
                VALUES (?, ?, ?, ?, ?)
            """, (
                patient_id,
                xray_type,
                file_path,
                datetime.now(),
                json.dumps(cephalometric_tracing) if cephalometric_tracing else None
            ))
            
            conn.commit()
    
    def save_model_analysis(self, patient_id: str, model_type: str, file_path: Optional[str] = None, measurements: Optional[Dict] = None):
        """模型分析データを保存"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO model_analysis (patient_id, model_type, file_path, upload_date, measurements)
                VALUES (?, ?, ?, ?, ?)
            """, (
                patient_id,
                model_type,
                file_path,
                datetime.now(),
                json.dumps(measurements) if measurements else None
            ))
            
            conn.commit()
    
    def get_patient_photos(self, patient_id: str) -> List[Dict]:
        """患者の写真データを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM photos WHERE patient_id = ?
                ORDER BY upload_date DESC
            """, (patient_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_patient_xrays(self, patient_id: str) -> List[Dict]:
        """患者のレントゲンデータを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM xrays WHERE patient_id = ?
                ORDER BY upload_date DESC
            """, (patient_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_patient_models(self, patient_id: str) -> List[Dict]:
        """患者の模型データを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM model_analysis WHERE patient_id = ?
                ORDER BY upload_date DESC
            """, (patient_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]