"""
Hospital information tools for non-payment items
"""
import json
import math
from typing import Dict, Any, List, Optional
from src.utils.api_client import (
    get_non_payment_item_hosp_list2,
    get_non_payment_item_hosp_dtl_list
)
from src.utils.region_mapper import (
    get_sido_code,
    get_hospital_type_code,
    get_hospital_type_name
)


async def hospital_search(
    npay_cd: str,
    sido: Optional[str] = None,
    sggu: Optional[str] = None,
    cl_cd: Optional[str] = None
) -> str:
    """
    Search for hospitals offering specific non-payment items
    
    Args:
        npay_cd: Non-payment code
        sido: City/Province name
        sggu: District name
        cl_cd: Hospital type code
        
    Returns:
        JSON string with hospital list
    """
    try:
        sido_cd = None
        if sido:
            sido_cd = get_sido_code(sido)
            if not sido_cd:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid city/province name: {sido}"
                }, ensure_ascii=False)
        
        # Convert hospital type name to code if needed
        hospital_type_code = cl_cd
        if cl_cd and not cl_cd.isdigit():
            hospital_type_code = get_hospital_type_code(cl_cd)
            if not hospital_type_code:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid hospital type: {cl_cd}"
                }, ensure_ascii=False)
        
        # Get hospital list
        all_hospitals = []
        page_no = 1
        num_of_rows = 100
        max_pages = 50  # Safety limit
        total_pages = None
        
        while True:
            items, total_count = await get_non_payment_item_hosp_list2(
                item_cd=npay_cd,
                page_no=page_no,
                num_of_rows=num_of_rows,
                cl_cd=hospital_type_code,
                sido_cd=sido_cd,
                sggu_cd=None  # sggu code mapping would need additional data
            )
            
            if not items:
                break
            
            # Calculate total pages from first response if available
            if total_count is not None and total_pages is None:
                total_pages = math.ceil(total_count / num_of_rows)
                # Use the smaller of calculated pages or safety limit
                max_pages = min(total_pages, max_pages)
            
            all_hospitals.extend(items)
            
            # Check if we've reached the end
            if len(items) < num_of_rows:
                break
            
            page_no += 1
            if page_no > max_pages:
                break
        
        # Format results
        results = []
        for item in all_hospitals:
            yadm_nm = item.get("yadmNm", "")
            cl_cd_nm = item.get("clCdNm", "")
            min_prc = item.get("minPrc", "")
            max_prc = item.get("maxPrc", "")
            sido_cd_nm = item.get("sidoCdNm", "")
            
            # Filter by city/province if specified
            if sido:
                if sido not in sido_cd_nm:
                    continue
            
            # Filter by district if specified
            if sggu:
                sggu_cd_nm = item.get("sgguCdNm", "")
                if sggu not in sggu_cd_nm:
                    continue
            
            try:
                min_price = int(min_prc) if min_prc else None
                max_price = int(max_prc) if max_prc else None
            except:
                min_price = None
                max_price = None
            
            results.append({
                "hospital": yadm_nm,
                "type": cl_cd_nm,
                "priceMin": min_price,
                "priceMax": max_price,
                "sido": item.get("sidoCdNm", ""),
                "sggu": item.get("sgguCdNm", "")
            })
        
        return json.dumps({
            "success": True,
            "results": results,
            "count": len(results)
        }, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


async def hospital_price_range(hospital: str, npay_cd: str) -> str:
    """
    Get price range for a specific item at a hospital
    
    Args:
        hospital: Hospital name
        npay_cd: Non-payment code
        
    Returns:
        JSON string with price range information
    """
    try:
        # Search for hospitals
        all_hospitals = []
        page_no = 1
        num_of_rows = 100
        max_pages = 50  # Safety limit
        total_pages = None
        
        while True:
            items, total_count = await get_non_payment_item_hosp_list2(
                item_cd=npay_cd,
                page_no=page_no,
                num_of_rows=num_of_rows
            )
            
            if not items:
                break
            
            # Calculate total pages from first response if available
            if total_count is not None and total_pages is None:
                total_pages = math.ceil(total_count / num_of_rows)
                # Use the smaller of calculated pages or safety limit
                max_pages = min(total_pages, max_pages)
            
            # Filter by hospital name
            for item in items:
                yadm_nm = item.get("yadmNm", "")
                if hospital in yadm_nm:
                    all_hospitals.append(item)
            
            # Check if we've reached the end
            if len(items) < num_of_rows:
                break
            
            page_no += 1
            if page_no > max_pages:
                break
        
        if not all_hospitals:
            return json.dumps({
                "success": False,
                "error": f"Hospital '{hospital}' not found for code {npay_cd}"
            }, ensure_ascii=False)
        
        # Get price ranges
        min_prices = []
        max_prices = []
        
        for item in all_hospitals:
            min_prc = item.get("minPrc", "")
            max_prc = item.get("maxPrc", "")
            
            try:
                if min_prc:
                    min_prices.append(int(min_prc))
                if max_prc:
                    max_prices.append(int(max_prc))
            except:
                pass
        
        if not min_prices and not max_prices:
            return json.dumps({
                "success": False,
                "error": "Price information not available"
            }, ensure_ascii=False)
        
        overall_min = min(min_prices) if min_prices else None
        overall_max = max(max_prices) if max_prices else None
        
        result = {
            "success": True,
            "hospital": hospital,
            "npayCd": npay_cd,
            "min": overall_min,
            "max": overall_max,
            "note": "병실 위치/동에 따라 차이가 있을 수 있습니다." if overall_min != overall_max else "단일 가격입니다."
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


async def hospital_compare(
    npay_cd: str,
    sido: str,
    sggu: Optional[str] = None
) -> str:
    """
    Compare prices across hospitals in the same region
    
    Args:
        npay_cd: Non-payment code
        sido: City/Province name
        sggu: District name (optional)
        
    Returns:
        JSON string with comparison results
    """
    try:
        # Get hospital list
        search_result = await hospital_search(npay_cd, sido, sggu)
        search_data = json.loads(search_result)
        
        if not search_data.get("success"):
            return search_result
        
        hospitals = search_data.get("results", [])
        
        if not hospitals:
            return json.dumps({
                "success": False,
                "error": "No hospitals found in the specified region"
            }, ensure_ascii=False)
        
        # Calculate statistics
        prices = []
        for hosp in hospitals:
            min_price = hosp.get("priceMin")
            max_price = hosp.get("priceMax")
            if min_price:
                prices.append(min_price)
            if max_price:
                prices.append(max_price)
        
        if not prices:
            return json.dumps({
                "success": False,
                "error": "No price information available"
            }, ensure_ascii=False)
        
        prices.sort()
        median_price = prices[len(prices) // 2] if prices else None
        
        # Find cheapest and most expensive
        cheapest_hosp = None
        most_expensive_hosp = None
        cheapest_price = float('inf')
        most_expensive_price = 0
        
        for hosp in hospitals:
            min_price = hosp.get("priceMin")
            if min_price and min_price < cheapest_price:
                cheapest_price = min_price
                cheapest_hosp = hosp.get("hospital")
            
            max_price = hosp.get("priceMax")
            if max_price and max_price > most_expensive_price:
                most_expensive_price = max_price
                most_expensive_hosp = hosp.get("hospital")
        
        result = {
            "success": True,
            "npayCd": npay_cd,
            "region": {
                "sido": sido,
                "sggu": sggu
            },
            "cheapest": cheapest_hosp,
            "cheapestPrice": cheapest_price if cheapest_price != float('inf') else None,
            "mostExpensive": most_expensive_hosp,
            "mostExpensivePrice": most_expensive_price if most_expensive_price > 0 else None,
            "medianPrice": median_price,
            "hospitalCount": len(hospitals)
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

