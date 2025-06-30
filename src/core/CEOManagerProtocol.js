/**
 * CEO-Manager連携プロトコル
 * 統合通信システムとワークフロー管理
 */

const InstructionInterpreter = require('./InstructionInterpreter');
const TeamAssignmentOptimizer = require('./TeamAssignmentOptimizer');
const StabilityManager = require('./StabilityManager');

class CEOManagerProtocol {
  constructor() {
    this.interpreter = new InstructionInterpreter();
    this.teamOptimizer = new TeamAssignmentOptimizer();
    this.contextAnalyzer = new ContextAnalyzer();
    this.reportingSystem = new IntelligentReporting();
    this.failsafeSystem = new FailsafeSystem();
    this.stabilityManager = new StabilityManager();
    
    this.activeProjects = new Map();
    this.communicationHistory = [];
    this.systemHealth = this.initializeSystemHealth();
    
    this.setupCommunicationChannels();
    this.setupStabilityMonitoring();
  }

  /**
   * CEO指示受信・処理
   * @param {Object} instruction - CEO指示
   * @returns {Object} 処理結果
   */
  async receiveFromCEO(instruction) {
    try {
      const timestamp = new Date().toISOString();
      this.logCommunication('CEO->Manager', instruction, timestamp);
      
      // 指示解釈
      const parsedInstruction = this.interpreter.parseInstruction(instruction.instruction);
      
      // コンテキスト分析
      const context = this.contextAnalyzer.analyzeCurrentSituation();
      
      // チーム推薦
      const teamRecommendation = this.teamOptimizer.recommendTeam(parsedInstruction);
      
      // 自律判断
      const managerDecision = await this.makeAutonomousDecision(parsedInstruction, context, teamRecommendation);
      
      // 実行計画作成
      const executionPlan = this.createExecutionPlan(managerDecision);
      
      // CEO報告判定
      const shouldReport = this.reportingSystem.shouldReportToCEO(managerDecision, context);
      
      if (shouldReport) {
        await this.sendToCEO({
          type: 'execution_plan',
          originalInstruction: instruction,
          interpretation: parsedInstruction,
          decision: managerDecision,
          plan: executionPlan,
          timestamp: timestamp
        });
      }
      
      // 実行開始
      const executionResult = await this.executeInstruction(executionPlan);
      
      return {
        success: true,
        interpretation: parsedInstruction,
        decision: managerDecision,
        execution: executionResult
      };
      
    } catch (error) {
      return this.handleError(error, instruction);
    }
  }

  /**
   * Manager自律判断
   * @param {Object} instruction 
   * @param {Object} context 
   * @param {Object} teamRecommendation 
   * @returns {Object} 判断結果
   */
  async makeAutonomousDecision(instruction, context, teamRecommendation) {
    // リスク評価
    const risks = this.contextAnalyzer.assessRiskFactors(context);
    
    // 優先度計算
    const priority = this.calculatePriority(instruction, context);
    
    // リソース利用可能性
    const resourceAvailability = this.assessResourceAvailability(teamRecommendation);
    
    // 出力量予測（役割認識）
    const outputPredictions = {};
    if (teamRecommendation.primary) {
      outputPredictions[teamRecommendation.primary] = 
        this.teamOptimizer.roleOptimizer.predictOutputVolume(teamRecommendation.primary, instruction);
    }
    if (teamRecommendation.secondary) {
      outputPredictions[teamRecommendation.secondary] = 
        this.teamOptimizer.roleOptimizer.predictOutputVolume(teamRecommendation.secondary, instruction);
    }
    
    // 判断ロジック
    const decision = {
      shouldProceed: this.decideProceed(instruction, risks, resourceAvailability),
      modifications: this.proposeModifications(instruction, context, risks),
      timeline: this.calculateTimeline(instruction, teamRecommendation),
      resourceAllocation: this.allocateResources(teamRecommendation, priority),
      contingencyPlans: this.createContingencyPlans(risks),
      confidence: this.calculateDecisionConfidence(instruction, context, teamRecommendation)
    };
    
    // 出力量考慮の統合
    const optimizedDecision = this.teamOptimizer.roleOptimizer.integrateOutputConsiderations(decision, outputPredictions);
    
    return optimizedDecision;
  }

  /**
   * 実行計画作成
   * @param {Object} decision 
   * @returns {Object} 実行計画
   */
  createExecutionPlan(decision) {
    if (!decision.shouldProceed) {
      return {
        status: 'rejected',
        reason: decision.modifications.reasons[0],
        alternatives: decision.modifications.alternatives
      };
    }

    return {
      status: 'approved',
      phases: this.createPhases(decision),
      timeline: decision.timeline,
      team: decision.resourceAllocation,
      milestones: this.createMilestones(decision),
      riskMitigation: decision.contingencyPlans,
      monitoring: this.createMonitoringPlan(decision)
    };
  }

  /**
   * 指示実行
   * @param {Object} plan 
   * @returns {Object} 実行結果
   */
  async executeInstruction(plan) {
    if (plan.status === 'rejected') {
      return {
        success: false,
        status: 'rejected',
        reason: plan.reason,
        alternatives: plan.alternatives
      };
    }

    // プロジェクト開始
    const projectId = this.generateProjectId();
    this.activeProjects.set(projectId, {
      plan: plan,
      status: 'in_progress',
      startTime: new Date().toISOString(),
      currentPhase: 0,
      completedTasks: [],
      issues: []
    });

    // チーム配置実行
    this.executeTeamAssignment(plan.team);

    // 第一フェーズ開始
    const firstPhaseResult = await this.executePhase(projectId, 0);

    return {
      success: true,
      projectId: projectId,
      status: 'started',
      initialPhase: firstPhaseResult,
      nextUpdate: this.calculateNextUpdate(plan)
    };
  }

  /**
   * CEO報告送信
   * @param {Object} update 
   */
  async sendToCEO(update) {
    const report = this.reportingSystem.generateReport(update, this.contextAnalyzer.analyzeCurrentSituation());
    
    const formatted = {
      timestamp: new Date().toISOString(),
      type: update.type,
      summary: this.generateExecutiveSummary(update),
      details: report,
      nextActions: this.identifyNextActions(update),
      requiresDecision: this.requiresCEODecision(update)
    };

    this.logCommunication('Manager->CEO', formatted, formatted.timestamp);
    
    // 実際の実装では、WebSocketまたはHTTP APIを使用
    console.log('📊 CEO Report:', formatted.summary);
    
    return formatted;
  }

  /**
   * 進捗更新・継続監視
   */
  async monitorAndUpdate() {
    for (const [projectId, project] of this.activeProjects) {
      const status = await this.checkProjectStatus(projectId);
      
      if (status.needsUpdate) {
        await this.sendProgressUpdate(projectId, status);
      }
      
      if (status.hasIssues) {
        await this.handleProjectIssues(projectId, status.issues);
      }
      
      if (status.isComplete) {
        await this.completeProject(projectId);
      }
    }
  }

  /**
   * エラー処理
   * @param {Error} error 
   * @param {Object} instruction 
   * @returns {Object} エラー対応結果
   */
  handleError(error, instruction) {
    console.error('CEO-Manager Protocol Error:', error);
    
    const failsafeResponse = this.failsafeSystem.handleError(error, instruction);
    
    // 緊急時CEO通知
    this.sendToCEO({
      type: 'error_alert',
      error: error.message,
      instruction: instruction,
      failsafeAction: failsafeResponse,
      timestamp: new Date().toISOString()
    });
    
    return {
      success: false,
      error: error.message,
      failsafeAction: failsafeResponse
    };
  }

  // === 内部ヘルパーメソッド ===

  /**
   * 優先度計算
   */
  calculatePriority(instruction, context) {
    const factors = {
      urgency: instruction.priority === 'urgent' ? 0.9 : 0.5,
      impact: instruction.complexity.level === 'high' ? 0.8 : 0.6,
      effort: instruction.complexity.score || 0.5,
      dependencies: context.activeProjects.length > 3 ? 0.3 : 0.7,
      strategicValue: 0.6
    };
    
    const priorityScore = 
      factors.urgency * 0.3 +
      factors.impact * 0.25 +
      (1 / factors.effort) * 0.2 +
      factors.dependencies * 0.15 +
      factors.strategicValue * 0.1;
    
    return {
      score: priorityScore,
      level: priorityScore >= 0.7 ? 'high' : priorityScore >= 0.4 ? 'medium' : 'low',
      factors: factors
    };
  }

  /**
   * リソース利用可能性評価
   */
  assessResourceAvailability(teamRecommendation) {
    return {
      overall: teamRecommendation.estimatedEfficiency || 0.8,
      primary: 0.9,
      secondary: 0.7,
      support: 0.6
    };
  }

  /**
   * 実行可否判断
   */
  decideProceed(instruction, risks, resourceAvailability) {
    const riskScore = risks.reduce((sum, risk) => sum + (risk.severity === 'high' ? 0.3 : 0.1), 0);
    const resourceScore = resourceAvailability.overall;
    const complexityPenalty = instruction.complexity.level === 'high' ? 0.2 : 0;
    
    const proceedScore = resourceScore - riskScore - complexityPenalty;
    return proceedScore > 0.5;
  }

  /**
   * 修正提案
   */
  proposeModifications(instruction, context, risks) {
    const modifications = {
      reasons: [],
      alternatives: [],
      recommendations: []
    };
    
    if (risks.length > 0) {
      modifications.reasons.push('リスク要因が検出されました');
      modifications.alternatives.push('段階的実装による段階的展開');
    }
    
    if (instruction.complexity.level === 'high') {
      modifications.recommendations.push('チームサイズ拡大');
      modifications.recommendations.push('詳細な要件定義フェーズ追加');
    }
    
    return modifications;
  }

  /**
   * タイムライン計算
   */
  calculateTimeline(instruction, teamRecommendation) {
    const baseTime = this.parseEstimatedTime(instruction.estimatedTime);
    const teamEfficiency = teamRecommendation.estimatedEfficiency;
    const complexityMultiplier = {
      'low': 1.0,
      'medium': 1.3,
      'high': 1.8
    }[instruction.complexity.level];
    
    const adjustedTime = Math.ceil(baseTime * complexityMultiplier / teamEfficiency);
    
    return {
      estimated: `${adjustedTime}日`,
      breakdown: this.createTimelineBreakdown(instruction, adjustedTime),
      bufferTime: Math.ceil(adjustedTime * 0.2)
    };
  }

  /**
   * リソース配置
   */
  allocateResources(teamRecommendation, priority) {
    return {
      primary: {
        dev: teamRecommendation.primary,
        allocation: priority.level === 'urgent' ? 1.0 : 0.8,
        role: 'Lead Developer'
      },
      secondary: teamRecommendation.secondary ? {
        dev: teamRecommendation.secondary,
        allocation: 0.6,
        role: 'Support Developer'
      } : null,
      support: teamRecommendation.support ? {
        dev: teamRecommendation.support,
        allocation: 0.3,
        role: 'QA & Testing'
      } : null
    };
  }

  /**
   * 緊急プラン作成
   */
  createContingencyPlans(risks) {
    return risks.map(risk => ({
      risk: risk.type,
      mitigation: risk.recommendation,
      trigger: `if ${risk.type} occurs`,
      action: `execute ${risk.recommendation}`
    }));
  }

  /**
   * 決定信頼度計算
   */
  calculateDecisionConfidence(instruction, context, teamRecommendation) {
    const complexityFactor = instruction.complexity.level === 'low' ? 0.9 : 
                           instruction.complexity.level === 'medium' ? 0.7 : 0.5;
    const teamFactor = teamRecommendation.confidence || 0.8;
    const contextFactor = context.systemHealth.status === 'healthy' ? 0.9 : 0.6;
    
    return (complexityFactor + teamFactor + contextFactor) / 3;
  }

  /**
   * フェーズ作成
   */
  createPhases(decision) {
    const phases = ['計画', '実装', 'テスト', '完了'];
    return phases.map((phase, index) => ({
      name: phase,
      order: index + 1,
      estimated: `${Math.ceil(decision.timeline.estimated.replace('日', '') / phases.length)}日`
    }));
  }

  /**
   * マイルストーン作成
   */
  createMilestones(decision) {
    return [
      { name: '設計完了', phase: 1, description: '要件と設計が確定' },
      { name: '実装完了', phase: 2, description: 'コア機能実装完了' },
      { name: 'テスト完了', phase: 3, description: '品質保証完了' }
    ];
  }

  /**
   * 監視計画作成
   */
  createMonitoringPlan(decision) {
    return {
      frequency: decision.timeline.estimated.includes('週') ? 'daily' : 'hourly',
      metrics: ['progress', 'quality', 'timeline'],
      alerts: ['delay_risk', 'quality_issue', 'resource_conflict']
    };
  }

  /**
   * チーム配置実行
   */
  executeTeamAssignment(team) {
    console.log(`👥 チーム配置: ${team.primary.dev} (主担当), ${team.secondary ? team.secondary.dev + ' (副担当)' : ''}${team.support ? ', ' + team.support.dev + ' (支援)' : ''}`);
    
    // 実際の実装では、各devに通知を送信
    return {
      success: true,
      assignments: Object.values(team).filter(Boolean)
    };
  }

  /**
   * フェーズ実行
   */
  async executePhase(projectId, phaseIndex) {
    const project = this.activeProjects.get(projectId);
    if (!project) return { success: false, error: 'Project not found' };
    
    console.log(`🚀 フェーズ ${phaseIndex + 1} 開始: ${project.plan.phases[phaseIndex].name}`);
    
    // フェーズ実行のシミュレーション
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          success: true,
          phase: phaseIndex,
          status: 'started',
          estimatedCompletion: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
        });
      }, 1000);
    });
  }

  /**
   * 次回更新時刻計算
   */
  calculateNextUpdate(plan) {
    const hours = plan.timeline.estimated.includes('時間') ? 4 : 24;
    return new Date(Date.now() + hours * 60 * 60 * 1000).toISOString();
  }

  /**
   * エグゼクティブサマリー生成
   */
  generateExecutiveSummary(update) {
    switch(update.type) {
      case 'execution_plan':
        return `新規タスク開始: ${update.interpretation.taskType} (見積: ${update.interpretation.estimatedTime})`;
      case 'error_alert':
        return `システムエラー発生: ${update.error}`;
      default:
        return `システム更新: ${update.type}`;
    }
  }

  /**
   * 次のアクション識別
   */
  identifyNextActions(update) {
    return ['進捗監視', '品質確認', 'リソース調整'];
  }

  /**
   * CEO決定要否判定
   */
  requiresCEODecision(update) {
    return update.type === 'error_alert' || update.type === 'major_milestone';
  }

  /**
   * プロジェクト状況確認
   */
  async checkProjectStatus(projectId) {
    const project = this.activeProjects.get(projectId);
    if (!project) return { needsUpdate: false };
    
    // シミュレーション
    return {
      needsUpdate: Math.random() > 0.7,
      hasIssues: Math.random() > 0.9,
      isComplete: Math.random() > 0.95,
      issues: []
    };
  }

  /**
   * 進捗更新送信
   */
  async sendProgressUpdate(projectId, status) {
    console.log(`📈 プロジェクト ${projectId} 進捗更新`);
  }

  /**
   * プロジェクト問題処理
   */
  async handleProjectIssues(projectId, issues) {
    console.log(`⚠️ プロジェクト ${projectId} 問題対応`);
  }

  /**
   * プロジェクト完了
   */
  async completeProject(projectId) {
    console.log(`✅ プロジェクト ${projectId} 完了`);
    this.activeProjects.delete(projectId);
  }

  /**
   * タイムライン詳細作成
   */
  createTimelineBreakdown(instruction, totalDays) {
    const phases = ['設計', '実装', 'テスト', '完了'];
    const distribution = [0.2, 0.5, 0.2, 0.1];
    
    return phases.map((phase, index) => ({
      phase: phase,
      days: Math.ceil(totalDays * distribution[index]),
      startDay: Math.ceil(totalDays * distribution.slice(0, index).reduce((sum, d) => sum + d, 0))
    }));
  }

  /**
   * 通信履歴記録
   */
  logCommunication(direction, content, timestamp) {
    this.communicationHistory.push({
      direction,
      content,
      timestamp,
      id: this.generateId()
    });
    
    // 履歴制限（最新100件保持）
    if (this.communicationHistory.length > 100) {
      this.communicationHistory = this.communicationHistory.slice(-100);
    }
  }

  /**
   * システムヘルス初期化
   */
  initializeSystemHealth() {
    return {
      communication: 'healthy',
      projects: 'operational',
      team: 'available',
      lastUpdate: new Date().toISOString()
    };
  }

  /**
   * ユーティリティメソッド
   */
  generateProjectId() {
    return `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  generateId() {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  parseEstimatedTime(timeString) {
    const match = timeString.match(/(\d+)/);
    return match ? parseInt(match[1]) : 3;
  }

  setupCommunicationChannels() {
    // WebSocket接続設定等
    console.log('CEO-Manager communication channels established');
  }

  /**
   * 安定性監視設定
   */
  setupStabilityMonitoring() {
    // 安定性管理システムとの連携
    console.log('🛡️ 安定性監視システム初期化');
    
    // auto-compact予防設定
    const preventionConfig = this.stabilityManager.preventAutoCompact();
    this.applyCompactPrevention(preventionConfig);
    
    // 異常検知ハンドラー設定
    setInterval(() => {
      const anomalies = this.stabilityManager.detectAnomalies();
      if (anomalies.length > 0) {
        this.handleSystemAnomalies(anomalies);
      }
    }, 5000);
  }

  /**
   * compact予防設定適用
   */
  applyCompactPrevention(config) {
    // メッセージ長制限
    this.maxMessageLength = config.messageControl.maxLength;
    
    // コンテキスト最適化
    this.contextOptimization = config.contextOptimization;
    
    // バッファ管理
    this.bufferConfig = config.bufferManagement;
    
    console.log('✅ Auto-compact予防機能を有効化');
  }

  /**
   * システム異常処理
   */
  handleSystemAnomalies(anomalies) {
    anomalies.forEach(anomaly => {
      if (anomaly.severity === 'critical') {
        console.log(`🚨 重大な異常検知: ${anomaly.type}`);
        
        // CEO緊急通知
        this.sendToCEO({
          type: 'system_anomaly',
          anomaly: anomaly,
          actions: this.stabilityManager.executeStabilityActions([anomaly]),
          timestamp: new Date().toISOString()
        });
      }
    });
  }

  /**
   * 指示処理前の安定性チェック
   */
  async checkStabilityBeforeExecution(instruction) {
    const metrics = this.stabilityManager.collectSystemMetrics();
    
    // コンテキストサイズチェック
    if (metrics.contextSize > 40000) {
      console.log('⚠️ コンテキスト圧縮を実行');
      this.stabilityManager.compressContext();
    }
    
    // メモリ使用率チェック
    if (metrics.memoryUsage > 0.8) {
      console.log('⚠️ メモリクリーンアップを実行');
      this.stabilityManager.cleanupMemory();
    }
    
    return true;
  }

  /**
   * CEO指示受信・処理（安定性強化版）
   */
  async receiveFromCEO(instruction) {
    try {
      // 安定性チェック
      await this.checkStabilityBeforeExecution(instruction);
      
      // メッセージ長チェック
      if (instruction.instruction.length > this.maxMessageLength) {
        instruction.instruction = this.splitLongInstruction(instruction.instruction);
      }
      
      // 既存の処理を継続
      return await this._originalReceiveFromCEO(instruction);
      
    } catch (error) {
      return this.handleError(error, instruction);
    }
  }

  /**
   * 長い指示の分割
   */
  splitLongInstruction(instruction) {
    if (instruction.length <= this.maxMessageLength) {
      return instruction;
    }
    
    // 重要な部分のみ抽出
    const keywords = this.extractKeywords(instruction);
    const summary = this.generateInstructionSummary(instruction);
    
    return `${keywords.join(' ')} - ${summary}`;
  }

  extractKeywords(text) {
    const keywords = text.match(/(\S+を\S+|緊急|重要|作成|修正|改善|分析)/g) || [];
    return keywords.slice(0, 10);
  }

  generateInstructionSummary(text) {
    return text.substring(0, 100) + '...';
  }

  /**
   * 元のreceiveFromCEO処理
   */
  async _originalReceiveFromCEO(instruction) {
    const timestamp = new Date().toISOString();
    this.logCommunication('CEO->Manager', instruction, timestamp);
    
    // 指示解釈
    const parsedInstruction = this.interpreter.parseInstruction(instruction.instruction);
    
    // コンテキスト分析
    const context = this.contextAnalyzer.analyzeCurrentSituation();
    
    // チーム推薦
    const teamRecommendation = this.teamOptimizer.recommendTeam(parsedInstruction);
    
    // 自律判断
    const managerDecision = await this.makeAutonomousDecision(parsedInstruction, context, teamRecommendation);
    
    // 実行計画作成
    const executionPlan = this.createExecutionPlan(managerDecision);
    
    // CEO報告判定
    const shouldReport = this.reportingSystem.shouldReportToCEO(managerDecision, context);
    
    if (shouldReport) {
      await this.sendToCEO({
        type: 'execution_plan',
        originalInstruction: instruction,
        interpretation: parsedInstruction,
        decision: managerDecision,
        plan: executionPlan,
        timestamp: timestamp
      });
    }
    
    // 実行開始
    const executionResult = await this.executeInstruction(executionPlan);
    
    return {
      success: true,
      interpretation: parsedInstruction,
      decision: managerDecision,
      execution: executionResult
    };
  }
}

/**
 * コンテキスト分析クラス
 */
class ContextAnalyzer {
  analyzeCurrentSituation() {
    return {
      activeProjects: this.getActiveProjects(),
      teamStatus: this.getTeamStatus(),
      systemHealth: this.getSystemHealth(),
      recentIssues: this.getRecentIssues(),
      upcomingDeadlines: this.getUpcomingDeadlines(),
      resourceAvailability: this.getResourceAvailability()
    };
  }

  assessRiskFactors(context) {
    const risks = [];
    
    // チームオーバーロード検知
    if (context.teamStatus.overloadScore > 0.8) {
      risks.push({
        type: "team_overload",
        severity: "high",
        recommendation: "task_redistribution"
      });
    }
    
    // 締切リスク
    context.upcomingDeadlines.forEach(deadline => {
      if (deadline.daysRemaining < 2 && deadline.completion < 0.7) {
        risks.push({
          type: "deadline_risk",
          severity: "urgent",
          project: deadline.project,
          recommendation: "resource_reallocation"
        });
      }
    });
    
    return risks;
  }

  // スタブメソッド（実際の実装では実データを取得）
  getActiveProjects() { return []; }
  getTeamStatus() { return { overloadScore: 0.3 }; }
  getSystemHealth() { return { status: 'healthy' }; }
  getRecentIssues() { return []; }
  getUpcomingDeadlines() { return []; }
  getResourceAvailability() { return { overall: 0.8 }; }
}

/**
 * インテリジェント報告システム
 */
class IntelligentReporting {
  shouldReportToCEO(event, context) {
    const eventPriority = this.assessEventPriority(event);
    const contextSensitivity = this.assessContextSensitivity(event, context);
    
    return eventPriority > 0.7 || contextSensitivity > 0.8;
  }

  generateReport(event, context) {
    const reportLevel = this.determineReportLevel(event);
    
    switch(reportLevel) {
      case 'executive_summary':
        return this.generateExecutiveSummary(event, context);
      case 'detailed_analysis':
        return this.generateDetailedAnalysis(event, context);
      case 'action_required':
        return this.generateActionRequiredReport(event, context);
      default:
        return this.generateStandardReport(event, context);
    }
  }

  assessEventPriority(event) { return 0.6; }
  assessContextSensitivity(event, context) { return 0.5; }
  determineReportLevel(event) { return 'executive_summary'; }
  generateExecutiveSummary(event, context) { return '概要報告'; }
  generateDetailedAnalysis(event, context) { return '詳細分析'; }
  generateActionRequiredReport(event, context) { return '対応要求'; }
  generateStandardReport(event, context) { return '標準報告'; }
}

/**
 * フェールセーフシステム
 */
class FailsafeSystem {
  handleError(error, instruction) {
    return {
      continuePendingTasks: true,
      escalationPath: ["manager", "dev1", "dev2", "dev3"],
      emergencyContacts: this.getEmergencyContacts(),
      fallbackProcedures: this.getFallbackProcedures()
    };
  }

  getEmergencyContacts() { return ['dev1']; }
  getFallbackProcedures() { return ['manual_intervention']; }
}

module.exports = CEOManagerProtocol;