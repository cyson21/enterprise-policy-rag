# Agent Plan

## Plan

1. 소스 파일 범위를 파악하고 backend, frontend, scripts/tests/infra로 나눈다.
2. Spark xhigh 서브에이전트에 분리된 파일 책임 범위를 맡긴다.
3. 서브에이전트 결과를 통합하면서 주석이 동작을 바꾸지 않았는지 diff를 검토한다.
4. 프로젝트 표준 검증 명령을 실행한다.
5. 변경 파일을 기록하고 커밋 후 원격 브랜치로 push한다.

## Delegation

- Backend worker: `app/**/*.py`
- Frontend worker: `web/src/**/*`, `web/*.ts`, `web/*.json` 중 소스성 파일
- Support worker: `scripts/**/*`, `tests/**/*`, `infra/**/*`, 루트 설정 중 주석 가능한 소스성 파일

## Guardrails

- 기능 로직을 바꾸지 않는다.
- 생성물과 의존성 산출물은 수정하지 않는다.
- 다른 에이전트나 기존 사용자 변경을 되돌리지 않는다.
- 주석에는 금지된 용어를 쓰지 않는다.
