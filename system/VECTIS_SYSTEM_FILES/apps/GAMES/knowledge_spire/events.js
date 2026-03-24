/**
 * KNOWLEDGE SPIRE - Event Definitions
 * ランダムイベント定義
 */

const EVENTS = [
    // ============================================
    // ポジティブイベント
    // ============================================
    {
        id: 'ancient_library',
        icon: '📚',
        title: '古代の図書館',
        description: '埃をかぶった本棚が並ぶ図書館を発見した。知識が眠っている...',
        choices: [
            {
                text: '📖 熱心に読む',
                effect: '知識カードを1枚獲得',
                action: (game) => {
                    const card = getRandomCard(KNOWLEDGE_CARDS);
                    game.deck.push(card);
                    return `「${card.name}」を獲得！`;
                }
            },
            {
                text: '🔍 貴重な本を探す',
                effect: 'ゴールド+50、ただしHP-5',
                action: (game) => {
                    game.gold += 50;
                    game.hp = Math.max(1, game.hp - 5);
                    return '古い金貨と共に棘のある本を見つけた...';
                }
            },
            {
                text: '🚶 立ち去る',
                effect: '何も起こらない',
                action: () => '先を急ぐことにした。'
            }
        ]
    },
    {
        id: 'healing_spring',
        icon: '⛲',
        title: '癒しの泉',
        description: '澄んだ水が湧き出る泉を見つけた。心身が癒される...',
        choices: [
            {
                text: '💧 水を飲む',
                effect: 'HP 30%回復',
                action: (game) => {
                    const heal = Math.floor(game.maxHp * 0.3);
                    game.hp = Math.min(game.maxHp, game.hp + heal);
                    return `HP ${heal} 回復！`;
                }
            },
            {
                text: '🧪 瓶に詰める',
                effect: '次の戦闘開始時にHP15回復',
                action: (game) => {
                    game.nextBattleHeal = 15;
                    return '泉の水を瓶に詰めた。';
                }
            }
        ]
    },
    {
        id: 'mysterious_merchant',
        icon: '🎭',
        title: '謎の商人',
        description: '「いい品がありますよ...」影から商人が現れた。',
        choices: [
            {
                text: '💰 カードを削除 (50G)',
                effect: 'デッキからカード1枚を削除',
                condition: (game) => game.gold >= 50,
                action: (game) => {
                    game.gold -= 50;
                    game.pendingCardRemoval = true;
                    return 'デッキからカードを1枚選んで削除できます。';
                }
            },
            {
                text: '🎲 賭け (30G)',
                effect: '50%で100G獲得、50%で失う',
                condition: (game) => game.gold >= 30,
                action: (game) => {
                    game.gold -= 30;
                    if (Math.random() < 0.5) {
                        game.gold += 100;
                        return '大当たり！100G獲得！';
                    } else {
                        return 'ハズレ...30G失った。';
                    }
                }
            },
            {
                text: '🚶 断る',
                effect: '何も起こらない',
                action: () => '商人は影に消えた...'
            }
        ]
    },

    // ============================================
    // リスク・リワードイベント
    // ============================================
    {
        id: 'cursed_chest',
        icon: '📦',
        title: '呪われた宝箱',
        description: '不気味なオーラを放つ宝箱がある。開けるべきか...',
        choices: [
            {
                text: '🔓 開ける',
                effect: 'レアカード獲得、ただし呪いカードも追加',
                action: (game) => {
                    const rareCard = getRandomCard(RARE_CARDS);
                    const curseCard = {
                        id: 'curse_pain',
                        name: '苦痛の呪い',
                        type: 'curse',
                        cost: 'X',
                        icon: '💀',
                        description: '廃棄不可。引いた時ダメージ1',
                        unplayable: true,
                        effect: { selfDamageOnDraw: 1 }
                    };
                    game.deck.push(rareCard, curseCard);
                    return `「${rareCard.name}」獲得！...しかし呪いも受けた。`;
                }
            },
            {
                text: '🔒 開けない',
                effect: '何も起こらない',
                action: () => '嫌な予感がする。放っておこう。'
            }
        ]
    },
    {
        id: 'training_dummy',
        icon: '🎯',
        title: '訓練人形',
        description: '古びた訓練人形がある。腕試しに丁度いい。',
        choices: [
            {
                text: '⚔️ 全力で打ち込む',
                effect: '筋力+1（永続）、HP-10',
                action: (game) => {
                    game.buffs.strength = (game.buffs.strength || 0) + 1;
                    game.hp = Math.max(1, game.hp - 10);
                    return '筋力が上がった！でも疲れた...';
                }
            },
            {
                text: '🛡️ 防御の練習',
                effect: '器用さ+1（永続）、HP-5',
                action: (game) => {
                    game.buffs.dexterity = (game.buffs.dexterity || 0) + 1;
                    game.hp = Math.max(1, game.hp - 5);
                    return '器用さが上がった！';
                }
            },
            {
                text: '🚶 通り過ぎる',
                effect: '何も起こらない',
                action: () => '今は先を急ごう。'
            }
        ]
    },

    // ============================================
    // クイズイベント（知識テスト）
    // ============================================
    {
        id: 'knowledge_trial',
        icon: '🧠',
        title: '知識の試練',
        description: '「答えよ、さすれば道は開かれん」謎の声が響く。',
        isQuizEvent: true,
        quizType: 'random',
        choices: [
            {
                text: '🎓 挑戦する',
                effect: '正解：HP全回復＋レアカード / 不正解：HP-20',
                action: (game, correct) => {
                    if (correct) {
                        game.hp = game.maxHp;
                        const rareCard = getRandomCard(RARE_CARDS);
                        game.deck.push(rareCard);
                        return `正解！HPが全回復し、「${rareCard.name}」を獲得！`;
                    } else {
                        game.hp = Math.max(1, game.hp - 20);
                        return '不正解...激痛が走る！';
                    }
                }
            },
            {
                text: '🚶 逃げる',
                effect: 'HP-5で逃走',
                action: (game) => {
                    game.hp = Math.max(1, game.hp - 5);
                    return '慌てて逃げる途中で転んだ...';
                }
            }
        ]
    },
    {
        id: 'math_puzzle',
        icon: '🧮',
        title: '数学パズル',
        description: '扉に不思議な数式が刻まれている。解かなければ進めない。',
        isQuizEvent: true,
        quizType: 'math',
        choices: [
            {
                text: '📐 解く',
                effect: '正解：次の戦闘でエネルギー+1 / 不正解：カード1枚使用不可',
                action: (game, correct) => {
                    if (correct) {
                        game.nextBattleEnergy = (game.nextBattleEnergy || 0) + 1;
                        return '扉が開いた！集中力が高まった。';
                    } else {
                        game.nextBattleCardDebuff = 1;
                        return '扉は開いたが...混乱が残る。';
                    }
                }
            }
        ]
    },

    // ============================================
    // 休憩イベント
    // ============================================
    {
        id: 'campfire',
        icon: '🔥',
        title: '焚き火',
        description: '安全そうな場所で一息つける。',
        choices: [
            {
                text: '😴 休む',
                effect: 'HP 30%回復',
                action: (game) => {
                    const heal = Math.floor(game.maxHp * 0.3);
                    game.hp = Math.min(game.maxHp, game.hp + heal);
                    return `ゆっくり休んだ。HP ${heal} 回復！`;
                }
            },
            {
                text: '⚒️ カードを強化',
                effect: 'デッキのカード1枚を強化',
                action: (game) => {
                    game.pendingCardUpgrade = true;
                    return 'カードを1枚選んで強化できます。';
                }
            },
            {
                text: '🎓 知識を深める',
                effect: '知識カードを1枚獲得',
                action: (game) => {
                    const card = getRandomCard(KNOWLEDGE_CARDS);
                    game.deck.push(card);
                    return `「${card.name}」を習得！`;
                }
            }
        ]
    }
];

// ============================================
// ヘルパー関数
// ============================================
function getRandomEvent() {
    const event = EVENTS[Math.floor(Math.random() * EVENTS.length)];
    return { ...event };
}

function getRestEvent() {
    return { ...EVENTS.find(e => e.id === 'campfire') };
}

// Export
window.EVENTS = EVENTS;
window.getRandomEvent = getRandomEvent;
window.getRestEvent = getRestEvent;
