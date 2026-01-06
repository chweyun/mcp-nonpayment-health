#!/usr/bin/env python3
"""
Run script for Remote MCP Server
"""
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "src.server_http:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

