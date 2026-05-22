from __future__ import annotations

from pydantic import BaseModel


class WorkspaceInfo(BaseModel):
    id: str
    name: str
    environment: str
    provider: str


class Persona(BaseModel):
    id: str
    display_name: str
    department_ids: list[str]
    role: str


DEMO_WORKSPACE = WorkspaceInfo(
    id="acme",
    name="ACME Enterprise",
    environment="local-demo",
    provider="fake",
)

DEMO_PERSONAS = [
    Persona(id="mina-security", display_name="Mina Kim", department_ids=["security"], role="employee"),
    Persona(id="joon-finance", display_name="Joon Park", department_ids=["finance"], role="employee"),
    Persona(id="hana-people", display_name="Hana Lee", department_ids=["people"], role="employee"),
    Persona(id="admin-platform", display_name="Admin Choi", department_ids=["platform"], role="admin"),
]
