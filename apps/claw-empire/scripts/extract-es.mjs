import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPORTS_DIR = path.resolve(__dirname, "../docs/reports");

async function askQuestion(query) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve) =>
    rl.question(query, (ans) => {
      rl.close();
      resolve(ans);
    })
  );
}

async function main() {
  const targetUrl = process.argv[2];
  const companyName = process.argv[3] || "unknown-company";

  if (!targetUrl) {
    console.error("Usage: node scripts/extract-es.mjs <URL> [company-name]");
    process.exit(1);
  }

  console.log(`[ES Extractor] Launching browser for ${companyName}...`);
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto(targetUrl);

  console.log("---------------------------------------------------------");
  console.log("1. Please log in manually in the browser window.");
  console.log("2. Navigate to the ES (Entry Sheet) input page.");
  console.log("3. Once the questions are visible, come back here.");
  console.log("---------------------------------------------------------");

  await askQuestion("Press Enter when you are on the ES question page...");

  console.log("[ES Extractor] Extracting questions...");

  // Heuristic extraction of questions
  // Look for:
  // - Labels associated with textareas or inputs
  // - Strong/B tags that might be question headers
  // - Specific patterns like "問1", "Q1", etc.
  const questions = await page.evaluate(() => {
    const results = [];
    
    // Strategy 1: Find labels for textareas
    const textareas = document.querySelectorAll("textarea");
    textareas.forEach((ta, index) => {
      let label = "";
      // Try to find a label element
      const id = ta.getAttribute("id");
      if (id) {
        const labelEl = document.querySelector(`label[for="${id}"]`);
        if (labelEl) label = labelEl.innerText.trim();
      }
      
      // If no label, check preceding elements
      if (!label) {
        let prev = ta.previousElementSibling;
        while (prev && !prev.innerText.trim()) {
          prev = prev.previousElementSibling;
        }
        if (prev) label = prev.innerText.trim();
      }

      results.push({
        type: "textarea",
        index: index + 1,
        label: label || `Question ${index + 1} (No label found)`,
        placeholder: ta.getAttribute("placeholder") || ""
      });
    });

    // Strategy 2: Find elements that look like questions (e.g., "【問1】", "Q.")
    const bodyText = document.body.innerText;
    // (This is harder to automate generally, so we stick to Strategy 1 and broad text search)

    return results;
  });

  if (questions.length === 0) {
    console.log("[ES Extractor] No textareas found. Trying broad text extraction...");
    // Fallback: Just take all text that ends with "?" or looks like a header
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const fileName = `es-questions-${companyName}-${timestamp}.md`;
  const filePath = path.join(REPORTS_DIR, fileName);

  if (!fs.existsSync(REPORTS_DIR)) {
    fs.mkdirSync(REPORTS_DIR, { recursive: true });
  }

  let content = `# ES Questions: ${companyName}

`;
  content += `Extracted on: ${new Date().toLocaleString()}
`;
  content += `Source: ${targetUrl}

`;
  content += `## Questions

`;

  questions.forEach((q) => {
    content += `### ${q.label}
`;
    if (q.placeholder) content += `*Placeholder: ${q.placeholder}*
`;
    content += `
[Your Answer Here]

`;
  });

  fs.writeFileSync(filePath, content, "utf8");

  console.log(`[ES Extractor] Successfully extracted ${questions.length} items.`);
  console.log(`[ES Extractor] Report saved to: ${filePath}`);

  await askQuestion("Press Enter to close the browser...");
  await browser.close();
}

main().catch(console.error);
