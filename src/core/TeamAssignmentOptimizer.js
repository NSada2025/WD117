/**
 * チーム編成最適化システム
 * タスクの特性に基づいて最適なチーム配置を推薦
 */

const RoleAwareOptimizer = require('./RoleAwareOptimizer');

class TeamAssignmentOptimizer {
  constructor() {
    this.roleOptimizer = new RoleAwareOptimizer();
    this.teamMatrix = {
      // タスクタイプ → 必要スキル → 推奨dev
      "web_development": {
        skills: ["frontend", "backend", "ui/ux"],
        primary: "dev1",
        secondary: "dev2",
        support: "dev3"
      },
      "data_analysis": {
        skills: ["python", "matlab", "statistics"],
        primary: "dev2",
        secondary: "dev1",
        support: "dev3"
      },
      "system_infrastructure": {
        skills: ["devops", "docker", "ci/cd"],
        primary: "dev3",
        secondary: "dev1",
        support: "dev2"
      },
      "research_tools": {
        skills: ["domain_knowledge", "tool_development"],
        primary: "dev1",
        secondary: "dev2",
        support: "dev3"
      },
      "project_management": {
        skills: ["coordination", "documentation"],
        primary: "dev1",
        secondary: "dev2",
        support: "dev3"
      },
      "emergency": {
        skills: ["quick_response", "troubleshooting"],
        primary: "dev1",
        secondary: "dev2", 
        support: "dev3"
      }
    };

    // dev能力プロファイル
    this.devCapabilities = {
      dev1: {
        skills: ["ui/ux", "frontend", "research_tools", "documentation", "coordination"],
        strength: ["problem_solving", "communication", "quick_learning"],
        currentLoad: 0,
        availability: 1.0,
        recentPerformance: 0.9
      },
      dev2: {
        skills: ["data_analysis", "python", "matlab", "backend", "statistics"],
        strength: ["analytical_thinking", "technical_depth", "research"],
        currentLoad: 0,
        availability: 1.0,
        recentPerformance: 0.85
      },
      dev3: {
        skills: ["infrastructure", "testing", "qa", "devops", "docker"],
        strength: ["system_design", "reliability", "automation"],
        currentLoad: 0,
        availability: 1.0,
        recentPerformance: 0.8
      }
    };
  }

  /**
   * 最適チーム編成を推薦
   * @param {Object} taskInfo - タスク情報
   * @returns {Object} チーム編成推薦
   */
  recommendTeam(taskInfo) {
    const taskMapping = this.mapTaskToType(taskInfo.taskType);
    const teamCapacity = this.evaluateTeamCapacity();
    const optimalAssignment = this.calculateOptimalAssignment(taskInfo, taskMapping, teamCapacity);
    
    // 役割認識による最適化
    const roleOptimized = this.roleOptimizer.optimizeTeamAssignmentByRole(taskInfo, optimalAssignment);
    
    return {
      primary: roleOptimized.primary,
      secondary: roleOptimized.secondary,
      support: roleOptimized.support,
      reasoning: roleOptimized.reasoning,
      confidence: roleOptimized.confidence,
      alternatives: roleOptimized.alternatives,
      estimatedEfficiency: roleOptimized.efficiency || optimalAssignment.efficiency,
      roleOptimizations: roleOptimized.roleOptimizations
    };
  }

  /**
   * タスクタイプマッピング
   * @param {string} taskType 
   * @returns {Object} マッピング情報
   */
  mapTaskToType(taskType) {
    const mapping = {
      "project_create": "web_development",
      "project_fix": "research_tools", 
      "project_improve": "web_development",
      "research": "research_tools",
      "analysis": "data_analysis",
      "documentation": "project_management",
      "infrastructure": "system_infrastructure",
      "configuration": "system_infrastructure",
      "testing": "system_infrastructure",
      "emergency": "emergency"
    };
    
    return this.teamMatrix[mapping[taskType]] || this.teamMatrix["research_tools"];
  }

  /**
   * チーム能力評価
   * @returns {Object} 現在のチーム状況
   */
  evaluateTeamCapacity() {
    const capacity = {};
    
    for (const [devId, capabilities] of Object.entries(this.devCapabilities)) {
      capacity[devId] = {
        currentLoad: this.getCurrentWorkload(devId),
        skills: capabilities.skills,
        availability: this.calculateAvailability(devId),
        recentPerformance: capabilities.recentPerformance,
        efficiency: this.calculateEfficiency(devId)
      };
    }
    
    return capacity;
  }

  /**
   * 現在の作業負荷取得
   * @param {string} devId 
   * @returns {number} 作業負荷 (0-1)
   */
  getCurrentWorkload(devId) {
    // 実際の実装では、現在のタスク状況を確認
    return this.devCapabilities[devId].currentLoad;
  }

  /**
   * 利用可能性計算
   * @param {string} devId 
   * @returns {number} 利用可能性 (0-1)
   */
  calculateAvailability(devId) {
    const load = this.getCurrentWorkload(devId);
    return Math.max(0, 1 - load); // 作業負荷が高いほど利用可能性は低下
  }

  /**
   * 効率性計算
   * @param {string} devId 
   * @returns {number} 効率性スコア (0-1)
   */
  calculateEfficiency(devId) {
    const dev = this.devCapabilities[devId];
    return (dev.availability * 0.4 + dev.recentPerformance * 0.6);
  }

  /**
   * 最適配置計算
   * @param {Object} taskInfo 
   * @param {Object} taskMapping 
   * @param {Object} teamCapacity 
   * @returns {Object} 最適配置
   */
  calculateOptimalAssignment(taskInfo, taskMapping, teamCapacity) {
    const skillMatches = this.calculateSkillMatches(taskMapping.skills, teamCapacity);
    const loadBalancing = this.calculateLoadBalancing(teamCapacity);
    const urgencyFactor = this.calculateUrgencyFactor(taskInfo.priority);
    
    // スコア計算
    const scores = {};
    for (const devId of Object.keys(teamCapacity)) {
      scores[devId] = (
        skillMatches[devId] * 0.4 +
        loadBalancing[devId] * 0.3 +
        teamCapacity[devId].recentPerformance * 0.2 +
        urgencyFactor[devId] * 0.1
      );
    }
    
    // ランキング作成
    const ranking = Object.entries(scores)
      .sort(([,a], [,b]) => b - a)
      .map(([devId]) => devId);
    
    const assignment = {
      primary: ranking[0],
      secondary: ranking[1],
      support: ranking[2],
      reasoning: this.generateReasoning(ranking, skillMatches, taskInfo),
      confidence: this.calculateConfidence(scores, taskInfo),
      alternatives: this.generateAlternatives(ranking, scores),
      efficiency: this.estimateTeamEfficiency(ranking, teamCapacity, taskInfo)
    };
    
    return assignment;
  }

  /**
   * スキルマッチング計算
   * @param {Array} requiredSkills 
   * @param {Object} teamCapacity 
   * @returns {Object} スキルマッチスコア
   */
  calculateSkillMatches(requiredSkills, teamCapacity) {
    const matches = {};
    
    for (const [devId, capacity] of Object.entries(teamCapacity)) {
      const matchCount = requiredSkills.filter(skill => 
        capacity.skills.includes(skill)
      ).length;
      matches[devId] = requiredSkills.length > 0 ? matchCount / requiredSkills.length : 0.5;
    }
    
    return matches;
  }

  /**
   * 負荷分散計算
   * @param {Object} teamCapacity 
   * @returns {Object} 負荷分散スコア
   */
  calculateLoadBalancing(teamCapacity) {
    const balancing = {};
    
    for (const [devId, capacity] of Object.entries(teamCapacity)) {
      balancing[devId] = capacity.availability;
    }
    
    return balancing;
  }

  /**
   * 緊急度ファクター計算
   * @param {string} priority 
   * @returns {Object} 緊急度対応スコア
   */
  calculateUrgencyFactor(priority) {
    const factor = {};
    const urgencyBonus = priority === "urgent" ? 0.2 : 0;
    
    // 緊急時は経験豊富で対応力の高いdevを優遇
    factor.dev1 = 0.8 + urgencyBonus; // コミュニケーション能力が高い
    factor.dev2 = 0.6 + urgencyBonus; // 技術的深度が高い
    factor.dev3 = 0.7 + urgencyBonus; // システム全体への理解が深い
    
    return factor;
  }

  /**
   * 推薦理由生成
   * @param {Array} ranking 
   * @param {Object} skillMatches 
   * @param {Object} taskInfo 
   * @returns {string} 推薦理由
   */
  generateReasoning(ranking, skillMatches, taskInfo) {
    const primary = ranking[0];
    const skillMatch = skillMatches[primary];
    const taskType = taskInfo.taskType;
    
    let reasoning = `${primary}を主担当に推薦: `;
    
    if (skillMatch >= 0.8) {
      reasoning += "必要スキルとの適合度が非常に高い";
    } else if (skillMatch >= 0.6) {
      reasoning += "必要スキルとの適合度が高い";
    } else {
      reasoning += "総合的な能力と利用可能性を考慮";
    }
    
    if (taskInfo.priority === "urgent") {
      reasoning += "。緊急対応能力も考慮。";
    }
    
    return reasoning;
  }

  /**
   * 信頼度計算
   * @param {Object} scores 
   * @param {Object} taskInfo 
   * @returns {number} 信頼度 (0-1)
   */
  calculateConfidence(scores, taskInfo) {
    const sortedScores = Object.values(scores).sort((a, b) => b - a);
    const topScore = sortedScores[0];
    const secondScore = sortedScores[1];
    
    // トップとセカンドの差が大きいほど信頼度が高い
    const scoreDifference = topScore - secondScore;
    const baseConfidence = Math.min(1, scoreDifference + 0.5);
    
    // タスクの複雑度が低いほど信頼度が高い
    const complexityFactor = taskInfo.complexity.level === "low" ? 0.1 : 
                           taskInfo.complexity.level === "medium" ? 0.05 : 0;
    
    return Math.min(1, baseConfidence + complexityFactor);
  }

  /**
   * 代替案生成
   * @param {Array} ranking 
   * @param {Object} scores 
   * @returns {Array} 代替案
   */
  generateAlternatives(ranking, scores) {
    return [
      {
        primary: ranking[1],
        secondary: ranking[0],
        reason: "作業負荷分散を重視した配置",
        score: scores[ranking[1]]
      },
      {
        primary: ranking[0],
        secondary: ranking[2],
        reason: "スキル補完を重視した配置",
        score: (scores[ranking[0]] + scores[ranking[2]]) / 2
      }
    ];
  }

  /**
   * チーム効率性推定
   * @param {Array} ranking 
   * @param {Object} teamCapacity 
   * @param {Object} taskInfo 
   * @returns {number} 効率性スコア (0-1)
   */
  estimateTeamEfficiency(ranking, teamCapacity, taskInfo) {
    const primaryEfficiency = teamCapacity[ranking[0]].efficiency;
    const teamSize = taskInfo.teamSize;
    
    if (teamSize === 1) {
      return primaryEfficiency;
    } else if (teamSize === 2) {
      const secondaryEfficiency = teamCapacity[ranking[1]].efficiency;
      return (primaryEfficiency * 0.7 + secondaryEfficiency * 0.3);
    } else {
      const secondaryEfficiency = teamCapacity[ranking[1]].efficiency;
      const supportEfficiency = teamCapacity[ranking[2]].efficiency;
      return (primaryEfficiency * 0.5 + secondaryEfficiency * 0.3 + supportEfficiency * 0.2);
    }
  }

  /**
   * 作業負荷更新
   * @param {string} devId 
   * @param {number} addedLoad 
   */
  updateWorkload(devId, addedLoad) {
    if (this.devCapabilities[devId]) {
      this.devCapabilities[devId].currentLoad = Math.min(1, 
        this.devCapabilities[devId].currentLoad + addedLoad
      );
    }
  }

  /**
   * パフォーマンス更新
   * @param {string} devId 
   * @param {number} newPerformance 
   */
  updatePerformance(devId, newPerformance) {
    if (this.devCapabilities[devId]) {
      this.devCapabilities[devId].recentPerformance = newPerformance;
    }
  }

  /**
   * チーム推薦のテスト実行
   * @param {Object} taskInfo 
   */
  testTeamAssignment(taskInfo) {
    console.log(`=== チーム編成テスト ===`);
    console.log(`タスク: ${taskInfo.taskType}`);
    console.log(`複雑度: ${taskInfo.complexity.level}`);
    console.log(`優先度: ${taskInfo.priority}`);
    
    const recommendation = this.recommendTeam(taskInfo);
    
    console.log(`推薦チーム:`);
    console.log(`  主担当: ${recommendation.primary}`);
    console.log(`  副担当: ${recommendation.secondary}`);
    console.log(`  支援: ${recommendation.support}`);
    console.log(`推薦理由: ${recommendation.reasoning}`);
    console.log(`信頼度: ${(recommendation.confidence * 100).toFixed(1)}%`);
    console.log(`期待効率: ${(recommendation.estimatedEfficiency * 100).toFixed(1)}%`);
    console.log(`===================\n`);
    
    return recommendation;
  }
}

module.exports = TeamAssignmentOptimizer;