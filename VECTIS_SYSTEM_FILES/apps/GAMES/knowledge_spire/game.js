/**
 * KNOWLEDGE SPIRE - Main Game Engine
 * メインゲームエンジン（ゲームロジック、UI、戦闘システム）
 */

// ============================================
// GAME STATE
// ============================================
const GameState = {
    // プレイヤー
    hp: 80,
    maxHp: 80,
    block: 0,
    energy: 3,
    maxEnergy: 3,
    gold: 0,

    // バフ・デバフ
    buffs: {},
    debuffs: {},

    // デッキ
    deck: [],
    drawPile: [],
    hand: [],
    discardPile: [],
    exhaustPile: [],

    // 進行状況
    floor: 1,
    currentNode: null,
    map: [],

    // 戦闘
    enemies: [],
    selectedEnemy: null,
    inBattle: false,
    turn: 0,

    // 統計
    enemiesKilled: 0,
    totalGoldEarned: 0,

    // 特殊フラグ
    nextBattleHeal: 0,
    nextBattleEnergy: 0,

    // UI状態
    currentScreen: 'title',
    draggingCard: null,
};

// Save/Load
function saveGameStats() {
    const stats = {
        highFloor: Math.max(GameState.floor, localStorage.getItem('ks_highFloor') || 1),
        totalRuns: (parseInt(localStorage.getItem('ks_totalRuns')) || 0) + 1,
    };
    localStorage.setItem('ks_highFloor', stats.highFloor);
    localStorage.setItem('ks_totalRuns', stats.totalRuns);
}

function loadGameStats() {
    return {
        highFloor: parseInt(localStorage.getItem('ks_highFloor')) || 1,
        totalRuns: parseInt(localStorage.getItem('ks_totalRuns')) || 0,
    };
}

// ============================================
// INITIALIZATION
// ============================================
function initGame() {
    // Reset state
    GameState.hp = 80;
    GameState.maxHp = 80;
    GameState.block = 0;
    GameState.energy = 3;
    GameState.maxEnergy = 3;
    GameState.gold = 50;
    GameState.buffs = {};
    GameState.debuffs = {};
    GameState.floor = 1;
    GameState.enemiesKilled = 0;
    GameState.totalGoldEarned = 0;
    GameState.nextBattleHeal = 0;
    GameState.nextBattleEnergy = 0;

    // Initialize deck
    GameState.deck = STARTER_CARDS.map(c => ({ ...c, instanceId: generateId() }));
    GameState.drawPile = [];
    GameState.hand = [];
    GameState.discardPile = [];
    GameState.exhaustPile = [];

    // Generate map
    generateMap();

    // Show map
    showScreen('map');
}

function generateId() {
    return Math.random().toString(36).substr(2, 9);
}

// ============================================
// MAP GENERATION
// ============================================
function generateMap() {
    GameState.map = [];
    const totalFloors = 10;

    for (let floor = 1; floor <= totalFloors; floor++) {
        const row = [];
        let nodesInRow;

        if (floor === 1) {
            nodesInRow = 1; // Start
        } else if (floor === totalFloors) {
            nodesInRow = 1; // Final boss
        } else if (floor % 3 === 0) {
            nodesInRow = 1; // Boss floors
        } else {
            nodesInRow = Math.floor(Math.random() * 2) + 2; // 2-3 nodes
        }

        for (let i = 0; i < nodesInRow; i++) {
            let nodeType;
            if (floor === 1) {
                nodeType = 'start';
            } else if (floor === totalFloors) {
                nodeType = 'boss';
            } else if (floor % 3 === 0) {
                nodeType = 'boss';
            } else {
                // Random node type
                const rand = Math.random();
                if (rand < 0.55) nodeType = 'enemy';
                else if (rand < 0.70) nodeType = 'event';
                else if (rand < 0.80) nodeType = 'elite';
                else if (rand < 0.90) nodeType = 'rest';
                else nodeType = 'treasure';
            }

            row.push({
                floor,
                index: i,
                type: nodeType,
                completed: false,
                available: floor === 1
            });
        }

        GameState.map.push(row);
    }
}

function renderMap() {
    const container = document.getElementById('map-container');
    container.innerHTML = '';

    GameState.map.forEach((row, floorIndex) => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'map-row';

        row.forEach((node, nodeIndex) => {
            const nodeDiv = document.createElement('div');
            nodeDiv.className = `map-node ${node.completed ? 'completed' : ''} ${node.available ? 'available' : ''} ${node.type === 'boss' ? 'boss' : ''}`;
            nodeDiv.innerHTML = getNodeIcon(node.type);

            if (node.available && !node.completed) {
                nodeDiv.onclick = () => selectNode(node);
            }

            rowDiv.appendChild(nodeDiv);
        });

        container.appendChild(rowDiv);
    });

    // Update header
    document.getElementById('map-hp').textContent = GameState.hp;
    document.getElementById('map-max-hp').textContent = GameState.maxHp;
    document.getElementById('map-gold').textContent = GameState.gold;
    document.getElementById('current-floor').textContent = GameState.floor;
}

function getNodeIcon(type) {
    const icons = {
        'start': '🏠',
        'enemy': '👹',
        'elite': '💀',
        'boss': '👑',
        'event': '❓',
        'rest': '🔥',
        'treasure': '💎',
        'shop': '🛒'
    };
    return icons[type] || '?';
}

function selectNode(node) {
    node.completed = true;
    GameState.currentNode = node;
    GameState.floor = node.floor;

    // Mark next floor as available
    if (node.floor < GameState.map.length) {
        GameState.map[node.floor].forEach(n => n.available = true);
    }

    // Handle node type
    switch (node.type) {
        case 'start':
        case 'enemy':
            startBattle(false, false);
            break;
        case 'elite':
            startBattle(true, false);
            break;
        case 'boss':
            startBattle(false, true);
            break;
        case 'event':
            showEvent(getRandomEvent());
            break;
        case 'rest':
            showEvent(getRestEvent());
            break;
        case 'treasure':
            GameState.gold += 50 + Math.floor(Math.random() * 50);
            showRewardScreen([getRandomCard(RARE_CARDS)]);
            break;
    }
}

// ============================================
// BATTLE SYSTEM
// ============================================
function startBattle(isElite = false, isBoss = false) {
    GameState.inBattle = true;
    GameState.turn = 0;
    GameState.block = 0;
    GameState.enemies = [];

    // Spawn enemies
    if (isBoss) {
        const boss = getBoss(GameState.floor);
        if (boss) GameState.enemies.push(boss);
        else GameState.enemies.push(getRandomEnemy(GameState.floor));
    } else if (isElite) {
        GameState.enemies.push(getElite(GameState.floor));
    } else {
        const count = Math.random() < 0.3 ? 2 : 1;
        for (let i = 0; i < count; i++) {
            GameState.enemies.push(getRandomEnemy(GameState.floor));
        }
    }

    // Apply pre-battle effects
    if (GameState.nextBattleHeal > 0) {
        GameState.hp = Math.min(GameState.maxHp, GameState.hp + GameState.nextBattleHeal);
        GameState.nextBattleHeal = 0;
    }
    if (GameState.nextBattleEnergy > 0) {
        GameState.maxEnergy += GameState.nextBattleEnergy;
        GameState.nextBattleEnergy = 0;
    }

    // Initialize deck
    GameState.drawPile = shuffleArray([...GameState.deck]);
    GameState.hand = [];
    GameState.discardPile = [];

    showScreen('battle');
    startPlayerTurn();
}

function startPlayerTurn() {
    GameState.turn++;
    GameState.energy = GameState.maxEnergy;
    GameState.block = 0;

    // Apply turn-start buffs
    if (GameState.buffs.strengthPerTurn) {
        GameState.buffs.strength = (GameState.buffs.strength || 0) + GameState.buffs.strengthPerTurn;
    }

    // Draw cards
    drawCards(5);

    renderBattle();
}

function drawCards(count) {
    for (let i = 0; i < count; i++) {
        if (GameState.drawPile.length === 0) {
            // Shuffle discard into draw
            GameState.drawPile = shuffleArray([...GameState.discardPile]);
            GameState.discardPile = [];
        }

        if (GameState.drawPile.length > 0) {
            const card = GameState.drawPile.pop();
            GameState.hand.push(card);

            // Curse on draw effects
            if (card.effect?.selfDamageOnDraw) {
                takeDamage(card.effect.selfDamageOnDraw);
            }
        }
    }
}

function endPlayerTurn() {
    // Discard hand
    GameState.discardPile.push(...GameState.hand);
    GameState.hand = [];

    // Enemy turns
    executeEnemyTurns();
}

function executeEnemyTurns() {
    GameState.enemies.forEach((enemy, index) => {
        if (enemy.hp <= 0) return;

        setTimeout(() => {
            executeEnemyAction(enemy);
            advanceEnemyPattern(enemy);

            // Check if all done
            if (index === GameState.enemies.length - 1) {
                setTimeout(() => {
                    if (GameState.hp > 0 && GameState.inBattle) {
                        startPlayerTurn();
                    }
                }, 500);
            }
        }, index * 800);
    });

    if (GameState.enemies.filter(e => e.hp > 0).length === 0) {
        setTimeout(startPlayerTurn, 500);
    }
}

function executeEnemyAction(enemy) {
    const intent = getEnemyIntent(enemy);

    switch (intent.type) {
        case INTENT_TYPES.ATTACK:
            let damage = intent.damage + (enemy.buffs?.strength || 0);
            const times = intent.times || 1;

            for (let i = 0; i < times; i++) {
                dealDamageToPlayer(damage);
            }

            shakeScreen();
            break;

        case INTENT_TYPES.DEFEND:
            enemy.block = (enemy.block || 0) + intent.block;
            if (intent.damage) {
                dealDamageToPlayer(intent.damage);
            }
            if (intent.heal) {
                enemy.hp = Math.min(enemy.maxHp, enemy.hp + intent.heal);
            }
            break;

        case INTENT_TYPES.BUFF:
            if (intent.buff) {
                enemy.buffs[intent.buff.type] = (enemy.buffs[intent.buff.type] || 0) + intent.buff.amount;
            }
            break;

        case INTENT_TYPES.DEBUFF:
            if (intent.debuff) {
                GameState.debuffs[intent.debuff.type] = (GameState.debuffs[intent.debuff.type] || 0) + intent.debuff.amount;
            }
            break;
    }

    renderBattle();

    // Check game over
    if (GameState.hp <= 0) {
        setTimeout(gameOver, 500);
    }
}

function dealDamageToPlayer(damage) {
    // Apply vulnerable
    if (GameState.debuffs.vulnerable > 0) {
        damage = Math.floor(damage * 1.5);
    }

    // Block first
    if (GameState.block > 0) {
        const blocked = Math.min(GameState.block, damage);
        GameState.block -= blocked;
        damage -= blocked;
        showDamagePopup(blocked, 'block', document.querySelector('.player-character'));
    }

    // Take remaining damage
    if (damage > 0) {
        GameState.hp -= damage;
        showDamagePopup(damage, 'damage', document.querySelector('.player-character'));
        document.querySelector('.player-character').classList.add('flash-damage');
        setTimeout(() => document.querySelector('.player-character').classList.remove('flash-damage'), 300);
    }
}

// ============================================
// CARD PLAYING
// ============================================
function playCard(card, targetEnemy = null) {
    // Check if playable
    if (card.cost === 'X') {
        // X cost cards use all energy
        card.tempCost = GameState.energy;
    } else if (card.cost > GameState.energy) {
        return false; // Not enough energy
    }

    // Check target requirement
    if (card.type === CARD_TYPES.ATTACK && !targetEnemy && GameState.enemies.length > 1) {
        // Need to select target first
        return false;
    }

    // Use energy
    const cost = card.cost === 'X' ? GameState.energy : card.cost;
    GameState.energy -= cost;

    // Execute card effects
    executeCardEffect(card, targetEnemy, cost);

    // Remove from hand
    const handIndex = GameState.hand.findIndex(c => c.instanceId === card.instanceId);
    if (handIndex > -1) {
        GameState.hand.splice(handIndex, 1);
    }

    // Add to discard (unless exhausted)
    if (!card.effect?.exhaust) {
        GameState.discardPile.push(card);
    } else {
        GameState.exhaustPile.push(card);
    }

    // Copy to discard effect
    if (card.effect?.copyToDiscard) {
        GameState.discardPile.push({ ...card, instanceId: generateId() });
    }

    renderBattle();
    checkBattleEnd();

    return true;
}

function executeCardEffect(card, targetEnemy, energySpent = 0) {
    const effect = card.effect;
    if (!effect) return;

    const target = targetEnemy || GameState.enemies[0];

    // Calculate strength bonus
    const strengthBonus = GameState.buffs.strength || 0;
    const strengthMultiplier = effect.strengthMultiplier || 1;

    // Apply weakness
    let damageMultiplier = 1;
    if (GameState.debuffs.weak > 0) {
        damageMultiplier = 0.75;
    }

    // Damage
    if (effect.damage) {
        let damage = Math.floor((effect.damage + strengthBonus * strengthMultiplier) * damageMultiplier);

        if (effect.aoe) {
            GameState.enemies.forEach(e => dealDamageToEnemy(e, damage));
        } else {
            dealDamageToEnemy(target, damage);
        }
    }

    // X cost damage
    if (effect.damagePerEnergy) {
        let damage = Math.floor(effect.damagePerEnergy * energySpent * damageMultiplier);
        if (effect.aoe) {
            GameState.enemies.forEach(e => dealDamageToEnemy(e, damage));
        }
    }

    // Block
    if (effect.block) {
        let block = effect.block + (GameState.buffs.dexterity || 0);
        GameState.block += block;
    }

    // Draw
    if (effect.draw) {
        drawCards(effect.draw);
    }

    // Energy
    if (effect.energy) {
        GameState.energy += effect.energy;
    }

    // Self damage
    if (effect.selfDamage) {
        GameState.hp -= effect.selfDamage;
    }

    // Debuff enemy
    if (effect.debuff && target) {
        target.debuffs[effect.debuff.type] = (target.debuffs[effect.debuff.type] || 0) + effect.debuff.amount;
    }

    // Buff self
    if (effect.buff) {
        GameState.buffs[effect.buff.type] = (GameState.buffs[effect.buff.type] || 0) + effect.buff.amount;
    }

    // Knowledge card quiz
    if (card.quiz) {
        triggerQuiz(card);
    }
}

function dealDamageToEnemy(enemy, damage) {
    // Apply vulnerable
    if (enemy.debuffs?.vulnerable > 0) {
        damage = Math.floor(damage * 1.5);
    }

    // Block
    if (enemy.block > 0) {
        const blocked = Math.min(enemy.block, damage);
        enemy.block -= blocked;
        damage -= blocked;
    }

    enemy.hp -= damage;

    // Show popup
    const enemyEl = document.querySelector(`[data-enemy-id="${enemy.id}"]`);
    if (enemyEl) {
        showDamagePopup(damage, 'damage', enemyEl);
        enemyEl.classList.add('shake');
        setTimeout(() => enemyEl.classList.remove('shake'), 300);
    }

    if (enemy.hp <= 0) {
        enemy.hp = 0;
        GameState.enemiesKilled++;
    }
}

function checkBattleEnd() {
    const aliveEnemies = GameState.enemies.filter(e => e.hp > 0);

    if (aliveEnemies.length === 0) {
        GameState.inBattle = false;

        // Victory
        setTimeout(() => {
            const goldReward = 10 + GameState.floor * 5 + Math.floor(Math.random() * 20);
            GameState.gold += goldReward;
            GameState.totalGoldEarned += goldReward;

            // Show reward
            const rewards = getRewardCards(3, GameState.floor);
            showRewardScreen(rewards);
        }, 500);
    }
}

// ============================================
// QUIZ SYSTEM
// ============================================
let currentQuizCallback = null;

function triggerQuiz(card) {
    const quizType = card.quiz.type;
    const quiz = getRandomQuiz(quizType);

    showQuizModal(quiz, (correct) => {
        if (correct) {
            // Execute positive effects
            if (card.effect.quizDamage) {
                const target = GameState.selectedEnemy || GameState.enemies[0];
                if (card.effect.quizAoe) {
                    GameState.enemies.forEach(e => dealDamageToEnemy(e, card.effect.quizDamage));
                } else if (target) {
                    dealDamageToEnemy(target, card.effect.quizDamage);
                }
            }
            if (card.effect.quizBlock) {
                GameState.block += card.effect.quizBlock;
            }
            if (card.effect.quizDraw) {
                drawCards(card.effect.quizDraw);
            }
            if (card.effect.quizEnergy) {
                GameState.energy += card.effect.quizEnergy;
            }
            if (card.effect.quizHeal) {
                GameState.hp = Math.min(GameState.maxHp, GameState.hp + card.effect.quizHeal);
            }
            if (card.effect.quizBuff) {
                GameState.buffs[card.effect.quizBuff.type] =
                    (GameState.buffs[card.effect.quizBuff.type] || 0) + card.effect.quizBuff.amount;
            }
        } else {
            // Execute fail effects
            if (card.effect.failDamage) {
                const target = GameState.selectedEnemy || GameState.enemies[0];
                if (target) dealDamageToEnemy(target, card.effect.failDamage);
            }
        }

        renderBattle();
        checkBattleEnd();
    });
}

function showQuizModal(quiz, callback) {
    // Create quiz modal
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.id = 'quiz-modal';

    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <h2>🧠 知識チャレンジ</h2>
            <p style="font-size: 1.3rem; margin: 1.5rem 0;">${quiz.q}</p>
            <div style="display: flex; flex-direction: column; gap: 0.8rem;">
                ${quiz.options.map((opt, i) => `
                    <button class="event-choice quiz-option" data-index="${i}">${opt}</button>
                `).join('')}
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Handle answers
    modal.querySelectorAll('.quiz-option').forEach((btn, i) => {
        btn.onclick = () => {
            const correct = i === quiz.answer;

            // Show result
            btn.style.background = correct ? 'var(--accent-green)' : 'var(--accent-red)';
            if (!correct) {
                modal.querySelectorAll('.quiz-option')[quiz.answer].style.background = 'var(--accent-green)';
            }

            setTimeout(() => {
                modal.remove();
                callback(correct);
            }, 1000);
        };
    });
}

// ============================================
// RENDERING
// ============================================
function renderBattle() {
    // Update player stats
    document.getElementById('battle-hp').textContent = GameState.hp;
    document.getElementById('battle-max-hp').textContent = GameState.maxHp;
    document.getElementById('player-block').textContent = GameState.block;
    document.getElementById('current-energy').textContent = GameState.energy;
    document.getElementById('max-energy').textContent = GameState.maxEnergy;

    // Render enemies
    const enemyArea = document.getElementById('enemy-area');
    enemyArea.innerHTML = '';

    GameState.enemies.forEach(enemy => {
        if (enemy.hp <= 0) return;

        const intent = getEnemyIntent(enemy);
        const intentDisplay = getIntentDisplay(intent);

        const enemyDiv = document.createElement('div');
        enemyDiv.className = 'enemy';
        enemyDiv.setAttribute('data-enemy-id', enemy.id);
        enemyDiv.innerHTML = `
            <div class="enemy-sprite">${enemy.sprite}</div>
            <div class="enemy-hp-bar">
                <div class="enemy-hp-fill" style="width: ${(enemy.hp / enemy.maxHp) * 100}%"></div>
            </div>
            <div style="font-size: 0.9rem;">${enemy.hp}/${enemy.maxHp}</div>
            ${enemy.block > 0 ? `<div class="enemy-block">🛡️ ${enemy.block}</div>` : ''}
            <div class="enemy-intent">${intentDisplay}</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">${enemy.name}</div>
        `;

        enemyDiv.onclick = () => {
            GameState.selectedEnemy = enemy;
            document.querySelectorAll('.enemy').forEach(e => e.classList.remove('targeted'));
            enemyDiv.classList.add('targeted');
        };

        enemyArea.appendChild(enemyDiv);
    });

    // Render hand
    renderHand();

    // Update piles
    document.querySelector('#draw-pile .pile-count').textContent = GameState.drawPile.length;
    document.querySelector('#discard-pile .pile-count').textContent = GameState.discardPile.length;
}

function getIntentDisplay(intent) {
    switch (intent.type) {
        case INTENT_TYPES.ATTACK:
            const times = intent.times || 1;
            return times > 1 ? `⚔️ ${intent.damage}×${times}` : `⚔️ ${intent.damage}`;
        case INTENT_TYPES.DEFEND:
            return `🛡️ ${intent.block}`;
        case INTENT_TYPES.BUFF:
            return '✨';
        case INTENT_TYPES.DEBUFF:
            return '💫';
        case INTENT_TYPES.UNKNOWN:
            return '❓';
        default:
            return '?';
    }
}

function renderHand() {
    const handContainer = document.getElementById('hand-container');
    handContainer.innerHTML = '';

    const handWidth = Math.min(GameState.hand.length * 110, 700);
    const cardSpacing = handWidth / Math.max(GameState.hand.length, 1);

    GameState.hand.forEach((card, index) => {
        const cardEl = createCardElement(card);
        const canPlay = card.cost === 'X' || card.cost <= GameState.energy;

        if (!canPlay || card.unplayable) {
            cardEl.classList.add('unplayable');
        }

        // Fan effect
        const offset = (index - (GameState.hand.length - 1) / 2);
        cardEl.style.transform = `rotate(${offset * 3}deg)`;
        cardEl.style.marginLeft = index > 0 ? '-30px' : '0';

        // Click to play
        cardEl.onclick = () => {
            if (!canPlay || card.unplayable) return;

            if (card.type === CARD_TYPES.ATTACK && GameState.enemies.length > 1 && !GameState.selectedEnemy) {
                // Need target
                alert('敵をクリックして選択してください');
                return;
            }

            playCard(card, GameState.selectedEnemy || GameState.enemies[0]);
        };

        handContainer.appendChild(cardEl);
    });
}

function createCardElement(card) {
    const cardEl = document.createElement('div');
    cardEl.className = `card ${card.type}`;
    cardEl.innerHTML = `
        <div class="card-cost">${card.cost}</div>
        <div class="card-name">${card.name}</div>
        <div class="card-icon">${card.icon}</div>
        <div class="card-description">${card.description}</div>
    `;
    return cardEl;
}

// ============================================
// EVENTS
// ============================================
function showEvent(event) {
    document.getElementById('event-icon').textContent = event.icon;
    document.getElementById('event-title').textContent = event.title;
    document.getElementById('event-description').textContent = event.description;

    const choicesContainer = document.getElementById('event-choices');
    choicesContainer.innerHTML = '';

    event.choices.forEach(choice => {
        // Check condition
        if (choice.condition && !choice.condition(GameState)) {
            return; // Skip unavailable choices
        }

        const btn = document.createElement('div');
        btn.className = 'event-choice';
        btn.innerHTML = `
            <div>${choice.text}</div>
            <div class="choice-effect">${choice.effect}</div>
        `;

        btn.onclick = () => {
            if (event.isQuizEvent && choice.text.includes('挑戦')) {
                // Quiz event
                const quizType = event.quizType === 'random' ?
                    ['math', 'logic', 'vocabulary', 'history'][Math.floor(Math.random() * 4)] :
                    event.quizType;
                const quiz = getRandomQuiz(quizType);

                showQuizModal(quiz, (correct) => {
                    const result = choice.action(GameState, correct);
                    alert(result);
                    returnToMap();
                });
            } else {
                const result = choice.action(GameState);
                alert(result);
                returnToMap();
            }
        };

        choicesContainer.appendChild(btn);
    });

    showScreen('event');
}

// ============================================
// REWARDS
// ============================================
function showRewardScreen(cards) {
    const container = document.getElementById('reward-cards');
    container.innerHTML = '';

    cards.forEach(card => {
        const cardEl = createCardElement(card);
        cardEl.onclick = () => {
            // Add to deck
            GameState.deck.push({ ...card, instanceId: generateId() });
            returnToMap();
        };
        container.appendChild(cardEl);
    });

    showScreen('reward');
}

// ============================================
// GAME OVER / VICTORY
// ============================================
function gameOver() {
    saveGameStats();

    document.getElementById('final-floor').textContent = GameState.floor;
    document.getElementById('enemies-killed').textContent = GameState.enemiesKilled;
    document.getElementById('gold-earned').textContent = GameState.totalGoldEarned;

    // Check if victory
    if (GameState.floor >= 10 && GameState.enemies.every(e => e.hp <= 0)) {
        document.getElementById('gameover-title').textContent = '🏆 Victory!';
        document.querySelector('.gameover-container').classList.add('victory');
    } else {
        document.getElementById('gameover-title').textContent = '💀 Game Over';
        document.querySelector('.gameover-container').classList.remove('victory');
    }

    showScreen('gameover');
}

// ============================================
// SCREEN MANAGEMENT
// ============================================
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(`${screenId}-screen`).classList.add('active');
    GameState.currentScreen = screenId;

    if (screenId === 'map') {
        renderMap();
    }
}

function returnToMap() {
    showScreen('map');
}

// ============================================
// UTILITIES
// ============================================
function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function takeDamage(amount) {
    if (GameState.block > 0) {
        const blocked = Math.min(GameState.block, amount);
        GameState.block -= blocked;
        amount -= blocked;
    }
    GameState.hp -= amount;
    if (GameState.hp <= 0) {
        gameOver();
    }
}

function showDamagePopup(amount, type, targetEl) {
    const popup = document.createElement('div');
    popup.className = `damage-popup ${type}`;
    popup.textContent = type === 'damage' ? `-${amount}` : (type === 'block' ? `🛡️${amount}` : `+${amount}`);

    const rect = targetEl.getBoundingClientRect();
    popup.style.left = `${rect.left + rect.width / 2}px`;
    popup.style.top = `${rect.top}px`;

    document.getElementById('damage-popups').appendChild(popup);

    setTimeout(() => popup.remove(), 1000);
}

function shakeScreen() {
    document.getElementById('game-container').classList.add('shake');
    setTimeout(() => document.getElementById('game-container').classList.remove('shake'), 300);
}

// ============================================
// EVENT LISTENERS
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Load stats
    const stats = loadGameStats();
    document.getElementById('high-floor').textContent = stats.highFloor;
    document.getElementById('total-runs').textContent = stats.totalRuns;

    // Title buttons
    document.getElementById('btn-start').onclick = initGame;
    document.getElementById('btn-how').onclick = () => {
        alert('🗼 Knowledge Spire - 遊び方\n\n' +
            '1. マップでノードを選んで進む\n' +
            '2. 敵との戦闘ではカードをクリックして攻撃・防御\n' +
            '3. エネルギー（⚡）を消費してカードを使用\n' +
            '4. 知識カード（🧮📖🧩）は正解でボーナス効果！\n' +
            '5. 塔の頂上を目指せ！');
    };

    // Battle buttons
    document.getElementById('btn-end-turn').onclick = endPlayerTurn;

    // Restart
    document.getElementById('btn-restart').onclick = initGame;

    // Skip reward
    document.getElementById('btn-skip-reward').onclick = returnToMap;

    // Deck view
    document.getElementById('btn-deck-view').onclick = () => {
        const deckView = document.getElementById('deck-view');
        const deckCards = document.getElementById('deck-cards');
        deckCards.innerHTML = '';

        GameState.deck.forEach(card => {
            deckCards.appendChild(createCardElement(card));
        });

        deckView.classList.add('active');
    };

    document.getElementById('btn-close-deck').onclick = () => {
        document.getElementById('deck-view').classList.remove('active');
    };
});
