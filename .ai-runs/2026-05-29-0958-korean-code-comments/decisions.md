# Decisions

- 프로젝트 소개 폴더가 아니라 실제 Git 레포인 `/Users/chanyang.son/Documents/side-projects/repos/enterprise-policy-rag`에서 작업한다.
- `main` 보호 규칙을 지키기 위해 `docs/comments/korean-code-comments` 브랜치를 사용한다.
- 시작 전 존재하던 `.ai-runs/templates/*` 변경은 되돌리지 않는다.
- 주석 추가 작업은 기능 변경이 아니므로 한국어 설명 주석만 추가하고 로직, API, UI 문구는 변경하지 않는다.
- JSON 파일은 주석 문법이 없어 변경하지 않는다.
- 일반 web build와 static web build는 같은 `web/dist`를 사용하므로 최종 검증에서는 순차 실행한다.
- 최종 리뷰에서 지적된 Python 모듈 설명 문자열 위치는 정식 모듈 docstring 위치로 정리한다.
