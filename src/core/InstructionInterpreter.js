/**
 * CEO指示自動解釈エンジン
 * 自然言語の指示を解析し、実行可能なタスクに変換
 */

const RoleAwareOptimizer = require('./RoleAwareOptimizer');

class InstructionInterpreter {
  constructor() {
    this.roleOptimizer = new RoleAwareOptimizer();
    this.instructionPatterns = {
      // プロジェクト系
      "新しい.*作って": { type: "project_create", complexity: "medium" },
      ".*を修正": { type: "project_fix", complexity: "low" },
      ".*を改善": { type: "project_improve", complexity: "medium" },
      "緊急.*対応": { type: "emergency", complexity: "high", priority: "urgent" },
      
      // 分析系
      ".*を調査": { type: "research", complexity: "medium" },
      ".*を分析": { type: "analysis", complexity: "high" },
      "レポート.*作成": { type: "documentation", complexity: "low" },
      
      // システム系
      "環境.*構築": { type: "infrastructure", complexity: "high" },
      "設定.*変更": { type: "configuration", complexity: "low" },
      "テスト.*実行": { type: "testing", complexity: "medium" }
    };

    this.complexityFactors = {
      keywords: {
        "緊急": 0.8,
        "大規模": 0.7,
        "完全": 0.6,
        "詳細": 0.5,
        "簡単": -0.3,
        "修正": -0.2
      },
      scope: {
        "全体": 0.8,
        "システム": 0.7,
        "複数": 0.5,
        "単一": -0.3,
        "部分": -0.2
      }
    };
  }

  /**
   * 指示を解析してタスク情報を抽出
   * @param {string} instruction - CEO指示文
   * @returns {Object} 解析結果
   */
  parseInstruction(instruction) {
    // 品質検証タスクの特別処理
    const optimizedInstruction = this.roleOptimizer.optimizeQualityVerificationInstructions({
      instruction: instruction
    });
    
    const matchedPattern = this.findMatchingPattern(optimizedInstruction.instruction);
    const complexity = this.assessComplexity(optimizedInstruction.instruction);
    const taskDecomposition = this.autoDecomposeTask(optimizedInstruction.instruction, complexity);
    
    const result = {
      originalInstruction: instruction,
      taskType: matchedPattern.type,
      complexity: complexity,
      subTasks: taskDecomposition.subTasks,
      dependencies: taskDecomposition.dependencies,
      estimatedTime: complexity.estimatedTime,
      requiredSkills: complexity.requiredSkills,
      teamSize: complexity.teamSize,
      priority: matchedPattern.priority || "normal"
    };
    
    // 品質検証タスクのメタデータを統合
    if (optimizedInstruction.metadata) {
      result.metadata = optimizedInstruction.metadata;
    }
    
    return result;
  }

  /**
   * 指示パターンマッチング
   * @param {string} instruction 
   * @returns {Object} マッチしたパターン情報
   */
  findMatchingPattern(instruction) {
    for (const [pattern, info] of Object.entries(this.instructionPatterns)) {
      const regex = new RegExp(pattern, 'i');
      if (regex.test(instruction)) {
        return info;
      }
    }
    
    // デフォルト
    return { type: "general", complexity: "medium" };
  }

  /**
   * 複雑度自動判定
   * @param {string} instruction 
   * @returns {Object} 複雑度情報
   */
  assessComplexity(instruction) {
    const factors = {
      keywords: this.analyzeKeywords(instruction),
      scope: this.determineScope(instruction),
      urgency: this.detectUrgency(instruction),
      dependencies: this.identifyDependencies(instruction)
    };
    
    const complexityScore = this.calculateComplexityScore(factors);
    
    return {
      level: this.mapScoreToLevel(complexityScore),
      score: complexityScore,
      estimatedTime: this.estimateTime(complexityScore),
      requiredSkills: this.identifyRequiredSkills(factors),
      teamSize: this.recommendTeamSize(complexityScore),
      factors: factors
    };
  }

  /**
   * キーワード分析
   * @param {string} instruction 
   * @returns {number} キーワードスコア
   */
  analyzeKeywords(instruction) {
    let score = 0;
    for (const [keyword, weight] of Object.entries(this.complexityFactors.keywords)) {
      if (instruction.includes(keyword)) {
        score += weight;
      }
    }
    return Math.max(0, Math.min(1, score + 0.5)); // 0-1に正規化
  }

  /**
   * スコープ判定
   * @param {string} instruction 
   * @returns {number} スコープスコア
   */
  determineScope(instruction) {
    let score = 0.5; // デフォルト
    for (const [scope, weight] of Object.entries(this.complexityFactors.scope)) {
      if (instruction.includes(scope)) {
        score = Math.max(score, weight + 0.5);
      }
    }
    return Math.max(0, Math.min(1, score));
  }

  /**
   * 緊急度検知
   * @param {string} instruction 
   * @returns {number} 緊急度スコア
   */
  detectUrgency(instruction) {
    const urgencyKeywords = ["緊急", "至急", "即座", "すぐに", "今すぐ"];
    const found = urgencyKeywords.some(keyword => instruction.includes(keyword));
    return found ? 0.9 : 0.3;
  }

  /**
   * 依存関係識別
   * @param {string} instruction 
   * @returns {number} 依存関係スコア
   */
  identifyDependencies(instruction) {
    const dependencyKeywords = ["連携", "統合", "全体", "システム", "環境"];
    let score = 0.3; // デフォルト
    dependencyKeywords.forEach(keyword => {
      if (instruction.includes(keyword)) score += 0.1;
    });
    return Math.min(1, score);
  }

  /**
   * 複雑度スコア計算
   * @param {Object} factors 
   * @returns {number} 総合スコア
   */
  calculateComplexityScore(factors) {
    return (
      factors.keywords * 0.3 +
      factors.scope * 0.25 +
      factors.urgency * 0.25 +
      factors.dependencies * 0.2
    );
  }

  /**
   * スコアをレベルにマッピング
   * @param {number} score 
   * @returns {string} 複雑度レベル
   */
  mapScoreToLevel(score) {
    if (score >= 0.7) return "high";
    if (score >= 0.4) return "medium";
    return "low";
  }

  /**
   * 時間見積もり
   * @param {number} complexityScore 
   * @returns {string} 見積もり時間
   */
  estimateTime(complexityScore) {
    if (complexityScore >= 0.8) return "3-7日";
    if (complexityScore >= 0.6) return "1-3日";
    if (complexityScore >= 0.4) return "4-8時間";
    return "1-4時間";
  }

  /**
   * 必要スキル識別
   * @param {Object} factors 
   * @returns {Array} スキルリスト
   */
  identifyRequiredSkills(factors) {
    const skills = ["問題解決"];
    
    if (factors.scope > 0.6) skills.push("システム設計");
    if (factors.dependencies > 0.5) skills.push("統合・連携");
    if (factors.urgency > 0.7) skills.push("緊急対応");
    
    return skills;
  }

  /**
   * チームサイズ推薦
   * @param {number} complexityScore 
   * @returns {number} 推奨チームサイズ
   */
  recommendTeamSize(complexityScore) {
    if (complexityScore >= 0.7) return 3;
    if (complexityScore >= 0.4) return 2;
    return 1;
  }

  /**
   * タスク自動分解
   * @param {string} instruction 
   * @param {Object} complexity 
   * @returns {Object} 分解結果
   */
  autoDecomposeTask(instruction, complexity) {
    const decomposition = {
      mainTask: this.extractMainObjective(instruction),
      subTasks: [],
      dependencies: [],
      milestones: []
    };
    
    // 複雑度に応じた分解
    switch(complexity.level) {
      case 'low':
        decomposition.subTasks = this.simpleDecomposition(instruction);
        break;
      case 'medium':
        decomposition.subTasks = this.structuredDecomposition(instruction);
        break;
      case 'high':
        decomposition.subTasks = this.advancedDecomposition(instruction);
        decomposition.milestones = this.generateMilestones(decomposition.subTasks);
        break;
    }
    
    return decomposition;
  }

  /**
   * メイン目標抽出
   * @param {string} instruction 
   * @returns {string} メイン目標
   */
  extractMainObjective(instruction) {
    // 動詞と目的語を抽出
    const actionMatch = instruction.match(/(作成|修正|改善|調査|分析|構築|変更|実行).*?(を|して|してください)/);
    return actionMatch ? actionMatch[0] : instruction;
  }

  /**
   * 単純分解
   * @param {string} instruction 
   * @returns {Array} サブタスク
   */
  simpleDecomposition(instruction) {
    return [
      "要件確認",
      "実装",
      "確認・テスト"
    ];
  }

  /**
   * 構造化分解
   * @param {string} instruction 
   * @returns {Array} サブタスク
   */
  structuredDecomposition(instruction) {
    return [
      "現状分析",
      "設計・計画",
      "実装・開発",
      "テスト・検証",
      "文書化"
    ];
  }

  /**
   * 高度分解
   * @param {string} instruction 
   * @returns {Array} サブタスク
   */
  advancedDecomposition(instruction) {
    return [
      "要件定義・スコープ確定",
      "技術調査・アーキテクチャ設計",
      "チーム編成・リソース配置",
      "段階的実装・統合",
      "品質保証・テスト",
      "デプロイ・運用準備",
      "文書化・引き継ぎ"
    ];
  }

  /**
   * マイルストーン生成
   * @param {Array} subTasks 
   * @returns {Array} マイルストーン
   */
  generateMilestones(subTasks) {
    const milestones = [];
    const midpoint = Math.floor(subTasks.length / 2);
    
    milestones.push({
      name: "設計完了",
      taskIndex: midpoint,
      description: "基本設計と計画が完了"
    });
    
    milestones.push({
      name: "実装完了",
      taskIndex: subTasks.length - 2,
      description: "コア機能の実装が完了"
    });
    
    return milestones;
  }

  /**
   * 指示解釈のテスト実行
   * @param {string} instruction 
   */
  testInstruction(instruction) {
    console.log(`=== 指示解釈テスト ===`);
    console.log(`入力: "${instruction}"`);
    
    const result = this.parseInstruction(instruction);
    
    console.log(`タスクタイプ: ${result.taskType}`);
    console.log(`複雑度: ${result.complexity.level} (${result.complexity.score.toFixed(2)})`);
    console.log(`見積もり時間: ${result.estimatedTime}`);
    console.log(`必要スキル: ${result.requiredSkills.join(', ')}`);
    console.log(`推奨チームサイズ: ${result.teamSize}人`);
    console.log(`サブタスク: ${result.subTasks.join(' → ')}`);
    console.log(`================\n`);
    
    return result;
  }
}

module.exports = InstructionInterpreter;