"""
Tools module - Register all MCP tools
"""
from mcp.server import Server
from mcp.types import Tool, TextContent

# Import tool functions
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


def register_tools(server: Server):
    """
    Register all tools with the MCP server
    
    Args:
        server: MCP Server instance
    """
    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        """
        List all available tools
        
        Returns:
            list[Tool]: List of available tools
        """
        return [
            # Code management tools
            Tool(
                name="nonpayment.code.search",
                description="Search for non-payment item codes by keyword. Returns matching codes with category information.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Search keyword (e.g., '1인실', 'MRI')"
                        },
                        "date": {
                            "type": "string",
                            "description": "Date for validation (YYYY-MM-DD format, optional)"
                        }
                    },
                    "required": ["keyword"]
                }
            ),
            Tool(
                name="nonpayment.code.hierarchy",
                description="Get classification hierarchy for a non-payment code. Returns major, middle, and sub categories.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        }
                    },
                    "required": ["npayCd"]
                }
            ),
            Tool(
                name="nonpayment.code.explain",
                description="Get plain-language explanation for a non-payment code. Helps patients understand what the code means.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        }
                    },
                    "required": ["npayCd"]
                }
            ),
            Tool(
                name="nonpayment.code.validate",
                description="Validate code validity and expiration date. Checks if a code is valid for a specific date.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        },
                        "date": {
                            "type": "string",
                            "description": "Date to check (YYYY-MM-DD format)"
                        }
                    },
                    "required": ["npayCd", "date"]
                }
            ),
            # Hospital information tools
            Tool(
                name="nonpayment.hospital.search",
                description="Search for hospitals offering specific non-payment items. Filter by region and hospital type.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        },
                        "sido": {
                            "type": "string",
                            "description": "City/Province name (e.g., '서울', '부산')"
                        },
                        "sggu": {
                            "type": "string",
                            "description": "District name (optional)"
                        },
                        "clCd": {
                            "type": "string",
                            "description": "Hospital type code or name (e.g., '상급종합', '종합병원')"
                        }
                    },
                    "required": ["npayCd"]
                }
            ),
            Tool(
                name="nonpayment.hospital.price-range",
                description="Get price range for a specific item at a hospital. Returns minimum and maximum prices.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "hospital": {
                            "type": "string",
                            "description": "Hospital name"
                        },
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        }
                    },
                    "required": ["hospital", "npayCd"]
                }
            ),
            Tool(
                name="nonpayment.hospital.compare",
                description="Compare prices across hospitals in the same region. Returns cheapest, most expensive, and median prices.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        },
                        "sido": {
                            "type": "string",
                            "description": "City/Province name"
                        },
                        "sggu": {
                            "type": "string",
                            "description": "District name (optional)"
                        }
                    },
                    "required": ["npayCd", "sido"]
                }
            ),
            # Statistical analysis tools
            Tool(
                name="nonpayment.stats.by-region",
                description="Get price statistics by region for a non-payment item. Returns average, min, and max prices per region.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        }
                    },
                    "required": ["npayCd"]
                }
            ),
            Tool(
                name="nonpayment.stats.by-hospital-type",
                description="Get price statistics by hospital type. Compares prices across different hospital types.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        }
                    },
                    "required": ["npayCd"]
                }
            ),
            Tool(
                name="nonpayment.stats.outlier-detect",
                description="Detect if a hospital's price is abnormally high or low. Compares against regional or hospital-specific averages.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "hospital": {
                            "type": "string",
                            "description": "Hospital name"
                        },
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        },
                        "price": {
                            "type": "number",
                            "description": "Price to check"
                        }
                    },
                    "required": ["hospital", "npayCd", "price"]
                }
            ),
            # Decision support tools
            Tool(
                name="nonpayment.decision.cheapest-option",
                description="Find the cheapest option based on location. Returns the most affordable hospital in the specified region.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        },
                        "sido": {
                            "type": "string",
                            "description": "City/Province name"
                        },
                        "sggu": {
                            "type": "string",
                            "description": "District name (optional)"
                        }
                    },
                    "required": ["npayCd", "sido"]
                }
            ),
            Tool(
                name="nonpayment.decision.reasonable-price",
                description="Determine if a price is reasonable. Compares against regional or overall averages.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        },
                        "price": {
                            "type": "number",
                            "description": "Price to check"
                        },
                        "sido": {
                            "type": "string",
                            "description": "City/Province name (optional, for regional comparison)"
                        }
                    },
                    "required": ["npayCd", "price"]
                }
            ),
            Tool(
                name="nonpayment.decision.explanation-report",
                description="Generate a patient-friendly explanation report. Provides comprehensive information about a non-payment item.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "npayCd": {
                            "type": "string",
                            "description": "Non-payment code"
                        },
                        "sido": {
                            "type": "string",
                            "description": "City/Province name (optional)"
                        }
                    },
                    "required": ["npayCd"]
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        """
        Handle tool calls
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            list[TextContent]: Tool execution results
        """
        try:
            # Code management tools
            if name == "nonpayment.code.search":
                keyword = arguments.get("keyword")
                date = arguments.get("date")
                result = await code_search(keyword, date)
            
            elif name == "nonpayment.code.hierarchy":
                npay_cd = arguments.get("npayCd")
                result = await code_hierarchy(npay_cd)
            
            elif name == "nonpayment.code.explain":
                npay_cd = arguments.get("npayCd")
                result = await code_explain(npay_cd)
            
            elif name == "nonpayment.code.validate":
                npay_cd = arguments.get("npayCd")
                date = arguments.get("date")
                result = await code_validate(npay_cd, date)
            
            # Hospital information tools
            elif name == "nonpayment.hospital.search":
                npay_cd = arguments.get("npayCd")
                sido = arguments.get("sido")
                sggu = arguments.get("sggu")
                cl_cd = arguments.get("clCd")
                result = await hospital_search(npay_cd, sido, sggu, cl_cd)
            
            elif name == "nonpayment.hospital.price-range":
                hospital = arguments.get("hospital")
                npay_cd = arguments.get("npayCd")
                result = await hospital_price_range(hospital, npay_cd)
            
            elif name == "nonpayment.hospital.compare":
                npay_cd = arguments.get("npayCd")
                sido = arguments.get("sido")
                sggu = arguments.get("sggu")
                result = await hospital_compare(npay_cd, sido, sggu)
            
            # Statistical analysis tools
            elif name == "nonpayment.stats.by-region":
                npay_cd = arguments.get("npayCd")
                result = await stats_by_region(npay_cd)
            
            elif name == "nonpayment.stats.by-hospital-type":
                npay_cd = arguments.get("npayCd")
                result = await stats_by_hospital_type(npay_cd)
            
            elif name == "nonpayment.stats.outlier-detect":
                hospital = arguments.get("hospital")
                npay_cd = arguments.get("npayCd")
                price = arguments.get("price")
                result = await stats_outlier_detect(hospital, npay_cd, price)
            
            # Decision support tools
            elif name == "nonpayment.decision.cheapest-option":
                npay_cd = arguments.get("npayCd")
                sido = arguments.get("sido")
                sggu = arguments.get("sggu")
                result = await decision_cheapest_option(npay_cd, sido, sggu)
            
            elif name == "nonpayment.decision.reasonable-price":
                npay_cd = arguments.get("npayCd")
                price = arguments.get("price")
                sido = arguments.get("sido")
                result = await decision_reasonable_price(npay_cd, price, sido)
            
            elif name == "nonpayment.decision.explanation-report":
                npay_cd = arguments.get("npayCd")
                sido = arguments.get("sido")
                result = await decision_explanation_report(npay_cd, sido)
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
            
            # Enforce 24k character limit (PlayMCP policy requirement)
            MAX_RESPONSE_SIZE = 24 * 1024  # 24k characters
            if len(result) > MAX_RESPONSE_SIZE:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Response exceeds 24k limit ({len(result)} chars), truncating to {MAX_RESPONSE_SIZE} chars")
                result = result[:MAX_RESPONSE_SIZE - 3] + "..."
            
            return [TextContent(
                type="text",
                text=result
            )]
        
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
