/**
 * 役割認識最適化システム
 * dev3の品質管理役割による高出力を考慮した最適化
 */

class RoleAwareOptimizer {
  constructor() {
    this.roleProfiles = this.initializeRoleProfiles();
    this.outputPredictor = new OutputVolumePredictor();
    this.taskSplitter = new HighOutputTaskSplitter();
    
    this.setupRoleBasedOptimization();
  }

  /**
   * 役割プロファイル初期化
   */
  initializeRoleProfiles() {
    return {
      dev1: {
        primaryRole: 'UI/UX・フロントエンド開発',
        secondaryRoles: ['プロジェクト管理', 'ドキュメント作成'],
        typicalOutputVolume: 'medium',
        outputPatterns: {
          code: 0.5,
          documentation: 0.3,
          communication: 0.2
        },
        riskFactors: {
          outputOverflow: 0.3,
          complexityHandling: 0.8
        }
      },
      dev2: {
        primaryRole: 'データ分析・バックエンド開発',
        secondaryRoles: ['統計解析', 'パフォーマンス最適化'],
        typicalOutputVolume: 'medium-high',
        outputPatterns: {
          analysis: 0.4,
          code: 0.4,
          reports: 0.2
        },
        riskFactors: {
          outputOverflow: 0.5,
          complexityHandling: 0.9
        }
      },
      dev3: {
        primaryRole: '品質管理・テスト実行',
        secondaryRoles: ['インフラ管理', 'CI/CD'],
        typicalOutputVolume: 'very-high', // 最大出力量
        outputPatterns: {
          testResults: 0.4,
          errorLogs: 0.3,
          verificationReports: 0.3
        },
        riskFactors: {
          outputOverflow: 0.9, // 高リスク
          complexityHandling: 0.7
        },
        specialConsiderations: {
          requiresOutputChunking: true,
          preferredBatchSize: 50,
          summaryRequired: true
        }
      }
    };
  }

  /**
   * 役割ベース最適化設定
   */
  setupRoleBasedOptimization() {
    console.log('🎯 役割認識最適化システム初期化');
    
    // dev3特別対策
    this.applyDev3SpecialOptimizations();
  }

  /**
   * dev3特別最適化
   */
  applyDev3SpecialOptimizations() {
    const dev3Profile = this.roleProfiles.dev3;
    
    // 出力チャンキング設定
    dev3Profile.outputChunkingConfig = {
      enabled: true,
      maxChunkSize: 1000, // 1000文字/チャンク
      delayBetweenChunks: 100, // 100ms遅延
      summaryGenerationRequired: true
    };
    
    // エラーログ圧縮設定
    dev3Profile.errorLogCompression = {
      enabled: true,
      compressionLevel: 'high',
      retainCriticalOnly: true
    };
    
    // テスト結果要約設定
    dev3Profile.testResultSummary = {
      enabled: true,
      format: 'compact',
      includeOnlyFailures: false,
      maxDetailLength: 500
    };
    
    console.log('✅ dev3専用最適化設定完了');
  }

  /**
   * タスク割当前の出力量予測
   * @param {string} devId 
   * @param {Object} task 
   * @returns {Object} 予測結果
   */
  predictOutputVolume(devId, task) {
    const profile = this.roleProfiles[devId];
    const baseVolume = this.outputPredictor.predictBaseVolume(task);
    
    // 役割別の出力倍率
    const roleMultiplier = this.getRoleOutputMultiplier(devId, task.type);
    
    // タスク複雑度による調整
    const complexityFactor = task.complexity.score || 0.5;
    
    // 最終予測
    const predictedVolume = baseVolume * roleMultiplier * (1 + complexityFactor);
    
    return {
      devId: devId,
      taskType: task.type,
      predictedVolume: predictedVolume,
      riskLevel: this.assessOutputRisk(predictedVolume, profile),
      recommendation: this.generateOutputRecommendation(predictedVolume, devId)
    };
  }

  /**
   * 役割別出力倍率取得
   * @param {string} devId 
   * @param {string} taskType 
   * @returns {number} 出力倍率
   */
  getRoleOutputMultiplier(devId, taskType) {
    const multipliers = {
      dev1: {
        'project_create': 1.0,
        'documentation': 0.8,
        'ui_development': 0.9
      },
      dev2: {
        'analysis': 1.5,
        'data_processing': 1.3,
        'backend_development': 1.0
      },
      dev3: {
        'testing': 2.5, // 最高倍率
        'quality_assurance': 2.0,
        'error_analysis': 2.2,
        'verification': 2.3
      }
    };
    
    return multipliers[devId]?.[taskType] || 1.0;
  }

  /**
   * 出力リスク評価
   * @param {number} predictedVolume 
   * @param {Object} profile 
   * @returns {string} リスクレベル
   */
  assessOutputRisk(predictedVolume, profile) {
    const threshold = {
      low: 5000,
      medium: 15000,
      high: 30000,
      critical: 40000
    };
    
    // 役割別リスク係数を適用
    const adjustedVolume = predictedVolume * profile.riskFactors.outputOverflow;
    
    if (adjustedVolume >= threshold.critical) return 'critical';
    if (adjustedVolume >= threshold.high) return 'high';
    if (adjustedVolume >= threshold.medium) return 'medium';
    return 'low';
  }

  /**
   * 出力推奨事項生成
   * @param {number} volume 
   * @param {string} devId 
   * @returns {Object} 推奨事項
   */
  generateOutputRecommendation(volume, devId) {
    const risk = this.assessOutputRisk(volume, this.roleProfiles[devId]);
    
    const recommendations = {
      critical: {
        action: 'split_task',
        method: 'automatic',
        chunks: Math.ceil(volume / 10000),
        summary: 'required',
        assignAlternative: true
      },
      high: {
        action: 'apply_compression',
        method: 'selective',
        chunks: Math.ceil(volume / 20000),
        summary: 'recommended',
        assignAlternative: false
      },
      medium: {
        action: 'monitor',
        method: 'standard',
        chunks: 1,
        summary: 'optional',
        assignAlternative: false
      },
      low: {
        action: 'proceed',
        method: 'normal',
        chunks: 1,
        summary: 'none',
        assignAlternative: false
      }
    };
    
    return recommendations[risk];
  }

  /**
   * 高出力タスクの自動分割
   * @param {Object} task 
   * @param {string} devId 
   * @returns {Array} 分割されたサブタスク
   */
  splitHighOutputTask(task, devId) {
    const prediction = this.predictOutputVolume(devId, task);
    
    if (prediction.riskLevel === 'critical' || prediction.riskLevel === 'high') {
      return this.taskSplitter.split(task, prediction.recommendation.chunks);
    }
    
    return [task]; // 分割不要
  }

  /**
   * チーム編成時の役割考慮
   * @param {Object} task 
   * @param {Object} teamRecommendation 
   * @returns {Object} 最適化されたチーム編成
   */
  optimizeTeamAssignmentByRole(task, teamRecommendation) {
    const optimized = { ...teamRecommendation };
    
    // 各dev候補の出力量予測
    const predictions = {};
    ['dev1', 'dev2', 'dev3'].forEach(devId => {
      predictions[devId] = this.predictOutputVolume(devId, task);
    });
    
    // dev3が主担当の場合の特別処理
    if (optimized.primary === 'dev3' && predictions.dev3.riskLevel === 'critical') {
      console.log('⚠️ dev3の高出力リスク検出 - チーム編成を調整');
      
      // タスク分割または代替割当を検討
      if (predictions.dev3.recommendation.assignAlternative) {
        // dev1またはdev2に主担当を変更
        if (predictions.dev1.riskLevel === 'low') {
          optimized.primary = 'dev1';
          optimized.secondary = 'dev3';
          optimized.reasoning += ' (dev3の出力量リスクを考慮して調整)';
        } else if (predictions.dev2.riskLevel === 'low') {
          optimized.primary = 'dev2';
          optimized.secondary = 'dev3';
          optimized.reasoning += ' (dev3の出力量リスクを考慮して調整)';
        }
      }
    }
    
    // 役割別最適化フラグ
    optimized.roleOptimizations = {
      outputChunking: predictions[optimized.primary].recommendation.chunks > 1,
      summaryGeneration: predictions[optimized.primary].recommendation.summary !== 'none',
      compressionEnabled: predictions[optimized.primary].recommendation.action === 'apply_compression'
    };
    
    return optimized;
  }

  /**
   * Manager判断への出力量考慮統合
   * @param {Object} decision 
   * @param {Object} outputPredictions 
   * @returns {Object} 更新された判断
   */
  integrateOutputConsiderations(decision, outputPredictions) {
    const updatedDecision = { ...decision };
    
    // 高出力タスクの場合の修正
    Object.entries(outputPredictions).forEach(([devId, prediction]) => {
      if (prediction.riskLevel === 'critical' || prediction.riskLevel === 'high') {
        // タイムライン調整
        if (updatedDecision.timeline) {
          updatedDecision.timeline.bufferTime *= 1.5; // バッファ時間を50%増加
        }
        
        // 実行計画に出力管理を追加
        updatedDecision.modifications = updatedDecision.modifications || {};
        updatedDecision.modifications.outputManagement = {
          required: true,
          strategy: prediction.recommendation.action,
          chunks: prediction.recommendation.chunks
        };
      }
    });
    
    return updatedDecision;
  }

  /**
   * CEO指示解釈への品質検証タスク特別扱い
   * @param {Object} instruction 
   * @returns {Object} 最適化された指示
   */
  optimizeQualityVerificationInstructions(instruction) {
    const qualityKeywords = ['テスト', '検証', '品質', 'QA', 'エラー', 'バグ'];
    const hasQualityTask = qualityKeywords.some(keyword => 
      instruction.instruction.includes(keyword)
    );
    
    if (hasQualityTask) {
      // 品質検証タスクとして特別マーク
      instruction.metadata = instruction.metadata || {};
      instruction.metadata.isQualityTask = true;
      instruction.metadata.expectedHighOutput = true;
      
      // 自動的に段階実行を推奨
      instruction.metadata.recommendedExecution = 'phased';
      instruction.metadata.outputStrategy = {
        summarization: 'required',
        chunking: 'automatic',
        compressionLevel: 'high'
      };
      
      console.log('🔍 品質検証タスクとして特別処理を適用');
    }
    
    return instruction;
  }
}

/**
 * 出力量予測器
 */
class OutputVolumePredictor {
  predictBaseVolume(task) {
    const baseVolumes = {
      'testing': 25000,
      'analysis': 15000,
      'project_create': 10000,
      'documentation': 8000,
      'project_fix': 5000,
      'configuration': 3000
    };
    
    return baseVolumes[task.type] || 10000;
  }
}

/**
 * 高出力タスク分割器
 */
class HighOutputTaskSplitter {
  split(task, chunks) {
    const subtasks = [];
    
    for (let i = 0; i < chunks; i++) {
      subtasks.push({
        ...task,
        id: `${task.id}_chunk_${i + 1}`,
        name: `${task.name} (Part ${i + 1}/${chunks})`,
        isChunked: true,
        chunkIndex: i,
        totalChunks: chunks,
        outputLimit: 10000 // チャンクあたりの出力制限
      });
    }
    
    return subtasks;
  }
}

module.exports = RoleAwareOptimizer;