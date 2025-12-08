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

애플리케이션 실행:
```bash
uv run main.py
```
