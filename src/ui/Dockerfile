FROM node:18-alpine

WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm ci

# アプリケーションコードのコピー
COPY . .

# ポート公開
EXPOSE 3000

# 起動コマンド
CMD ["npm", "start"]