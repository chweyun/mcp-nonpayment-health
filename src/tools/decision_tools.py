"""
Decision support tools for non-payment items
"""
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from src.tools.hospital_tools import hospital_search, hospital_compare
from src.tools.stats_tools import stats_by_region, stats_by_hospital_type
from src.tools.code_tools import code_explain

logger = logging.getLogger(__name__)

# Overall timeout for decision operations (50 seconds to leave buffer for PlayMCP 1-minute timeout)
DECISION_OPERATION_TIMEOUT = 50


async def decision_cheapest_option(
    npay_cd: str,
    sido: str,
    sggu: Optional[str] = None
) -> str:
    """
    Find the cheapest option based on location
    
    Args:
        npay_cd: Non-payment code
        sido: City/Province name
        sggu: District name (optional)
        
    Returns:
        JSON string with cheapest option information
    """
    try:
        # Get hospital comparison
        compare_result = await hospital_compare(npay_cd, sido, sggu)
        compare_data = json.loads(compare_result)
        
        if not compare_data.get("success"):
            return compare_result
        
        cheapest = compare_data.get("cheapest")
        cheapest_price = compare_data.get("cheapestPrice")
        median_price = compare_data.get("medianPrice")
        
        if not cheapest:
            return json.dumps({
                "success": False,
                "error": "No cheapest option found"
            }, ensure_ascii=False)
        
        # Get code explanation
        explain_result = await code_explain(npay_cd)
        explain_data = json.loads(explain_result)
        explanation = explain_data.get("plainExplanation", "") if explain_data.get("success") else ""
        
        result = {
            "success": True,
            "npayCd": npay_cd,
            "region": {
                "sido": sido,
                "sggu": sggu
            },
            "cheapestOption": {
                "hospital": cheapest,
                "price": cheapest_price
            },
            "medianPrice": median_price,
            "savings": median_price - cheapest_price if median_price and cheapest_price else None,
            "explanation": explanation
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


async def _decision_reasonable_price_impl(
    npay_cd: str,
    price: float,
    sido: Optional[str] = None
) -> str:
    """
    Internal implementation of decision_reasonable_price (without timeout wrapper)
    """
    # First, verify code exists (quick check)
    from src.tools.code_tools import code_hierarchy
    code_check = await code_hierarchy(npay_cd)
    code_data = json.loads(code_check)
    
    if not code_data.get("success"):
        return json.dumps({
            "success": False,
            "error": f"Cannot determine reasonableness: Code {npay_cd} not found. Please verify the code is correct."
        }, ensure_ascii=False)
    
    # Get statistics
    if sido:
        stats_result = await stats_by_region(npay_cd)
        stats_data = json.loads(stats_result)
        
        if stats_data.get("success"):
            regions = stats_data.get("regions", {})
            region_data = regions.get(sido, {})
            
            if region_data:
                avg_price = region_data.get("avg", 0)
                min_price = region_data.get("min", 0)
                max_price = region_data.get("max", 0)
                
                if avg_price > 0:
                    # Calculate deviation from average
                    deviation = abs(price - avg_price) / avg_price
                    
                    # Reasonable if within 20% of average
                    is_reasonable = deviation <= 0.2
                    
                    # Determine judgement
                    if is_reasonable:
                        judgement = "합리적"
                        basis = f"{sido} 지역 평균({avg_price:,}원) 대비 ±20% 이내"
                    elif price > avg_price:
                        judgement = "비싼 편"
                        basis = f"{sido} 지역 평균({avg_price:,}원)보다 {((price - avg_price) / avg_price * 100):.1f}% 높음"
                    else:
                        judgement = "저렴한 편"
                        basis = f"{sido} 지역 평균({avg_price:,}원)보다 {((avg_price - price) / avg_price * 100):.1f}% 낮음"
                    
                    result = {
                        "success": True,
                        "judgement": judgement,
                        "basis": basis,
                        "price": price,
                        "region": sido,
                        "statistics": {
                            "average": avg_price,
                            "min": min_price,
                            "max": max_price
                        },
                        "deviation": deviation
                    }
                    
                    return json.dumps(result, ensure_ascii=False, indent=2)
            
            # If region data not found but stats_by_region succeeded, try overall from same result
            overall = stats_data.get("overall", {})
            overall_avg = overall.get("avg", 0)
            
            if overall_avg > 0:
                # Use overall statistics from region stats
                deviation = abs(price - overall_avg) / overall_avg
                is_reasonable = deviation <= 0.2
                
                if is_reasonable:
                    judgement = "합리적"
                    basis = f"전체 평균({overall_avg:,}원) 대비 ±20% 이내 ({sido} 지역 데이터 없음)"
                elif price > overall_avg:
                    judgement = "비싼 편"
                    basis = f"전체 평균({overall_avg:,}원)보다 {((price - overall_avg) / overall_avg * 100):.1f}% 높음 ({sido} 지역 데이터 없음)"
                else:
                    judgement = "저렴한 편"
                    basis = f"전체 평균({overall_avg:,}원)보다 {((overall_avg - price) / overall_avg * 100):.1f}% 낮음 ({sido} 지역 데이터 없음)"
                
                result = {
                    "success": True,
                    "judgement": judgement,
                    "basis": basis,
                    "price": price,
                    "region": sido,
                    "note": f"{sido} 지역별 데이터가 없어 전체 통계를 사용했습니다.",
                    "statistics": {
                        "average": overall_avg,
                        "min": overall.get("min", 0),
                        "max": overall.get("max", 0)
                    },
                    "deviation": deviation
                }
                
                return json.dumps(result, ensure_ascii=False, indent=2)
            # If stats_by_region succeeded but no data available, continue to fallback
    
    # Fallback to overall statistics from hospital type
    stats_result = await stats_by_hospital_type(npay_cd)
    stats_data = json.loads(stats_result)
    
    if not stats_data.get("success"):
        # Try to get more detailed error message
        error_msg = stats_data.get("error", "insufficient data")
        logger.warning(f"CheckReasonablePrice failed for {npay_cd}: stats_by_hospital_type error - {error_msg}")
        
        # Code exists but no statistics available
        code_name = code_data.get("fullName", npay_cd)
        return json.dumps({
            "success": False,
            "error": f"Cannot determine reasonableness: Statistics data not available for code {npay_cd} ({code_name}). This code exists but may not have sufficient price data in the statistics database yet. You can try using SearchNonPaymentHospitals to find hospitals offering this item and check their prices directly.",
            "codeName": code_name,
            "suggestion": "Use SearchNonPaymentHospitals to find hospitals and check prices directly"
        }, ensure_ascii=False)
    
    overall = stats_data.get("overall", {})
    avg_price = overall.get("avg", 0)
    
    if avg_price == 0:
        logger.warning(f"CheckReasonablePrice failed for {npay_cd}: avg_price is 0")
        code_name = code_data.get("fullName", npay_cd)
        return json.dumps({
            "success": False,
            "error": f"Cannot determine reasonableness: No average price data available for code {npay_cd} ({code_name}). This code exists but does not have sufficient price data in the statistics database. You can try using SearchNonPaymentHospitals to find hospitals offering this item.",
            "codeName": code_name,
            "suggestion": "Use SearchNonPaymentHospitals to find hospitals and check prices directly"
        }, ensure_ascii=False)
    
    # Calculate deviation
    deviation = abs(price - avg_price) / avg_price
    is_reasonable = deviation <= 0.2
    
    if is_reasonable:
        judgement = "합리적"
        basis = f"전체 평균({avg_price:,}원) 대비 ±20% 이내"
    elif price > avg_price:
        judgement = "비싼 편"
        basis = f"전체 평균({avg_price:,}원)보다 {((price - avg_price) / avg_price * 100):.1f}% 높음"
    else:
        judgement = "저렴한 편"
        basis = f"전체 평균({avg_price:,}원)보다 {((avg_price - price) / avg_price * 100):.1f}% 낮음"
    
    result = {
        "success": True,
        "judgement": judgement,
        "basis": basis,
        "price": price,
        "statistics": {
            "average": avg_price,
            "min": overall.get("min", 0),
            "max": overall.get("max", 0)
        },
        "deviation": deviation
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


async def decision_reasonable_price(
    npay_cd: str,
    price: float,
    sido: Optional[str] = None
) -> str:
    """
    Determine if a price is reasonable
    
    Args:
        npay_cd: Non-payment code
        price: Price to check
        sido: City/Province name (optional)
        
    Returns:
        JSON string with reasonableness assessment
    """
    try:
        # Wrap with timeout
        result = await asyncio.wait_for(
            _decision_reasonable_price_impl(npay_cd, price, sido),
            timeout=DECISION_OPERATION_TIMEOUT
        )
        return result
    except asyncio.TimeoutError:
        return json.dumps({
            "success": False,
            "error": f"Request timeout: Price reasonableness check for code {npay_cd} took too long. Please try again later."
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


async def decision_explanation_report(
    npay_cd: str,
    sido: Optional[str] = None
) -> str:
    """
    Generate a patient-friendly explanation report
    
    Args:
        npay_cd: Non-payment code
        sido: City/Province name (optional)
        
    Returns:
        JSON string with explanation report
    """
    try:
        # Get code explanation
        explain_result = await code_explain(npay_cd)
        explain_data = json.loads(explain_result)
        
        if not explain_data.get("success"):
            return explain_result
        
        explanation = explain_data.get("plainExplanation", "")
        category = explain_data.get("category", {})
        
        # Get statistics
        stats_result = await stats_by_region(npay_cd)
        stats_data = json.loads(stats_result)
        
        price_variation = None
        recommendation = None
        
        if stats_data.get("success"):
            overall = stats_data.get("overall", {})
            min_price = overall.get("min", 0)
            max_price = overall.get("max", 0)
            avg_price = overall.get("avg", 0)
            
            if min_price > 0 and max_price > 0:
                variation_ratio = max_price / min_price if min_price > 0 else 1
                price_variation = f"병원 간 최대 {variation_ratio:.1f}배 차이"
                
                if variation_ratio > 1.5:
                    recommendation = "병원 간 가격 차이가 크므로 여러 병원의 가격을 비교해보시기 바랍니다."
                else:
                    recommendation = "병원 간 가격 차이가 크지 않으므로 편의성을 고려하여 선택하시면 됩니다."
        
        # Get hospital type statistics
        type_stats_result = await stats_by_hospital_type(npay_cd)
        type_stats_data = json.loads(type_stats_result)
        
        hospital_type_recommendation = None
        if type_stats_data.get("success"):
            hospital_types = type_stats_data.get("hospitalTypes", {})
            
            # Find cheapest hospital type
            cheapest_type = None
            cheapest_avg = float('inf')
            
            for type_name, type_data in hospital_types.items():
                avg = type_data.get("avg", 0)
                if avg > 0 and avg < cheapest_avg:
                    cheapest_avg = avg
                    cheapest_type = type_name
            
            if cheapest_type:
                hospital_type_recommendation = f"{cheapest_type}에서 평균적으로 가장 저렴한 가격대를 제공합니다."
        
        # Build summary
        summary_parts = []
        
        if explanation:
            summary_parts.append(explanation)
        
        if price_variation:
            summary_parts.append(f"이 비급여 항목은 {price_variation}가 있습니다.")
        
        if hospital_type_recommendation:
            summary_parts.append(hospital_type_recommendation)
        
        summary = " ".join(summary_parts) if summary_parts else "비급여 항목에 대한 정보를 찾을 수 없습니다."
        
        result = {
            "success": True,
            "npayCd": npay_cd,
            "summary": summary,
            "recommendation": recommendation or "병원을 선택할 때 가격뿐만 아니라 의료진의 전문성과 시설도 함께 고려하시기 바랍니다.",
            "category": category,
            "priceInfo": {
                "variation": price_variation,
                "hospitalTypeRecommendation": hospital_type_recommendation
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

