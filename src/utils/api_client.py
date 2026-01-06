"""
Public Data Portal API Client
"""
import os
import aiohttp
import xmltodict
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode


BASE_URL = "http://apis.data.go.kr/B551182/nonPaymentDamtInfoService"
SERVICE_KEY = os.getenv("DATA_GO_KR_API_KEY", "")


async def call_api(
    endpoint: str,
    params: Dict[str, Any],
    use_service_key: bool = True
) -> Dict[str, Any]:
    """
    Call Public Data Portal API
    
    Args:
        endpoint: API endpoint path
        params: Query parameters
        use_service_key: Whether to include service key
        
    Returns:
        Dict: Parsed XML response as dictionary
    """
    if use_service_key and SERVICE_KEY:
        params["ServiceKey"] = SERVICE_KEY
    
    url = f"{BASE_URL}/{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"API call failed with status {response.status}")
            
            text = await response.text()
            data = xmltodict.parse(text)
            
            # Check for errors
            if "response" in data:
                header = data["response"].get("header", {})
                result_code = header.get("resultCode", "")
                result_msg = header.get("resultMsg", "")
                
                if result_code != "00":
                    raise Exception(f"API error: {result_code} - {result_msg}")
            
            return data


async def get_non_payment_item_code_list2(
    page_no: int = 1,
    num_of_rows: int = 10
) -> tuple[List[Dict[str, Any]], Optional[int]]:
    """
    Get non-payment item code list (after 2016.3)
    
    Args:
        page_no: Page number
        num_of_rows: Number of rows per page
        
    Returns:
        Tuple of (list of non-payment item codes, totalCount)
    """
    params = {
        "pageNo": page_no,
        "numOfRows": num_of_rows
    }
    
    data = await call_api("getNonPaymentItemCodeList2", params)
    
    items = []
    total_count = None
    if "response" in data and "body" in data["response"]:
        body = data["response"]["body"]
        if "items" in body and body["items"]:
            item_list = body["items"].get("item", [])
            if not isinstance(item_list, list):
                item_list = [item_list]
            items = item_list
        # Extract totalCount
        total_count_str = body.get("totalCount")
        if total_count_str:
            try:
                total_count = int(total_count_str)
            except (ValueError, TypeError):
                pass
    
    return items, total_count


async def get_non_payment_item_hosp_list2(
    item_cd: str,
    page_no: int = 1,
    num_of_rows: int = 10,
    cl_cd: Optional[str] = None,
    sido_cd: Optional[str] = None,
    sggu_cd: Optional[str] = None,
    yadm_nm: Optional[str] = None,
    search_wrd: Optional[str] = None
) -> tuple[List[Dict[str, Any]], Optional[int]]:
    """
    Get non-payment item hospital list summary (after 2016.3)
    
    Args:
        item_cd: Item code (required)
        page_no: Page number
        num_of_rows: Number of rows per page
        cl_cd: Hospital type code
        sido_cd: City/Province code
        sggu_cd: District code
        yadm_nm: Hospital name
        search_wrd: Search keyword
        
    Returns:
        Tuple of (list of hospitals, totalCount)
    """
    params = {
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "itemCd": item_cd
    }
    
    if cl_cd:
        params["clCd"] = cl_cd
    if sido_cd:
        params["sidoCd"] = sido_cd
    if sggu_cd:
        params["sgguCd"] = sggu_cd
    if yadm_nm:
        params["yadmNm"] = yadm_nm
    if search_wrd:
        params["searchWrd"] = search_wrd
    
    data = await call_api("getNonPaymentItemHospList2", params)
    
    items = []
    total_count = None
    if "response" in data and "body" in data["response"]:
        body = data["response"]["body"]
        if "items" in body and body["items"]:
            item_list = body["items"].get("item", [])
            if not isinstance(item_list, list):
                item_list = [item_list]
            items = item_list
        # Extract totalCount
        total_count_str = body.get("totalCount")
        if total_count_str:
            try:
                total_count = int(total_count_str)
            except (ValueError, TypeError):
                pass
    
    return items, total_count


async def get_non_payment_item_hosp_dtl_list(
    ykiho: str,
    page_no: int = 1,
    num_of_rows: int = 10,
    cl_cd: Optional[str] = None,
    sido_cd: Optional[str] = None,
    sggu_cd: Optional[str] = None,
    yadm_nm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get non-payment item hospital detail list (after 2016.3)
    
    Args:
        ykiho: Encrypted hospital code (required)
        page_no: Page number
        num_of_rows: Number of rows per page
        cl_cd: Hospital type code
        sido_cd: City/Province code
        sggu_cd: District code
        yadm_nm: Hospital name
        
    Returns:
        List of hospital details
    """
    params = {
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "ykiho": ykiho
    }
    
    if cl_cd:
        params["clCd"] = cl_cd
    if sido_cd:
        params["sidoCd"] = sido_cd
    if sggu_cd:
        params["sgguCd"] = sggu_cd
    if yadm_nm:
        params["yadmNm"] = yadm_nm
    
    data = await call_api("getNonPaymentItemHospDtlList", params)
    
    items = []
    if "response" in data and "body" in data["response"]:
        body = data["response"]["body"]
        if "items" in body and body["items"]:
            item_list = body["items"].get("item", [])
            if not isinstance(item_list, list):
                item_list = [item_list]
            items = item_list
    
    return items


async def get_non_payment_item_clcd_list(
    page_no: int = 1,
    num_of_rows: int = 10
) -> tuple[List[Dict[str, Any]], Optional[int]]:
    """
    Get non-payment item statistics by hospital type
    
    Args:
        page_no: Page number
        num_of_rows: Number of rows per page
        
    Returns:
        Tuple of (list of statistics by hospital type, totalCount)
    """
    params = {
        "pageNo": page_no,
        "numOfRows": num_of_rows
    }
    
    data = await call_api("getNonPaymentItemClcdList", params)
    
    items = []
    total_count = None
    if "response" in data and "body" in data["response"]:
        body = data["response"]["body"]
        if "items" in body and body["items"]:
            item_list = body["items"].get("item", [])
            if not isinstance(item_list, list):
                item_list = [item_list]
            items = item_list
        # Extract totalCount
        total_count_str = body.get("totalCount")
        if total_count_str:
            try:
                total_count = int(total_count_str)
            except (ValueError, TypeError):
                pass
    
    return items, total_count


async def get_non_payment_item_sido_cd_list(
    page_no: int = 1,
    num_of_rows: int = 10
) -> tuple[List[Dict[str, Any]], Optional[int]]:
    """
    Get non-payment item statistics by region
    
    Args:
        page_no: Page number
        num_of_rows: Number of rows per page
        
    Returns:
        Tuple of (list of statistics by region, totalCount)
    """
    params = {
        "pageNo": page_no,
        "numOfRows": num_of_rows
    }
    
    data = await call_api("getNonPaymentItemSidoCdList", params)
    
    items = []
    total_count = None
    if "response" in data and "body" in data["response"]:
        body = data["response"]["body"]
        if "items" in body and body["items"]:
            item_list = body["items"].get("item", [])
            if not isinstance(item_list, list):
                item_list = [item_list]
            items = item_list
        # Extract totalCount
        total_count_str = body.get("totalCount")
        if total_count_str:
            try:
                total_count = int(total_count_str)
            except (ValueError, TypeError):
                pass
    
    return items, total_count

