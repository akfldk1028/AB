# A2A LangGraph Multi-Agent System 사용 가이드

## 🎯 시스템 개요

**최신 구현된 기능:**
- ✅ **Official Google A2A Protocol** (`message/send` 방식)
- ✅ **Multi-Agent 협업** (Currency + Weather Agents)
- ✅ **LangGraph ReAct** 지능형 라우팅
- ✅ **MCP (Model Context Protocol)** 도구 통합
- ✅ **실시간 대화형 Interface**

## 🚀 빠른 시작

### 1. 모든 에이전트 한번에 실행
```bash
# 프로젝트 루트에서
start_agents.bat
```

### 2. 수동으로 각각 실행 (개발자 모드)

**터미널 1: Currency Agent (포트 8000)**
```bash
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph
powershell -ExecutionPolicy Bypass -Command "& ..\venv\Scripts\Activate.ps1; python agents\worker_agent.py"
```

**터미널 2: Weather Agent (포트 8001)**
```bash
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph
powershell -ExecutionPolicy Bypass -Command "& ..\venv\Scripts\Activate.ps1; python agents\weather\weather_agent.py"
```

**터미널 3: Host Agent (대화형)**
```bash
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph
powershell -ExecutionPolicy Bypass -Command "& ..\venv\Scripts\Activate.ps1; python host\main.py"
```

## 💬 테스트 시나리오

### 기본 기능 테스트
```
Convert 100 USD to EUR
What's the weather in Seoul?
Convert 500 USD to KRW
What's the weather in Tokyo?
```

### Multi-Agent 협업 테스트
```
I'm planning a trip to Seoul. What's the weather like there and how much would 500 USD be in local currency?

I need to prepare for a business trip to London. Can you tell me the weather and convert 1000 USD to British pounds?

Planning vacation in Tokyo - need weather forecast and 2000 USD in Japanese yen
```

### 종료
```
quit
exit
bye
```

## 🏗️ 시스템 아키텍처

```
사용자 입력
    ↓
[Host Agent - LangGraph ReAct]
    ↓                     ↓
[Currency Agent]    [Weather Agent]
   (Port 8000)        (Port 8001)
    ↓                     ↓
[MCP Tools]         [Weather Tools]
Exchange Rates      City Weather Data
```

### Agent 상세 정보

#### 🏦 Currency Agent (Port 8000)
- **기능**: 환율 변환 및 계산
- **지원 통화**: USD, EUR, GBP, JPY, KRW, CAD, AUD, CHF
- **프로토콜**: Official A2A `message/send`
- **MCP 도구**: 실시간 환율 데이터

#### 🌤️ Weather Agent (Port 8001)
- **기능**: 도시별 날씨 정보 제공
- **지원 도시**: Seoul, Tokyo, New York, London, Paris, Sydney
- **프로토콜**: Official A2A `message/send`
- **데이터**: 온도, 습도, 바람, 날씨 상태

#### 🎛️ Host Agent
- **기능**: 사용자 인터페이스 및 Agent 라우팅
- **AI 엔진**: GPT-4o + LangGraph ReAct
- **특징**: 자동 Agent 선택 및 결과 통합

## 📋 환경 설정

### 필수 환경변수
```bash
# .env 파일 생성
OPENAI_API_KEY=your_openai_api_key_here
```

### 의존성 설치 (최초 설정)
```bash
cd D:\Data\05_CGXR\A2A\LangGrpah
python -m venv venv
venv\Scripts\activate.bat
pip install -r A2A-LangGraph\requirements.txt
```

## 🛠️ 기술 스택

- **AI Framework**: LangGraph + LangChain
- **Protocol**: Google A2A Protocol (JSON-RPC 2.0)
- **Tool Integration**: MCP (Model Context Protocol)
- **Web Framework**: FastAPI + Uvicorn
- **AI Model**: OpenAI GPT-4o-mini

## 📁 프로젝트 구조

```
D:\Data\05_CGXR\A2A\LangGrpah\
├── start_agents.bat              # 🆕 원클릭 실행
├── HOW_TO_USE.md                # 🆕 최신 가이드
├── venv/                        # Python 가상환경
└── A2A-LangGraph/
    ├── .env                     # API 키 설정
    ├── requirements.txt         # 의존성 목록
    ├── agents/                  # 🆕 Agent 구현
    │   ├── worker_agent.py     # Currency Agent
    │   ├── mcp_server.py       # MCP 도구 서버
    │   └── weather/            # Weather Agent
    │       ├── weather_agent.py
    │       └── weather_agent_core.py
    ├── host/                   # 🆕 Host Agent
    │   └── main.py            # 메인 인터페이스
    ├── shared/                 # 🆕 공통 라이브러리
    │   ├── agent.py           # LangGraph Agent 구현
    │   ├── task_manager.py    # A2A 태스크 관리
    │   ├── server.py          # A2A 서버 기반
    │   ├── custom_types.py    # A2A 타입 정의
    │   └── ...
    └── tools/                  # 🆕 도구 및 유틸리티
        └── graph_visualization.html
```

## 🎮 실제 사용 예시

### 1. 단일 Agent 호출
```
사용자: Convert 100 USD to EUR
Host Agent: 100 USD is approximately 92.00 EUR at the current exchange rate.
```

### 2. Multi-Agent 협업
```
사용자: I'm planning a trip to Seoul. What's the weather like there and how much would 500 USD be in local currency?

Host Agent: Here's the information for your trip to Seoul:

- **Weather in Seoul:** The current weather is 22°C with partly cloudy skies. The humidity level is 65%, and there's a wind speed of 10 km/h. It's a pleasant day overall with some clouds.

- **Currency Conversion:** 500 USD is approximately 660,000 KRW based on the current exchange rate of 1 USD = 1320.0000 KRW.
```

## 🔍 문제 해결

### 1. API 키 관련
```bash
# 오류: "OPENAI_API_KEY not found"
# 해결: .env 파일 확인
echo OPENAI_API_KEY=sk-your-key-here > .env
```

### 2. 포트 충돌
```bash
# 오류: "Address already in use"
# 해결: 포트 8000, 8001 확인
netstat -ano | findstr :8000
netstat -ano | findstr :8001
```

### 3. 가상환경 문제
```bash
# PowerShell 실행 정책 오류시
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. 모듈 Import 오류
```bash
# shared 모듈 경로 문제시
cd A2A-LangGraph
python -c "import sys; print(sys.path)"
```

## 🚦 상태 확인

### Agent 연결 확인
```bash
# Currency Agent (포트 8000)
curl http://localhost:8000/.well-known/agent.json

# Weather Agent (포트 8001)  
curl http://localhost:8001/.well-known/agent.json
```

### 로그 모니터링
각 터미널에서 다음 로그들을 확인:
- `DEBUG: A2A message/send received:` - A2A 프로토콜 요청
- `DEBUG: Sync MCP tool wrapper called` - MCP 도구 호출
- `DEBUG: Found final AI message:` - AI 응답 완료

## 🔧 개발자 팁

### 1. 새로운 Agent 추가
```python
# agents/new_agent/new_agent.py 생성
# shared/agent.py 를 기반으로 구현
# A2A protocol 지원 추가
```

### 2. MCP 도구 추가
```python
# agents/mcp_server.py 에 새 도구 등록
# shared/agent.py 의 sync wrapper 추가
```

### 3. 디버깅 모드
```bash
# 더 상세한 로그를 위해
export LANGCHAIN_VERBOSE=true
export LANGCHAIN_TRACING=true
```

## 🎯 다음 단계

1. **Real-time UI 모니터링**: `tools/graph_visualization.html` 활용
2. **더 많은 Agent 추가**: 번역, 검색, 데이터 분석 등
3. **Production 배포**: Docker 컨테이너화
4. **성능 최적화**: Agent 캐싱 및 병렬 처리

## 📞 지원 및 문의

**시스템 상태 확인 체크리스트:**
- [ ] `.env` 파일에 OPENAI_API_KEY 설정됨
- [ ] 가상환경 활성화됨
- [ ] 포트 8000, 8001 사용 가능
- [ ] 모든 Agent가 "INFO: Application startup complete" 표시
- [ ] Host Agent가 "Connected to: http://localhost:8000, http://localhost:8001" 표시

**성공적인 A2A Multi-Agent 협업 시스템이 완성되었습니다!** 🎉