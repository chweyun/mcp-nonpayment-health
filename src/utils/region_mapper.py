"""
Region code and name mapping utilities
"""
from typing import Dict, Optional


# City/Province code mapping
# Note: API uses different codes than standard administrative codes
SIDO_CODE_MAP: Dict[str, str] = {
    "서울": "110000",
    "부산": "210000",
    "대구": "230000",
    "인천": "220000",
    "광주": "240000",
    "대전": "250000",
    "울산": "260000",
    "세종": "360000",
    "경기": "310000",
    "강원": "320000",
    "충북": "330000",
    "충남": "340000",
    "전북": "350000",
    "전남": "360000",
    "경북": "370000",
    "경남": "380000",
    "제주": "500000"
}

# Reverse mapping
SIDO_NAME_MAP: Dict[str, str] = {v: k for k, v in SIDO_CODE_MAP.items()}

# Hospital type code mapping
HOSPITAL_TYPE_MAP: Dict[str, str] = {
    "상급종합": "01",
    "종합병원": "11",
    "치과병원": "41",
    "한방병원": "31",
    "병원": "21",
    "요양병원": "71"
}

# Reverse mapping
HOSPITAL_TYPE_NAME_MAP: Dict[str, str] = {v: k for k, v in HOSPITAL_TYPE_MAP.items()}


def get_sido_code(sido_name: str) -> Optional[str]:
    """
    Get city/province code from name
    
    Args:
        sido_name: City/Province name
        
    Returns:
        City/Province code or None
    """
    return SIDO_CODE_MAP.get(sido_name)


def get_sido_name(sido_code: str) -> Optional[str]:
    """
    Get city/province name from code
    
    Args:
        sido_code: City/Province code
        
    Returns:
        City/Province name or None
    """
    return SIDO_NAME_MAP.get(sido_code)


def get_hospital_type_code(hospital_type: str) -> Optional[str]:
    """
    Get hospital type code from name
    
    Args:
        hospital_type: Hospital type name
        
    Returns:
        Hospital type code or None
    """
    return HOSPITAL_TYPE_MAP.get(hospital_type)


def get_hospital_type_name(hospital_type_code: str) -> Optional[str]:
    """
    Get hospital type name from code
    
    Args:
        hospital_type_code: Hospital type code
        
    Returns:
        Hospital type name or None
    """
    return HOSPITAL_TYPE_NAME_MAP.get(hospital_type_code)

