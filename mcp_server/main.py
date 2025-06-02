# weatherChatbot/mcp_server/main.py
from fastapi import FastAPI
from mcp_server.router import router

app = FastAPI(title="MCP Weather Server")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "MCP Weather Server is running!"}