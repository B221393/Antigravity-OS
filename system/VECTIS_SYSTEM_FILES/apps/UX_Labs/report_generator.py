
import os
import datetime

class ReportGenerator:
    def __init__(self):
        self.issues = []
        self.conversation_log = []

    def log_interaction(self, persona, screen, action, response):
        entry = f"**{persona}** on `{screen}`: {action} -> {response}"
        self.conversation_log.append(entry)

    def log_issue(self, persona, screen, complaint, severity="Medium"):
        self.issues.append({
            "persona": persona,
            "screen": screen,
            "complaint": complaint,
            "severity": severity
        })

    def generate_markdown(self, filename="UX_AUDIT_REPORT.md"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"# UX Audit Report\n\n"
        md += f"**Date**: {now}\n"
        md += f"**Agent**: Universal UX Architect v1.1\n\n"

        md += "## 🚨 Critical Issues\n"
        md += "| Severity | Persona | Screen | Complaint |\n"
        md += "|---|---|---|---|\n"
        
        for issue in self.issues:
            icon = "🔴" if issue['severity'] == "High" else "🟡"
            md += f"| {icon} {issue['severity']} | {issue['persona']} | {issue['screen']} | {issue['complaint']} |\n"

        md += "\n## 💬 Evaluation Log\n"
        for log in self.conversation_log:
            md += f"- {log}\n"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(md)
        
        return os.path.abspath(filename)

    def generate_json(self, filename="latest_audit.json"):
        import json
        data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": "Universal UX Architect v1.1",
            "issues": self.issues,
            "log": self.conversation_log
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return os.path.abspath(filename)
