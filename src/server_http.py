"""
HTTP based Remote MCP Server entry point
Compliant with MCP specification 2025-03-26
- Streamable HTTP transport
- Stateless server (no session management)
- Remote server (publicly accessible URL)
"""
import os
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server import Server
from contextlib import asynccontextmanager

from src.tools import register_tools
from src.tools.code_tools import (
    code_search,
    code_hierarchy,
    code_explain,
    code_validate
)
from src.tools.hospital_tools import (
    hospital_search,
    hospital_price_range,
    hospital_compare
)
from src.tools.stats_tools import (
    stats_by_region,
    stats_by_hospital_type,
    stats_outlier_detect
)
from src.tools.decision_tools import (
    decision_cheapest_option,
    decision_reasonable_price,
    decision_explanation_report
)
from src.resources import register_resources
from mcp.types import TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API prefix for multi-server hosting
API_PREFIX = os.getenv("API_PREFIX", "/nonpayment-health")

# Create MCP server instance
mcp_server = Server("nonpayment-health")

# Register tools and resources
register_tools(mcp_server)
register_resources(mcp_server)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Non-Payment Health MCP Server (Remote)...")
    yield
    # Shutdown
    logger.info("Shutting down Non-Payment Health MCP Server...")


app = FastAPI(
    title="Non-Payment Health MCP Server",
    description="Remote MCP Server for non-payment medical expense information",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "nonpayment-health",
        "version": "1.0.0",
        "status": "running",
        "description": "Remote MCP Server for non-payment medical expense information",
        "mcp_version": "2025-03-26",
        "api_prefix": API_PREFIX,
        "endpoint": f"{API_PREFIX}/messages"
    }


@app.get(f"{API_PREFIX}/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "nonpayment-health"}


@app.post(f"{API_PREFIX}/messages")
async def messages_endpoint(request: Request):
    """
    MCP protocol messages endpoint
    Handles JSON-RPC style messages from MCP clients
    """
    try:
        body = await request.json()
        
        # Extract method and params from JSON-RPC request
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        # Handle different MCP methods
        if method == "initialize":
            # Return server capabilities
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "nonpayment-health",
                        "version": "1.0.0"
                    }
                }
            }
            return JSONResponse(content=response)
        
        elif method == "tools/list":
            # Get list of tools from server
            tools_list = await mcp_server.list_tools()
            
            tools_dict = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools_list
            ]
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools_dict
                }
            }
            return JSONResponse(content=response)
        
        elif method == "tools/call":
            # Call a tool
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            try:
                # Route to appropriate tool function
                result_text = None
                
                # Code management tools
                if tool_name == "nonpayment.code.search":
                    result_text = await code_search(
                        tool_args.get("keyword"),
                        tool_args.get("date")
                    )
                elif tool_name == "nonpayment.code.hierarchy":
                    result_text = await code_hierarchy(tool_args.get("npayCd"))
                elif tool_name == "nonpayment.code.explain":
                    result_text = await code_explain(tool_args.get("npayCd"))
                elif tool_name == "nonpayment.code.validate":
                    result_text = await code_validate(
                        tool_args.get("npayCd"),
                        tool_args.get("date")
                    )
                
                # Hospital information tools
                elif tool_name == "nonpayment.hospital.search":
                    result_text = await hospital_search(
                        tool_args.get("npayCd"),
                        tool_args.get("sido"),
                        tool_args.get("sggu"),
                        tool_args.get("clCd")
                    )
                elif tool_name == "nonpayment.hospital.price-range":
                    result_text = await hospital_price_range(
                        tool_args.get("hospital"),
                        tool_args.get("npayCd")
                    )
                elif tool_name == "nonpayment.hospital.compare":
                    result_text = await hospital_compare(
                        tool_args.get("npayCd"),
                        tool_args.get("sido"),
                        tool_args.get("sggu")
                    )
                
                # Statistical analysis tools
                elif tool_name == "nonpayment.stats.by-region":
                    result_text = await stats_by_region(tool_args.get("npayCd"))
                elif tool_name == "nonpayment.stats.by-hospital-type":
                    result_text = await stats_by_hospital_type(tool_args.get("npayCd"))
                elif tool_name == "nonpayment.stats.outlier-detect":
                    result_text = await stats_outlier_detect(
                        tool_args.get("hospital"),
                        tool_args.get("npayCd"),
                        tool_args.get("price")
                    )
                
                # Decision support tools
                elif tool_name == "nonpayment.decision.cheapest-option":
                    result_text = await decision_cheapest_option(
                        tool_args.get("npayCd"),
                        tool_args.get("sido"),
                        tool_args.get("sggu")
                    )
                elif tool_name == "nonpayment.decision.reasonable-price":
                    result_text = await decision_reasonable_price(
                        tool_args.get("npayCd"),
                        tool_args.get("price"),
                        tool_args.get("sido")
                    )
                elif tool_name == "nonpayment.decision.explanation-report":
                    result_text = await decision_explanation_report(
                        tool_args.get("npayCd"),
                        tool_args.get("sido")
                    )
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
                    return JSONResponse(content=response, status_code=404)
                
                if result_text is None:
                    raise Exception("Tool returned None")
                
                # Enforce 24k character limit (PlayMCP policy requirement)
                MAX_RESPONSE_SIZE = 24 * 1024  # 24k characters
                if len(result_text) > MAX_RESPONSE_SIZE:
                    logger.warning(f"Response exceeds 24k limit ({len(result_text)} chars), truncating to {MAX_RESPONSE_SIZE} chars")
                    result_text = result_text[:MAX_RESPONSE_SIZE - 3] + "..."
                
                content = [TextContent(type="text", text=result_text)]
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": item.type,
                                "text": item.text
                            }
                            for item in content
                        ]
                    }
                }
                return JSONResponse(content=response)
            
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {str(e)}")
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                return JSONResponse(content=response, status_code=500)
        
        else:
            # Unknown method
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            return JSONResponse(content=response, status_code=404)
    
    except json.JSONDecodeError:
        return JSONResponse(
            content={"error": "Invalid JSON"},
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error in messages endpoint: {str(e)}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "src.server_http:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )

