"""
Statistical analysis tools for non-payment items
"""
import json
from typing import Dict, Any, List, Optional
from src.utils.api_client import (
    get_non_payment_item_sido_cd_list,
    get_non_payment_item_clcd_list,
    get_non_payment_item_hosp_list2
)
from src.utils.region_mapper import get_sido_name, get_hospital_type_name


async def stats_by_region(npay_cd: str) -> str:
    """
    Get price statistics by region for a non-payment item
    
    Args:
        npay_cd: Non-payment code
        
    Returns:
        JSON string with regional statistics
    """
    try:
        # Get regional statistics
        found_stat = None
        page_no = 1
        num_of_rows = 100
        max_pages = 50  # Increased limit to search more pages
        
        while page_no <= max_pages:
            items = await get_non_payment_item_sido_cd_list(page_no, num_of_rows)
            if not items:
                break
            
            # Find matching code in current page
            for item in items:
                if item.get("npayCd") == npay_cd:
                    found_stat = item
                    break  # Found, exit inner loop
            
            # If found, exit outer loop
            if found_stat:
                break
            
            # If this page has fewer items than requested, we've reached the end
            if len(items) < num_of_rows:
                break
            
            page_no += 1
        
        if not found_stat:
            return json.dumps({
                "success": False,
                "error": f"Statistics not found for code {npay_cd}"
            }, ensure_ascii=False)
        
        stat = found_stat
        
        # Map region codes to names
        regions = {}
        region_mapping = {
            "prcAvgSl": "서울",
            "prcAvgPs": "부산",
            "prcAvgIch": "인천",
            "prcAvgTg": "대구",
            "prcAvgKw": "광주",
            "prcAvgDj": "대전",
            "prcAvgUsn": "울산",
            "prcAvgKyg": "경기",
            "prcAvgKaw": "강원",
            "prcAvgCcbk": "충북",
            "prcAvgCcn": "충남",
            "prcAvgClb": "전북",
            "prcAvgCln": "전남",
            "prcAvgKsb": "경북",
            "prcAvgKsn": "경남",
            "prcAvgChj": "제주",
            "prcAvgSejong": "세종"
        }
        
        for key, region_name in region_mapping.items():
            price = stat.get(key, "0")
            try:
                price_int = int(price)
                if price_int > 0:
                    regions[region_name] = {
                        "avg": price_int,
                        "min": int(stat.get(key.replace("Avg", "Min"), "0") or "0"),
                        "max": int(stat.get(key.replace("Avg", "Max"), "0") or "0")
                    }
            except:
                pass
        
        result = {
            "success": True,
            "npayCd": npay_cd,
            "npayKorNm": stat.get("npayKorNm", ""),
            "regions": regions,
            "overall": {
                "avg": int(stat.get("prcAvgAll", "0") or "0"),
                "min": int(stat.get("prcMinAll", "0") or "0"),
                "max": int(stat.get("prcMaxAll", "0") or "0")
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


async def stats_by_hospital_type(npay_cd: str) -> str:
    """
    Get price statistics by hospital type
    
    Args:
        npay_cd: Non-payment code
        
    Returns:
        JSON string with hospital type statistics
    """
    try:
        # Get hospital type statistics
        found_stat = None
        page_no = 1
        num_of_rows = 100
        max_pages = 50  # Increased limit to search more pages
        
        while page_no <= max_pages:
            items = await get_non_payment_item_clcd_list(page_no, num_of_rows)
            if not items:
                break
            
            # Find matching code in current page
            for item in items:
                if item.get("npayCd") == npay_cd:
                    found_stat = item
                    break  # Found, exit inner loop
            
            # If found, exit outer loop
            if found_stat:
                break
            
            # If this page has fewer items than requested, we've reached the end
            if len(items) < num_of_rows:
                break
            
            page_no += 1
        
        if not found_stat:
            return json.dumps({
                "success": False,
                "error": f"Statistics not found for code {npay_cd}"
            }, ensure_ascii=False)
        
        stat = found_stat
        
        # Map hospital type codes to names
        hospital_types = {}
        type_mapping = {
            "prcAvgUsgh": "상급종합",
            "prcAvgGnhp": "종합병원",
            "prcAvgDety": "치과병원",
            "prcAvgCmdc": "한방병원",
            "prcAvgHosp": "병원",
            "prcAvgRecu": "요양병원"
        }
        
        for key, type_name in type_mapping.items():
            price = stat.get(key, "0")
            try:
                price_int = int(price)
                if price_int > 0:
                    hospital_types[type_name] = {
                        "avg": price_int,
                        "min": int(stat.get(key.replace("Avg", "Min"), "0") or "0"),
                        "max": int(stat.get(key.replace("Avg", "Max"), "0") or "0")
                    }
            except:
                pass
        
        result = {
            "success": True,
            "npayCd": npay_cd,
            "npayKorNm": stat.get("npayKorNm", ""),
            "hospitalTypes": hospital_types,
            "overall": {
                "avg": int(stat.get("prcAvgAll", "0") or "0"),
                "min": int(stat.get("prcMinAll", "0") or "0"),
                "max": int(stat.get("prcMaxAll", "0") or "0")
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


async def stats_outlier_detect(
    hospital: str,
    npay_cd: str,
    price: float
) -> str:
    """
    Detect if a hospital's price is abnormally high or low
    
    Args:
        hospital: Hospital name
        npay_cd: Non-payment code
        price: Price to check
        
    Returns:
        JSON string with outlier detection result
    """
    try:
        # Get hospital price range
        from src.tools.hospital_tools import hospital_price_range
        price_range_result = await hospital_price_range(hospital, npay_cd)
        price_range_data = json.loads(price_range_result)
        
        if not price_range_data.get("success"):
            # Try to get regional statistics instead
            region_stats_result = await stats_by_region(npay_cd)
            region_stats_data = json.loads(region_stats_result)
            
            if not region_stats_data.get("success"):
                return json.dumps({
                    "success": False,
                    "error": "Cannot determine if price is outlier: insufficient data"
                }, ensure_ascii=False)
            
            overall = region_stats_data.get("overall", {})
            avg_price = overall.get("avg", 0)
            
            if avg_price == 0:
                return json.dumps({
                    "success": False,
                    "error": "Cannot determine if price is outlier: no average price data"
                }, ensure_ascii=False)
            
            # Calculate deviation
            deviation = abs(price - avg_price) / avg_price
            
            is_outlier = deviation > 0.3  # More than 30% deviation
            is_high = price > avg_price
            
            result = {
                "success": True,
                "isOutlier": is_outlier,
                "isHigh": is_high,
                "reason": f"지역 평균 대비 {deviation * 100:.1f}% {'높음' if is_high else '낮음'}",
                "price": price,
                "averagePrice": avg_price,
                "deviation": deviation
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        # Use hospital-specific price range
        min_price = price_range_data.get("min")
        max_price = price_range_data.get("max")
        
        if min_price is None or max_price is None:
            return json.dumps({
                "success": False,
                "error": "Price range information not available"
            }, ensure_ascii=False)
        
        # Check if price is within range
        is_outlier = price < min_price or price > max_price
        is_high = price > max_price
        
        if is_outlier:
            if is_high:
                reason = f"병원 최대 가격({max_price:,}원)보다 {price - max_price:,.0f}원 높음"
            else:
                reason = f"병원 최소 가격({min_price:,}원)보다 {min_price - price:,.0f}원 낮음"
        else:
            reason = "정상 범위 내"
        
        result = {
            "success": True,
            "isOutlier": is_outlier,
            "isHigh": is_high,
            "reason": reason,
            "price": price,
            "priceRange": {
                "min": min_price,
                "max": max_price
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

