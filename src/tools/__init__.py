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
    stats_by_hospital_type
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
            description="""🔍 비급여 항목 코드 검색 - 키워드로 비급여 항목 코드를 검색 (워크플로우의 첫 단계)

📋 사용 시점:
✅ 사용자가 항목명이나 키워드만 말했을 때 (코드를 모를 때) - 반드시 먼저 호출
✅ "1인실", "MRI", "초음파" 같은 일반적인 용어로 검색할 때
✅ 여러 관련 항목 중 선택하거나 확인할 때

❌ 사용하지 말아야 할 때:
❌ 이미 정확한 코드(npayCd)를 알고 있을 때 → 다른 도구 사용
❌ 코드가 이미 확인된 상태에서 병원 검색/가격 확인 → SearchNonPaymentHospitals 등 사용

🔄 일반적인 워크플로우:
1. 사용자 질문 → SearchNonPaymentCode로 코드 찾기
2. 코드 확인 → 다른 도구(병원검색, 가격비교 등) 사용

Args:
keyword: 검색 키워드 (예: '1인실', 'MRI', '초음파')
date: 검증 날짜 (YYYY-MM-DD 형식, 선택사항)

Returns:
매칭되는 비급여 코드 목록 (npayCd, 이름, 카테고리, 유효시작일) - 최대 10개""",
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
            description="""📊 비급여 코드 분류 체계 조회 - 코드의 대/중/소분류 정보 확인 (분류 정보가 필요할 때)

📋 사용 시점:
✅ 사용자가 "이 항목의 카테고리나 분류는 뭐야?"라고 물었을 때
✅ 코드가 어떤 분야에 속하는지 알고 싶을 때
✅ 코드 검증 또는 상세 정보가 필요할 때

❌ 사용하지 말아야 할 때:
❌ 일반 환자에게 설명할 때 → ExplainNonPaymentCode 사용 (더 환자 친화적)
❌ 단순히 코드가 존재하는지만 확인 → 다른 도구 사용

🔄 비교:
- ExplainNonPaymentCode: 환자 친화적 설명 (일반 설명)
- GetNonPaymentCodeHierarchy: 기술적 분류 정보 (정확한 분류 체계)

⚠️ 필수 조건:
- 정확한 비급여 코드(npayCd) 필요 (SearchNonPaymentCode로 먼저 찾기)

Args:
npayCd: 비급여 코드 (필수)

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
            description="""📝 비급여 코드 환자 친화적 설명 - 비급여 항목이 무엇인지 일반인이 이해하기 쉽게 설명

📋 사용 시점:
✅ "이 비급여 항목이 뭐예요?", "XXX가 무엇인지 설명해줘" 같은 질문
✅ 환자에게 항목을 설명해야 할 때 (가장 일반적)
✅ 코드 이름만 보고 실제 내용을 알고 싶을 때

❌ 사용하지 말아야 할 때:
❌ 가격 정보나 병원 정보가 필요할 때 → SearchNonPaymentHospitals 등 사용
❌ 종합 정보(가격 통계, 추천 등)가 필요할 때 → GenerateExplanationReport 사용

🔄 비교:
- ExplainNonPaymentCode: 단순 설명만 (항목이 무엇인지)
- GenerateExplanationReport: 종합 정보 (설명 + 가격 통계 + 추천)

⚠️ 필수 조건:
- 정확한 비급여 코드(npayCd) 필요

Args:
npayCd: 비급여 코드 (필수)

Returns:
환자 친화적 설명(plainExplanation)과 카테고리 정보""",
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
            description="""✅ 비급여 코드 유효성 검증 - 특정 날짜에 코드가 사용 가능한지 확인 (과거/미래 날짜 포함)

📋 사용 시점:
✅ "2024년 1월에 이 코드 사용 가능했나요?" (과거 날짜)
✅ "내년에도 이 코드 사용 가능한가요?" (미래 날짜)
✅ 코드의 유효기간(시작일/종료일)을 정확히 알고 싶을 때
✅ 특정 날짜 기준으로 코드 사용 가능 여부 확인

❌ 사용하지 말아야 할 때:
❌ 현재 날짜만 확인하면 될 때 → 다른 도구에서 에러로 확인 가능
❌ 일반적인 코드 검색/설명 → SearchNonPaymentCode, ExplainNonPaymentCode 사용

⚠️ 필수 조건:
- 정확한 비급여 코드(npayCd)와 날짜(YYYY-MM-DD) 필요

Args:
npayCd: 비급여 코드 (필수)
date: 확인할 날짜 (YYYY-MM-DD 형식, 필수)

Returns:
유효성 여부(isValid), 유효시작일(validFrom), 유효종료일(validUntil - "No expiration"일 수 있음)""",
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
            description="""🏥 비급여 항목 제공 병원 검색 - 특정 항목을 제공하는 병원 목록 조회 (가격 정보 포함)

📋 사용 시점:
✅ "서울에서 이 비급여 항목 받을 수 있는 병원 찾아줘" → 병원 목록 검색
✅ 특정 지역/병원 유형으로 필터링된 병원 목록이 필요할 때
✅ 병원 후보 목록을 먼저 확인하고 싶을 때
✅ 각 병원의 최소/최대 가격을 함께 확인하고 싶을 때

❌ 사용하지 말아야 할 때:
❌ 특정 병원 1개의 가격만 필요할 때 → GetHospitalPriceRange 사용 (더 빠름)
❌ 지역 내 가격 비교가 필요할 때 → CompareHospitalPrices 사용
❌ 최저가 병원만 필요할 때 → FindCheapestOption 사용

🔄 비교:
- SearchNonPaymentHospitals: 병원 목록 + 각 병원 가격 범위 (목록 중심)
- GetHospitalPriceRange: 특정 병원의 정확한 가격 범위 (단일 병원)
- CompareHospitalPrices: 지역 내 가격 비교 (비교 중심)

⚠️ 필수 조건:
- 비급여 코드(npayCd) 필요 (SearchNonPaymentCode로 먼저 찾기)

Args:
npayCd: 비급여 코드 (필수)
sido: 시도명 (예: '서울', '부산', 선택사항 - 지역 필터링)
sggu: 시군구명 (선택사항 - 세부 지역 필터링)
clCd: 병원 유형 (예: '상급종합', '종합병원', 선택사항 - 유형 필터링)

Returns:
병원 목록 (병원명, 유형, 최소가격, 최대가격, 지역)""",
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
            description="""💰 특정 병원의 가격 범위 조회 - 하나의 병원에서 받을 수 있는 최소/최대 가격 확인

📋 사용 시점:
✅ "서울대병원에서 이 항목 가격이 얼마예요?" → 특정 병원 가격만 필요
✅ 특정 병원 1곳의 가격 정보만 확인하고 싶을 때 (가장 빠름)
✅ 병원에서 제시한 가격이 정상 범위인지 확인할 때

❌ 사용하지 말아야 할 때:
❌ 여러 병원 목록이 필요할 때 → SearchNonPaymentHospitals 사용
❌ 지역 내 여러 병원 가격 비교 → CompareHospitalPrices 사용
❌ 최저가 병원 찾기 → FindCheapestOption 사용

🔄 비교:
- GetHospitalPriceRange: 1개 병원 가격 (단일 조회, 빠름)
- SearchNonPaymentHospitals: 여러 병원 목록 + 가격 (목록 중심)
- CompareHospitalPrices: 지역 내 비교 통계 (비교 분석)

⚠️ 필수 조건:
- 정확한 병원명 (일부 이름만으로는 검색 실패 가능)
- 비급여 코드(npayCd)

Args:
hospital: 병원명 (필수 - 정확한 병원명 권장)
npayCd: 비급여 코드 (필수)

Returns:
최소 가격(min), 최대 가격(max), 참고사항(note - 병실 위치에 따른 차이 안내)""",
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
            description="""📊 지역별 병원 가격 비교 - 특정 지역 내 병원들의 가격을 비교 분석 (최저가, 최고가, 중간가, 절약액 포함)

📋 사용 시점:
✅ "서울에서 이 항목 가장 저렴한 곳 어디예요?" → 지역 내 가격 비교
✅ "강남구에서 이 항목 가격 비교해줘" → 지역별 비교 통계
✅ 가격 분포와 통계가 필요할 때 (최저/최고/중간가)
✅ 여러 병원 중 선택을 위한 비교 정보가 필요할 때

❌ 사용하지 말아야 할 때:
❌ 특정 병원 1곳의 가격만 필요할 때 → GetHospitalPriceRange 사용 (더 빠름)
❌ 병원 목록만 필요할 때 → SearchNonPaymentHospitals 사용
❌ 최저가만 간단히 필요할 때 → FindCheapestOption 사용 (더 간단)

🔄 비교:
- CompareHospitalPrices: 상세 비교 통계 (최저/최고/중간가 모두, 통계 중심)
- FindCheapestOption: 최저가만 추출 (간소화된 결과, 설명 포함)
- SearchNonPaymentHospitals: 병원 목록 (목록 중심, 각 병원 가격)

⚠️ 필수 조건:
- 비급여 코드(npayCd)
- 시도명(sido) - 필수

Args:
npayCd: 비급여 코드 (필수)
sido: 시도명 (필수 - 예: '서울', '부산')
sggu: 시군구명 (선택사항 - 예: '강남구', 세부 지역 지정)

Returns:
최저가 병원/가격(cheapest, cheapestPrice), 최고가 병원/가격(mostExpensive, mostExpensivePrice), 중간가(medianPrice), 절약액(savings), 병원 수(hospitalCount)""",
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
            description="""📈 지역별 비급여 항목 통계 - 전국 17개 지역별 평균/최소/최대 가격 통계 (대규모 통계 분석)

📋 사용 시점:
✅ "서울과 부산 가격 차이가 얼마나 나요?" → 지역 간 비교
✅ "전국 지역별 평균 가격이 어떻게 되나요?" → 전국 통계
✅ 특정 지역의 평균 가격이 궁금할 때
✅ CheckReasonablePrice에서 지역 평균이 필요할 때 (내부적으로 사용)

❌ 사용하지 말아야 할 때:
❌ 특정 지역 내 병원 비교 → CompareHospitalPrices 사용 (더 구체적)
❌ 개별 병원 가격 확인 → GetHospitalPriceRange 사용

🔄 비교:
- GetNonPaymentStatsByRegion: 전국 17개 지역 통계 (거시적, 평균 중심)
- CompareHospitalPrices: 특정 지역 내 병원 비교 (미시적, 개별 병원 비교)

⚠️ 필수 조건:
- 비급여 코드(npayCd) 필요

Args:
npayCd: 비급여 코드 (필수)

Returns:
지역별 통계(regions: 서울/부산/인천 등 각 지역의 avg, min, max) 및 전체 통계(overall)""",
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
            description="""🏥 병원 유형별 비급여 항목 통계 - 병원 유형(상급종합/종합/병원 등)별 평균/최소/최대 가격 통계

📋 사용 시점:
✅ "상급종합병원과 종합병원 가격 차이가 얼마나 나요?" → 유형별 비교
✅ "어떤 병원 유형이 가장 저렴한가요?" → 유형별 가격 비교
✅ 병원 유형 선택 시 가격 기준으로 추천이 필요할 때
✅ CheckReasonablePrice에서 전체 평균이 필요할 때 (내부적으로 사용)

❌ 사용하지 말아야 할 때:
❌ 특정 병원 가격 확인 → GetHospitalPriceRange 사용
❌ 지역 내 비교 → CompareHospitalPrices 사용

🔄 비교:
- GetNonPaymentStatsByHospitalType: 유형별 통계 (상급종합, 종합, 병원 등)
- GetNonPaymentStatsByRegion: 지역별 통계 (서울, 부산 등)
- CompareHospitalPrices: 특정 지역 내 개별 병원 비교

⚠️ 필수 조건:
- 비급여 코드(npayCd) 필요

Args:
npayCd: 비급여 코드 (필수)

Returns:
병원 유형별 통계(hospitalTypes: 상급종합/종합병원/병원 등 각 유형의 avg, min, max) 및 전체 통계(overall)""",
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
        # Decision support tools
        Tool(
            name="FindCheapestOption",
            description="""💵 지역별 최저가 병원 찾기 - 특정 지역에서 가장 저렴한 병원을 간단히 찾기 (설명 포함)

📋 사용 시점:
✅ "서울에서 이 항목 가장 싼 병원 어디예요?" → 최저가만 간단히
✅ 가격이 가장 중요한 기준일 때
✅ 최저가 병원과 절약액이 필요할 때

❌ 사용하지 말아야 할 때:
❌ 최고가, 중간가 등 전체 통계가 필요할 때 → CompareHospitalPrices 사용
❌ 여러 병원 목록이 필요할 때 → SearchNonPaymentHospitals 사용

🔄 비교:
- FindCheapestOption: 최저가만 추출 (간소화, 설명 포함, 빠른 결과)
- CompareHospitalPrices: 전체 비교 통계 (최저/최고/중간가 모두, 상세 분석)

💡 내부 동작:
- CompareHospitalPrices를 호출하여 최저가 정보만 추출
- 항목 설명(explanation) 자동 포함
- 절약액 계산 포함

⚠️ 필수 조건:
- 비급여 코드(npayCd)
- 시도명(sido) - 필수

Args:
npayCd: 비급여 코드 (필수)
sido: 시도명 (필수 - 예: '서울', '부산')
sggu: 시군구명 (선택사항 - 예: '강남구')

Returns:
최저가 병원/가격(cheapestOption), 중간가(medianPrice), 절약액(savings), 항목 설명(explanation)""",
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
            description="""💡 가격 합리성 판단 및 이상치 탐지 - 제시된 가격이 적정한지 평가

📋 사용 시점:
✅ "병원에서 10만원 받는데 이 가격 괜찮나요?" → 가격 평가 필요
✅ "이 가격이 정상 범위인가요?" → 가격 검증
✅ 가격 협상 전 기준 확인이 필요할 때

🎯 두 가지 모드:

1️⃣ 합리성 판단 모드 (기본):
- "이 가격 합리한가요?" → 기본 모드 사용
- 평균 대비 ±20% 이내면 "합리적"
- 파라미터: threshold=0.2 (기본값)

2️⃣ 이상치 탐지 모드:
- "이 가격이 비정상적으로 높거나 낮은가요?" → 이상치 탐지
- 평균 대비 ±30% 이상 차이나면 "이상치"
- 파라미터: useOutlierDetection=true, threshold=0.3 권장
- hospital 파라미터 제공 시 병원별 가격 범위 우선 확인

🔄 비교:
- CheckReasonablePrice: 가격 평가/판단 (제시된 가격 기준)
- GetHospitalPriceRange: 병원 가격 범위 조회 (범위 확인)
- CompareHospitalPrices: 지역 내 비교 (다른 병원과 비교)

⚠️ 필수 조건:
- 비급여 코드(npayCd)
- 확인할 가격(price)

💡 팁:
- hospital 제공 시: 해당 병원의 가격 범위와 비교 (더 정확)
- sido 제공 시: 해당 지역 평균과 비교 (없으면 전체 평균)
- 기본 모드: 합리성 판단 (관대한 기준, 20%)
- 이상치 모드: 비정상 여부 판단 (엄격한 기준, 30%)

Args:
npayCd: 비급여 코드 (필수)
price: 확인할 가격 (필수)
sido: 시도명 (선택사항 - 지역 평균과 비교)
hospital: 병원명 (선택사항 - 병원 가격 범위 우선 확인)
threshold: 편차 임계값 (선택사항, 기본값 0.2=20%)
useOutlierDetection: 이상치 탐지 모드 (선택사항, 기본값 false)

Returns:
판단 결과(judgement), 판단 근거(basis), 통계 정보(statistics), 편차(deviation), 모드(mode)""",
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
                    },
                    "hospital": {
                        "type": "string",
                        "description": "Hospital name (optional, for hospital-specific price range check and outlier detection)"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Deviation threshold (optional, default 0.2=20%, use 0.3=30% for outlier detection)"
                    },
                    "useOutlierDetection": {
                        "type": "boolean",
                        "description": "Use outlier detection mode (optional, default false)"
                    }
                },
                "required": ["npayCd", "price"]
            }
        ),
        Tool(
            name="GenerateExplanationReport",
            description="""📋 비급여 항목 종합 설명 보고서 - 항목 설명 + 가격 통계 + 선택 가이드를 포함한 종합 정보

📋 사용 시점:
✅ "이 비급여 항목에 대해 자세히 알려줘" → 종합 정보 필요
✅ "이 항목 선택할 때 고려사항은 뭐예요?" → 선택 가이드 필요
✅ 환자에게 항목 설명 + 가격 정보 + 추천을 모두 제공할 때

❌ 사용하지 말아야 할 때:
❌ 단순히 "이 항목이 뭐예요?"만 물었을 때 → ExplainNonPaymentCode 사용 (더 빠름)
❌ 가격만 필요할 때 → 다른 가격 관련 도구 사용

🔄 비교:
- GenerateExplanationReport: 종합 정보 (설명 + 통계 + 추천, 완전한 가이드)
- ExplainNonPaymentCode: 기본 설명만 (항목이 무엇인지, 빠른 응답)
- CompareHospitalPrices: 가격 비교 중심 (지역별 비교)

📊 포함 내용:
1. 항목 설명 (ExplainNonPaymentCode 포함)
2. 가격 변동성 (병원 간 가격 차이)
3. 병원 유형별 추천 (어떤 유형이 저렴한지)
4. 선택 가이드 (고려사항)

⚠️ 필수 조건:
- 비급여 코드(npayCd)

Args:
npayCd: 비급여 코드 (필수)
sido: 시도명 (선택사항 - 지역별 정보 포함 시)

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
                include_explanation = arguments.get("includeExplanation", False)
                result = await hospital_compare(npay_cd, sido, sggu, include_explanation)
            
            # Statistical analysis tools
            elif name == "GetNonPaymentStatsByRegion":
                npay_cd = arguments.get("npayCd")
                result = await stats_by_region(npay_cd)
            
            elif name == "GetNonPaymentStatsByHospitalType":
                npay_cd = arguments.get("npayCd")
                result = await stats_by_hospital_type(npay_cd)
            
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
                hospital = arguments.get("hospital")
                threshold = arguments.get("threshold", 0.2)  # Default 20% for reasonable price
                use_outlier_detection = arguments.get("useOutlierDetection", False)
                result = await decision_reasonable_price(
                    npay_cd, 
                    price, 
                    sido, 
                    hospital, 
                    threshold, 
                    use_outlier_detection
                )
            
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
