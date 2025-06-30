/**
 * 重要コードバックアップ
 * 再起動後の参照用
 */

// 1. CEO指示解釈の核心ロジック
const parseInstructionCore = (instruction) => {
  const patterns = {
    "新しい.*作って": { type: "project_create", complexity: "medium" },
    ".*を修正": { type: "project_fix", complexity: "low" },
    ".*を改善": { type: "project_improve", complexity: "medium" },
    "緊急.*対応": { type: "emergency", complexity: "high", priority: "urgent" }
  };
  
  // 品質検証タスクの特別処理
  const qualityKeywords = ['テスト', '検証', '品質', 'QA', 'エラー', 'バグ'];
  const hasQualityTask = qualityKeywords.some(keyword => instruction.includes(keyword));
  
  if (hasQualityTask) {
    return {
      type: 'testing',
      expectedHighOutput: true,
      recommendedExecution: 'phased'
    };
  }
};

// 2. 役割別出力量予測
const roleOutputMultipliers = {
  dev1: { testing: 1.0, project_create: 1.0 },
  dev2: { analysis: 1.5, data_processing: 1.3 },
  dev3: { testing: 2.5, quality_assurance: 2.0, error_analysis: 2.2 }
};

// 3. auto-compact予防設定
const compactPrevention = {
  messageControl: {
    maxLength: 2000,
    splitThreshold: 1800,
    compressionEnabled: true
  },
  contextOptimization: {
    essentialOnly: true,
    removeRedundancy: true,
    priorityBasedRetention: true
  },
  bufferManagement: {
    maxBufferSize: 50000,
    rotationPolicy: 'FIFO',
    compressionThreshold: 0.8
  }
};

// 4. 異常検知閾値
const anomalyThresholds = {
  responseTime: 5000,      // 5秒
  memoryUsage: 0.85,       // 85%
  contextSize: 45000,      // 45KB
  errorRate: 0.05          // 5%
};

// 5. dev3特別最適化
const dev3Optimizations = {
  outputChunkingConfig: {
    enabled: true,
    maxChunkSize: 1000,
    delayBetweenChunks: 100,
    summaryGenerationRequired: true
  },
  errorLogCompression: {
    enabled: true,
    compressionLevel: 'high',
    retainCriticalOnly: true
  },
  testResultSummary: {
    enabled: true,
    format: 'compact',
    includeOnlyFailures: false,
    maxDetailLength: 500
  }
};

// 6. チーム編成マトリックス
const teamMatrix = {
  "web_development": {
    primary: "dev1",
    secondary: "dev2",
    support: "dev3"
  },
  "data_analysis": {
    primary: "dev2",
    secondary: "dev1",
    support: "dev3"
  },
  "testing": {
    primary: "dev3", // 注意: 高出力リスク
    secondary: "dev1",
    support: "dev2"
  }
};

// 7. 文脈保持優先順位
const contextPriorities = {
  high: ['activeProjects', 'recentInstructions', 'urgentTasks'],
  medium: ['teamStatus', 'systemHealth'],
  low: ['historicalData', 'completedTasks']
};

// 8. モバイル安定性設定
const mobileStabilityConfig = {
  autoReconnect: {
    enabled: true,
    maxAttempts: 5,
    interval: 5000
  },
  performanceOptimization: {
    responseTimeThreshold: 3000,
    memoryUsageThreshold: 0.8,
    animationSimplification: true
  },
  offlineSupport: {
    enabled: true,
    localStorageKey: 'offlineData',
    syncOnReconnect: true
  }
};

// エクスポート
module.exports = {
  parseInstructionCore,
  roleOutputMultipliers,
  compactPrevention,
  anomalyThresholds,
  dev3Optimizations,
  teamMatrix,
  contextPriorities,
  mobileStabilityConfig
};