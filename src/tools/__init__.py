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


def get_all_tools() -> list[Tool]:
    """
    Get all available tools as a list
    
    Returns:
        list[Tool]: List of all available tools
    """
    return [
        # Code management tools
        Tool(
            name="SearchNonPaymentCode",
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
            name="GetNonPaymentCodeHierarchy",
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
            name="ExplainNonPaymentCode",
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
            name="ValidateNonPaymentCode",
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
            name="SearchNonPaymentHospitals",
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
            name="GetHospitalPriceRange",
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
            name="CompareHospitalPrices",
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
            name="GetNonPaymentStatsByRegion",
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
            name="GetNonPaymentStatsByHospitalType",
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
            name="DetectPriceOutlier",
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
            name="FindCheapestOption",
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
            name="CheckReasonablePrice",
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
            name="GenerateExplanationReport",
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
        return get_all_tools()

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
            if name == "SearchNonPaymentCode":
                keyword = arguments.get("keyword")
                date = arguments.get("date")
                result = await code_search(keyword, date)
            
            elif name == "GetNonPaymentCodeHierarchy":
                npay_cd = arguments.get("npayCd")
                result = await code_hierarchy(npay_cd)
            
            elif name == "ExplainNonPaymentCode":
                npay_cd = arguments.get("npayCd")
                result = await code_explain(npay_cd)
            
            elif name == "ValidateNonPaymentCode":
                npay_cd = arguments.get("npayCd")
                date = arguments.get("date")
                result = await code_validate(npay_cd, date)
            
            # Hospital information tools
            elif name == "SearchNonPaymentHospitals":
                npay_cd = arguments.get("npayCd")
                sido = arguments.get("sido")
                sggu = arguments.get("sggu")
                cl_cd = arguments.get("clCd")
                result = await hospital_search(npay_cd, sido, sggu, cl_cd)
            
            elif name == "GetHospitalPriceRange":
                hospital = arguments.get("hospital")
                npay_cd = arguments.get("npayCd")
                result = await hospital_price_range(hospital, npay_cd)
            
            elif name == "CompareHospitalPrices":
                npay_cd = arguments.get("npayCd")
                sido = arguments.get("sido")
                sggu = arguments.get("sggu")
                result = await hospital_compare(npay_cd, sido, sggu)
            
            # Statistical analysis tools
            elif name == "GetNonPaymentStatsByRegion":
                npay_cd = arguments.get("npayCd")
                result = await stats_by_region(npay_cd)
            
            elif name == "GetNonPaymentStatsByHospitalType":
                npay_cd = arguments.get("npayCd")
                result = await stats_by_hospital_type(npay_cd)
            
            elif name == "DetectPriceOutlier":
                hospital = arguments.get("hospital")
                npay_cd = arguments.get("npayCd")
                price = arguments.get("price")
                result = await stats_outlier_detect(hospital, npay_cd, price)
            
            # Decision support tools
            elif name == "FindCheapestOption":
                npay_cd = arguments.get("npayCd")
                sido = arguments.get("sido")
                sggu = arguments.get("sggu")
                result = await decision_cheapest_option(npay_cd, sido, sggu)
            
            elif name == "CheckReasonablePrice":
                npay_cd = arguments.get("npayCd")
                price = arguments.get("price")
                sido = arguments.get("sido")
                result = await decision_reasonable_price(npay_cd, price, sido)
            
            elif name == "GenerateExplanationReport":
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
