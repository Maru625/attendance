# Kada Commute System (카다 출퇴근 시스템)

구글 스프레드시트 기반의 출퇴근 관리 시스템입니다.

## 설정 (Setup)

### 1. 필수 도구 설치

이 프로젝트는 **`uv`** 패키지 매니저를 사용합니다. `uv`는 Python 환경과 의존성을 매우 빠르게 관리해줍니다.

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -lsSf https://astral.sh/uv/install.sh | sh
```

### 2. 프로젝트 설정 및 의존성 설치
`pyproject.toml` 파일에 정의된 모든 의존성을 한 번에 설치하고 가상환경을 동기화하려면 아래 명령어를 실행하세요.

```bash
# 프로젝트의 모든 의존성(gspread, google-auth 등)을 한번에 설치 및 동기화
uv sync
```

### 3. 구글 스프레드시트 설정
서비스 계정 키 파일을 프로젝트 루트에 `kada-admin.json` 이름으로 위치시키세요.
*참고: 이 파일은 보안상 git에 포함되지 않습니다.*

## Git 설정 (Git Setup)
원격 저장소와 연동하는 방법입니다:

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit"

# 브랜치명 변경
git branch -M main

# 원격 저장소 추가
git remote add origin https://github.com/Maru625/attendance.git

# 푸시 (충돌 시 먼저 pull 필요)
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 사용법 (Usage)

## 프로젝트 구조 (Project Structure)
```
root/
├── app/
│   ├── main.py              # FastAPI 서버 진입점
│   ├── models.py            # 데이터 모델 (Request/Response)
│   ├── services/
│   │   └── sheet_service.py # 구글 스프레드시트 연동 로직
│   └── static/              # 웹 프론트엔드 (HTML/CSS/JS)
├── legacy_cli.py            # (구) CLI 실행 파일
├── kada-admin.json          # 구글 서비스 계정 키 (비공개)
└── pyproject.toml           # 프로젝트 의존성 관리
```

## 사용법 (Usage)

### 1. 웹 애플리케이션 실행 (권장)
새로운 웹 인터페이스를 통해 출퇴근을 기록하고, 기록을 수정/삭제할 수 있습니다.

```bash
# 서버 실행
uv run python -m app.main
```
또는 개발 모드 (자동 재시작):
```bash
uv run uvicorn app.main:app --reload
```

서버가 실행되면 브라우저에서 아래 주소로 접속하세요:
👉 **[http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)**

### 2. CLI 실행 (레거시)
기존의 터미널 기반 인터페이스입니다.
```bash
uv run legacy_cli.py
```

## 주요 기능
- **출/퇴근 기록**: 현재 시간 또는 직접 입력한 시간으로 기록.
- **기록 관리 (웹 전용)**:
    - **히스토리 조회**: 전체 출퇴근 기록 확인.
    - **수정**: 연필 아이콘을 눌러 시간 수정.
    - **삭제**: 휴지통 아이콘을 눌러 잘못된 기록 삭제.
- **실시간 로그**: 웹 UI 하단 콘솔에서 서버 로그 확인 가능.
