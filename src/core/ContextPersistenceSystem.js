/**
 * 文脈保持システム
 * CEO-Manager連携での文脈継続性を保証
 */

class ContextPersistenceSystem {
  constructor() {
    this.contextStore = new Map();
    this.sessionHistory = [];
    this.maxContextSize = 45000;
    this.compressionEnabled = true;
    
    this.initializePersistence();
  }

  /**
   * 文脈保存
   * @param {string} sessionId - セッションID
   * @param {Object} context - 保存する文脈
   */
  saveContext(sessionId, context) {
    const timestamp = new Date().toISOString();
    
    // 文脈圧縮
    const compressedContext = this.compressionEnabled ? 
      this.compressContext(context) : context;
    
    // 重要度に基づく選択保存
    const prioritizedContext = this.prioritizeContext(compressedContext);
    
    this.contextStore.set(sessionId, {
      context: prioritizedContext,
      timestamp: timestamp,
      size: this.calculateSize(prioritizedContext),
      metadata: this.extractMetadata(context)
    });
    
    // セッション履歴更新
    this.updateSessionHistory(sessionId, timestamp);
    
    // サイズ管理
    this.enforceStorageLimit();
    
    return {
      saved: true,
      sessionId: sessionId,
      size: this.calculateSize(prioritizedContext),
      timestamp: timestamp
    };
  }

  /**
   * 文脈復元
   * @param {string} sessionId - セッションID
   * @returns {Object} 復元された文脈
   */
  restoreContext(sessionId) {
    const stored = this.contextStore.get(sessionId);
    
    if (!stored) {
      return this.createNewContext();
    }
    
    // 文脈展開
    const expandedContext = this.expandContext(stored.context);
    
    // 関連文脈の統合
    const enrichedContext = this.enrichWithRelatedContexts(expandedContext, sessionId);
    
    return {
      context: enrichedContext,
      metadata: stored.metadata,
      lastUpdate: stored.timestamp,
      continuity: this.calculateContinuity(sessionId)
    };
  }

  /**
   * 文脈圧縮
   * @param {Object} context 
   * @returns {Object} 圧縮された文脈
   */
  compressContext(context) {
    return {
      // 重要情報の抽出
      instructions: this.extractInstructions(context),
      decisions: this.extractDecisions(context),
      activeProjects: this.extractActiveProjects(context),
      teamStatus: this.extractTeamStatus(context),
      summary: this.generateContextSummary(context)
    };
  }

  /**
   * 文脈優先順位付け
   * @param {Object} context 
   * @returns {Object} 優先順位付けされた文脈
   */
  prioritizeContext(context) {
    const prioritized = {};
    
    // 優先度高: 進行中プロジェクト
    if (context.activeProjects) {
      prioritized.activeProjects = context.activeProjects.filter(p => 
        p.status === 'in_progress' || p.priority === 'urgent'
      );
    }
    
    // 優先度高: 最近の指示
    if (context.instructions) {
      prioritized.recentInstructions = context.instructions.slice(-10);
    }
    
    // 優先度中: チーム状況
    if (context.teamStatus) {
      prioritized.teamStatus = {
        availability: context.teamStatus.availability,
        workload: context.teamStatus.workload
      };
    }
    
    // 優先度低: サマリーのみ
    prioritized.summary = context.summary || this.generateQuickSummary(context);
    
    return prioritized;
  }

  /**
   * 文脈展開
   * @param {Object} compressedContext 
   * @returns {Object} 展開された文脈
   */
  expandContext(compressedContext) {
    const expanded = { ...compressedContext };
    
    // 不足情報の補完
    if (!expanded.systemHealth) {
      expanded.systemHealth = this.getDefaultSystemHealth();
    }
    
    // 文脈間の関連付け復元
    if (expanded.activeProjects) {
      expanded.projectRelations = this.inferProjectRelations(expanded.activeProjects);
    }
    
    return expanded;
  }

  /**
   * 関連文脈による強化
   * @param {Object} context 
   * @param {string} sessionId 
   * @returns {Object} 強化された文脈
   */
  enrichWithRelatedContexts(context, sessionId) {
    const relatedSessions = this.findRelatedSessions(sessionId);
    
    relatedSessions.forEach(relatedId => {
      const relatedContext = this.contextStore.get(relatedId);
      if (relatedContext) {
        // 関連プロジェクト情報の統合
        context.relatedProjects = context.relatedProjects || [];
        context.relatedProjects.push(...this.extractRelevantProjects(relatedContext));
        
        // 過去の判断履歴の追加
        context.historicalDecisions = context.historicalDecisions || [];
        context.historicalDecisions.push(...this.extractRelevantDecisions(relatedContext));
      }
    });
    
    return context;
  }

  /**
   * ストレージ制限管理
   */
  enforceStorageLimit() {
    let totalSize = 0;
    const entries = Array.from(this.contextStore.entries());
    
    // サイズ計算
    entries.forEach(([_, value]) => {
      totalSize += value.size;
    });
    
    // 制限超過時の処理
    if (totalSize > this.maxContextSize * 2) { // 2倍まで許容
      // 古い/優先度低い文脈を削除
      const sortedEntries = entries.sort((a, b) => 
        new Date(a[1].timestamp) - new Date(b[1].timestamp)
      );
      
      let removed = 0;
      while (totalSize > this.maxContextSize && removed < sortedEntries.length / 2) {
        const [sessionId] = sortedEntries[removed];
        const entry = this.contextStore.get(sessionId);
        
        // 重要でない文脈のみ削除
        if (!this.isImportantContext(entry)) {
          totalSize -= entry.size;
          this.contextStore.delete(sessionId);
        }
        removed++;
      }
    }
  }

  /**
   * セッション間継続性確保
   * @param {string} fromSessionId 
   * @param {string} toSessionId 
   */
  bridgeSessions(fromSessionId, toSessionId) {
    const fromContext = this.restoreContext(fromSessionId);
    const bridgedContext = {
      ...fromContext.context,
      previousSession: fromSessionId,
      bridgedAt: new Date().toISOString(),
      continuityScore: fromContext.continuity
    };
    
    this.saveContext(toSessionId, bridgedContext);
    
    return {
      bridged: true,
      from: fromSessionId,
      to: toSessionId,
      continuity: fromContext.continuity
    };
  }

  /**
   * 継続性スコア計算
   * @param {string} sessionId 
   * @returns {number} 継続性スコア (0-1)
   */
  calculateContinuity(sessionId) {
    const stored = this.contextStore.get(sessionId);
    if (!stored) return 0;
    
    const timeSinceUpdate = Date.now() - new Date(stored.timestamp).getTime();
    const hoursElapsed = timeSinceUpdate / (1000 * 60 * 60);
    
    // 時間経過による減衰
    const timeFactor = Math.max(0, 1 - (hoursElapsed / 24)); // 24時間で0
    
    // 文脈完全性
    const completeness = this.assessContextCompleteness(stored.context);
    
    // 関連セッション数
    const relatedCount = this.findRelatedSessions(sessionId).length;
    const relationFactor = Math.min(1, relatedCount / 5); // 5セッション以上で最大
    
    return (timeFactor * 0.5 + completeness * 0.3 + relationFactor * 0.2);
  }

  /**
   * 自動バックアップ
   */
  async autoBackup() {
    const backup = {
      contexts: Array.from(this.contextStore.entries()),
      history: this.sessionHistory,
      timestamp: new Date().toISOString()
    };
    
    // ローカルストレージまたはファイルシステムに保存
    try {
      localStorage.setItem('context_backup', JSON.stringify(backup));
      return { success: true, size: JSON.stringify(backup).length };
    } catch (error) {
      console.error('Backup failed:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * バックアップ復元
   */
  async restoreFromBackup() {
    try {
      const backup = JSON.parse(localStorage.getItem('context_backup') || '{}');
      
      if (backup.contexts) {
        this.contextStore = new Map(backup.contexts);
        this.sessionHistory = backup.history || [];
        return { success: true, restored: backup.contexts.length };
      }
      
      return { success: false, error: 'No backup found' };
    } catch (error) {
      console.error('Restore failed:', error);
      return { success: false, error: error.message };
    }
  }

  // ヘルパーメソッド
  initializePersistence() {
    // 定期バックアップ設定 (1時間ごと)
    setInterval(() => {
      this.autoBackup();
    }, 60 * 60 * 1000);
    
    // 起動時の復元試行
    this.restoreFromBackup();
  }

  calculateSize(obj) {
    return JSON.stringify(obj).length;
  }

  extractMetadata(context) {
    return {
      projectCount: context.activeProjects?.length || 0,
      instructionCount: context.instructions?.length || 0,
      teamMembers: context.teamStatus?.members || [],
      priority: context.priority || 'normal'
    };
  }

  updateSessionHistory(sessionId, timestamp) {
    this.sessionHistory.push({ sessionId, timestamp });
    // 最新1000件のみ保持
    if (this.sessionHistory.length > 1000) {
      this.sessionHistory = this.sessionHistory.slice(-1000);
    }
  }

  createNewContext() {
    return {
      context: {
        instructions: [],
        activeProjects: [],
        teamStatus: this.getDefaultTeamStatus(),
        systemHealth: this.getDefaultSystemHealth()
      },
      metadata: {
        created: new Date().toISOString(),
        isNew: true
      }
    };
  }

  getDefaultSystemHealth() {
    return { status: 'healthy', lastCheck: new Date().toISOString() };
  }

  getDefaultTeamStatus() {
    return { 
      availability: { dev1: 1.0, dev2: 1.0, dev3: 1.0 },
      workload: { dev1: 0, dev2: 0, dev3: 0 }
    };
  }

  findRelatedSessions(sessionId) {
    // 時間的に近いセッションを検索
    const related = [];
    const currentTime = this.contextStore.get(sessionId)?.timestamp;
    
    if (currentTime) {
      this.contextStore.forEach((value, key) => {
        if (key !== sessionId) {
          const timeDiff = Math.abs(new Date(currentTime) - new Date(value.timestamp));
          if (timeDiff < 24 * 60 * 60 * 1000) { // 24時間以内
            related.push(key);
          }
        }
      });
    }
    
    return related;
  }

  isImportantContext(entry) {
    return entry.metadata.priority === 'urgent' || 
           entry.metadata.projectCount > 0 ||
           entry.size > 10000;
  }

  extractInstructions(context) {
    return context.instructions || [];
  }

  extractDecisions(context) {
    return context.decisions || [];
  }

  extractActiveProjects(context) {
    return context.activeProjects || [];
  }

  extractTeamStatus(context) {
    return context.teamStatus || this.getDefaultTeamStatus();
  }

  generateContextSummary(context) {
    return `Projects: ${context.activeProjects?.length || 0}, Instructions: ${context.instructions?.length || 0}`;
  }

  generateQuickSummary(context) {
    return `Context from ${new Date().toISOString()}`;
  }

  inferProjectRelations(projects) {
    // プロジェクト間の関連性を推論
    return projects.map(p => p.id);
  }

  extractRelevantProjects(relatedContext) {
    return relatedContext.context?.activeProjects || [];
  }

  extractRelevantDecisions(relatedContext) {
    return relatedContext.context?.decisions || [];
  }

  assessContextCompleteness(context) {
    let score = 0;
    if (context.instructions?.length > 0) score += 0.25;
    if (context.activeProjects?.length > 0) score += 0.25;
    if (context.teamStatus) score += 0.25;
    if (context.summary) score += 0.25;
    return score;
  }
}

module.exports = ContextPersistenceSystem;