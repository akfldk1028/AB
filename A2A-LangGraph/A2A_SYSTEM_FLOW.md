# A2A (Agent-to-Agent) Multi-Agent System Flow

## 🏗️ 시스템 아키텍처 개요

```
사용자 → Host Agent (Claude Code 세션) → A2A Worker Agents → Claude AI 응답
                     ↓
              JSON-RPC 2.0 A2A Protocol
                     ↓
     [Frontend Worker] ←→ [Backend Worker] ←→ [Unity Worker]
           8010            8021             8012
```

## 📁 파일 구조

```
A2A-LangGraph/
├── CLAUDE.md                          # Host Agent 설정 (현재 세션)
├── A2A_SYSTEM_FLOW.md                 # 이 문서
├── agents/claude_cli/                 # A2A Worker Agent들
│   ├── frontend/
│   │   ├── agent.py                   # Frontend A2A Worker 서버
│   │   ├── server.py                  # FastAPI 서버 실행
│   │   └── CLAUDE.md                  # Frontend Agent 설정
│   ├── backend/
│   │   ├── agent.py                   # Backend A2A Worker 서버
│   │   ├── server.py                  # FastAPI 서버 실행
│   │   └── CLAUDE.md                  # Backend Agent 설정
│   └── unity/
│       ├── agent.py                   # Unity A2A Worker 서버
│       ├── server.py                  # FastAPI 서버 실행
│       └── CLAUDE.md                  # Unity Agent 설정
├── projects/                          # 생성된 프로젝트 파일들
│   ├── TTT/
│   │   ├── TicTacToe.jsx             # Frontend Worker 생성
│   │   └── tictactoe_api.py          # Backend Worker 생성
│   └── MAS/
│       ├── AgentDashboard.jsx        # Frontend Worker 생성
│       └── multi_agent_system.py     # Backend Worker 생성
└── shared/                           # 공유 모듈들
    ├── custom_types.py
    └── server.py
```

## 🚀 시스템 시작 Flow

### 1. A2A Worker 서버 시작
```bash
# Terminal 1: Frontend Worker
cd agents/claude_cli/frontend && python server.py
# → http://localhost:8010 에서 실행

# Terminal 2: Backend Worker  
cd agents/claude_cli/backend && python server.py
# → http://localhost:8021 에서 실행

# Terminal 3: Unity Worker (선택적)
cd agents/claude_cli/unity && python server.py
# → http://localhost:8012 에서 실행
```

### 2. Host Agent 초기화
- Host Agent는 현재 Claude Code 세션
- `CLAUDE.md`에서 A2A 통신 함수들 로드
- 워커들의 상태 확인 (`/.well-known/agent.json`)

## 💬 A2A 통신 Flow

### Host Agent → Worker Agent 통신

```python
# 1. 사용자 요청 분석
user_request = "Create a React component"

# 2. 적절한 워커 선택
agent_type = "frontend"  # 또는 "backend", "unity"

# 3. A2A 메시지 생성
message = {
    "jsonrpc": "2.0",
    "id": f"host_to_{agent_type}_{timestamp}",
    "method": "message/send",
    "params": {
        "message": {
            "role": "user",
            "parts": [{"kind": "text", "text": task}],
            "messageId": f"msg_{timestamp}",
            "kind": "message"
        }
    }
}

# 4. HTTP POST 요청
response = requests.post(f"http://localhost:{port}/", json=message)

# 5. 응답 처리 및 사용자에게 반환
```

### Worker Agent ↔ Worker Agent 통신

```python
# Backend Worker → Frontend Worker 예시
def communicate_with_frontend(message: str) -> str:
    url = "http://localhost:8010/"
    payload = {
        "jsonrpc": "2.0",
        "id": "backend_to_frontend",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": f"backend_msg_{timestamp}",
                "parts": [{"kind": "text", "text": message}]
            }
        }
    }
    
    response = requests.post(url, json=payload)
    return extract_response_content(response)
```

## 🔄 Worker Agent 내부 Flow

### 1. 서버 실행 (server.py)
```python
# FastAPI 서버 시작
# A2A 프로토콜 엔드포인트 설정
# Agent Card 제공 (/.well-known/agent.json)
```

### 2. 요청 처리 (agent.py)
```python
# A2A 메시지 수신
# ↓
# Claude CLI 명령어 구성
cmd = ["claude.cmd", "--print", "--permission-mode", "bypassPermissions", 
       "--add-dir", agent_directory, "--append-system-prompt", system_instruction]
# ↓  
# stdin으로 query 전달
process.communicate(input=query.encode('utf-8'))
# ↓
# Claude AI 응답 받기
# ↓
# A2A 형식으로 응답 반환
```

### 3. 파일 생성 Flow
```
사용자 요청 → Host Agent → Worker Agent → Claude CLI 
                                              ↓
projects/[PROJECT_NAME]/filename.ext ← Claude AI 응답
```

## 🛠️ 주요 설정 파일들

### CLAUDE.md (Host Agent - 현재 세션)
- A2A 통신 함수 정의
- Worker Agent 포트 및 URL 설정
- 태스크 라우팅 로직
- Multi-Agent 협업 패턴

### agents/claude_cli/*/CLAUDE.md (Worker Agents)
- 각 도메인별 전문 지식 설정
- **파일 생성 경로 강제 지정**: `projects/[PROJECT_NAME]/`
- Agent 간 직접 통신 함수 포함
- 10분 타임아웃 설정

### agents/claude_cli/*/agent.py (Worker Servers)
- FastAPI 기반 A2A 서버
- JSON-RPC 2.0 프로토콜 구현
- Claude CLI subprocess 호출
- UTF-8 인코딩 처리
- stdin 방식 query 전달

## 📋 사용 예시

### 1. 단일 Agent 작업
```
사용자: "Create a login form in React"
↓
Host Agent: frontend 선택
↓
Frontend Worker: TicTacToe.jsx 생성 in projects/APP/
↓
사용자: React 컴포넌트 완성됨
```

### 2. Multi-Agent 협업
```
사용자: "Build a fullstack chat app"
↓
Host Agent: frontend + backend 선택
↓
Frontend Worker: chat UI 생성
Backend Worker: chat API 생성
↓
Worker 간 A2A 통신으로 API 스펙 협의
↓
사용자: 통합된 풀스택 솔루션 제공
```

### 3. Worker 간 직접 소통
```
Backend Worker: "Frontend Agent에게 API 스펙 문의"
↓
A2A Protocol: JSON-RPC 2.0 메시지 전송
↓
Frontend Worker: "데이터 포맷 제안 응답"
↓
Backend Worker: 협의된 스펙으로 API 개발
```

## ⚙️ 핵심 개선사항

### 1. 타임아웃 개선
- **Before**: 300초 (5분)
- **After**: 600초 (10분)
- **효과**: 복잡한 AI 응답과 A2A 통신에 충분한 시간

### 2. 파일 경로 강제 지정
- **문제**: Agent 디렉토리에 파일 생성
- **해결**: `projects/[PROJECT_NAME]/` 강제 지정
- **효과**: 깔끔한 프로젝트 구조 유지

### 3. 인코딩 문제 해결
- **문제**: 한글 텍스트 깨짐
- **해결**: UTF-8 인코딩 강제 적용
- **효과**: 안정적인 다국어 처리

### 4. Claude CLI 명령어 개선
- **문제**: "Input must be provided" 에러
- **해결**: stdin 방식으로 query 전달
- **효과**: 안정적인 Claude AI 호출

## 🔍 디버깅 및 모니터링

### Worker 로그 확인
```bash
# Frontend Worker 로그
BashOutput bash_id: bash_10

# Backend Worker 로그  
BashOutput bash_id: bash_11
```

### Agent Card 확인
```bash
curl http://localhost:8010/.well-known/agent.json  # Frontend
curl http://localhost:8021/.well-known/agent.json  # Backend
curl http://localhost:8012/.well-known/agent.json  # Unity
```

### A2A 통신 테스트
```python
# 간단한 테스트
test_message = {"jsonrpc": "2.0", "id": "test", "method": "message/send", ...}
response = requests.post("http://localhost:8010/", json=test_message)
```

## 🎯 다음 개발 방향

1. **Unity Worker 활성화**: 게임 개발 워크플로우
2. **Database Worker 추가**: 데이터베이스 전문 에이전트
3. **ML Worker 추가**: 머신러닝/AI 모델 전문 에이전트
4. **웹 UI 대시보드**: Agent 상태 모니터링
5. **로깅 시스템**: A2A 통신 추적 및 분석

---

## 📚 참고 정보

- **A2A 프로토콜**: Google ADK 표준 준수
- **통신 방식**: HTTP JSON-RPC 2.0
- **AI 엔진**: Claude AI (Claude Code CLI)
- **서버 프레임워크**: FastAPI
- **포트**: Frontend(8010), Backend(8021), Unity(8012)