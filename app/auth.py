from __future__ import annotations

import os
from typing import Any, Mapping, Protocol

from pydantic import BaseModel, Field

from app.personas import DEMO_PERSONAS, DEMO_WORKSPACE


class AuthContextError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class AuthSession(BaseModel):
    workspace_id: str
    user_id: str
    display_name: str
    department_ids: list[str]
    role: str
    auth_mode: str
    source: str


class SessionSearchQuery(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0, ge=0, le=1)


class AuthContextProvider(Protocol):
    def current_session(self, headers: Mapping[str, str]) -> AuthSession:
        """Resolve the authenticated user and permission context for a request."""


class DemoAuthContextProvider:
    def current_session(self, _headers: Mapping[str, str]) -> AuthSession:
        persona = DEMO_PERSONAS[0]
        return AuthSession(
            workspace_id=DEMO_WORKSPACE.id,
            user_id=persona.id,
            display_name=persona.display_name,
            department_ids=persona.department_ids,
            role=persona.role,
            auth_mode="demo",
            source="demo_persona",
        )


class TrustedHeaderAuthContextProvider:
    def current_session(self, headers: Mapping[str, str]) -> AuthSession:
        workspace_id = _header_value(headers, "x-enterprise-workspace-id")
        user_id = _header_value(headers, "x-enterprise-user-id")
        display_name = _header_value(headers, "x-enterprise-display-name")
        department_ids = _header_value(headers, "x-enterprise-department-ids")
        role = _header_value(headers, "x-enterprise-role")

        if not all([workspace_id, user_id, display_name, department_ids, role]):
            raise AuthContextError(status_code=401, detail="missing trusted identity headers")

        normalized_role = role.strip().lower()
        if normalized_role not in {"employee", "admin"}:
            raise AuthContextError(status_code=401, detail="invalid trusted identity role")

        return AuthSession(
            workspace_id=workspace_id.strip(),
            user_id=user_id.strip(),
            display_name=display_name.strip(),
            department_ids=_normalize_departments(department_ids.split(",")),
            role=normalized_role,
            auth_mode="trusted_headers",
            source="trusted_headers",
        )


class OIDCJWTAuthContextProvider:
    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        hs256_secret: str | None = None,
        jwks_url: str | None = None,
        algorithms: list[str] | None = None,
        workspace_claim: str = "workspace_id",
        user_claim: str = "sub",
        display_name_claim: str = "name",
        department_ids_claim: str = "department_ids",
        role_claim: str = "role",
    ) -> None:
        if not issuer:
            raise RuntimeError("OIDC_ISSUER is required for oidc_jwt auth")
        if not audience:
            raise RuntimeError("OIDC_AUDIENCE is required for oidc_jwt auth")
        if not hs256_secret and not jwks_url:
            raise RuntimeError("OIDC_HS256_SECRET or OIDC_JWKS_URL is required for oidc_jwt auth")

        self.issuer = issuer
        self.audience = audience
        self.hs256_secret = hs256_secret
        self.jwks_url = jwks_url
        self.algorithms = algorithms or (["RS256"] if jwks_url else ["HS256"])
        self.workspace_claim = workspace_claim
        self.user_claim = user_claim
        self.display_name_claim = display_name_claim
        self.department_ids_claim = department_ids_claim
        self.role_claim = role_claim

    @classmethod
    def from_env(cls) -> "OIDCJWTAuthContextProvider":
        algorithms = _csv_env("OIDC_JWT_ALGORITHMS")
        return cls(
            issuer=os.getenv("OIDC_ISSUER", "").strip(),
            audience=os.getenv("OIDC_AUDIENCE", "").strip(),
            hs256_secret=os.getenv("OIDC_HS256_SECRET") or None,
            jwks_url=os.getenv("OIDC_JWKS_URL") or None,
            algorithms=algorithms or None,
            workspace_claim=os.getenv("OIDC_WORKSPACE_CLAIM", "workspace_id").strip(),
            user_claim=os.getenv("OIDC_USER_CLAIM", "sub").strip(),
            display_name_claim=os.getenv("OIDC_DISPLAY_NAME_CLAIM", "name").strip(),
            department_ids_claim=os.getenv("OIDC_DEPARTMENT_IDS_CLAIM", "department_ids").strip(),
            role_claim=os.getenv("OIDC_ROLE_CLAIM", "role").strip(),
        )

    def current_session(self, headers: Mapping[str, str]) -> AuthSession:
        token = _bearer_token(headers)
        claims = self._decode(token)
        workspace_id = _required_claim(claims, self.workspace_claim)
        user_id = _required_claim(claims, self.user_claim)
        display_name = _string_claim(claims.get(self.display_name_claim)) or user_id
        department_ids = _department_claim(claims.get(self.department_ids_claim))
        role = _role_claim(claims.get(self.role_claim))

        if not workspace_id or not user_id or not department_ids:
            raise AuthContextError(status_code=401, detail="missing oidc session claims")

        return AuthSession(
            workspace_id=workspace_id,
            user_id=user_id,
            display_name=display_name,
            department_ids=department_ids,
            role=role,
            auth_mode="oidc_jwt",
            source=self.issuer,
        )

    def _decode(self, token: str) -> dict[str, Any]:
        try:
            import jwt
            from jwt import PyJWKClient
            from jwt.exceptions import PyJWKClientError, PyJWTError
        except ModuleNotFoundError as exc:
            raise RuntimeError("PyJWT is required for oidc_jwt auth") from exc

        try:
            key: Any
            if self.jwks_url:
                key = PyJWKClient(self.jwks_url).get_signing_key_from_jwt(token).key
            else:
                key = self.hs256_secret
            return jwt.decode(
                token,
                key=key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer,
            )
        except (PyJWTError, PyJWKClientError) as exc:
            raise AuthContextError(status_code=401, detail="invalid oidc token") from exc


def build_auth_context_provider_from_env() -> AuthContextProvider:
    mode = os.getenv("AUTH_CONTEXT_PROVIDER", "demo").strip().lower()
    if mode in {"", "demo"}:
        return DemoAuthContextProvider()
    if mode in {"trusted_headers", "headers"}:
        return TrustedHeaderAuthContextProvider()
    if mode in {"oidc", "oidc_jwt"}:
        return OIDCJWTAuthContextProvider.from_env()
    raise RuntimeError(f"unsupported AUTH_CONTEXT_PROVIDER: {mode}")


def _header_value(headers: Mapping[str, str], key: str) -> str:
    value = headers.get(key)
    if value is not None:
        return value
    value = headers.get(key.lower())
    if value is not None:
        return value
    for header_key, header_value in headers.items():
        if header_key.lower() == key.lower():
            return header_value
    return ""


def _normalize_departments(value: list[str]) -> list[str]:
    return sorted({item.strip() for item in value if item.strip()})


def _csv_env(key: str) -> list[str]:
    return _normalize_departments(os.getenv(key, "").split(","))


def _bearer_token(headers: Mapping[str, str]) -> str:
    value = _header_value(headers, "authorization")
    prefix = "bearer "
    if not value.lower().startswith(prefix):
        raise AuthContextError(status_code=401, detail="missing bearer token")
    token = value[len(prefix) :].strip()
    if not token:
        raise AuthContextError(status_code=401, detail="missing bearer token")
    return token


def _required_claim(claims: Mapping[str, Any], name: str) -> str:
    value = _string_claim(claims.get(name))
    if not value:
        raise AuthContextError(status_code=401, detail="missing oidc session claims")
    return value


def _string_claim(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _department_claim(value: Any) -> list[str]:
    if isinstance(value, str):
        return _normalize_departments(value.split(","))
    if isinstance(value, list):
        return _normalize_departments([item for item in value if isinstance(item, str)])
    return []


def _role_claim(value: Any) -> str:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"employee", "admin"}:
            return normalized
    if isinstance(value, list):
        normalized_values = {item.strip().lower() for item in value if isinstance(item, str)}
        if "admin" in normalized_values:
            return "admin"
        if "employee" in normalized_values:
            return "employee"
    raise AuthContextError(status_code=401, detail="invalid oidc role")
