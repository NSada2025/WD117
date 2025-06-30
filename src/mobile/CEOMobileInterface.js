/**
 * CEO専用モバイルインターフェース
 * スマホでの直感的操作に最適化
 */

class CEOMobileInterface {
  constructor() {
    this.voiceProcessor = new VoiceCommandProcessor();
    this.projectTemplates = this.initializeProjectTemplates();
    this.currentSession = null;
    this.isListening = false;
    this.stabilityMonitor = new MobileStabilityMonitor();
    
    this.initializeInterface();
    this.setupEventListeners();
    this.setupStabilityFeatures();
  }

  /**
   * インターフェース初期化
   */
  initializeInterface() {
    this.createMobileLayout();
    this.setupTouchOptimization();
    this.initializeVoiceInterface();
  }

  /**
   * モバイルレイアウト作成
   */
  createMobileLayout() {
    const container = document.createElement('div');
    container.className = 'ceo-mobile-dashboard';
    container.innerHTML = `
      <!-- ヘッダー -->
      <header class="mobile-header">
        <h1 class="dashboard-title">CEO Dashboard</h1>
        <div class="status-indicator">
          <span class="connection-status" id="connectionStatus">🟢 接続中</span>
        </div>
      </header>

      <!-- クイックアクション -->
      <section class="quick-actions">
        <button class="action-btn urgent" data-action="emergency_meeting">
          <span class="icon">🚨</span>
          <span class="label">緊急</span>
        </button>
        <button class="action-btn normal" data-action="status_check">
          <span class="icon">📊</span>
          <span class="label">状況</span>
        </button>
        <button class="action-btn create" data-action="new_project">
          <span class="icon">➕</span>
          <span class="label">新規</span>
        </button>
        <button class="action-btn voice" id="voiceCommand">
          <span class="icon">🎤</span>
          <span class="label">音声</span>
        </button>
      </section>

      <!-- プロジェクト状況カード -->
      <section class="project-cards-container" id="projectCards">
        <div class="project-card active">
          <div class="card-header">
            <h3>CEO-Manager連携強化</h3>
            <span class="priority high">高優先度</span>
          </div>
          <div class="progress-section">
            <div class="progress-bar">
              <div class="progress" style="width: 75%"></div>
            </div>
            <span class="progress-text">75% Complete</span>
          </div>
          <div class="card-footer">
            <span class="eta">ETA: 2日</span>
            <button class="detail-btn">詳細</button>
          </div>
        </div>
      </section>

      <!-- 音声入力エリア -->
      <section class="voice-input-section" id="voiceSection" style="display: none;">
        <div class="voice-animation">
          <div class="voice-wave"></div>
          <div class="voice-wave"></div>
          <div class="voice-wave"></div>
        </div>
        <p class="voice-prompt">何かご指示はありますか？</p>
        <button class="stop-listening" id="stopListening">停止</button>
      </section>

      <!-- 通知エリア -->
      <section class="notification-area" id="notifications">
        <!-- 動的に通知が表示される -->
      </section>

      <!-- フローティングメニュー -->
      <div class="floating-menu" id="floatingMenu">
        <button class="fab-main" id="fabMain">⚙️</button>
        <div class="fab-options" id="fabOptions" style="display: none;">
          <button class="fab-option" data-action="settings">設定</button>
          <button class="fab-option" data-action="team_status">チーム</button>
          <button class="fab-option" data-action="analytics">分析</button>
        </div>
      </div>
    `;

    document.body.appendChild(container);
    this.addMobileCSS();
  }

  /**
   * モバイル用CSS追加
   */
  addMobileCSS() {
    const style = document.createElement('style');
    style.textContent = `
      .ceo-mobile-dashboard {
        width: 100%;
        max-width: 100vw;
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        overflow-x: hidden;
      }

      .mobile-header {
        padding: 20px 16px 16px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
      }

      .dashboard-title {
        color: white;
        margin: 0;
        font-size: 24px;
        font-weight: 600;
      }

      .connection-status {
        color: rgba(255, 255, 255, 0.9);
        font-size: 14px;
      }

      .quick-actions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        padding: 24px 16px;
      }

      .action-btn {
        background: rgba(255, 255, 255, 0.95);
        border: none;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      }

      .action-btn:active {
        transform: scale(0.95);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
      }

      .action-btn.urgent {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
      }

      .action-btn.voice.listening {
        background: linear-gradient(135deg, #4ecdc4, #44a08d);
        color: white;
        animation: pulse 1.5s infinite;
      }

      .action-btn .icon {
        font-size: 24px;
        margin-bottom: 8px;
      }

      .action-btn .label {
        font-size: 14px;
        font-weight: 500;
      }

      .project-cards-container {
        padding: 0 16px;
        max-height: 40vh;
        overflow-y: auto;
      }

      .project-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
      }

      .card-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #2c3e50;
      }

      .priority {
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
      }

      .priority.high {
        background: #ff6b6b;
        color: white;
      }

      .progress-section {
        margin-bottom: 16px;
      }

      .progress-bar {
        width: 100%;
        height: 8px;
        background: #ecf0f1;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 8px;
      }

      .progress {
        height: 100%;
        background: linear-gradient(90deg, #4ecdc4, #44a08d);
        transition: width 0.3s ease;
      }

      .progress-text {
        font-size: 14px;
        color: #7f8c8d;
      }

      .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .eta {
        font-size: 14px;
        color: #7f8c8d;
      }

      .detail-btn {
        background: #3498db;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 14px;
        cursor: pointer;
      }

      .voice-input-section {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.9);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        z-index: 1000;
      }

      .voice-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
      }

      .voice-wave {
        width: 4px;
        height: 40px;
        background: #4ecdc4;
        margin: 0 2px;
        border-radius: 2px;
        animation: wave 1s infinite;
      }

      .voice-wave:nth-child(2) {
        animation-delay: 0.1s;
      }

      .voice-wave:nth-child(3) {
        animation-delay: 0.2s;
      }

      .voice-prompt {
        color: white;
        font-size: 18px;
        margin-bottom: 20px;
      }

      .stop-listening {
        background: #e74c3c;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        cursor: pointer;
      }

      .floating-menu {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 999;
      }

      .fab-main {
        width: 56px;
        height: 56px;
        border-radius: 28px;
        background: #3498db;
        border: none;
        color: white;
        font-size: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        cursor: pointer;
        transition: all 0.3s ease;
      }

      .fab-main:active {
        transform: scale(0.9);
      }

      .fab-options {
        position: absolute;
        bottom: 70px;
        right: 0;
        background: white;
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
      }

      .fab-option {
        display: block;
        width: 100%;
        padding: 12px 16px;
        background: none;
        border: none;
        text-align: left;
        font-size: 14px;
        cursor: pointer;
        border-radius: 8px;
        margin: 2px 0;
      }

      .fab-option:hover {
        background: #f8f9fa;
      }

      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
      }

      @keyframes wave {
        0%, 100% { height: 20px; }
        50% { height: 60px; }
      }

      .notification-area {
        position: fixed;
        top: 80px;
        left: 16px;
        right: 16px;
        z-index: 998;
      }

      .notification {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease;
      }

      @keyframes slideIn {
        from { transform: translateY(-100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }

      /* タッチ最適化 */
      @media (max-width: 768px) {
        .action-btn {
          min-height: 70px;
          padding: 16px;
        }
        
        .project-card {
          padding: 16px;
        }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * イベントリスナー設定
   */
  setupEventListeners() {
    // クイックアクションボタン
    document.querySelectorAll('.action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = e.currentTarget.dataset.action;
        this.handleQuickAction(action);
      });
    });

    // 音声コマンドボタン
    const voiceBtn = document.getElementById('voiceCommand');
    voiceBtn.addEventListener('click', () => {
      this.toggleVoiceInput();
    });

    // フローティングメニュー
    const fabMain = document.getElementById('fabMain');
    const fabOptions = document.getElementById('fabOptions');
    
    fabMain.addEventListener('click', () => {
      fabOptions.style.display = fabOptions.style.display === 'none' ? 'block' : 'none';
    });

    // タッチジェスチャー
    this.setupTouchGestures();
  }

  /**
   * クイックアクション処理
   * @param {string} action 
   */
  handleQuickAction(action) {
    switch(action) {
      case 'emergency_meeting':
        this.triggerEmergencyResponse();
        break;
      case 'status_check':
        this.requestStatusUpdate();
        break;
      case 'new_project':
        this.showProjectTemplates();
        break;
      default:
        console.log(`Unknown action: ${action}`);
    }
  }

  /**
   * 緊急対応トリガー
   */
  triggerEmergencyResponse() {
    this.showNotification('🚨 緊急対応モードを開始', 'urgent');
    
    // Managerに緊急対応指示を送信
    this.sendToManager({
      type: 'emergency',
      priority: 'urgent',
      instruction: '緊急対応が必要です。現在の状況を即座に報告し、対応策を提案してください。',
      timestamp: new Date().toISOString()
    });
  }

  /**
   * 状況確認要求
   */
  requestStatusUpdate() {
    this.showNotification('📊 状況確認中...', 'info');
    
    this.sendToManager({
      type: 'status_request',
      priority: 'high',
      instruction: 'プロジェクト全体の現在状況を報告してください',
      timestamp: new Date().toISOString()
    });
  }

  /**
   * プロジェクトテンプレート表示
   */
  showProjectTemplates() {
    const templates = Object.values(this.projectTemplates);
    const templateHTML = templates.map(template => `
      <div class="template-card" data-template="${template.id}">
        <h4>${template.name}</h4>
        <p>期間: ${template.estimatedTime}</p>
        <p>チーム: ${template.team.join(', ')}</p>
      </div>
    `).join('');

    this.showModal('新規プロジェクト', templateHTML);
  }

  /**
   * 音声入力切り替え
   */
  toggleVoiceInput() {
    if (this.isListening) {
      this.stopVoiceInput();
    } else {
      this.startVoiceInput();
    }
  }

  /**
   * 音声入力開始
   */
  startVoiceInput() {
    this.isListening = true;
    document.getElementById('voiceSection').style.display = 'block';
    document.getElementById('voiceCommand').classList.add('listening');
    
    this.voiceProcessor.startListening((command) => {
      this.processVoiceCommand(command);
    });
  }

  /**
   * 音声入力停止
   */
  stopVoiceInput() {
    this.isListening = false;
    document.getElementById('voiceSection').style.display = 'none';
    document.getElementById('voiceCommand').classList.remove('listening');
    
    this.voiceProcessor.stopListening();
  }

  /**
   * 音声コマンド処理
   * @param {string} command 
   */
  processVoiceCommand(command) {
    this.showNotification(`🎤 "${command}"`, 'info');
    
    this.sendToManager({
      type: 'voice_instruction',
      priority: 'normal',
      instruction: command,
      timestamp: new Date().toISOString()
    });
    
    this.stopVoiceInput();
  }

  /**
   * 通知表示
   * @param {string} message 
   * @param {string} type 
   */
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.getElementById('notifications').appendChild(notification);
    
    // 3秒後に自動削除
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  /**
   * モーダル表示
   * @param {string} title 
   * @param {string} content 
   */
  showModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>${title}</h3>
          <button class="close-modal">×</button>
        </div>
        <div class="modal-body">
          ${content}
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('.close-modal').addEventListener('click', () => {
      modal.remove();
    });
  }

  /**
   * Managerに指示送信
   * @param {Object} instruction 
   */
  sendToManager(instruction) {
    // 実際の実装では、WebSocketまたはHTTP APIを使用
    console.log('Sending to Manager:', instruction);
    
    // シミュレーション: 2秒後にレスポンス
    setTimeout(() => {
      this.receiveFromManager({
        type: 'response',
        message: `指示を受信しました: ${instruction.instruction}`,
        timestamp: new Date().toISOString()
      });
    }, 2000);
  }

  /**
   * Managerからのレスポンス受信
   * @param {Object} response 
   */
  receiveFromManager(response) {
    this.showNotification(`Manager: ${response.message}`, 'success');
  }

  /**
   * プロジェクトテンプレート初期化
   * @returns {Object} テンプレート定義
   */
  initializeProjectTemplates() {
    return {
      web_app: {
        id: "web_app",
        name: "Webアプリケーション開発",
        estimatedTime: "2-4週間",
        team: ["dev1", "dev2"],
        phases: ["設計", "開発", "テスト", "デプロイ"]
      },
      data_analysis: {
        id: "data_analysis",
        name: "データ分析プロジェクト",
        estimatedTime: "1-2週間",
        team: ["dev2", "dev1"],
        phases: ["データ収集", "分析", "可視化", "レポート"]
      },
      infrastructure: {
        id: "infrastructure",
        name: "インフラ構築・改善",
        estimatedTime: "1-3週間",
        team: ["dev3", "dev1"],
        phases: ["要件定義", "設計", "構築", "テスト"]
      }
    };
  }

  /**
   * タッチジェスチャー設定
   */
  setupTouchGestures() {
    // プロジェクトカードのスワイプ
    const projectContainer = document.getElementById('projectCards');
    let startX, startY, currentX, currentY;
    
    projectContainer.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    });
    
    projectContainer.addEventListener('touchmove', (e) => {
      currentX = e.touches[0].clientX;
      currentY = e.touches[0].clientY;
    });
    
    projectContainer.addEventListener('touchend', () => {
      const diffX = currentX - startX;
      const diffY = currentY - startY;
      
      // 横スワイプでプロジェクト切り替え
      if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
        if (diffX > 0) {
          this.showPreviousProject();
        } else {
          this.showNextProject();
        }
      }
    });
  }

  /**
   * タッチ最適化設定
   */
  setupTouchOptimization() {
    // ダブルタップズーム無効化
    document.addEventListener('touchstart', (e) => {
      if (e.touches.length > 1) {
        e.preventDefault();
      }
    });
    
    // クリック遅延解消
    document.addEventListener('touchend', (e) => {
      e.preventDefault();
      const touch = e.changedTouches[0];
      const element = document.elementFromPoint(touch.clientX, touch.clientY);
      if (element && element.click) {
        element.click();
      }
    });
  }

  /**
   * 前のプロジェクト表示
   */
  showPreviousProject() {
    console.log('Previous project');
    // 実装: プロジェクト切り替えロジック
  }

  /**
   * 次のプロジェクト表示
   */
  showNextProject() {
    console.log('Next project');
    // 実装: プロジェクト切り替えロジック
  }

  /**
   * 安定性機能設定
   */
  setupStabilityFeatures() {
    // 自動再接続
    this.enableAutoReconnect();
    
    // オフライン対応
    this.enableOfflineSupport();
    
    // パフォーマンス監視
    this.enablePerformanceMonitoring();
    
    console.log('🛡️ モバイル安定性機能を有効化');
  }

  /**
   * 自動再接続機能
   */
  enableAutoReconnect() {
    let reconnectAttempts = 0;
    const maxAttempts = 5;
    
    this.connectionMonitor = setInterval(() => {
      if (!this.isConnected() && reconnectAttempts < maxAttempts) {
        console.log('🔄 再接続試行中...');
        this.attemptReconnect();
        reconnectAttempts++;
      }
    }, 5000);
  }

  /**
   * オフライン対応
   */
  enableOfflineSupport() {
    // オフライン検知
    window.addEventListener('offline', () => {
      this.showNotification('📡 オフラインモード', 'warning');
      this.enableOfflineMode();
    });
    
    // オンライン復帰
    window.addEventListener('online', () => {
      this.showNotification('✅ オンライン復帰', 'success');
      this.syncOfflineData();
    });
  }

  /**
   * パフォーマンス監視
   */
  enablePerformanceMonitoring() {
    this.stabilityMonitor.startMonitoring((metrics) => {
      if (metrics.responseTime > 3000) {
        this.optimizePerformance();
      }
      
      if (metrics.memoryUsage > 0.8) {
        this.clearUnusedResources();
      }
    });
  }

  /**
   * パフォーマンス最適化
   */
  optimizePerformance() {
    // アニメーション簡略化
    document.querySelectorAll('.voice-wave').forEach(el => {
      el.style.animation = 'none';
    });
    
    // 不要な要素削除
    this.removeOldNotifications();
    
    console.log('⚡ パフォーマンス最適化実行');
  }

  /**
   * 未使用リソースクリア
   */
  clearUnusedResources() {
    // 古い通知削除
    this.removeOldNotifications();
    
    // キャッシュクリア
    this.clearProjectCache();
    
    console.log('🧹 リソースクリーンアップ完了');
  }

  /**
   * オフラインモード有効化
   */
  enableOfflineMode() {
    // ローカルストレージ使用
    this.useLocalStorage = true;
    
    // UI調整
    document.getElementById('connectionStatus').textContent = '🔴 オフライン';
  }

  /**
   * オフラインデータ同期
   */
  syncOfflineData() {
    const offlineData = this.getOfflineData();
    if (offlineData.length > 0) {
      offlineData.forEach(data => {
        this.sendToManager(data);
      });
      this.clearOfflineData();
    }
  }

  // ヘルパーメソッド
  isConnected() {
    return navigator.onLine && this.currentSession !== null;
  }

  attemptReconnect() {
    // 再接続ロジック
    this.currentSession = 'reconnected';
  }

  removeOldNotifications() {
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach((notification, index) => {
      if (index > 5) notification.remove();
    });
  }

  clearProjectCache() {
    // プロジェクトキャッシュクリア
    this.projectCache = null;
  }

  getOfflineData() {
    return JSON.parse(localStorage.getItem('offlineData') || '[]');
  }

  clearOfflineData() {
    localStorage.removeItem('offlineData');
  }
}

/**
 * モバイル安定性監視
 */
class MobileStabilityMonitor {
  constructor() {
    this.metrics = {
      responseTime: 0,
      memoryUsage: 0,
      fps: 60,
      networkLatency: 0
    };
  }

  startMonitoring(callback) {
    setInterval(() => {
      this.updateMetrics();
      callback(this.metrics);
    }, 2000);
  }

  updateMetrics() {
    // パフォーマンス測定
    this.metrics.responseTime = this.measureResponseTime();
    this.metrics.memoryUsage = this.measureMemoryUsage();
    this.metrics.fps = this.measureFPS();
    this.metrics.networkLatency = this.measureNetworkLatency();
  }

  measureResponseTime() {
    // レスポンスタイム測定（シミュレーション）
    return Math.random() * 2000 + 500;
  }

  measureMemoryUsage() {
    // メモリ使用率測定（シミュレーション）
    if (performance.memory) {
      return performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit;
    }
    return Math.random() * 0.3 + 0.5;
  }

  measureFPS() {
    // FPS測定（シミュレーション）
    return 60 - Math.floor(Math.random() * 20);
  }

  measureNetworkLatency() {
    // ネットワーク遅延測定（シミュレーション）
    return Math.random() * 100 + 20;
  }
}

/**
 * 音声コマンド処理クラス
 */
class VoiceCommandProcessor {
  constructor() {
    this.recognition = null;
    this.isSupported = this.checkSupport();
    this.setupRecognition();
  }

  /**
   * 音声認識サポート確認
   */
  checkSupport() {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  }

  /**
   * 音声認識設定
   */
  setupRecognition() {
    if (!this.isSupported) return;
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.lang = 'ja-JP';
    this.recognition.maxAlternatives = 1;
  }

  /**
   * 音声認識開始
   * @param {Function} callback 
   */
  startListening(callback) {
    if (!this.isSupported || !this.recognition) return;
    
    this.recognition.onresult = (event) => {
      const command = event.results[0][0].transcript;
      callback(command);
    };
    
    this.recognition.onerror = (event) => {
      console.error('Voice recognition error:', event.error);
    };
    
    this.recognition.start();
  }

  /**
   * 音声認識停止
   */
  stopListening() {
    if (this.recognition) {
      this.recognition.stop();
    }
  }
}

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CEOMobileInterface, VoiceCommandProcessor };
}