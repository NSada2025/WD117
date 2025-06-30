#!/usr/bin/env python3
"""
バックエンドAPIコネクタ
UIとバックエンドの通信を管理
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class ConnectionConfig:
    """接続設定"""
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 0.3


class BackendConnector:
    """バックエンドAPIコネクタ"""
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        """初期化"""
        self.config = config or ConnectionConfig()
        self.logger = logging.getLogger(__name__)
        
        # セッション設定
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _build_url(self, endpoint: str) -> str:
        """完全なURLを構築"""
        return f"{self.config.backend_url}{endpoint}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """レスポンスを処理"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            return {"error": str(e), "status_code": response.status_code}
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return {"error": "Invalid JSON response"}
    
    # 患者管理API
    
    def get_patients(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """患者リストを取得"""
        endpoint = f"/patients?skip={skip}&limit={limit}"
        try:
            response = self.session.get(
                self._build_url(endpoint),
                timeout=self.config.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
    
    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """特定患者の詳細情報を取得"""
        endpoint = f"/patients/{patient_id}"
        try:
            response = self.session.get(
                self._build_url(endpoint),
                timeout=self.config.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
    
    def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """新規患者を登録"""
        endpoint = "/patients"
        try:
            response = self.session.post(
                self._build_url(endpoint),
                json=patient_data,
                timeout=self.config.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
    
    def update_patient(self, patient_id: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """患者情報を更新"""
        endpoint = f"/patients/{patient_id}"
        try:
            response = self.session.put(
                self._build_url(endpoint),
                json=patient_data,
                timeout=self.config.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
    
    # 分析API
    
    def analyze_data(self, patient_id: str, analysis_type: str, 
                    data: Dict[str, Any]) -> Dict[str, Any]:
        """データ分析を実行"""
        endpoint = "/analyze"
        request_data = {
            "patient_id": patient_id,
            "analysis_type": analysis_type,
            "data": data
        }
        try:
            response = self.session.post(
                self._build_url(endpoint),
                json=request_data,
                timeout=self.config.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
    
    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """患者の総合サマリーを取得"""
        endpoint = f"/patients/{patient_id}/summary"
        try:
            response = self.session.get(
                self._build_url(endpoint),
                timeout=self.config.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
    
    # 治療計画API
    
    def generate_treatment_plan(self, patient_id: str, patient_age: int,
                              occlusion_analysis: Optional[Dict[str, Any]] = None,
                              preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """治療計画を生成"""
        endpoint = f"/patients/{patient_id}/treatment-plan"
        params = {"patient_age": patient_age}
        
        if occlusion_analysis:
            params["occlusion_analysis"] = json.dumps(occlusion_analysis)
        if preferences:
            params["preferences"] = json.dumps(preferences)
        
        try:
            response = self.session.post(
                self._build_url(endpoint),
                params=params,
                timeout=self.config.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
    
    # ファイルアップロードAPI
    
    def upload_photo(self, patient_id: str, photo_type: str, 
                    file_path: str) -> Dict[str, Any]:
        """写真をアップロード"""
        endpoint = f"/patients/{patient_id}/photos"
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'photo_type': photo_type}
                response = self.session.post(
                    self._build_url(endpoint),
                    files=files,
                    data=data,
                    timeout=self.config.timeout
                )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
        except IOError as e:
            self.logger.error(f"File error: {e}")
            return {"error": str(e)}
    
    def upload_xray(self, patient_id: str, xray_type: str,
                   file_path: str) -> Dict[str, Any]:
        """レントゲン画像をアップロード"""
        endpoint = f"/patients/{patient_id}/xrays"
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'xray_type': xray_type}
                response = self.session.post(
                    self._build_url(endpoint),
                    files=files,
                    data=data,
                    timeout=self.config.timeout
                )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"error": str(e)}
        except IOError as e:
            self.logger.error(f"File error: {e}")
            return {"error": str(e)}
    
    # ヘルスチェック
    
    def health_check(self) -> bool:
        """バックエンドのヘルスチェック"""
        try:
            response = self.session.get(
                self._build_url("/health"),
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def close(self):
        """セッションを閉じる"""
        self.session.close()


# 使用例
if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(level=logging.INFO)
    
    # コネクタ初期化
    connector = BackendConnector()
    
    # ヘルスチェック
    if connector.health_check():
        print("バックエンドは正常に動作しています")
    else:
        print("バックエンドに接続できません")
    
    # 患者リスト取得
    patients = connector.get_patients()
    print(f"患者リスト: {patients}")
    
    # クリーンアップ
    connector.close()