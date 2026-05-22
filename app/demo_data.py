from __future__ import annotations

from app.models import DocumentCreate, Visibility
from app.operations import seed_demo_query_logs
from app.services import PolicyRagServices


DEMO_DOCUMENTS = [
    DocumentCreate(
        workspace_id="acme",
        title="Remote Access Policy",
        source_uri="policy://remote-access",
        content=(
            "VPN 등록 절차는 사내 포털에서 기기 등록을 완료한 뒤 보안 승인을 요청합니다.\n\n"
            "Remote access requires VPN enrollment before connecting to internal tools."
        ),
        content_type="text/markdown",
        owner_user_id="admin-platform",
        department_ids=["platform", "security"],
        visibility=Visibility.PUBLIC,
    ),
    DocumentCreate(
        workspace_id="acme",
        title="Security Incident Manual",
        source_uri="policy://security-incident",
        content=(
            "보안 사고 발생 시 즉시 Security on-call 채널에 알리고 incident commander를 지정합니다.\n\n"
            "Security incident evidence must be preserved before remediation work starts."
        ),
        content_type="text/markdown",
        owner_user_id="mina-security",
        department_ids=["security"],
        visibility=Visibility.DEPARTMENT,
    ),
    DocumentCreate(
        workspace_id="acme",
        title="Finance Reimbursement Policy",
        source_uri="policy://finance-reimbursement",
        content=(
            "식대 정산 기준은 영수증 제출과 프로젝트 코드 입력을 포함합니다.\n\n"
            "Finance reimbursement requests are reviewed by the finance operations team."
        ),
        content_type="text/markdown",
        owner_user_id="joon-finance",
        department_ids=["finance"],
        visibility=Visibility.DEPARTMENT,
    ),
    DocumentCreate(
        workspace_id="acme",
        title="Executive Access Exception",
        source_uri="policy://executive-access",
        content=(
            "임원 접근 예외 절차는 platform admin owner 승인이 있어야 진행됩니다.\n\n"
            "Executive access exceptions are private until approval is complete."
        ),
        content_type="text/markdown",
        owner_user_id="admin-platform",
        department_ids=["platform"],
        visibility=Visibility.PRIVATE,
    ),
]


def seed_demo_documents(services: PolicyRagServices) -> None:
    for document in DEMO_DOCUMENTS:
        services.ingest_document(document)


def seed_demo_state(services: PolicyRagServices) -> None:
    seed_demo_documents(services)
    seed_demo_query_logs(services)
