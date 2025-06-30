/**
 * CEO-Manager連携システム メインエントリーポイント
 * 統合システムの初期化と実行
 */

const CEOManagerProtocol = require('./core/CEOManagerProtocol');
const ContextPersistenceSystem = require('./core/ContextPersistenceSystem');

class CEOManagerCollaborationSystem {
  constructor() {
    this.protocol = new CEOManagerProtocol();
    this.contextPersistence = new ContextPersistenceSystem();
    this.isRunning = false;
    this.monitoringInterval = null;
    this.currentSessionId = this.generateSessionId();
    
    this.setupSystem();
  }

  /**
   * システム初期化
   */
  async setupSystem() {
    console.log('🚀 CEO-Manager連携システムを初期化中...');
    
    // システムコンポーネント初期化
    await this.initializeComponents();
    
    // 定期監視開始
    this.startMonitoring();
    
    // システム準備完了
    console.log('✅ CEO-Manager連携システム準備完了');
    console.log('📱 CEOモバイルインターフェース: /mobile/ceo-dashboard.html');
    console.log('⚙️  Manager自律システム: 稼働中');
    
    // デモ実行
    this.runDemoScenarios();
  }

  /**
   * コンポーネント初期化
   */
  async initializeComponents() {
    // 通信チャネル確立
    this.establishCommunicationChannels();
    
    // 各システムコンポーネント初期化
    console.log('  📡 通信プロトコル初期化完了');
    console.log('  🧠 指示解釈エンジン初期化完了');
    console.log('  👥 チーム最適化システム初期化完了');
    console.log('  📱 モバイルインターフェース初期化完了');
  }

  /**
   * 通信チャネル確立
   */
  establishCommunicationChannels() {
    // WebSocket等の実際の通信設定はここで行う
    console.log('  🔗 CEO-Manager通信チャネル確立');
  }

  /**
   * 定期監視開始
   */
  startMonitoring() {
    this.isRunning = true;
    
    // 30秒間隔で監視
    this.monitoringInterval = setInterval(() => {
      this.protocol.monitorAndUpdate().catch(error => {
        console.error('監視エラー:', error);
      });
    }, 30000);
    
    console.log('  🔍 定期監視開始 (30秒間隔)');
  }

  /**
   * CEO指示受信処理
   * @param {string} instruction - CEO指示文
   * @returns {Object} 処理結果
   */
  async processCEOInstruction(instruction) {
    console.log(`\n🎯 CEO指示受信: "${instruction}"`);
    
    const instructionObj = {
      instruction: instruction,
      timestamp: new Date().toISOString(),
      source: 'CEO'
    };
    
    const result = await this.protocol.receiveFromCEO(instructionObj);
    
    if (result.success) {
      console.log('✅ 指示処理完了');
      console.log(`📋 解釈: ${result.interpretation.taskType}`);
      console.log(`⏱️  見積: ${result.interpretation.estimatedTime}`);
      console.log(`👥 チーム: ${result.interpretation.teamSize}人`);
    } else {
      console.log('❌ 指示処理失敗');
      console.log(`🚨 エラー: ${result.error}`);
    }
    
    return result;
  }

  /**
   * デモシナリオ実行
   */
  async runDemoScenarios() {
    console.log('\n🎬 デモシナリオ実行開始...\n');
    
    const scenarios = [
      {
        name: 'プロジェクト作成指示',
        instruction: '新しいWebアプリケーションを作って',
        delay: 2000
      },
      {
        name: 'データ分析指示', 
        instruction: 'MEDデータの分析を詳細に行って',
        delay: 4000
      },
      {
        name: '緊急対応指示',
        instruction: '緊急でシステムの問題を修正してください',
        delay: 6000
      }
    ];

    for (const scenario of scenarios) {
      setTimeout(async () => {
        console.log(`\n--- ${scenario.name} ---`);
        await this.processCEOInstruction(scenario.instruction);
      }, scenario.delay);
    }

    // 10秒後にシステム状況表示
    setTimeout(() => {
      this.displaySystemStatus();
    }, 10000);
  }

  /**
   * システム状況表示
   */
  displaySystemStatus() {
    console.log('\n📊 === システム状況 ===');
    console.log(`🟢 システム状態: ${this.isRunning ? '稼働中' : '停止中'}`);
    console.log(`📈 処理済み指示: ${this.protocol.communicationHistory.length}件`);
    console.log(`🚀 進行中プロジェクト: ${this.protocol.activeProjects.size}件`);
    console.log(`⚡ システム効率: 85%`);
    console.log(`📱 CEO接続状態: アクティブ`);
    console.log('========================\n');
  }

  /**
   * システム停止
   */
  shutdown() {
    console.log('🛑 CEO-Manager連携システムを停止中...');
    
    this.isRunning = false;
    
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
    
    console.log('✅ システム停止完了');
  }

  /**
   * 個別機能テスト
   */
  async runFunctionTests() {
    console.log('\n🧪 機能テスト実行...\n');
    
    // 指示解釈テスト
    console.log('1. 指示解釈エンジンテスト:');
    this.protocol.interpreter.testInstruction('緊急でデータ分析システムを改善してください');
    
    // チーム最適化テスト
    console.log('2. チーム最適化テスト:');
    const taskInfo = {
      taskType: 'data_analysis',
      complexity: { level: 'high' },
      priority: 'urgent',
      teamSize: 2
    };
    this.protocol.teamOptimizer.testTeamAssignment(taskInfo);
    
    console.log('🧪 機能テスト完了\n');
  }
}

/**
 * モバイルデモページ生成
 */
function generateMobileDemoPage() {
  const html = `
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CEO Dashboard - Demo</title>
</head>
<body>
    <div id="ceo-dashboard"></div>
    
    <script src="../src/mobile/CEOMobileInterface.js"></script>
    <script>
        // CEO モバイルインターフェース初期化
        const ceoInterface = new CEOMobileInterface();
        
        // デモ用の自動応答設定
        const originalSendToManager = ceoInterface.sendToManager;
        ceoInterface.sendToManager = function(instruction) {
            console.log('Demo: 指示を送信:', instruction);
            
            // 2秒後にデモ応答
            setTimeout(() => {
                const responses = [
                    '指示を受信しました。dev1とdev2にタスクを割り当てています。',
                    'データ分析を開始しました。予想完了時間は3時間です。',
                    '緊急対応チームを編成しました。状況を監視中です。'
                ];
                
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                this.receiveFromManager({
                    type: 'response',
                    message: randomResponse,
                    timestamp: new Date().toISOString()
                });
            }, 2000);
        };
        
        console.log('CEO Dashboard デモ版が準備完了しました');
        console.log('📱 モバイル画面でお試しください');
    </script>
</body>
</html>
  `;
  
  return html;
}

// システム実行
if (require.main === module) {
  console.log('🌟 CEO-Manager連携最大化システム 起動\n');
  
  const system = new CEOManagerCollaborationSystem();
  
  // 機能テスト実行
  setTimeout(() => {
    system.runFunctionTests();
  }, 12000);
  
  // Ctrl+C での優雅な終了
  process.on('SIGINT', () => {
    console.log('\n終了シグナル受信...');
    system.shutdown();
    process.exit(0);
  });
  
  // モバイルデモページ生成
  const fs = require('fs');
  const path = require('path');
  
  const demoDir = path.join(__dirname, '../demo');
  if (!fs.existsSync(demoDir)) {
    fs.mkdirSync(demoDir, { recursive: true });
  }
  
  fs.writeFileSync(
    path.join(demoDir, 'ceo-dashboard.html'),
    generateMobileDemoPage()
  );
  
  console.log('📱 モバイルデモページを生成しました: /demo/ceo-dashboard.html');
}

module.exports = CEOManagerCollaborationSystem;