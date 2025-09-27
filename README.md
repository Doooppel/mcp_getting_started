Demo using latest OpenAI api to access Google Gemini, build one mcp server and client. 
which can make LLM access local filesystem.

uv init mcp_getting_started
cd mcp_getting_started
uv venv
.venv\Scripts\activate.bat
uv add "mcp[cli]" httpx openai


npx -y @modelcontextprotocol/inspector uv run file_system.py

python mcp_client_with_file_system.py