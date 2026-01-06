# 비급여 진료비 정보 MCP 서버 🏥

비급여 진료비 정보를 조회하고 분석하는 Model Context Protocol (MCP) 서버입니다. 건강보험심사평가원의 비급여진료비정보서비스 API를 활용하여 비급여 항목 코드 조회, 병원별 가격 정보, 통계 분석, 의사결정 지원 기능을 제공합니다.

**Python 3.11+** | **MCP 호환** | **라이선스: MIT**

## ✨ 주요 기능

### 📋 코드 관리 도구
- **코드 검색**: 키워드로 비급여 항목 코드 검색
- **코드 분류 체계**: 코드의 분류 체계 조회
- **코드 설명**: 일반인이 이해하기 쉬운 코드 설명 제공
- **코드 유효성 검증**: 코드 유효성 및 만료일 확인

### 🏥 병원 정보 도구
- **병원 검색**: 특정 비급여 항목을 제공하는 병원 찾기
- **가격 범위**: 병원별 특정 항목의 가격 범위 조회
- **가격 비교**: 같은 지역 내 병원 간 가격 비교

### 📊 통계 분석 도구
- **지역별 통계**: 지역별 가격 통계 조회
- **병원 종별 통계**: 병원 종별 가격 비교
- **이상 가격 탐지**: 비정상적으로 높거나 낮은 가격 탐지

### 💡 의사결정 지원 도구
- **최저가 옵션**: 위치 기반 최저가 옵션 찾기
- **합리적 가격 판단**: 가격이 합리적인지 판단
- **설명 리포트**: 환자 친화적인 설명 리포트 생성

## 🚀 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/your-username/mcp-nonpayment-health.git
cd mcp-nonpayment-health

# 의존성 설치
pip install -r requirements.txt
```

### 설정

`.env` 파일을 생성하세요:

```bash
# 공공데이터포털 API 키 (필수)
# https://www.data.go.kr 에서 발급받으세요
DATA_GO_KR_API_KEY=your_api_key_here

# 서버 설정
PORT=8000                    # 서버 포트 (기본값: 8000)
HOST=0.0.0.0                 # 서버 호스트 (기본값: 0.0.0.0)
DEBUG=False                  # 디버그 모드 (기본값: False)

# API 경로 prefix (선택)
# 같은 서버에 여러 MCP 서버를 호스팅할 때 사용
# 기본값: /nonpayment-health
API_PREFIX=/nonpayment-health
```

#### 환경 변수 설명

| 변수명 | 필수 | 기본값 | 설명 |
|--------|------|--------|------|
| `DATA_GO_KR_API_KEY` | ✅ | - | 공공데이터포털에서 발급받은 API 키 |
| `PORT` | ❌ | `8000` | 서버가 사용할 포트 번호 |
| `HOST` | ❌ | `0.0.0.0` | 서버가 바인딩할 호스트 주소 |
| `DEBUG` | ❌ | `False` | 디버그 모드 활성화 (`True`/`False`) |
| `API_PREFIX` | ❌ | `/nonpayment-health` | API 엔드포인트 경로 prefix |

### MCP 서버 실행

**로컬 모드 (stdio):**
```bash
python -m src.server
```

**원격 모드 (HTTP):**
```bash
python run_server.py
```

또는 uvicorn을 직접 사용:
```bash
uvicorn src.server_http:app --host 0.0.0.0 --port 8000
```

### Docker를 사용한 실행

**Docker Compose 사용 (권장):**
```bash
# .env 파일 생성 (API 키 설정)
echo "DATA_GO_KR_API_KEY=your_api_key_here" > .env

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

**Docker 직접 사용:**
```bash
# 이미지 빌드
docker build -t nonpayment-health-mcp .

# 컨테이너 실행
docker run -d \
  -p 8001:8000 \
  -e DATA_GO_KR_API_KEY=your_api_key_here \
  -e API_PREFIX=/nonpayment-health \
  --name nonpayment-health-mcp \
  nonpayment-health-mcp
```

**개발 모드:**
`docker-compose.yml`은 개발 모드를 위해 소스 코드를 볼륨으로 마운트하여 코드 변경 시 자동으로 반영됩니다.

## 🛠️ 사용 가능한 도구

### 코드 관리 도구

#### 1. `nonpayment.code.search`
키워드로 비급여 항목 코드를 검색합니다.

**매개변수:**
- `keyword` (string, 필수): 검색 키워드 (예: "1인실", "MRI")
- `date` (string, 선택): 유효성 검증 날짜 (YYYY-MM-DD 형식)

**예제:**
```json
{
  "name": "nonpayment.code.search",
  "arguments": {
    "keyword": "1인실",
    "date": "2025-01-01"
  }
}
```

#### 2. `nonpayment.code.hierarchy`
비급여 코드의 분류 체계를 조회합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드

**예제:**
```json
{
  "name": "nonpayment.code.hierarchy",
  "arguments": {
    "npayCd": "RZ6410000"
  }
}
```

#### 3. `nonpayment.code.explain`
비급여 코드에 대한 일반인이 이해하기 쉬운 설명을 제공합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드

#### 4. `nonpayment.code.validate`
코드 유효성 및 만료일을 확인합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드
- `date` (string, 필수): 확인할 날짜 (YYYY-MM-DD 형식)

### 병원 정보 도구

#### 5. `nonpayment.hospital.search`
특정 비급여 항목을 제공하는 병원을 검색합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드
- `sido` (string, 선택): 시/도 이름 (예: "서울", "부산")
- `sggu` (string, 선택): 시/군/구 이름
- `clCd` (string, 선택): 병원 종별 코드 또는 이름 (예: "상급종합", "종합병원")

#### 6. `nonpayment.hospital.price-range`
특정 병원의 특정 항목에 대한 가격 범위를 조회합니다.

**매개변수:**
- `hospital` (string, 필수): 병원 이름
- `npayCd` (string, 필수): 비급여 코드

#### 7. `nonpayment.hospital.compare`
같은 지역 내 병원 간 가격을 비교합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드
- `sido` (string, 필수): 시/도 이름
- `sggu` (string, 선택): 시/군/구 이름

### 통계 분석 도구

#### 8. `nonpayment.stats.by-region`
비급여 항목의 지역별 가격 통계를 조회합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드

#### 9. `nonpayment.stats.by-hospital-type`
병원 종별 가격 통계를 조회합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드

#### 10. `nonpayment.stats.outlier-detect`
병원의 가격이 비정상적으로 높거나 낮은지 탐지합니다.

**매개변수:**
- `hospital` (string, 필수): 병원 이름
- `npayCd` (string, 필수): 비급여 코드
- `price` (number, 필수): 확인할 가격

### 의사결정 지원 도구

#### 11. `nonpayment.decision.cheapest-option`
위치를 기반으로 최저가 옵션을 찾습니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드
- `sido` (string, 필수): 시/도 이름
- `sggu` (string, 선택): 시/군/구 이름

#### 12. `nonpayment.decision.reasonable-price`
가격이 합리적인지 판단합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드
- `price` (number, 필수): 확인할 가격
- `sido` (string, 선택): 시/도 이름 (지역별 비교 시 사용)

#### 13. `nonpayment.decision.explanation-report`
환자 친화적인 설명 리포트를 생성합니다.

**매개변수:**
- `npayCd` (string, 필수): 비급여 코드
- `sido` (string, 선택): 시/도 이름

## 📋 요구사항

- **Python 3.11+**
- **aiohttp** - 비동기 HTTP 클라이언트
- **fastapi** - HTTP 서버 프레임워크
- **uvicorn** - ASGI 서버
- **mcp** - Model Context Protocol SDK
- **pydantic** - 데이터 검증
- **xmltodict** - XML 파싱

## 🌐 배포

### MCP 클라이언트와 함께 사용하기

**Amazon Q CLI:**
```json
{
  "mcpServers": {
    "nonpayment-health": {
      "command": "python",
      "args": ["run_server.py"],
      "cwd": "/path/to/mcp-nonpayment-health"
    }
  }
}
```

**기타 MCP 클라이언트:**
```json
{
  "mcpServers": {
    "nonpayment-health": {
      "url": "https://your-server.com/nonpayment-health/messages"
    }
  }
}
```

**참고:** 같은 서버에 여러 MCP 서버를 호스팅하는 경우, 각 서버는 다른 API 경로를 사용합니다:
- `mcp-link-scan`: `/messages` 또는 `/link-scan/messages`
- `mcp-nonpayment-health`: `/nonpayment-health/messages`

환경 변수 `API_PREFIX`를 설정하여 경로를 변경할 수 있습니다:
```bash
API_PREFIX=/custom-path
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 🙏 감사의 말

- **건강보험심사평가원** - 비급여진료비정보서비스 API 제공
- **MCP** 팀 - Model Context Protocol 명세
- **Pydantic** 팀 - 데이터 검증 라이브러리

