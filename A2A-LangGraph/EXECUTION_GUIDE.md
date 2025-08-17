# Claude CLI Multi-Agent System 실행 가이드

## 🎯 시스템 구조

이 시스템은 **사용자가 처음 여는 Claude CLI가 Host Agent**가 되어, 필요에 따라 전문 worker agent들을 subprocess로 호출하는 구조입니다.

```
사용자 Claude CLI (Host Agent)
    ↓ subprocess 호출
    ├── Frontend Agent (React, Vue.js 등)
    ├── Backend Agent (API, 데이터베이스 등)  
    └── Unity Agent (게임 개발)
```

## 🚀 실행 방법

### 1단계: Claude CLI 설정

Host Agent로 동작할 Claude CLI에 설정을 적용합니다:

```bash
# 프로젝트 디렉토리로 이동
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph

# Claude CLI를 Host Agent 설정으로 시작
claude --context "CLAUDE.md"
```

### 2단계: Worker Agent 서버 실행 (백그라운드)

Worker agent들은 A2A 프로토콜을 위해 백그라운드 서버로 실행합니다:

#### PowerShell/CMD 창 1: Frontend Agent
```bash
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph
python -m agents.claude_cli.frontend.server
```

#### PowerShell/CMD 창 2: Backend Agent  
```bash
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph
python -m agents.claude_cli.backend.server
```

#### PowerShell/CMD 창 3: Unity Agent
```bash
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph
python -m agents.claude_cli.unity.server
```

### 3단계: Host Claude CLI에서 작업 요청

이제 Host Claude CLI에서 작업을 요청하면, 자동으로 적절한 worker agent를 호출합니다.

## 💬 사용 예시

### 단일 Agent 작업

#### Frontend 작업
```
사용자: "Create a React login form component with email and password fields"

Host Agent 처리:
1. 키워드 분석: "React", "component" → Frontend Agent 필요
2. Frontend Agent subprocess 호출
3. 결과를 사용자에게 반환
```

#### Backend 작업
```
사용자: "Design a REST API for user authentication with JWT tokens"

Host Agent 처리:
1. 키워드 분석: "REST API", "authentication" → Backend Agent 필요  
2. Backend Agent subprocess 호출
3. 결과를 사용자에게 반환
```

#### Unity 작업
```
사용자: "Create a Unity character controller script for third-person movement"

Host Agent 처리:
1. 키워드 분석: "Unity", "character controller" → Unity Agent 필요
2. Unity Agent subprocess 호출  
3. 결과를 사용자에게 반환
```

### 멀티 Agent 조정 작업

#### 풀스택 앱 개발
```
사용자: "Build a task management application with React frontend and Node.js backend"

Host Agent 처리:
1. 분석: Frontend + Backend 모두 필요
2. Frontend Agent 호출 → React 컴포넌트 설계
3. Backend Agent 호출 → Node.js API 설계  
4. 두 결과를 통합하여 완전한 솔루션 제공
```

#### 게임 + 백엔드 시스템
```
사용자: "Create a Unity multiplayer game with leaderboard system"

Host Agent 처리:
1. 분석: Unity + Backend 필요
2. Unity Agent 호출 → 멀티플레이어 게임 클라이언트
3. Backend Agent 호출 → 리더보드 API 서버
4. 통합된 게임 시스템 솔루션 제공
```

## 🔧 Host Agent 동작 원리

Host Claude CLI는 `CLAUDE.md`에 정의된 로직에 따라:

### 1. **요청 분석**
- 키워드 기반으로 필요한 agent 판단
- Frontend: UI, component, React, Vue, styling
- Backend: API, database, server, authentication  
- Unity: game, Unity, 3D, physics, GameObject

### 2. **Agent 호출**
```python
# 실제 subprocess 호출 예시
subprocess.run([
    "claude",
    "--context", "agents/claude_cli/frontend/CLAUDE.md", 
    "--system", "You are a Frontend Developer expert",
    "Create a React login form"
], capture_output=True, text=True)
```

### 3. **응답 통합**
- 단일 agent: 결과를 그대로 반환
- 멀티 agent: 여러 결과를 논리적으로 통합

## 📁 파일 위치 확인

실행 전 다음 파일들이 있는지 확인:

```
A2A-LangGraph/
├── CLAUDE.md                           # ✅ Host Agent 설정
├── agents/claude_cli/frontend/
│   ├── CLAUDE.md                       # ✅ Frontend Agent 설정
│   └── server.py                       # ✅ Frontend A2A 서버
├── agents/claude_cli/backend/  
│   ├── CLAUDE.md                       # ✅ Backend Agent 설정
│   └── server.py                       # ✅ Backend A2A 서버
└── agents/claude_cli/unity/
    ├── CLAUDE.md                       # ✅ Unity Agent 설정
    └── server.py                       # ✅ Unity A2A 서버
```

## 🧪 테스트 방법

### 방법 1: Host Claude CLI에서 직접 테스트

```bash
# Host Claude CLI 시작
claude --context "CLAUDE.md"

# 테스트 요청들
"Create a simple React button component"
"Design a user registration API"  
"Create a Unity jump mechanic script"
"Build a todo app with React and Express.js"
```

### 방법 2: Worker Agent A2A 서버 테스트

```bash
# Frontend Agent 테스트
curl -X POST http://localhost:8010/api/a2a \
  -H "Content-Type: application/json" \
  -d @test_frontend_message.json

# Backend Agent 테스트  
curl -X POST http://localhost:8011/api/a2a \
  -H "Content-Type: application/json" \
  -d @test_backend_message.json

# Unity Agent 테스트
curl -X POST http://localhost:8012/api/a2a \
  -H "Content-Type: application/json" \
  -d @test_unity_message.json
```

## 🐛 문제해결

### Host Claude CLI 관련

#### 1. Context 파일을 찾을 수 없음
```bash
# 현재 디렉토리 확인
pwd
# 응답: D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph

# CLAUDE.md 파일 존재 확인
ls CLAUDE.md
```

#### 2. Subprocess 호출 실패
```bash
# Claude CLI 설치 확인
claude --version

# PATH 환경변수 확인
echo $PATH
```

#### 3. Worker Agent 응답 없음
```bash
# Worker Agent 서버 상태 확인
netstat -ano | findstr :8010
netstat -ano | findstr :8011  
netstat -ano | findstr :8012

# 각 서버가 실행 중인지 확인
curl http://localhost:8010/health  # (있다면)
curl http://localhost:8011/health
curl http://localhost:8012/health
```

### Worker Agent 서버 관련

#### 1. 포트 충돌
```bash
# 사용중인 포트 확인 및 종료
netstat -ano | findstr :8010
taskkill /PID <PID> /F
```

#### 2. 모듈 Import 에러
```bash
# Python 경로 설정
set PYTHONPATH=D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph

# 또는 프로젝트 루트에서 실행
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph
python -m agents.claude_cli.frontend.server
```

## 🔄 개발 워크플로우

### Host Agent 설정 수정
1. `CLAUDE.md` 편집
2. Claude CLI 재시작: `claude --context "CLAUDE.md"`

### Worker Agent 설정 수정  
1. `agents/claude_cli/{agent}/CLAUDE.md` 편집
2. 해당 worker agent 서버 재시작

### 새로운 Agent 추가
1. 새 agent 디렉토리 생성
2. `CLAUDE.md` 에서 agent 설정 추가
3. Host Agent의 `CLAUDE.md`에 routing 로직 추가

## ✅ 실행 체크리스트

시작하기 전:
- [ ] Claude CLI 설치 확인
- [ ] 프로젝트 디렉토리에 있음
- [ ] Python 환경 준비 완료
- [ ] 포트 8010, 8011, 8012 사용 가능

실행 순서:
- [ ] 1. Worker agent 서버들 시작 (백그라운드)
- [ ] 2. Host Claude CLI 시작: `claude --context "CLAUDE.md"`  
- [ ] 3. Host CLI에서 작업 요청
- [ ] 4. 자동으로 worker agent 호출되는지 확인

## 🎉 성공 확인

Host Claude CLI에서 다음과 같이 요청했을 때:

```
"Create a React login form with email and password fields"
```

올바르게 동작하면:
1. Host가 "Frontend Agent가 필요하다"고 판단
2. Frontend Agent subprocess 호출
3. React 컴포넌트 코드 반환
4. 사용자에게 완전한 솔루션 제공

이렇게 되면 Claude CLI Multi-Agent 시스템이 정상 작동하는 것입니다! 🚀