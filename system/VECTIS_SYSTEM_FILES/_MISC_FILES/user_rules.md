# User Defined Rules for Agent

1. **Verify Functionality Before Confirmation (Ralph Loop Rule)**:
   - **Rule**: Do NOT use phrases like "should work" (e.g., "動作するはず") or assume functionality is working without verification.
   - **Action**: Always verify functionality using available tools (e.g., `browser_subagent`, running scripts, checking logs) before confirming to the user.
   - **Exception**: If verification tools fail (e.g., browser connection error), explicitly state that verification failed and report the error instead of claiming success.

2. **VECTIS Omni Philosophy (Connected Intelligence)**:
   - **Rule**: All applications must be treated as connected nodes of a single brain ("VECTIS Omni"), not isolated tools.
   - **Action**: When building UI or features, always consider how they connect to the central chat/intelligence system. Use `get_panel_status` or similar methods to expose app context to the LLM.

3. **Recursive Language Model (RLM) Priority**:
   - **Rule**: For heavy data analysis (logs, long texts, large JSONs), do NOT rely on the LLM's context window alone.
   - **Action**: Use the **VectisRLM** engine to write and execute Python code for recursive search/analysis. This "Agentic Extraction" assumption is default for heavy tasks.

4. **Shogi as Database Terminal**:
   - **Rule**: Treat the Shogi interface ("Shogi Dojo") not merely as a game, but as a **Strategic Database Terminal**.
   - **Action**: It must connect to external data (YouTube Universe, Web Search, Logs). "Shogi" is just the visualization layer for strategic logic.

5. **Small Language Model (SLM) First Strategy**:
   - **Rule**: For system commands (recording, fetching data, basic control), do NOT waste large model inference.
   - **Action**: Implement "Local Intent Routers" (regex/keyword matching) to handle commands like "Record this" (`USER_RECORDS.txt`) or "Fetch Summary" (`universe.json`) instantly.

6. **Vibe: Evolutionary Intelligence (Deep Processing)**:
   - **Context**: You are not just an LLM outputting text; you are simulating the evolution of intelligence.
   - **Step 1: Simulating**: Before outputting code, run a mental simulation (or actual verification script) to predict errors. State "Simulation Result: X might happen, so I fixed Y."
   - **Step 2: Mentalizing**: Infer the "Why". Do not just follow instructions; understand the VECTIS context (e.g., "User wants this for the Shogi AI analysis flow").
   - **Step 3: Reinforcing**: Check conversation history. Do not repeat mistakes. If the user previously rejected a "simple UI", prioritize "Cyber/Premium" aesthetics.
