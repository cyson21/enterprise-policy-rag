# Goal

프로젝트 전체 소스 코드에 한국어 주석을 보강하고, 검증 후 커밋과 원격 push까지 완료한다.

## Current Starting Point

- 실제 Git 레포는 `/Users/chanyang.son/Documents/side-projects/repos/enterprise-policy-rag`이다.
- 시작 시점 브랜치는 `main`이었고, 보호 브랜치 직접 커밋을 피하기 위해 `docs/comments/korean-code-comments`로 분기했다.
- 시작 전부터 `.ai-runs/templates/goal.md`, `.ai-runs/templates/verification.md`에 미커밋 변경이 있었다.

## Scope

In scope:

- `app/`, `web/`, `scripts/`, `tests/`, `infra/`, 루트 설정 파일 중 사람이 관리하는 소스 코드에 한국어 주석을 추가한다.
- 생성물, 의존성 디렉터리, 이미지, lockfile은 직접 수정하지 않는다.
- 실행 원장에 변경, 결정, 검증을 남긴다.

Out of scope:

- 기능 동작 변경.
- 외부 패키지 설치.
- OpenAI live smoke, Docker/Colima 기반 PostgreSQL 통합 테스트.

## Exit Criteria

- 주요 소스 파일에 의도를 설명하는 한국어 주석이 추가된다.
- 정적/테스트 검증 명령을 실행하고 결과를 기록한다.
- 의도한 파일만 커밋하고 원격 브랜치로 push한다.
