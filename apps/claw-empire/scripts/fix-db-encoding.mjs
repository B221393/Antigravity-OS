import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

async function fix() {
  const db = await open({
    filename: './claw-empire.sqlite',
    driver: sqlite3.Database
  });

  console.log('Fixing agent names...');
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
    await db.run('UPDATE agents SET name_ja = ? WHERE name = ?', [name_ja, name]);
  }

  console.log('Fixing department names...');
  const deptFixes = [
    ['planning', '企画チーム'],
    ['dev', '開発チーム'],
    ['design', 'デザインチーム'],
    ['qa', '品質管理チーム'],
    ['devsecops', 'インフラ・セキュリティ'],
    ['operations', '運用チーム']
  ];

  for (const [id, name_ja] of deptFixes) {
    await db.run('UPDATE departments SET name_ja = ? WHERE id = ?', [name_ja, id]);
  }

  console.log('Database encoding fix completed.');
  await db.close();
}

fix().catch(console.error);
