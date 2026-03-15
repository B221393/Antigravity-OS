import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

async function importAnimas() {
  const dbPath = "./claw-empire.sqlite";
  const db = new DatabaseSync(dbPath);
  
  const animasDir = "C:/Users/Yuto/.animaworks/animas";
  if (!fs.existsSync(animasDir)) {
    console.error("AnimaWorks directory not found.");
    return;
  }

  const animas = fs.readdirSync(animasDir).filter(f => fs.statSync(path.join(animasDir, f)).isDirectory());
  
  console.log(`Found Animas: ${animas.join(', ')}`);

  for (const anima of animas) {
    // Check if already exists
    const existing = db.prepare('SELECT id FROM agents WHERE name = ?').get(anima) as { id: string } | undefined;
    if (existing) {
      console.log(`Anima ${anima} already exists in Claw-Empire (ID: ${existing.id}). Skipping.`);
      continue;
    }

    const id = crypto.randomUUID();
    // Default to 'dev' department and 'junior' role for imported animas
    const department_id = 'dev'; 
    const role = 'junior';
    
    // Create Japanese name by capitalizing and adding a label
    const name_ja = anima.charAt(0).toUpperCase() + anima.slice(1) + ' (Anima)';

    console.log(`Importing Anima: ${anima} as ${name_ja} into Claw-Empire...`);

    const stmt = db.prepare(`
      INSERT INTO agents (
        id, name, name_ko, name_ja, name_zh, department_id, workflow_pack_key, 
        role, acts_as_planning_leader, cli_provider, status, avatar_emoji, sprite_number
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      id, 
      anima, 
      '', // name_ko
      name_ja, 
      '', // name_zh
      department_id, 
      'development', // workflow_pack_key
      role, 
      0, // acts_as_planning_leader
      'api', // cli_provider: Mark as API to distinguish
      'idle', 
      '🤖', // avatar_emoji
      Math.floor(Math.random() * 12) + 1 // random sprite 1-12
    );
  }

  console.log('AnimaWorks integration (Import) completed successfully.');
}

importAnimas().catch(console.error);
