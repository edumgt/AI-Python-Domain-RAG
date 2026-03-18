# 도메인 특화 RAG AI 에이전트

**FastAPI + Qdrant + PostgreSQL + Redis + vLLM** 기반의 도메인 특화 RAG(검색 증강 생성) 서비스입니다.
의학과 고교 영어 두 가지 도메인에 특화된 AI 에이전트로, 바닐라 JS 프론트엔드가 포함된 완성형 구조입니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 🏥 의학 도메인 | 고혈압·당뇨병 등 의학 문서 기반 전문 답변, 안전장치(전문의 상담 권고) 내장 |
| 📖 고교 영어 도메인 | 수능 영어 문법·독해·어휘 문서 기반 학습 지원 답변 |
| 🌐 일반 도메인 | 범용 문서 기반 RAG 응답 |
| 📁 파일 업로드 | TXT / PDF 파일 업로드 후 자동 청킹·임베딩·벡터 저장 |
| ✏️ 텍스트 직접 등록 | API 또는 UI에서 텍스트 직접 등록 |
| 💬 멀티턴 채팅 | 세션 기반 대화 이력 관리 |
| 🔍 벡터 검색 | Qdrant 기반 도메인 필터링 유사도 검색 |
| 📊 로그 저장 | PostgreSQL에 질문·답변·도메인·세션 ID 저장 |
| 🖥️ 웹 UI | 바닐라 JS 기반 SPA 프론트엔드 (별도 빌드 불필요) |

---

## 아키텍처

```
사용자 브라우저 (바닐라 JS)
        │
        ▼
  FastAPI (포트 8000)
  ├── GET  /           → 프론트엔드 SPA 서빙
  ├── POST /chat       → 질문 → 벡터 검색 → LLM 답변
  ├── POST /ingest/text → 텍스트 등록
  ├── POST /ingest/file → 파일 업로드 및 등록
  └── GET  /health     → 상태 확인
        │
   ┌────┴────────────┬────────────┐
   ▼                 ▼            ▼
Qdrant           PostgreSQL     Redis
(벡터 DB)        (채팅 로그)    (캐시/확장)
        │
        ▼
  vLLM / OpenAI 호환 API
  (외부 LLM 서버)
```

---

## 빠른 시작

### 1. 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성하거나 기존 파일을 수정합니다:

```env
VLLM_BASE_URL=http://host.docker.internal:8001/v1
VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct
VLLM_API_KEY=EMPTY
```

> vLLM이 없는 경우 OpenAI 호환 엔드포인트(예: OpenAI API, LM Studio, Ollama)로 대체 가능합니다.

### 2. Docker로 실행

```bash
docker compose up --build
```

- **웹 UI**: http://localhost:8000
- **Swagger API 문서**: http://localhost:8000/docs
- **상태 확인**: http://localhost:8000/health

---

## API 사용 예시

### 상태 확인

```bash
curl http://localhost:8000/health
```

### 텍스트 등록 (의학 도메인)

```bash
curl -X POST http://localhost:8000/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "med-001",
    "title": "고혈압 치료 가이드라인",
    "content": "고혈압의 1차 치료는 생활습관 교정(나트륨 제한, 운동, 금연)부터 시작하며, 조절이 안 되면 ACE 억제제 또는 ARB를 사용한다.",
    "domain": "medical"
  }'
```

### 파일 업로드 (고교 영어 도메인)

```bash
curl -X POST http://localhost:8000/ingest/file \
  -F "file=@./data/samples/english_grammar.txt" \
  -F "domain=english"
```

### 채팅 (의학 도메인)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "고혈압의 1차 치료 원칙은 무엇인가요?",
    "domain": "medical",
    "top_k": 4
  }'
```

### 채팅 (고교 영어 도메인)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the difference between since and for?",
    "domain": "english",
    "top_k": 4
  }'
```

---

## 도메인 지원

| 도메인 | 값 | 시스템 프롬프트 특징 |
|--------|-----|-------------------|
| 의학 | `medical` | 근거 기반 답변, 전문의 상담 권고 안전장치 |
| 고교 영어 | `english` | 학습 친화적 설명, 예문 제공, 한/영 혼용 지원 |
| 일반 | `general` | 범용 RAG 답변 |

---

## 샘플 데이터

`data/samples/` 폴더에 도메인별 샘플 문서가 포함되어 있습니다:

| 파일 | 도메인 | 내용 |
|------|--------|------|
| `medical_hypertension.txt` | 의학 | 고혈압 진료 가이드라인 |
| `medical_diabetes.txt` | 의학 | 당뇨병 진단 및 관리 |
| `english_grammar.txt` | 고교 영어 | 핵심 문법 (시제, 관계대명사, 가정법) |
| `english_reading_writing.txt` | 고교 영어 | 독해·작문·어휘 전략 |

---

## 프로젝트 구조

```
.
├── app/
│   ├── api/routes/         # FastAPI 라우터 (chat, ingest, health)
│   ├── core/               # 설정(config), 데이터베이스(database)
│   ├── models/             # SQLAlchemy 모델 (chat_log)
│   ├── schemas/            # Pydantic 스키마 (chat, ingest, domain)
│   ├── services/           # 핵심 서비스 (RAG, LLM, 벡터DB, 임베딩, 청킹, 파싱)
│   ├── utils/              # 유틸리티 (텍스트 정제)
│   └── main.py             # FastAPI 앱 진입점 + 프론트엔드 서빙
├── frontend/
│   ├── index.html          # SPA 메인 HTML
│   ├── style.css           # 다크 테마 CSS
│   └── app.js              # 바닐라 JS 로직
├── data/
│   ├── samples/            # 도메인별 샘플 문서
│   └── uploads/            # 업로드된 파일 저장 디렉터리
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI: 린트 + 테스트
│       └── cd.yml          # CD: AWS ECR 빌드 + ECS 배포
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## CI/CD (GitHub Actions)

### CI 파이프라인 (`.github/workflows/ci.yml`)

`main` / `develop` 브랜치 push 및 PR 시 자동 실행:

1. Python 3.11 환경 설정
2. 의존성 설치
3. flake8 린트 검사
4. pytest 단위 테스트 실행

### CD 파이프라인 (`.github/workflows/cd.yml`)

`main` 브랜치 push 또는 버전 태그(`v*.*.*`) 시 자동 실행:

1. AWS ECR 로그인
2. Docker 이미지 빌드 및 ECR 푸시
3. ECS 태스크 정의 업데이트
4. ECS 서비스 배포 (롤링 업데이트)

#### 필요한 GitHub Secrets / Variables

| 이름 | 종류 | 설명 |
|------|------|------|
| `AWS_ACCESS_KEY_ID` | Secret | AWS IAM 액세스 키 |
| `AWS_SECRET_ACCESS_KEY` | Secret | AWS IAM 시크릿 키 |
| `AWS_REGION` | Variable | AWS 리전 (기본값: `ap-northeast-2`) |
| `ECR_REPOSITORY` | Variable | ECR 리포지토리 이름 |
| `ECS_CLUSTER` | Variable | ECS 클러스터 이름 |
| `ECS_SERVICE` | Variable | ECS 서비스 이름 |
| `CONTAINER_NAME` | Variable | 컨테이너 이름 |

---

## 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| API 서버 | FastAPI + Uvicorn |
| 프론트엔드 | 바닐라 JS (빌드 불필요) |
| 벡터 DB | Qdrant |
| 관계형 DB | PostgreSQL 16 |
| 캐시 | Redis 7 |
| 임베딩 | sentence-transformers (all-MiniLM-L6-v2) |
| PDF 파싱 | pypdf |
| LLM 연동 | httpx + OpenAI 호환 API (vLLM 등) |
| 컨테이너화 | Docker + Docker Compose |
| CI/CD | GitHub Actions + AWS ECR + ECS |

---

## 확장 포인트

- 🔐 JWT 인증 및 권한 기반 문서 접근 제어
- 🔁 Reranker 모델 추가 (BGE-reranker 등)
- 📈 Prometheus + Grafana 모니터링 연동
- 🌊 SSE(Server-Sent Events) 기반 스트리밍 답변
- 🗃️ 문서 버전 관리 및 삭제 API
- 🤖 멀티에이전트 오케스트레이션 (LangGraph 등)

