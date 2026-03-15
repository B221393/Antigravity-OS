/**
 * KNOWLEDGE SPIRE - Card Definitions
 * カード定義（攻撃、スキル、パワー、知識カード）
 */

const CARD_TYPES = {
    ATTACK: 'attack',
    SKILL: 'skill',
    POWER: 'power',
    KNOWLEDGE: 'knowledge'
};

// ============================================
// スターターデッキカード
// ============================================
const STARTER_CARDS = [
    // 基本攻撃 x5
    {
        id: 'strike', name: '一撃', type: CARD_TYPES.ATTACK, cost: 1, icon: '⚔️',
        description: '敵に6ダメージ', effect: { damage: 6 }
    },
    {
        id: 'strike', name: '一撃', type: CARD_TYPES.ATTACK, cost: 1, icon: '⚔️',
        description: '敵に6ダメージ', effect: { damage: 6 }
    },
    {
        id: 'strike', name: '一撃', type: CARD_TYPES.ATTACK, cost: 1, icon: '⚔️',
        description: '敵に6ダメージ', effect: { damage: 6 }
    },
    {
        id: 'strike', name: '一撃', type: CARD_TYPES.ATTACK, cost: 1, icon: '⚔️',
        description: '敵に6ダメージ', effect: { damage: 6 }
    },
    {
        id: 'strike', name: '一撃', type: CARD_TYPES.ATTACK, cost: 1, icon: '⚔️',
        description: '敵に6ダメージ', effect: { damage: 6 }
    },

    // 基本防御 x5
    {
        id: 'defend', name: '防御', type: CARD_TYPES.SKILL, cost: 1, icon: '🛡️',
        description: 'ブロック5を得る', effect: { block: 5 }
    },
    {
        id: 'defend', name: '防御', type: CARD_TYPES.SKILL, cost: 1, icon: '🛡️',
        description: 'ブロック5を得る', effect: { block: 5 }
    },
    {
        id: 'defend', name: '防御', type: CARD_TYPES.SKILL, cost: 1, icon: '🛡️',
        description: 'ブロック5を得る', effect: { block: 5 }
    },
    {
        id: 'defend', name: '防御', type: CARD_TYPES.SKILL, cost: 1, icon: '🛡️',
        description: 'ブロック5を得る', effect: { block: 5 }
    },
    {
        id: 'defend', name: '防御', type: CARD_TYPES.SKILL, cost: 1, icon: '🛡️',
        description: 'ブロック5を得る', effect: { block: 5 }
    },
];

// ============================================
// 報酬プール（共通カード）
// ============================================
const COMMON_CARDS = [
    // 攻撃系
    {
        id: 'bash', name: '強打', type: CARD_TYPES.ATTACK, cost: 2, icon: '🔨',
        description: '敵に8ダメージ。弱体2を与える',
        effect: { damage: 8, debuff: { type: 'weak', amount: 2 } }
    },

    {
        id: 'cleave', name: '薙ぎ払い', type: CARD_TYPES.ATTACK, cost: 1, icon: '💫',
        description: '全敵に8ダメージ', effect: { damage: 8, aoe: true }
    },

    {
        id: 'quick_slash', name: '素早い斬撃', type: CARD_TYPES.ATTACK, cost: 1, icon: '⚡',
        description: 'カードを1枚引く。敵に5ダメージ',
        effect: { damage: 5, draw: 1 }
    },

    {
        id: 'anger', name: '怒り', type: CARD_TYPES.ATTACK, cost: 0, icon: '😤',
        description: '敵に6ダメージ。このカードのコピーを捨札に入れる',
        effect: { damage: 6, copyToDiscard: true }
    },

    // 防御系
    {
        id: 'armaments', name: '武装', type: CARD_TYPES.SKILL, cost: 1, icon: '🔧',
        description: 'ブロック5を得る。手札のカード1枚をアップグレード',
        effect: { block: 5, upgradeHand: 1 }
    },

    {
        id: 'shrug', name: '肩すくめ', type: CARD_TYPES.SKILL, cost: 1, icon: '🤷',
        description: 'ブロック8を得る。カードを1枚引く',
        effect: { block: 8, draw: 1 }
    },

    {
        id: 'true_grit', name: '根性', type: CARD_TYPES.SKILL, cost: 1, icon: '💪',
        description: 'ブロック7を得る。手札をランダムに1枚廃棄',
        effect: { block: 7, exhaustRandom: 1 }
    },
];

// ============================================
// レアカード
// ============================================
const RARE_CARDS = [
    {
        id: 'heavy_blade', name: '重剣', type: CARD_TYPES.ATTACK, cost: 2, icon: '🗡️',
        description: '14ダメージ。筋力3倍適用',
        effect: { damage: 14, strengthMultiplier: 3 }
    },

    {
        id: 'whirlwind', name: '旋風', type: CARD_TYPES.ATTACK, cost: 'X', icon: '🌀',
        description: '全敵にX×5ダメージ', effect: { damagePerEnergy: 5, aoe: true, costAll: true }
    },

    {
        id: 'impervious', name: '不屈', type: CARD_TYPES.SKILL, cost: 2, icon: '🏰',
        description: 'ブロック30を得る。廃棄',
        effect: { block: 30, exhaust: true }
    },

    {
        id: 'offering', name: '供物', type: CARD_TYPES.SKILL, cost: 0, icon: '🩸',
        description: 'HP6を失う。エネルギー2とカード3枚を得る。廃棄',
        effect: { selfDamage: 6, energy: 2, draw: 3, exhaust: true }
    },

    {
        id: 'demon_form', name: '悪魔の形', type: CARD_TYPES.POWER, cost: 3, icon: '👿',
        description: '毎ターン開始時、筋力2を得る',
        effect: { buff: { type: 'strengthPerTurn', amount: 2 } }
    },
];

// ============================================
// 知識カード（SPI・教養要素）
// ============================================
const KNOWLEDGE_CARDS = [
    // 数学系
    {
        id: 'math_logic', name: '論理的思考', type: CARD_TYPES.KNOWLEDGE, cost: 1, icon: '🧮',
        description: '正解で12ダメージ、不正解で6ダメージ',
        effect: { quizDamage: 12, failDamage: 6 },
        quiz: { type: 'math', difficulty: 1 }
    },

    {
        id: 'probability', name: '確率論', type: CARD_TYPES.KNOWLEDGE, cost: 2, icon: '🎲',
        description: '正解でカード2枚引く＋ブロック10',
        effect: { quizDraw: 2, quizBlock: 10 },
        quiz: { type: 'probability', difficulty: 2 }
    },

    // 言語系
    {
        id: 'vocabulary', name: '語彙力', type: CARD_TYPES.KNOWLEDGE, cost: 1, icon: '📖',
        description: '正解で全敵に8ダメージ',
        effect: { quizDamage: 8, quizAoe: true },
        quiz: { type: 'vocabulary', difficulty: 1 }
    },

    {
        id: 'reading_comp', name: '読解力', type: CARD_TYPES.KNOWLEDGE, cost: 0, icon: '📚',
        description: '正解でエネルギー1を得る',
        effect: { quizEnergy: 1 },
        quiz: { type: 'reading', difficulty: 1 }
    },

    // 論理系
    {
        id: 'deduction', name: '推論', type: CARD_TYPES.KNOWLEDGE, cost: 2, icon: '🔍',
        description: '正解で敵の行動を見破る（次のターン敵行動表示）',
        effect: { quizRevealIntent: true },
        quiz: { type: 'logic', difficulty: 2 }
    },

    {
        id: 'pattern', name: 'パターン認識', type: CARD_TYPES.KNOWLEDGE, cost: 1, icon: '🧩',
        description: '正解でカード1枚引く＋5ダメージ',
        effect: { quizDraw: 1, quizDamage: 5 },
        quiz: { type: 'pattern', difficulty: 1 }
    },

    // 教養系
    {
        id: 'history', name: '歴史知識', type: CARD_TYPES.KNOWLEDGE, cost: 1, icon: '🏛️',
        description: '正解で筋力1を得る（永続）',
        effect: { quizBuff: { type: 'strength', amount: 1 } },
        quiz: { type: 'history', difficulty: 2 }
    },

    {
        id: 'science', name: '科学知識', type: CARD_TYPES.KNOWLEDGE, cost: 2, icon: '🔬',
        description: '正解で15ダメージ＋弱体2',
        effect: { quizDamage: 15, quizDebuff: { type: 'weak', amount: 2 } },
        quiz: { type: 'science', difficulty: 2 }
    },

    {
        id: 'geography', name: '地理知識', type: CARD_TYPES.KNOWLEDGE, cost: 1, icon: '🌍',
        description: '正解で10を回復',
        effect: { quizHeal: 10 },
        quiz: { type: 'geography', difficulty: 2 }
    },
];

// ============================================
// クイズデータ（SPI風）
// ============================================
const QUIZ_DATA = {
    math: [
        { q: '3 + 5 × 2 = ?', options: ['16', '13', '11', '10'], answer: 1 },
        { q: '√144 = ?', options: ['12', '14', '11', '13'], answer: 0 },
        { q: '2³ = ?', options: ['6', '8', '9', '4'], answer: 1 },
        { q: '15% of 200 = ?', options: ['30', '25', '35', '20'], answer: 0 },
        { q: '1/4 + 1/2 = ?', options: ['3/4', '2/6', '1/6', '2/4'], answer: 0 },
    ],
    probability: [
        { q: 'サイコロ2つで合計7が出る確率は？', options: ['1/6', '1/9', '5/36', '1/12'], answer: 0 },
        { q: 'コイン3回投げて全て表の確率は？', options: ['1/8', '1/4', '1/6', '3/8'], answer: 0 },
        { q: '52枚からハートを引く確率は？', options: ['1/4', '1/13', '1/2', '4/13'], answer: 0 },
    ],
    vocabulary: [
        { q: '「忖度」の意味は？', options: ['他人の心を推し量る', '物事を粗末にする', '厳しく批判する', '素早く行動する'], answer: 0 },
        { q: '「脆弱」の読み方は？', options: ['ぜいじゃく', 'せいじゃく', 'もろよわ', 'きじゃく'], answer: 0 },
        { q: '「慣用句」の反対語は？', options: ['新語', '古語', '死語', '方言'], answer: 0 },
    ],
    logic: [
        { q: '全ての猫は動物。タマは猫。よって...', options: ['タマは動物', 'タマは犬ではない', '全ての動物は猫', '猫は4本足'], answer: 0 },
        { q: 'A>B, B>C ならば...', options: ['A>C', 'C>A', 'A=C', '不明'], answer: 0 },
        { q: '「AならばB」の対偶は？', options: ['BでないならAでない', 'BならばA', 'AでないならBでない', 'AかつB'], answer: 0 },
    ],
    pattern: [
        { q: '2, 4, 8, 16, ?', options: ['32', '24', '20', '18'], answer: 0 },
        { q: '1, 1, 2, 3, 5, ?', options: ['8', '7', '6', '9'], answer: 0 },
        { q: 'A, C, E, G, ?', options: ['I', 'H', 'J', 'K'], answer: 0 },
    ],
    history: [
        { q: '明治維新は何年？', options: ['1868年', '1854年', '1872年', '1860年'], answer: 0 },
        { q: '関ヶ原の戦いの勝者は？', options: ['徳川家康', '石田三成', '豊臣秀吉', '織田信長'], answer: 0 },
        { q: 'フランス革命は何世紀？', options: ['18世紀', '17世紀', '19世紀', '16世紀'], answer: 0 },
    ],
    science: [
        { q: '水の化学式は？', options: ['H2O', 'CO2', 'NaCl', 'O2'], answer: 0 },
        { q: '光の速度は秒速約...', options: ['30万km', '3万km', '300万km', '3000km'], answer: 0 },
        { q: 'DNAの二重らせん発見者は？', options: ['ワトソンとクリック', 'アインシュタイン', 'ニュートン', 'ダーウィン'], answer: 0 },
    ],
    geography: [
        { q: '日本で一番長い川は？', options: ['信濃川', '利根川', '石狩川', '北上川'], answer: 0 },
        { q: 'アマゾン川がある大陸は？', options: ['南アメリカ', 'アフリカ', 'アジア', 'オーストラリア'], answer: 0 },
        { q: '世界で一番高い山は？', options: ['エベレスト', 'K2', '富士山', 'キリマンジャロ'], answer: 0 },
    ],
    reading: [
        { q: '「石橋を叩いて渡る」の意味は？', options: ['慎重に行動する', '危険を冒す', '急いで行動する', '他人を頼る'], answer: 0 },
        { q: '「塵も積もれば山となる」の教訓は？', options: ['小さな努力の積み重ね', '無駄な努力', '大きな目標', 'すぐ諦める'], answer: 0 },
    ],
};

// ============================================
// ヘルパー関数
// ============================================
function getRandomCard(pool) {
    return { ...pool[Math.floor(Math.random() * pool.length)] };
}

function getRewardCards(count = 3, floor = 1) {
    const rewards = [];
    const hasKnowledge = Math.random() < 0.4; // 40%で知識カード含む

    for (let i = 0; i < count; i++) {
        let pool;
        const rareChance = Math.min(0.1 + floor * 0.02, 0.3); // 階が上がるとレア確率UP

        if (i === 0 && hasKnowledge) {
            pool = KNOWLEDGE_CARDS;
        } else if (Math.random() < rareChance) {
            pool = RARE_CARDS;
        } else {
            pool = COMMON_CARDS;
        }

        rewards.push(getRandomCard(pool));
    }

    return rewards;
}

function getRandomQuiz(type, difficulty = 1) {
    const quizzes = QUIZ_DATA[type] || QUIZ_DATA.math;
    const quiz = quizzes[Math.floor(Math.random() * quizzes.length)];
    return { ...quiz };
}

// Export for use in game.js
window.CARD_TYPES = CARD_TYPES;
window.STARTER_CARDS = STARTER_CARDS;
window.COMMON_CARDS = COMMON_CARDS;
window.RARE_CARDS = RARE_CARDS;
window.KNOWLEDGE_CARDS = KNOWLEDGE_CARDS;
window.QUIZ_DATA = QUIZ_DATA;
window.getRandomCard = getRandomCard;
window.getRewardCards = getRewardCards;
window.getRandomQuiz = getRandomQuiz;
