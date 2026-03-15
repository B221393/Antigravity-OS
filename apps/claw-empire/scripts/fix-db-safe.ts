import { DatabaseSync } from "node:sqlite";

async function fix() {
  const dbPath = "./claw-empire.sqlite";
  const db = new DatabaseSync(dbPath);

  console.log('Fixing agent names (UTF-8 safe)...');
  const agentFixes = [
    ['Aria', 'アリア'],
    ['Bolt', 'ボルト'],
    ['Nova', 'ノバ'],
    ['Pixel', 'ピクセル'],
    ['Luna', 'ルナ'],
    ['Sage', 'セージ'],
    ['Clio', 'クリオ'],
    ['Atlas', 'アトラス'],
    ['Turbo', 'ターボ'],
    ['Hawk', 'ホーク'],
    ['Lint', 'リント'],
    ['Vault', 'ヴォルト'],
    ['Pipe', 'パイプ'],
    ['DORO', 'ドロ'],
    ['髴忿', 'インターン']
  ];

  for (const [name, name_ja] of agentFixes) {
    const stmt = db.prepare('UPDATE agents SET name_ja = ? WHERE name = ?');
    stmt.run(name_ja, name);
  }

  console.log('Fixing department names (UTF-8 safe)...');
  const deptFixes = [
    ['planning', '企画チーム'],
    ['dev', '開発チーム'],
    ['design', 'デザインチーム'],
    ['qa', '品質管理チーム'],
    ['devsecops', 'インフラ・セキュリティ'],
    ['operations', '運用チーム']
  ];

  for (const [id, name_ja] of deptFixes) {
    const stmt = db.prepare('UPDATE departments SET name_ja = ? WHERE id = ?');
    stmt.run(name_ja, id);
  }

  console.log('Database encoding fix completed.');
}

fix().catch(console.error);
