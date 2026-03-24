import discord
from discord import app_commands
import os
import io
import sys
import json
import asyncio
from contextlib import redirect_stdout

# --- LOAD SECRETS ---
SECRETS_FILE = os.path.join(os.path.dirname(__file__), "secrets.json")
try:
    with open(SECRETS_FILE, "r") as f:
        secrets = json.load(f)
        DISCORD_TOKEN = secrets.get("discord_token", "")
except FileNotFoundError:
    print(f"Error: {SECRETS_FILE} not found.")
    sys.exit(1)

# --- CONFIG ---
# sys.path hack to find modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from modules.unified_llm import UnifiedLLM

llm = UnifiedLLM() # Uses default (Ollama/Phi-4)

# DISABLE PRIVILEGED INTENTS (Fix for PrivilegedIntentsRequired)
intents = discord.Intents.default()
intents.message_content = False 
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# --- LOGIC MODULE ---
try:
    from apps.discord_bot.logic import DiscordLogic
    logic = DiscordLogic()
except ImportError as e:
    print(f"Logic Import Error: {e}")
    sys.exit(1)

# --- SLASH COMMANDS ---

@tree.command(name="diary", description="Write to Neural Log (Syncs with PC)")
async def diary(interaction: discord.Interaction, content: str):
    await interaction.response.defer()
    result = logic.add_diary_entry(content)
    if result["success"]:
        await interaction.followup.send(f"✅ Diary Saved: `{content}`")
    else:
        await interaction.followup.send(f"⚠️ Error: {result.get('error')}")

@tree.command(name="task", description="Add Task to Manager Memo")
async def task(interaction: discord.Interaction, content: str):
    await interaction.response.defer()
    result = logic.add_task(content)
    if result["success"]:
        await interaction.followup.send(f"✅ Task Added: `{content}`")
    else:
        await interaction.followup.send(f"⚠️ Error: {result.get('error')}")

@tree.command(name="research", description="Search the web via PC Agent")
async def research(interaction: discord.Interaction, query: str):
    await interaction.followup.send("⚠️ Feature disabled in Local Mode (Phi-4).")

@tree.command(name="code", description="Execute Python Code on PC (phi-4 Local)")
async def code(interaction: discord.Interaction, instruction: str):
    await interaction.response.defer()
    
    SYSTEM_PROMPT = """
    You are a Python Code Generator for PC Automation.
    User request: "{instruction}"
    Generate Python code to execute this on Windows.
    Return ONLY ```python ... ``` logic within code blocks.
    Assume 'os', 'sys' imported.
    """
    
    try:
        # Use Local Phi-4 via UnifiedLLM
        content = llm.generate(SYSTEM_PROMPT.replace("{instruction}", instruction))

        if "```python" in content:
            py_code = content.split("```python")[1].split("```")[0].strip()
            
            # Execute
            f = io.StringIO()
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
            exec_globals = {'os': os, 'sys': sys, 'project_root': project_root}
            
            try:
                with redirect_stdout(f):
                    exec(py_code, exec_globals)
                output = f.getvalue() or "Done (No Output)"
                # Truncate output if too long
                if len(output) > 1800: output = output[:1800] + "...(truncated)"
                
                await interaction.followup.send(f"⚙️ Executed:\n```python\n{py_code}\n```\n✅ Result:\n```\n{output}\n```")
            except Exception as e:
                await interaction.followup.send(f"⚠️ Exec Logic Error:\n```\n{e}\n```")
        else:
            await interaction.followup.send(f"⚠️ Failed to generate code. Response:\n{content}")

    except Exception as e:
        await interaction.followup.send(f"⚠️ API Error: {e}")

@client.event
async def on_ready():
    print(f'✅ VECTIS SLASH BOT: Logged in as {client.user}')
    await tree.sync()
    print('Slash Commands Synced.')

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ Secrets Error.")
    else:
        client.run(DISCORD_TOKEN)
