"""
Code management tools for non-payment items
"""
import json
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.utils.api_client import get_non_payment_item_code_list2
from src.utils.region_mapper import get_sido_code


async def code_search(keyword: str, date: Optional[str] = None) -> str:
    """
    Search for non-payment item codes by keyword
    
    Args:
        keyword: Search keyword
        date: Date for validation (YYYY-MM-DD format)
        
    Returns:
        JSON string with search results
    """
    try:
        # Search through all pages to find matching items
        all_items = []
        page_no = 1
        num_of_rows = 100
        max_pages = 50  # Safety limit
        total_pages = None
        
        while True:
            items, total_count = await get_non_payment_item_code_list2(page_no, num_of_rows)
            if not items:
                break
            
            # Calculate total pages from first response if available
            if total_count is not None and total_pages is None:
                total_pages = math.ceil(total_count / num_of_rows)
                # Use the smaller of calculated pages or safety limit
                max_pages = min(total_pages, max_pages)
            
            # Filter by keyword
            matching_items = []
            for item in items:
                npay_kor_nm = item.get("npayKorNm", "")
                if keyword.lower() in npay_kor_nm.lower():
                    matching_items.append(item)
            
            all_items.extend(matching_items)
            
            # Check if we've reached the end
            if len(items) < num_of_rows:
                break
            
            page_no += 1
            if page_no > max_pages:
                break
        
        # Format results
        results = []
        for item in all_items[:10]:  # Limit to 10 results
            npay_cd = item.get("npayCd", "")
            npay_kor_nm = item.get("npayKorNm", "")
            npay_mdiv_cd_nm = item.get("npayMdivCdNm", "")
            npay_sdiv_cd_nm = item.get("npaySdivCdNm", "")
            npay_dtl_div_cd_nm = item.get("npayDtlDivCdNm", "")
            adt_fr_dd = item.get("adtFrDd", "")
            adt_end_dd = item.get("adtEndDd", "")
            
            # Format date
            valid_from = None
            if adt_fr_dd:
                try:
                    valid_from = f"{adt_fr_dd[:4]}-{adt_fr_dd[4:6]}-{adt_fr_dd[6:8]}"
                except:
                    pass
            
            category = []
            if npay_mdiv_cd_nm:
                category.append(npay_mdiv_cd_nm)
            if npay_sdiv_cd_nm:
                category.append(npay_sdiv_cd_nm)
            if npay_dtl_div_cd_nm:
                category.append(npay_dtl_div_cd_nm)
            
            results.append({
                "npayCd": npay_cd,
                "name": npay_kor_nm,
                "category": category,
                "validFrom": valid_from
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


async def code_hierarchy(npay_cd: str) -> str:
    """
    Get classification hierarchy for a non-payment code
    
    Args:
        npay_cd: Non-payment code
        
    Returns:
        JSON string with hierarchy information
    """
    try:
        # Search for the code
        found_item = None
        page_no = 1
        num_of_rows = 100
        max_pages = 50  # Safety limit
        total_pages = None
        
        while True:
            items, total_count = await get_non_payment_item_code_list2(page_no, num_of_rows)
            if not items:
                break
            
            # Calculate total pages from first response if available
            if total_count is not None and total_pages is None:
                total_pages = math.ceil(total_count / num_of_rows)
                # Use the smaller of calculated pages or safety limit
                max_pages = min(total_pages, max_pages)
            
            # Search for the code in current page
            for item in items:
                if item.get("npayCd") == npay_cd:
                    found_item = item
                    break  # Found, exit inner loop
            
            # If found, exit outer loop
            if found_item:
                break
            
            # Check if we've reached the end
            if len(items) < num_of_rows:
                break
            
            page_no += 1
            if page_no > max_pages:
                break
        
        if not found_item:
            return json.dumps({
                "success": False,
                "error": f"Code {npay_cd} not found"
            }, ensure_ascii=False)
        
        item = found_item
        
        result = {
            "success": True,
            "npayCd": npay_cd,
            "major": item.get("npayMdivCdNm", ""),
            "middle": item.get("npaySdivCdNm", ""),
            "sub": item.get("npayDtlDivCdNm", ""),
            "description": item.get("cmmtTxt", ""),
            "fullName": item.get("npayKorNm", "")
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


async def code_explain(npay_cd: str) -> str:
    """
    Get plain-language explanation for a non-payment code
    
    Args:
        npay_cd: Non-payment code
        
    Returns:
        JSON string with explanation
    """
    try:
        # Get hierarchy first
        hierarchy_result = await code_hierarchy(npay_cd)
        hierarchy_data = json.loads(hierarchy_result)
        
        if not hierarchy_data.get("success"):
            return hierarchy_result
        
        # Generate explanation
        major = hierarchy_data.get("major", "")
        middle = hierarchy_data.get("middle", "")
        sub = hierarchy_data.get("sub", "")
        description = hierarchy_data.get("description", "")
        full_name = hierarchy_data.get("fullName", "")
        
        # Build explanation
        explanation_parts = []
        
        if full_name:
            explanation_parts.append(full_name)
        
        if description:
            explanation_parts.append(description)
        elif major and middle:
            explanation_parts.append(f"{major}의 {middle} 항목으로, 건강보험이 적용되지 않아 병원별 비용 차이가 있을 수 있습니다.")
        
        plain_explanation = " ".join(explanation_parts) if explanation_parts else "비급여 항목에 대한 설명을 찾을 수 없습니다."
        
        result = {
            "success": True,
            "npayCd": npay_cd,
            "plainExplanation": plain_explanation,
            "category": {
                "major": major,
                "middle": middle,
                "sub": sub
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


async def code_validate(npay_cd: str, date: str) -> str:
    """
    Validate code validity and expiration date
    
    Args:
        npay_cd: Non-payment code
        date: Date to check (YYYY-MM-DD format)
        
    Returns:
        JSON string with validation result
    """
    try:
        # Parse date
        check_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Search for the code
        found_item = None
        page_no = 1
        num_of_rows = 100
        max_pages = 50  # Safety limit
        total_pages = None
        
        while True:
            items, total_count = await get_non_payment_item_code_list2(page_no, num_of_rows)
            if not items:
                break
            
            # Calculate total pages from first response if available
            if total_count is not None and total_pages is None:
                total_pages = math.ceil(total_count / num_of_rows)
                # Use the smaller of calculated pages or safety limit
                max_pages = min(total_pages, max_pages)
            
            # Search for the code in current page
            for item in items:
                if item.get("npayCd") == npay_cd:
                    found_item = item
                    break  # Found, exit inner loop
            
            # If found, exit outer loop
            if found_item:
                break
            
            # Check if we've reached the end
            if len(items) < num_of_rows:
                break
            
            page_no += 1
            if page_no > max_pages:
                break
        
        if not found_item:
            return json.dumps({
                "success": False,
                "isValid": False,
                "error": f"Code {npay_cd} not found"
            }, ensure_ascii=False)
        
        item = found_item
        adt_fr_dd = item.get("adtFrDd", "")
        adt_end_dd = item.get("adtEndDd", "")
        
        # Parse dates
        valid_from = None
        valid_until = None
        
        if adt_fr_dd:
            try:
                valid_from = datetime.strptime(adt_fr_dd, "%Y%m%d")
            except:
                pass
        
        if adt_end_dd:
            try:
                if adt_end_dd == "99991231":
                    valid_until = None  # No expiration
                else:
                    valid_until = datetime.strptime(adt_end_dd, "%Y%m%d")
            except:
                pass
        
        # Check validity
        is_valid = True
        if valid_from and check_date < valid_from:
            is_valid = False
        if valid_until and check_date > valid_until:
            is_valid = False
        
        result = {
            "success": True,
            "isValid": is_valid,
            "validFrom": valid_from.strftime("%Y-%m-%d") if valid_from else None,
            "validUntil": valid_until.strftime("%Y-%m-%d") if valid_until else "No expiration"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except ValueError as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid date format: {str(e)}"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

