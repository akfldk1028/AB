# User Profile API

Backend Agent가 생성한 간단한 사용자 프로필 API입니다.

## 기능

- 사용자 생성 (POST /api/users)
- 사용자 조회 (GET /api/users/{user_id})
- 모든 사용자 조회 (GET /api/users)
- 사용자 정보 수정 (PUT /api/users/{user_id})
- 사용자 삭제 (DELETE /api/users/{user_id})

## 데이터 모델

```json
{
  "id": "uuid",
  "name": "string",
  "email": "email@example.com",
  "createdAt": "2024-01-01T00:00:00"
}
```

## 설치 및 실행

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 서버 실행:
```bash
python user_profile_api.py
```

3. API 문서 확인:
브라우저에서 http://localhost:8000/docs 접속

4. 테스트 실행:
```bash
python test_user_api.py
```

## API 엔드포인트

### 1. 헬스 체크
- **GET** `/`
- 응답: `{"message": "User Profile API is running", "version": "1.0.0"}`

### 2. 사용자 생성
- **POST** `/api/users`
- 요청 본문:
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

### 3. 사용자 조회
- **GET** `/api/users/{user_id}`
- 응답: 사용자 정보

### 4. 모든 사용자 조회
- **GET** `/api/users`
- 응답: 모든 사용자 목록과 총 개수

### 5. 사용자 수정
- **PUT** `/api/users/{user_id}`
- 요청 본문 (선택적 필드):
```json
{
  "name": "New Name",
  "email": "newemail@example.com"
}
```

### 6. 사용자 삭제
- **DELETE** `/api/users/{user_id}`
- 응답: 삭제 확인 메시지와 삭제된 사용자 정보

## 특징

- FastAPI 기반으로 자동 문서화 지원
- Pydantic을 사용한 데이터 검증
- 인메모리 저장소 (재시작 시 데이터 초기화)
- 이메일 중복 체크
- UUID 기반 사용자 ID 생성