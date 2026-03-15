import { DatabaseSync } from "node:sqlite";

async function fix() {
  const dbPath = "./claw-empire.sqlite";
  const db = new DatabaseSync(dbPath);

  // Unicode escape sequence to avoid terminal encoding issues
  const deptMap: Record<string, string> = {
    'planning': '\u4f01\u753b\u30c1\u30fc\u30e0', // 企画チーム
    'dev': '\u958b\u767a\u30c1\u30fc\u30e0', // 開発チーム
    'design': '\u30c7\u30b6\u30a4\u30f3\u30c1\u30fc\u30e0', // デザインチーム
    'qa': '\u54c1\u8cea\u7ba1\u7406\u30c1\u30fc\u30e0', // 品質管理チーム
    'devsecops': '\u30a4\u30f3\u30d5\u30e9\u30fb\u30bb\u30ad\u30e5\u30ea\u30c6\u30a3', // インフラ・セキュリティ
    'operations': '\u904b\u7528\u30c1\u30fc\u30e0', // 運用チーム
    'breakRoom': '\u4fe1\u61a9\u5ba4', // 休憩室
    'ceoOffice': 'CEO\u5ba4' // CEO室
  };

  const agentMap: Record<string, string> = {
    'Aria': '\u30a2\u30ea\u30a2', 'Bolt': '\u30dc\u30eb\u30c8', 'Nova': '\u30ce\u30d0', 'Pixel': '\u30d4\u30af\u30bb\u30eb',
    'Luna': '\u30eb\u30ca', 'Sage': '\u30bb\u30fc\u30b8', 'Clio': '\u30af\u30ea\u30aa', 'Atlas': '\u30a2\u30c8\u30e9\u30b9',
    'Turbo': '\u30bf\u30fc\u30dc', 'Hawk': '\u30db\u30fc\u30af', 'Lint': '\u30ea\u30f3\u30c8', 'Vault': '\u30f4\u30a9\u30eb\u30c8',
    'Pipe': '\u30d1\u30a4\u30d7', 'DORO': '\u30c9\u30ed', '髴忿': '\u30a4\u30f3\u30bf\u30fc\u30f3'
  };

  console.log('Fetching departments...');
  const departments = db.prepare('SELECT id, name FROM departments').all() as { id: string, name: string }[];
  for (const dept of departments) {
    const name_ja = deptMap[dept.id] || dept.name;
    db.prepare('UPDATE departments SET name_ja = ?, name_ko = ? WHERE id = ?').run(name_ja, '', dept.id);
  }

  console.log('Fetching agents...');
  const agents = db.prepare('SELECT id, name FROM agents').all() as { id: string, name: string }[];
  for (const agent of agents) {
    const name_ja = agentMap[agent.name] || agent.name;
    db.prepare('UPDATE agents SET name_ja = ?, name_ko = ? WHERE id = ?').run(name_ja, '', agent.id);
  }

  console.log('Database fix completed (Unicode escaped).');
}

fix().catch(console.error);
