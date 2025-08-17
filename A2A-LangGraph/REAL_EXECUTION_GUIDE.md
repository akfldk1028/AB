# Claude CLI Multi-Agent System 실행 가이드

## 🎯 시스템 개념

Host Agent (현재 Claude 세션)가 사용자와 대화하며, 필요시 A2A 프로토콜로 전문 Worker Agent들과 협업하는 시스템입니다.

```
사용자 ↔ Host Agent (현재 Claude CLI)
           ↓ call_a2a_agent() 함수 호출
    ┌─────────────────────────┐
    │  A2A Worker Agents     │
    │ Frontend ↔ Backend ↔ Unity │
    │ (각각 독립 Claude AI)    │
    └─────────────────────────┘
```

## 🚀 실행 방법

### 1단계: Worker Agent 서버들 실행

먼저 백그라운드에서 전문 agent 서버들을 실행합니다:

### 방법 1: 개별 터미널에서 실행

#### 터미널 1: Frontend Agent (포트 8010)
```bash
cd "D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph\agents\claude_cli\frontend"
python server.py

# 종료: Ctrl+C 또는 터미널 닫기
```

#### 터미널 2: Backend Agent (포트 8021)  
```bash
cd "D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph\agents\claude_cli\backend"
python server.py

# 종료: Ctrl+C 또는 터미널 닫기
```

#### 터미널 3: Unity Agent (포트 8012)
```bash
cd "D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph\agents\claude_cli\unity"
python server.py

# 종료: Ctrl+C 또는 터미널 닫기
```

### 방법 2: 한 번에 모든 Agent 실행 ⚡

#### 🚀 **가장 쉬운 방법**: 준비된 스크립트 실행

**Windows 배치파일 실행:**
```bash
# 프로젝트 디렉토리에서 실행
start_all_agents.bat
```

**또는 PowerShell 스크립트 실행:**
```powershell
# PowerShell에서 실행
.\start_all_agents.ps1
```

#### 수동 일괄 실행 (PowerShell)
```powershell
cd "D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph"

# 백그라운드에서 모든 agent 실행
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd agents\claude_cli\frontend; python server.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd agents\claude_cli\backend; python server.py" 
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd agents\claude_cli\unity; python server.py"

echo "All agents starting... Check the opened windows for status"
```

#### 수동 배치 명령어
```batch
@echo off
cd /d "D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph"

start "Frontend Agent (8010)" cmd /k "cd agents\claude_cli\frontend && python server.py"
start "Backend Agent (8021)" cmd /k "cd agents\claude_cli\backend && python server.py"  
start "Unity Agent (8012)" cmd /k "cd agents\claude_cli\unity && python server.py"
```

### 2단계: Claude CLI 시작

Claude CLI는 자동으로 `CLAUDE.md` 파일을 감지합니다:

```bash
# 프로젝트 디렉토리로 이동
cd D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph

# Claude CLI 시작 (CLAUDE.md 자동 감지됨)
claude
```

> 💡 **자동 감지**: Claude CLI가 시작되면 프로젝트의 `CLAUDE.md` 파일을 자동으로 찾아서 Multi-Agent 설정을 로드합니다.

## 💬 사용 방법 (자연스러운 대화)

Claude CLI가 시작되면, 자연어로 대화하면 됩니다. AI가 자동으로 적절한 agent들을 호출합니다.

### 🎨 Frontend 작업 예시

```
💬 사용자: "React로 로그인 폼 컴포넌트 만들어줘"

🤖 Claude: 
React 로그인 폼을 만들어드리겠습니다. Frontend Agent를 호출하여 
최적화된 컴포넌트를 생성하겠습니다.

[Frontend Agent 자동 호출]
→ React 로그인 폼 컴포넌트 코드 생성
→ CSS 스타일링 포함
→ 사용법 예시 제공

여기 완성된 로그인 폼 컴포넌트입니다:
[상세한 코드와 설명]
```

### ⚙️ Backend 작업 예시

```
💬 사용자: "사용자 인증 API 설계해줘"

🤖 Claude:
사용자 인증 API를 설계하겠습니다. Backend Agent에서 
보안을 고려한 REST API를 생성하겠습니다.

[Backend Agent 자동 호출]
→ JWT 기반 인증 API 설계
→ 데이터베이스 스키마 설계
→ 보안 미들웨어 구현

완성된 인증 API 시스템입니다:
[API 엔드포인트, 코드, 문서]
```

### 🎮 Unity 작업 예시

```
💬 사용자: "Unity에서 캐릭터 이동 스크립트 만들어줘"

🤖 Claude:
Unity 캐릭터 컨트롤러를 만들어드리겠습니다. 
Unity Agent에서 최적화된 스크립트를 생성하겠습니다.

[Unity Agent 자동 호출]
→ 3인칭 캐릭터 컨트롤러 스크립트
→ 물리 기반 이동 시스템
→ 설정 방법 가이드

캐릭터 이동 시스템이 완성되었습니다:
[C# 스크립트, 설정 방법, 사용법]
```

### 🚀 Multi-Agent 협업 예시

```
💬 사용자: "할일 관리 앱을 React + Node.js로 풀스택 개발해줘"

🤖 Claude:
풀스택 할일 관리 앱을 개발하겠습니다. 
Frontend와 Backend Agent가 협업하여 완전한 시스템을 만들겠습니다.

[Multi-Agent 협업 시작]
Frontend Agent → React UI 컴포넌트 설계
Backend Agent → Node.js API 서버 설계
[A2A 프로토콜로 데이터 형식 조율]

완성된 풀스택 앱입니다:
📱 Frontend: React 컴포넌트 + 상태관리
🔧 Backend: Express.js API + 데이터베이스
🔗 통합: API 연동 코드
📖 배포: 실행 방법 가이드
```

### 🎯 게임 + 백엔드 협업 예시

```
💬 사용자: "Unity 멀티플레이어 게임에 리더보드 시스템 추가해줘"

🤖 Claude:
멀티플레이어 게임용 리더보드 시스템을 구축하겠습니다.
Unity Agent와 Backend Agent가 협업합니다.

[Unity + Backend 협업]
Unity Agent → 게임 내 리더보드 UI
Backend Agent → 리더보드 API 서버
[A2A로 스코어 데이터 형식 협의]

게임 리더보드 시스템 완성:
🎮 Unity: 리더보드 UI + 네트워킹
🔧 Backend: 스코어 API + 랭킹 시스템  
📊 실시간: WebSocket 스코어 업데이트
```

## 🔍 AI 자동 판단 로직

Claude CLI의 AI가 다음과 같이 자동으로 agent를 선택합니다:

### Frontend Agent 호출 조건
- **키워드**: React, Vue, Angular, 컴포넌트, UI, 스타일링
- **예시**: "버튼 만들어줘", "반응형 레이아웃", "다크모드"

### Backend Agent 호출 조건  
- **키워드**: API, 데이터베이스, 서버, 인증, REST, GraphQL
- **예시**: "로그인 API", "데이터베이스 설계", "JWT 토큰"

### Unity Agent 호출 조건
- **키워드**: Unity, 게임, 3D, 물리, 애니메이션, 캐릭터
- **예시**: "캐릭터 이동", "게임 오브젝트", "셰이더"

### Multi-Agent 협업 조건
- **풀스택**: "React + Node.js", "프론트엔드 + 백엔드"
- **게임 백엔드**: "Unity + 서버", "멀티플레이어 + API"
- **복합 시스템**: 여러 기술 스택이 언급된 경우

## 🔗 A2A 프로토콜 자동 동작

Agent들이 협업할 때 A2A 프로토콜이 자동으로 동작합니다:

```
Frontend Agent ↔ Backend Agent
     ↕
  A2A Messages
     ↕  
Unity Agent ↔ Backend Agent
```

**자동 협업 시나리오:**
1. **데이터 형식 조율**: API 스펙 통일
2. **인터페이스 정의**: 컴포넌트 props와 API 응답 매칭
3. **에러 처리**: 통일된 에러 형식
4. **인증 시스템**: JWT 토큰 공유 방식

## ⚡ 고급 사용법

### Slash 명령어 활용

```bash
# 컨텍스트 초기화
/clear

# 이전 세션 재개
/resume  

# 프로젝트 설정 파일 생성 (선택사항)
/init
```

> 💡 **참고**: `/init`은 새 프로젝트에서 `CLAUDE.md` 파일을 생성할 때만 사용합니다. 기존 프로젝트는 자동 감지됩니다.

### 파일 참조

```
💬 "이 컴포넌트를 개선해줘 @LoginForm.jsx"
💬 "이 API와 연동되는 프론트엔드 만들어줘 @userAPI.js"
```

### 이미지 참조 (디자인 구현)

```
💬 "이 디자인 목업을 React로 구현해줘" [이미지 붙여넣기]
```

## 🐛 문제해결

### Agent 서버 상태 확인

```bash
# 포트 확인
netstat -ano | findstr :8010  # Frontend
netstat -ano | findstr :8021  # Backend (실제 포트)
netstat -ano | findstr :8012  # Unity

# Agent Card 테스트
curl http://localhost:8010/.well-known/agent.json
curl http://localhost:8021/.well-known/agent.json  
curl http://localhost:8012/.well-known/agent.json

# A2A 메시지 테스트
# Frontend Agent
curl -X POST http://localhost:8010/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":\"test\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"msg_001\",\"taskId\":\"task_001\",\"contextId\":\"session_001\",\"parts\":[{\"kind\":\"text\",\"text\":\"Create a React login form\"}]}}}"

# Backend Agent  
curl -X POST http://localhost:8021/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":\"test\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"msg_001\",\"taskId\":\"task_001\",\"contextId\":\"session_001\",\"parts\":[{\"kind\":\"text\",\"text\":\"Create a REST API for user registration\"}]}}}"

# Unity Agent
curl -X POST http://localhost:8012/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":\"test\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"msg_001\",\"taskId\":\"task_001\",\"contextId\":\"session_001\",\"parts\":[{\"kind\":\"text\",\"text\":\"Create a Unity character controller\"}]}}}"
```

### Claude CLI 문제

```bash
# Claude CLI 재시작
# Ctrl+C로 종료 후 다시 실행
claude

# 컨텍스트 문제 시
/clear
```

### Agent 호출 안될 때

1. **CLAUDE.md 확인**: 프로젝트 루트에 설정 파일 존재 확인
2. **Agent 서버 확인**: 3개 서버 모두 실행 중인지 확인
3. **요청 명확화**: 더 구체적인 키워드 사용

## ✅ 성공 확인 체크리스트

- [ ] Agent 서버 3개 모두 실행 중 (포트 8010, 8021, 8012)
- [ ] `claude` 명령어로 CLI 정상 시작
- [ ] 자연어 요청 시 적절한 agent 자동 호출
- [ ] Multi-agent 작업 시 A2A 협업 동작
- [ ] 통합된 결과를 자연스럽게 제공

## ⚡ 빠른 시작 가이드

### 1. 한 번에 모든 Agent 실행
```bash
# 프로젝트 디렉토리에서 실행
start_all_agents.bat
```

### 2. Claude CLI 시작  
```bash
claude
```

### 3. 자연스럽게 대화 시작
```
💬 "React 대시보드 만들어줘"
💬 "사용자 관리 API 설계해줘"  
💬 "Unity 캐릭터 컨트롤러 만들어줘"
💬 "게시판 시스템을 풀스택으로 개발해줘"
```

## 🧪 빠른 테스트 명령어

### Agent 상태 확인
```bash
# 모든 Agent Card 확인 (한 번에)
curl http://localhost:8010/.well-known/agent.json && curl http://localhost:8021/.well-known/agent.json && curl http://localhost:8012/.well-known/agent.json
```

### 각 Agent별 테스트
```bash
# Frontend Agent 테스트
curl -X POST http://localhost:8010/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":\"test\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"msg_001\",\"taskId\":\"task_001\",\"contextId\":\"session_001\",\"parts\":[{\"kind\":\"text\",\"text\":\"Create a React login form\"}]}}}"

# Backend Agent 테스트
curl -X POST http://localhost:8021/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":\"test\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"msg_001\",\"taskId\":\"task_001\",\"contextId\":\"session_001\",\"parts\":[{\"kind\":\"text\",\"text\":\"Create a REST API\"}]}}}"

# Unity Agent 테스트  
curl -X POST http://localhost:8012/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":\"test\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"msg_001\",\"taskId\":\"task_001\",\"contextId\":\"session_001\",\"parts\":[{\"kind\":\"text\",\"text\":\"Create Unity controller\"}]}}}"
```

## 🎉 완료!

이제 Claude CLI와 자연스럽게 대화하면, AI가 알아서 최적의 전문 agent들을 호출하고 협업시켜서 완성된 솔루션을 제공합니다! 🚀

**성공 확인**: 각 agent가 실제 코드를 생성하고 A2A 프로토콜로 협업하는 것을 확인할 수 있습니다.