# Production Auth and SSO Boundary

작성일: 2026-05-26

## 목표

Enterprise Policy RAG의 검색 권한은 `workspace_id`, `user_id`, `department_ids`, `role`에서 결정된다. 현재 데모는 persona selector가 이 값을 직접 보낸다. production 전환 시에는 클라이언트가 권한 값을 임의로 보내지 않고, 인증된 session context에서 retrieval/answer 입력을 구성해야 한다.

## 1차 범위

- 기본 실행은 계속 `demo` auth context를 사용한다.
- CI와 local verification은 API key, IdP, OAuth client secret 없이 통과해야 한다.
- SSO/OIDC/JWT 검증은 provider boundary 뒤에 둔다.
- production gateway가 검증한 identity claim을 backend auth context로 매핑할 수 있는 구조를 둔다.
- opt-in OIDC JWT provider는 Bearer token의 issuer, audience, signature, expiry를 검증하고 session claim을 매핑한다.

## Auth Context Model

| 필드 | 의미 |
|---|---|
| `workspace_id` | tenant/workspace boundary |
| `user_id` | subject/user identifier |
| `display_name` | UI display hint |
| `department_ids` | retrieval permission filter input |
| `role` | `employee` 또는 `admin` |
| `auth_mode` | `demo`, `trusted_headers`, `oidc_jwt` |
| `source` | context가 어디서 왔는지 표시 |

## Provider Boundary

```text
Client
  -> GET /auth/session
  -> POST /auth/retrieve
  -> POST /auth/answer
      FastAPI route
        -> AuthContextProvider.current_session(headers)
        -> RetrievalQuery / AnswerQuery 구성
        -> 기존 PolicyRagServices
```

### `demo`

- 기본값이다.
- 기존 demo persona 중 `mina-security`를 current session으로 사용한다.
- portfolio static demo와 local test가 credentials 없이 동작한다.

### `trusted_headers`

- future production mode다.
- backend 앞단의 identity-aware proxy 또는 SSO gateway가 사용자를 검증했다고 가정하고, backend는 정해진 header를 auth context로 매핑한다.
- 직접 인터넷에 노출해서 쓰는 모드가 아니다.

필수 header:

```text
x-enterprise-workspace-id
x-enterprise-user-id
x-enterprise-display-name
x-enterprise-department-ids
x-enterprise-role
```

### `oidc_jwt`

- `AUTH_CONTEXT_PROVIDER=oidc_jwt`일 때 활성화한다.
- `Authorization: Bearer <jwt>`에서 token을 읽는다.
- 기본 로컬/CI 검증은 `OIDC_HS256_SECRET`을 사용해 외부 IdP 없이 수행한다.
- 실제 IdP는 `OIDC_JWKS_URL`과 issuer/audience env를 통해 연결한다.
- 기본 claim mapping:

```text
workspace_id       -> workspace_id
sub                -> user_id
name               -> display_name
department_ids     -> department_ids
role               -> role
```

필수 env:

```text
AUTH_CONTEXT_PROVIDER=oidc_jwt
OIDC_ISSUER
OIDC_AUDIENCE
OIDC_HS256_SECRET 또는 OIDC_JWKS_URL
```

## Security Notes

- request body의 `user_id`, `department_ids`를 production 권한 근거로 쓰지 않는다.
- session-bound endpoint는 body에 권한 필드가 들어와도 무시하고 auth context를 우선한다.
- 실제 production에서는 gateway와 backend 사이의 network boundary와 header spoofing 방지 설정이 추가되어야 한다.
- admin workflow는 role check와 audit log를 통해 session context를 사용한다.

## Excluded

- OAuth authorization code flow
- session cookie 발급
- user provisioning
- SCIM/Okta/Google Workspace 동기화
