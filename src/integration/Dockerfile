FROM python:3.9-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー（統合モジュール全体）
COPY . .

# ポート公開
EXPOSE 8080

# 起動コマンド
CMD ["uvicorn", "integration.api.integration_api:app", "--host", "0.0.0.0", "--port", "8080"]