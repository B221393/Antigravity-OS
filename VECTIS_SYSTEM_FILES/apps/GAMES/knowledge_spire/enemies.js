/**
 * KNOWLEDGE SPIRE - Enemy Definitions
 * 敵キャラクター定義
 */

// ============================================
// 敵の行動パターン
// ============================================
const INTENT_TYPES = {
    ATTACK: 'attack',
    DEFEND: 'defend',
    BUFF: 'buff',
    DEBUFF: 'debuff',
    UNKNOWN: 'unknown'
};

// ============================================
// 通常敵（フロア1-3）
// ============================================
const FLOOR_1_ENEMIES = [
    {
        id: 'slime',
        name: 'スライム',
        sprite: '🟢',
        hp: 12,
        maxHp: 12,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 5, icon: '⚔️' },
            { type: INTENT_TYPES.ATTACK, damage: 8, icon: '⚔️' },
        ]
    },
    {
        id: 'goblin',
        name: 'ゴブリン',
        sprite: '👺',
        hp: 18,
        maxHp: 18,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 6, icon: '⚔️' },
            { type: INTENT_TYPES.ATTACK, damage: 4, times: 2, icon: '⚔️×2' },
            { type: INTENT_TYPES.DEFEND, block: 6, icon: '🛡️' },
        ]
    },
    {
        id: 'cultist',
        name: 'カルト信者',
        sprite: '🧙',
        hp: 22,
        maxHp: 22,
        ritual: 0,
        patterns: [
            { type: INTENT_TYPES.BUFF, buff: { type: 'ritual', amount: 1 }, icon: '✨' },
            { type: INTENT_TYPES.ATTACK, damage: 6, usesRitual: true, icon: '⚔️' },
        ]
    },
];

// ============================================
// 中盤敵（フロア4-6）
// ============================================
const FLOOR_2_ENEMIES = [
    {
        id: 'wizard',
        name: '闇の魔術師',
        sprite: '🧙‍♂️',
        hp: 35,
        maxHp: 35,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 12, icon: '🔥' },
            { type: INTENT_TYPES.DEBUFF, debuff: { type: 'weak', amount: 2 }, icon: '💫' },
            { type: INTENT_TYPES.DEFEND, block: 10, icon: '🛡️' },
        ]
    },
    {
        id: 'knight',
        name: '堕落した騎士',
        sprite: '🗡️',
        hp: 45,
        maxHp: 45,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 10, icon: '⚔️' },
            { type: INTENT_TYPES.ATTACK, damage: 6, times: 2, icon: '⚔️×2' },
            { type: INTENT_TYPES.DEFEND, block: 12, damage: 5, icon: '🛡️⚔️' },
        ]
    },
    {
        id: 'ignorance',
        name: '無知の化身',
        sprite: '👁️',
        hp: 40,
        maxHp: 40,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 15, icon: '💀' },
            { type: INTENT_TYPES.DEBUFF, debuff: { type: 'confused', amount: 1 }, icon: '❓' },
            { type: INTENT_TYPES.ATTACK, damage: 8, times: 2, icon: '⚔️×2' },
        ]
    },
];

// ============================================
// 上層敵（フロア7-9）
// ============================================
const FLOOR_3_ENEMIES = [
    {
        id: 'demon',
        name: '知識を喰らう悪魔',
        sprite: '👿',
        hp: 60,
        maxHp: 60,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 20, icon: '🔥' },
            { type: INTENT_TYPES.BUFF, buff: { type: 'strength', amount: 2 }, icon: '💪' },
            { type: INTENT_TYPES.ATTACK, damage: 8, times: 3, icon: '⚔️×3' },
        ]
    },
    {
        id: 'sphinx',
        name: 'スフィンクス',
        sprite: '🦁',
        hp: 55,
        maxHp: 55,
        asksRiddles: true,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 18, icon: '💀' },
            { type: INTENT_TYPES.UNKNOWN, icon: '❓' }, // 謎かけ
            { type: INTENT_TYPES.DEFEND, block: 15, icon: '🛡️' },
        ]
    },
];

// ============================================
// ボス
// ============================================
const BOSSES = {
    floor3: {
        id: 'slime_king',
        name: 'スライムキング',
        sprite: '👑🟢',
        hp: 80,
        maxHp: 80,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 15, icon: '⚔️' },
            { type: INTENT_TYPES.BUFF, buff: { type: 'strength', amount: 2 }, summon: 'slime', icon: '✨+🟢' },
            { type: INTENT_TYPES.ATTACK, damage: 25, chargeUp: true, icon: '💥' },
        ]
    },
    floor6: {
        id: 'ignorance_lord',
        name: '無知の王',
        sprite: '🌑',
        hp: 120,
        maxHp: 120,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 20, icon: '💀' },
            { type: INTENT_TYPES.DEBUFF, debuff: { type: 'weak', amount: 2 }, debuff2: { type: 'vulnerable', amount: 2 }, icon: '💫💫' },
            { type: INTENT_TYPES.ATTACK, damage: 10, times: 3, icon: '⚔️×3' },
            { type: INTENT_TYPES.DEFEND, block: 20, heal: 10, icon: '🛡️❤️' },
        ]
    },
    floor10: {
        id: 'truth_guardian',
        name: '真理の守護者',
        sprite: '⚡👁️⚡',
        hp: 200,
        maxHp: 200,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 25, icon: '⚡' },
            { type: INTENT_TYPES.UNKNOWN, quizRequired: true, icon: '❓' },
            { type: INTENT_TYPES.ATTACK, damage: 12, times: 3, icon: '⚔️×3' },
            { type: INTENT_TYPES.BUFF, buff: { type: 'strength', amount: 3 }, icon: '💪' },
        ]
    }
};

// ============================================
// エリート敵
// ============================================
const ELITE_ENEMIES = [
    {
        id: 'lagger',
        name: 'ラガヴーリン（知の番人）',
        sprite: '⚔️💤',
        hp: 50,
        maxHp: 50,
        sleeping: true,
        wakeThreshold: 2,
        patterns: [
            { type: INTENT_TYPES.UNKNOWN, icon: '💤' }, // 寝ている
            { type: INTENT_TYPES.ATTACK, damage: 18, icon: '⚔️' },
            { type: INTENT_TYPES.DEBUFF, debuff: { type: 'weak', amount: 1 }, debuff2: { type: 'dexDown', amount: 1 }, icon: '💫' },
        ]
    },
    {
        id: 'gremlin_nob',
        name: 'グレムリンの親分',
        sprite: '👹',
        hp: 65,
        maxHp: 65,
        enrageOnSkill: true,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 12, icon: '⚔️' },
            { type: INTENT_TYPES.ATTACK, damage: 20, icon: '💥' },
            { type: INTENT_TYPES.BUFF, buff: { type: 'enrage', amount: 2 }, icon: '😤' },
        ]
    },
    {
        id: 'three_sentries',
        name: '三体の番兵',
        sprite: '🛡️🛡️🛡️',
        hp: 40,
        maxHp: 40,
        multiEnemy: 3,
        patterns: [
            { type: INTENT_TYPES.ATTACK, damage: 10, icon: '⚔️' },
            { type: INTENT_TYPES.DEFEND, block: 8, icon: '🛡️' },
        ]
    },
];

// ============================================
// ヘルパー関数
// ============================================
function getRandomEnemy(floor) {
    let pool;
    if (floor <= 3) {
        pool = FLOOR_1_ENEMIES;
    } else if (floor <= 6) {
        pool = FLOOR_2_ENEMIES;
    } else {
        pool = FLOOR_3_ENEMIES;
    }

    const template = pool[Math.floor(Math.random() * pool.length)];
    return createEnemyInstance(template, floor);
}

function createEnemyInstance(template, floor = 1) {
    const hpScale = 1 + (floor - 1) * 0.1; // 階が上がるとHP増加
    return {
        ...template,
        hp: Math.floor(template.hp * hpScale),
        maxHp: Math.floor(template.maxHp * hpScale),
        block: 0,
        buffs: {},
        debuffs: {},
        currentPatternIndex: 0,
        turnsTaken: 0
    };
}

function getBoss(floor) {
    if (floor === 3) return createEnemyInstance(BOSSES.floor3, floor);
    if (floor === 6) return createEnemyInstance(BOSSES.floor6, floor);
    if (floor >= 10) return createEnemyInstance(BOSSES.floor10, floor);
    return null;
}

function getElite(floor) {
    const template = ELITE_ENEMIES[Math.floor(Math.random() * ELITE_ENEMIES.length)];
    return createEnemyInstance(template, floor);
}

function getEnemyIntent(enemy) {
    const patterns = enemy.patterns;
    const pattern = patterns[enemy.currentPatternIndex % patterns.length];
    return pattern;
}

function advanceEnemyPattern(enemy) {
    enemy.currentPatternIndex = (enemy.currentPatternIndex + 1) % enemy.patterns.length;
    enemy.turnsTaken++;
}

// Export
window.INTENT_TYPES = INTENT_TYPES;
window.FLOOR_1_ENEMIES = FLOOR_1_ENEMIES;
window.FLOOR_2_ENEMIES = FLOOR_2_ENEMIES;
window.FLOOR_3_ENEMIES = FLOOR_3_ENEMIES;
window.BOSSES = BOSSES;
window.ELITE_ENEMIES = ELITE_ENEMIES;
window.getRandomEnemy = getRandomEnemy;
window.createEnemyInstance = createEnemyInstance;
window.getBoss = getBoss;
window.getElite = getElite;
window.getEnemyIntent = getEnemyIntent;
window.advanceEnemyPattern = advanceEnemyPattern;
