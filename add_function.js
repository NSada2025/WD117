/**
 * 数値の加算を行う関数
 * @param {number} a - 第一引数
 * @param {number} b - 第二引数
 * @returns {number} a と b の和
 */
function add(a, b) {
  // 入力値の型チェック
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new TypeError('両方の引数は数値である必要があります');
  }
  
  // NaN チェック
  if (isNaN(a) || isNaN(b)) {
    throw new Error('NaN は有効な入力ではありません');
  }
  
  // 無限大チェック
  if (!isFinite(a) || !isFinite(b)) {
    throw new Error('無限大は有効な入力ではありません');
  }
  
  // 正確な計算を実行
  return a + b;
}

// テストケース
console.log('=== add関数のテスト ===');
console.log('add(1, 1) =', add(1, 1)); // 2
console.log('add(0, 0) =', add(0, 0)); // 0
console.log('add(-1, 1) =', add(-1, 1)); // 0
console.log('add(0.1, 0.2) =', add(0.1, 0.2)); // 0.30000000000000004 (浮動小数点の精度問題)
console.log('add(10, -5) =', add(10, -5)); // 5

// エラーケースのテスト
try {
  add('1', 1);
} catch (e) {
  console.log('エラーテスト (文字列):', e.message);
}

try {
  add(NaN, 1);
} catch (e) {
  console.log('エラーテスト (NaN):', e.message);
}

try {
  add(Infinity, 1);
} catch (e) {
  console.log('エラーテスト (無限大):', e.message);
}

module.exports = add;