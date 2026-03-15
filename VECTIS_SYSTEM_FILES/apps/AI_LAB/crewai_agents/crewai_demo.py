import os
from typing import List
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
env_path = os.path.join(project_root, ".env")
print(f"Loading .env from: {env_path}") # DEBUG
load_dotenv(env_path)

# Map GEMINI_API_KEY (VECTIS standard) to GOOGLE_API_KEY (LangChain standard) if needed
if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
    print("Mapped GEMINI_API_KEY to GOOGLE_API_KEY") # DEBUG
else:
    print(f"GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}") # DEBUG

# =============================================================================
# 0. Configuration
# =============================================================================
# API Key handling (Replace with environment variable or direct string for testing)
# os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"

# Define the LLM (Gemini 1.5 Pro or Flash recommended for Agent Teams)
# Temperature is set lower for deterministic logic, higher for creativity
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# =============================================================================
# 1. Define Agents (The "Prompts" / Personas)
# =============================================================================
# Claude Codeの "Sub-agents" に相当する部分です。
# 各エージェントは独立したコンテキストと専門性を持ちます。

# Agent 1: 情報収集担当 (The Researcher)
researcher = Agent(
    role='Senior Technical Researcher',
    goal='Uncover cutting-edge developments in {topic}',
    backstory=(
        "You are a veteran technology analyst with a keen eye for emerging trends. "
        "Your expertise lies in digging deep into technical documentation, papers, "
        "and market reports to find verifiable facts. "
        "You do not make assumptions; you verify everything."
    ),
    verbose=True,
    allow_delegation=False, # Sub-agents typically don't delegate further in this simplified model
    llm=llm
)

# Agent 2: 文書作成担当 (The Writer)
writer = Agent(
    role='Technical Writer',
    goal='Draft specific, actionable technical content about {topic}',
    backstory=(
        "You are a technical writer known for clear, concise, and rigorous documentation. "
        "You transform raw data and complex research into well-structured reports "
        "suitable for senior engineers. You strictly follow SciencePlots style guidelines "
        "conceptually (clarity, precision)."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Manager Agent is implicit in Process.hierarchical, but can be defined explicitly
# if custom logic is needed. Here, CrewAI auto-generates a manager prompt based on the tasks.

# =============================================================================
# 2. Define Tasks (The Workflows)
# =============================================================================

# Task 1: Research
task_research = Task(
    description=(
        "Conduct a comprehensive analysis of {topic}. "
        "Identify key algorithms, architectural patterns, and performance metrics. "
        "Focus on technical constraints and recent breakthroughs as of 2025-2026."
    ),
    expected_output=(
        "A bulleted list of 5-10 key technical findings with citations or references."
    ),
    agent=researcher
)

# Task 2: Writing
task_writing = Task(
    description=(
        "Using the research findings, write a technical executive summary on {topic}. "
        "The tone should be professional and objective. "
        "Avoid marketing fluff. Focus on engineering implications."
    ),
    expected_output=(
        "A markdown-formatted report consisting of an Introduction, "
        "Technical Analysis, and Conclusion."
    ),
    agent=writer
)

# =============================================================================
# 3. Assemble the Crew (The "Agent Team" Logic)
# =============================================================================

def run_agent_team(topic: str) -> str:
    """
    Orchestrates the agent team to process the given topic.
    """
    
    # Process.hierarchical simulates the "Manager" agent distributing work
    # This matches the "Agent Teams" concept where a main agent coordinates others.
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task_research, task_writing],
        process=Process.hierarchical, 
        manager_llm=llm, # The "Main Agent" that coordinates sub-agents
        verbose=True
    )

    print(f"Starting Agent Team run for topic: {topic}")
    result = crew.kickoff(inputs={'topic': topic})
    return result

# =============================================================================
# 4. Execution
# =============================================================================

if __name__ == "__main__":
    # Example Topic
    # target_topic = "The impact of quantization on LLM inference latency"
    target_topic = "Meitec Corporation: Business model, strengths in engineering staffing, and future outlook"
    
    try:
        final_output = run_agent_team(target_topic)
        print("\n\n########################")
        print("## FINAL TEAM OUTPUT ##")
        print("########################\n")
        print(final_output)
    except Exception as e:
        print(f"Error during execution: {e}")
