import { DatabaseSync } from "node:sqlite";

async function fix() {
  const dbPath = "./claw-empire.sqlite";
  const db = new DatabaseSync(dbPath);

  console.log('Fetching all departments...');
  const departments = db.prepare('SELECT id, name FROM departments').all() as { id: string, name: string }[];
  
  const deptMap: Record<string, string> = {
    'planning': '企画チーム',
    'dev': '開発チーム',
    'design': 'デザインチーム',
    'qa': '品質管理チーム',
    'devsecops': 'インフラ・セキュリティ',
    'operations': '運用チーム',
    'breakRoom': '休憩室',
    'ceoOffice': 'CEO室'
  };

  console.log('Fixing department names (UTF-8 safe)...');
  for (const dept of departments) {
    const name_ja = deptMap[dept.id] || dept.name; // フォールバックとして英語名を使用
    console.log(`Updating ${dept.id} -> ${name_ja}`);
    const stmt = db.prepare('UPDATE departments SET name_ja = ?, name_ko = ? WHERE id = ?');
    // name_ko も念のため空にするか、日本語と同じにする
    stmt.run(name_ja, '', dept.id);
  }

  console.log('Fixing agent names again...');
  const agents = db.prepare('SELECT id, name FROM agents').all() as { id: string, name: string }[];
  const agentMap: Record<string, string> = {
    'Aria': 'アリア', 'Bolt': 'ボルト', 'Nova': 'ノバ', 'Pixel': 'ピクセル',
    'Luna': 'ルナ', 'Sage': 'セージ', 'Clio': 'クリオ', 'Atlas': 'アトラス',
    'Turbo': 'ターボ', 'Hawk': 'ホーク', 'Lint': 'リント', 'Vault': 'ヴォルト',
    'Pipe': 'パイプ', 'DORO': 'ドロ', '髴忿': 'インターン', 'Mina': 'ミナ',
    'Juno': 'ジュノ', 'Rian': 'リアン', 'Haru': 'ハル', 'Noa': 'ノア',
    'Theo': 'テオ', 'Kai': 'カイ', 'Liam': 'リアム', 'Sena': 'セナ',
    'Rowan': 'ローワン', 'Yuna': 'ユナ', 'Miro': 'ミロ', 'Iris': 'アイリス',
    'Speaky': 'スピーキー', 'Vera': 'ヴェラ', 'Quinn': 'クイン', 'Tori': 'トリ',
    'Hayoon': 'ハユン', 'Nari': 'ナリ', 'Owen': 'オーウェン', 'Dami': 'ダミ',
    'Kira': 'キラ', 'Sol': 'ソル', 'VoltS': 'ボルトS', 'Sion': 'シオン',
    'Knox': 'ノックス', 'Raven': 'レイヴン', 'Mira': 'ミラ', 'Alex': 'アレックス'
  };

  for (const agent of agents) {
    const name_ja = agentMap[agent.name] || agent.name;
    const stmt = db.prepare('UPDATE agents SET name_ja = ?, name_ko = ? WHERE id = ?');
    stmt.run(name_ja, '', agent.id);
  }

  console.log('Database fix completed.');
}

fix().catch(console.error);
