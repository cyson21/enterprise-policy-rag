from __future__ import annotations

import os
from typing import Mapping, Protocol

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


def build_auth_context_provider_from_env() -> AuthContextProvider:
    mode = os.getenv("AUTH_CONTEXT_PROVIDER", "demo").strip().lower()
    if mode in {"", "demo"}:
        return DemoAuthContextProvider()
    if mode in {"trusted_headers", "headers"}:
        return TrustedHeaderAuthContextProvider()
    raise RuntimeError(f"unsupported AUTH_CONTEXT_PROVIDER: {mode}")


def _header_value(headers: Mapping[str, str], key: str) -> str:
    value = headers.get(key)
    if value is not None:
        return value
    return headers.get(key.lower(), "")


def _normalize_departments(value: list[str]) -> list[str]:
    return sorted({item.strip() for item in value if item.strip()})
