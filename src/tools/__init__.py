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
            description="""🔍 비급여 항목 코드 검색 - 키워드로 비급여 항목 코드를 검색하여 매칭되는 코드와 카테고리 정보를 반환
📍 사용 시나리오:
- 특정 키워드로 비급여 항목 코드 찾기
- 검색 결과에서 정확한 코드 확인 후 다른 도구 사용
- 비급여 항목의 카테고리 정보 확인

💡 LLM이 이 도구를 사용해야 하는 경우:
- "1인실 비급여 코드 찾아줘" → 키워드로 검색
- "MRI 검사 비급여 항목" → 관련 코드 검색
- 사용자가 항목명만 알고 있을 때 → 코드를 찾기 위해 먼저 호출

⚠️ 주의사항:
- 검색 결과는 최대 10개까지만 반환됨
- date 파라미터는 선택사항이며, 특정 날짜 기준 유효성 검증 시 사용

Args:
keyword: 검색 키워드 (예: '1인실', 'MRI')
date: 검증 날짜 (YYYY-MM-DD 형식, 선택사항)

Returns:
매칭되는 비급여 코드 목록 (코드, 이름, 카테고리, 유효시작일 등)""",
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
            description="""📊 비급여 코드 분류 체계 조회 - 비급여 코드의 대분류, 중분류, 소분류 정보를 반환
📍 사용 시나리오:
- 비급여 항목의 카테고리 구조 파악
- 코드의 상위/하위 분류 확인
- 비급여 항목의 전체적인 분류 체계 이해

💡 LLM이 이 도구를 사용해야 하는 경우:
- "RZ6410000 코드의 분류 체계 알려줘" → 계층 구조 확인
- 비급여 항목의 카테고리 정보가 필요할 때
- 코드 설명 전에 분류 정보 확인

⚠️ 주의사항:
- 정확한 비급여 코드(npayCd)가 필요함
- 코드가 존재하지 않으면 에러 반환

Args:
npayCd: 비급여 코드

Returns:
대분류(major), 중분류(middle), 소분류(sub), 설명(description), 전체명(fullName)""",
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
            description="""📝 비급여 코드 설명 조회 - 비급여 코드를 환자가 이해하기 쉬운 언어로 설명
📍 사용 시나리오:
- 환자에게 비급여 항목이 무엇인지 설명
- 코드의 의미를 일반인도 이해할 수 있게 전달
- 비급여 항목에 대한 기본 정보 제공

💡 LLM이 이 도구를 사용해야 하는 경우:
- "RZ6410000이 뭔지 설명해줘" → 환자 친화적 설명 제공
- 비급여 항목에 대한 질문이 있을 때
- 코드의 의미를 알려줘야 할 때

⚠️ 주의사항:
- 정확한 비급여 코드(npayCd)가 필요함
- 설명이 없는 경우 기본 카테고리 정보로 설명 생성

Args:
npayCd: 비급여 코드

Returns:
비급여 코드에 대한 환자 친화적 설명(plainExplanation)과 카테고리 정보""",
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
            description="""✅ 비급여 코드 유효성 검증 - 특정 날짜 기준으로 비급여 코드의 유효성과 만료일 확인
📍 사용 시나리오:
- 특정 날짜에 코드가 유효한지 확인
- 코드의 유효기간 확인
- 과거/미래 날짜 기준 코드 사용 가능 여부 확인

💡 LLM이 이 도구를 사용해야 하는 경우:
- "2024년 1월 1일에 RZ6410000 코드 사용 가능해?" → 날짜별 유효성 확인
- 코드의 유효기간이 궁금할 때
- 특정 시점의 코드 유효성 검증 필요 시

⚠️ 주의사항:
- date는 YYYY-MM-DD 형식으로 입력 필요
- 코드가 존재하지 않으면 에러 반환
- 유효기간이 없는 경우(99991231) "No expiration" 반환

Args:
npayCd: 비급여 코드
date: 확인할 날짜 (YYYY-MM-DD 형식)

Returns:
유효성 여부(isValid), 유효시작일(validFrom), 유효종료일(validUntil)""",
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
            description="""🏥 비급여 항목 제공 병원 검색 - 특정 비급여 항목을 제공하는 병원 목록을 지역 및 병원 유형으로 필터링하여 검색
📍 사용 시나리오:
- 특정 비급여 항목을 제공하는 병원 찾기
- 지역별/병원 유형별 병원 목록 확인
- 병원 선택 전 후보 병원 파악

💡 LLM이 이 도구를 사용해야 하는 경우:
- "서울에서 RZ6410000 제공하는 병원 찾아줘" → 지역별 병원 검색
- "강남구 상급종합병원 중 비급여 항목 제공하는 곳" → 지역+유형 필터링
- 특정 비급여 항목 병원 목록이 필요할 때

⚠️ 주의사항:
- npayCd는 필수 파라미터
- sido, sggu, clCd는 선택사항이며 필터링에 사용
- 검색 결과는 페이징 처리됨

Args:
npayCd: 비급여 코드 (필수)
sido: 시도명 (예: '서울', '부산', 선택사항)
sggu: 시군구명 (선택사항)
clCd: 병원 유형 코드 또는 이름 (예: '상급종합', '종합병원', 선택사항)

Returns:
해당 비급여 항목을 제공하는 병원 목록 (병원명, 주소, 병원 유형 등)""",
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
            description="""💰 병원별 비급여 항목 가격 범위 조회 - 특정 병원의 특정 비급여 항목에 대한 최소/최대 가격 조회
📍 사용 시나리오:
- 특정 병원의 비급여 항목 가격 범위 확인
- 병원별 가격 비교 전 기본 정보 수집
- 예상 비용 파악

💡 LLM이 이 도구를 사용해야 하는 경우:
- "서울대병원에서 RZ6410000 가격 범위 알려줘" → 특정 병원 가격 확인
- 병원별 가격 비교를 위해 각 병원의 가격 범위 확인
- 예상 비용이 궁금할 때

⚠️ 주의사항:
- 정확한 병원명이 필요함 (병원명이 정확하지 않으면 검색 실패 가능)
- 해당 병원에서 해당 비급여 항목을 제공하지 않으면 에러 반환

Args:
hospital: 병원명
npayCd: 비급여 코드

Returns:
해당 병원의 최소 가격(min), 최대 가격(max) 정보""",
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
            description="""📊 지역별 병원 가격 비교 - 같은 지역 내 병원들의 비급여 항목 가격을 비교하여 최저가, 최고가, 중간가 반환
📍 사용 시나리오:
- 특정 지역 내 병원 간 가격 비교
- 가장 저렴한 병원 찾기
- 지역별 가격 분포 파악

💡 LLM이 이 도구를 사용해야 하는 경우:
- "서울 강남구에서 RZ6410000 가장 저렴한 병원" → 지역별 가격 비교
- "부산에서 이 비급여 항목 가격 비교해줘" → 지역 내 병원 가격 비교
- 가격 비교가 필요할 때

⚠️ 주의사항:
- sido는 필수, sggu는 선택사항
- 해당 지역에 병원이 없으면 에러 반환
- 가격 정보가 없는 병원은 제외됨

Args:
npayCd: 비급여 코드
sido: 시도명 (필수)
sggu: 시군구명 (선택사항)

Returns:
최저가 병원(cheapest), 최저가(cheapestPrice), 최고가(mostExpensive), 최고가(mostExpensivePrice), 중간가(medianPrice)""",
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
            description="""📈 지역별 비급여 항목 통계 조회 - 비급여 항목의 지역별 평균, 최소, 최대 가격 통계 조회
📍 사용 시나리오:
- 전국 지역별 가격 분포 파악
- 지역 간 가격 차이 확인
- 특정 지역의 평균 가격 확인

💡 LLM이 이 도구를 사용해야 하는 경우:
- "RZ6410000 지역별 가격 통계 알려줘" → 전국 지역별 통계
- "서울과 부산 가격 차이" → 지역별 통계 비교
- 지역별 가격 정보가 필요할 때

⚠️ 주의사항:
- 정확한 비급여 코드(npayCd)가 필요함
- 통계 데이터가 없는 경우 에러 반환
- 각 지역별 평균, 최소, 최대 가격 정보 제공

Args:
npayCd: 비급여 코드

Returns:
지역별 통계(regions: 서울, 부산, 인천 등 각 지역의 avg, min, max) 및 전체 통계(overall)""",
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
            description="""🏥 병원 유형별 비급여 항목 통계 조회 - 병원 유형별(상급종합, 종합병원, 병원 등) 평균, 최소, 최대 가격 통계 조회
📍 사용 시나리오:
- 병원 유형별 가격 차이 파악
- 어떤 병원 유형이 저렴한지 확인
- 병원 유형 선택 시 가격 정보 참고

💡 LLM이 이 도구를 사용해야 하는 경우:
- "상급종합병원과 종합병원 가격 차이" → 병원 유형별 통계 비교
- "RZ6410000 병원 유형별 가격 통계" → 유형별 가격 정보
- 병원 유형 선택 시 가격 고려가 필요할 때

⚠️ 주의사항:
- 정확한 비급여 코드(npayCd)가 필요함
- 통계 데이터가 없는 경우 에러 반환
- 상급종합, 종합병원, 병원, 치과병원, 한방병원, 요양병원 유형별 통계 제공

Args:
npayCd: 비급여 코드

Returns:
병원 유형별 통계(hospitalTypes: 각 유형별 avg, min, max) 및 전체 통계(overall)""",
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
            description="""⚠️ 병원 가격 이상치 탐지 - 특정 병원의 비급여 항목 가격이 정상 범위를 벗어났는지 확인
📍 사용 시나리오:
- 병원에서 제시한 가격이 비정상적으로 높거나 낮은지 확인
- 가격 검증이 필요할 때
- 가격 협상 전 기준 확인

💡 LLM이 이 도구를 사용해야 하는 경우:
- "서울대병원에서 10만원 받는데 정상인가요?" → 가격 이상치 확인
- "이 가격이 비싼 편인가요?" → 가격 정상성 검증
- 가격에 대한 의문이 있을 때

⚠️ 주의사항:
- 병원명, 비급여 코드, 가격 모두 필수
- 병원별 가격 범위가 있으면 그것을 기준으로, 없으면 지역 평균 기준으로 판단
- 평균 대비 30% 이상 차이나면 이상치로 판단

Args:
hospital: 병원명
npayCd: 비급여 코드
price: 확인할 가격

Returns:
이상치 여부(isOutlier), 높은지 여부(isHigh), 판단 근거(reason), 평균 가격(averagePrice), 편차(deviation)""",
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
            description="""💵 지역별 최저가 옵션 찾기 - 특정 지역에서 해당 비급여 항목을 가장 저렴하게 제공하는 병원 찾기
📍 사용 시나리오:
- 특정 지역에서 가장 저렴한 병원 찾기
- 가격 중심으로 병원 선택
- 지역 내 가격 비교 후 최저가 병원 확인

💡 LLM이 이 도구를 사용해야 하는 경우:
- "서울 강남구에서 RZ6410000 가장 저렴한 병원 찾아줘" → 최저가 병원 검색
- "부산에서 이 비급여 항목 가장 싼 곳" → 지역별 최저가 찾기
- 가격이 가장 중요한 선택 기준일 때

⚠️ 주의사항:
- sido는 필수, sggu는 선택사항
- 해당 지역에 병원이 없으면 에러 반환
- 중간가와의 차이(savings)도 함께 제공

Args:
npayCd: 비급여 코드
sido: 시도명 (필수)
sggu: 시군구명 (선택사항)

Returns:
최저가 병원(cheapestOption: hospital, price), 중간가(medianPrice), 절약액(savings), 항목 설명(explanation)""",
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
            description="""💡 가격 합리성 판단 - 제시된 가격이 합리적인지 지역 평균 또는 전체 평균과 비교하여 판단
📍 사용 시나리오:
- 병원에서 제시한 가격이 합리적인지 확인
- 가격 협상 전 기준 확인
- 가격에 대한 의문 해소

💡 LLM이 이 도구를 사용해야 하는 경우:
- "75000원이 합리적인 가격인가요?" → 가격 합리성 판단
- "이 가격 괜찮나요?" → 가격 평가 필요 시
- 가격에 대한 의문이 있을 때
- sido가 제공되면 해당 지역 평균과 비교, 없으면 전체 평균과 비교

⚠️ 주의사항:
- npayCd와 price는 필수, sido는 선택사항
- sido가 제공되면 해당 지역 평균과 비교, 없으면 전체 병원 유형별 평균과 비교
- 평균 대비 ±20% 이내면 "합리적", 그 외는 "비싼 편" 또는 "저렴한 편"으로 판단
- 통계 데이터가 없으면 에러 반환

Args:
npayCd: 비급여 코드 (필수)
price: 확인할 가격 (필수)
sido: 시도명 (선택사항, 지역별 비교 시 사용)

Returns:
판단 결과(judgement: 합리적/비싼 편/저렴한 편), 판단 근거(basis), 통계 정보(statistics: average, min, max), 편차(deviation)""",
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
            description="""📋 비급여 항목 종합 설명 보고서 생성 - 환자가 이해하기 쉬운 비급여 항목에 대한 종합 정보 제공
📍 사용 시나리오:
- 비급여 항목에 대한 종합적인 정보 제공
- 환자에게 비급여 항목 선택 가이드 제공
- 가격 변동성과 병원 유형별 추천 정보 제공

💡 LLM이 이 도구를 사용해야 하는 경우:
- "RZ6410000에 대해 자세히 설명해줘" → 종합 정보 제공
- "이 비급여 항목 선택할 때 고려사항 알려줘" → 선택 가이드 제공
- 비급여 항목에 대한 종합적인 정보가 필요할 때

⚠️ 주의사항:
- npayCd는 필수, sido는 선택사항
- 항목 설명, 가격 변동성, 병원 유형별 추천 정보 포함
- 통계 데이터가 없어도 기본 설명은 제공

Args:
npayCd: 비급여 코드 (필수)
sido: 시도명 (선택사항, 지역별 정보 포함 시 사용)

Returns:
종합 요약(summary), 추천사항(recommendation), 카테고리 정보(category), 가격 정보(priceInfo)""",
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
