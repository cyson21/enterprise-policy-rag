from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from app.auth import AuthContextError, SessionSearchQuery, build_auth_context_provider_from_env
from app.demo_data import seed_demo_state
from app.evaluation import list_eval_runs, run_eval
from app.models import AnswerQuery, DocumentCreate, DocumentUpdate, EvalRunRequest, RetrievalQuery
from app.personas import DEMO_PERSONAS, DEMO_WORKSPACE
from app.runtime import build_services_from_env


def create_app(seed_demo: bool = True, require_auth: bool | None = None) -> Any:
    # 앱 시작 시점에 서비스/인증 공급자를 먼저 생성해 라우트와 fallback 경로에 동일한 제어권한 모델을 적용한다.
    services = build_services_from_env()
    auth_provider = build_auth_context_provider_from_env()
    # require_auth가 명시되지 않으면 인증 모드에 따라 자동 결정한다.
    # demo 모드(공개 데모/로컬/테스트)는 현행 동작을 유지하고,
    # trusted_headers/oidc 등 실제 인증 모드에서는 비공개 엔드포인트에 인증·스코프를 강제한다.
    effective_require_auth = _resolve_require_auth(os.environ) if require_auth is None else require_auth
    if seed_demo:
        seed_demo_state(services)
    try:
        from fastapi import FastAPI, HTTPException, Request

        app = FastAPI(title="Enterprise Policy RAG", version="0.1.0")
        _configure_cors(app, os.environ)

        def guard_workspace(headers: Any, requested_workspace_id: str | None) -> str | None:
            # 비공개 read 엔드포인트의 workspace 스코프를 인증 세션 기준으로 강제한다.
            try:
                return _scoped_workspace(
                    require_auth=effective_require_auth,
                    auth_provider=auth_provider,
                    headers=headers,
                    requested_workspace_id=requested_workspace_id,
                )
            except AuthContextError as exc:
                raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

        def guard_search_query(headers: Any, payload: RetrievalQuery) -> RetrievalQuery:
            # /retrieve·/answer가 본문의 권한 컨텍스트를 신뢰하지 않도록 세션 컨텍스트로 치환한다.
            try:
                return _scoped_search_query(
                    require_auth=effective_require_auth,
                    auth_provider=auth_provider,
                    headers=headers,
                    payload=payload,
                )
            except AuthContextError as exc:
                raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

        @app.get("/health")
        def health() -> dict[str, str]:
            return {"status": "ok"}

        @app.get("/workspaces/current")
        def current_workspace() -> dict[str, Any]:
            return DEMO_WORKSPACE.model_dump(mode="json")

        @app.get("/personas")
        def personas() -> dict[str, Any]:
            return {"personas": [persona.model_dump(mode="json") for persona in DEMO_PERSONAS]}

        @app.get("/auth/session")
        def auth_session(request: Request) -> dict[str, Any]:
            try:
                return _current_auth_session(auth_provider, request.headers).model_dump(mode="json")
            except AuthContextError as exc:
                raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

        @app.post("/documents", status_code=201)
        def ingest_document(payload: DocumentCreate, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, payload.workspace_id)
            if scoped is not None and scoped != payload.workspace_id:
                payload = payload.model_copy(update={"workspace_id": scoped})
            try:
                return services.ingest_document(payload).model_dump(mode="json")
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

        @app.get("/documents")
        def list_documents(workspace_id: str, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, workspace_id)
            return services.list_documents(scoped).model_dump(mode="json")

        @app.get("/documents/{document_id}")
        def get_document_detail(document_id: str, workspace_id: str, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, workspace_id)
            result = services.get_document_detail(workspace_id=scoped, document_id=document_id)
            if result is None:
                raise HTTPException(status_code=404, detail="document not found")
            return result.model_dump(mode="json")

        @app.patch("/admin/documents/{document_id}")
        def admin_update_document(document_id: str, payload: DocumentUpdate, request: Request) -> dict[str, Any]:
            try:
                session = _require_admin_session(auth_provider, request.headers)
            except AuthContextError as exc:
                raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
            result = services.update_document(
                workspace_id=session.workspace_id,
                document_id=document_id,
                payload=payload,
                actor_user_id=session.user_id,
            )
            if result is None:
                raise HTTPException(status_code=404, detail="document not found")
            return result.model_dump(mode="json")

        @app.delete("/admin/documents/{document_id}")
        def admin_delete_document(document_id: str, request: Request) -> dict[str, Any]:
            try:
                session = _require_admin_session(auth_provider, request.headers)
            except AuthContextError as exc:
                raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
            result = services.delete_document(
                workspace_id=session.workspace_id,
                document_id=document_id,
                actor_user_id=session.user_id,
            )
            if result is None:
                raise HTTPException(status_code=404, detail="document not found")
            return result.model_dump(mode="json")

        @app.get("/admin/audit-logs")
        def admin_audit_logs(request: Request) -> dict[str, Any]:
            try:
                session = _require_admin_session(auth_provider, request.headers)
            except AuthContextError as exc:
                raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
            return services.list_admin_audit_logs(session.workspace_id).model_dump(mode="json")

        @app.get("/metrics/summary")
        def metrics_summary(workspace_id: str, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, workspace_id)
            return services.get_metrics_summary(scoped).model_dump(mode="json")

        @app.get("/metrics/trend")
        def metrics_trend(workspace_id: str, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, workspace_id)
            return services.get_query_trend(scoped).model_dump(mode="json")

        @app.get("/queries/recent")
        def recent_queries(workspace_id: str, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, workspace_id)
            return services.list_recent_queries(scoped).model_dump(mode="json")

        @app.get("/queries/{query_id}")
        def query_detail(query_id: str, workspace_id: str, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, workspace_id)
            result = services.get_query_detail(workspace_id=scoped, query_id=query_id)
            if result is None:
                raise HTTPException(status_code=404, detail="query not found")
            return result.model_dump(mode="json")

        @app.get("/evidence/top")
        def top_evidence(workspace_id: str, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, workspace_id)
            return services.list_top_evidence(scoped).model_dump(mode="json")

        @app.post("/eval-runs")
        def create_eval_run(payload: EvalRunRequest, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, payload.workspace_id)
            if scoped is not None and scoped != payload.workspace_id:
                payload = payload.model_copy(update={"workspace_id": scoped})
            return run_eval(services, payload).model_dump(mode="json")

        @app.get("/eval-runs")
        def eval_runs(workspace_id: str, request: Request) -> dict[str, Any]:
            scoped = guard_workspace(request.headers, workspace_id)
            return list_eval_runs(services, scoped).model_dump(mode="json")

        @app.post("/retrieve")
        def retrieve(payload: RetrievalQuery, request: Request) -> dict[str, Any]:
            scoped = guard_search_query(request.headers, payload)
            return services.retrieve(scoped).model_dump(mode="json")

        @app.post("/answer")
        def answer(payload: AnswerQuery, request: Request) -> dict[str, Any]:
            scoped = guard_search_query(request.headers, payload)
            return services.answer(scoped).model_dump(mode="json")

        @app.post("/auth/retrieve")
        def auth_retrieve(payload: SessionSearchQuery, request: Request) -> dict[str, Any]:
            try:
                session = _current_auth_session(auth_provider, request.headers)
            except AuthContextError as exc:
                raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
            return services.retrieve(_retrieval_query_from_session(session, payload)).model_dump(mode="json")

        @app.post("/auth/answer")
        def auth_answer(payload: SessionSearchQuery, request: Request) -> dict[str, Any]:
            try:
                session = _current_auth_session(auth_provider, request.headers)
            except AuthContextError as exc:
                raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
            return services.answer(_answer_query_from_session(session, payload)).model_dump(mode="json")

        return app
    # FastAPI 미설치 환경에서는 Starlette만으로도 기본 API 호환 엔드포인트를 제공한다.
    except ModuleNotFoundError as exc:
        if exc.name != "fastapi":
            raise
        return _create_starlette_fallback(services, auth_provider, effective_require_auth)


def _create_starlette_fallback(services: Any, auth_provider: Any, require_auth: bool) -> Any:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    def scoped_workspace_or_error(headers: Any, requested_workspace_id: str | None) -> Any:
        # 스코프 검증 실패를 JSONResponse로 변환해 fallback 경로에서도 동일한 오류 형식을 유지한다.
        try:
            return _scoped_workspace(
                require_auth=require_auth,
                auth_provider=auth_provider,
                headers=headers,
                requested_workspace_id=requested_workspace_id,
            ), None
        except AuthContextError as exc:
            return None, JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    async def health(_request: Any) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    async def current_workspace(_request: Any) -> JSONResponse:
        return JSONResponse(DEMO_WORKSPACE.model_dump(mode="json"))

    async def personas(_request: Any) -> JSONResponse:
        return JSONResponse({"personas": [persona.model_dump(mode="json") for persona in DEMO_PERSONAS]})

    async def auth_session(request: Any) -> JSONResponse:
        try:
            session = _current_auth_session(auth_provider, request.headers)
        except AuthContextError as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        return JSONResponse(session.model_dump(mode="json"))

    async def ingest_document(request: Any) -> JSONResponse:
        try:
            payload = DocumentCreate.model_validate(await request.json())
        except (ValidationError, ValueError) as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, payload.workspace_id)
        if error is not None:
            return error
        if scoped is not None and scoped != payload.workspace_id:
            payload = payload.model_copy(update={"workspace_id": scoped})
        try:
            result = services.ingest_document(payload)
        except (ValidationError, ValueError) as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        return JSONResponse(result.model_dump(mode="json"), status_code=201)

    async def list_documents(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, workspace_id)
        if error is not None:
            return error
        result = services.list_documents(scoped)
        return JSONResponse(result.model_dump(mode="json"))

    async def get_document_detail(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, workspace_id)
        if error is not None:
            return error
        result = services.get_document_detail(
            workspace_id=scoped,
            document_id=request.path_params["document_id"],
        )
        if result is None:
            return JSONResponse({"detail": "document not found"}, status_code=404)
        return JSONResponse(result.model_dump(mode="json"))

    async def admin_update_document(request: Any) -> JSONResponse:
        try:
            session = _require_admin_session(auth_provider, request.headers)
            payload = DocumentUpdate.model_validate(await request.json())
            result = services.update_document(
                workspace_id=session.workspace_id,
                document_id=request.path_params["document_id"],
                payload=payload,
                actor_user_id=session.user_id,
            )
        except AuthContextError as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        if result is None:
            return JSONResponse({"detail": "document not found"}, status_code=404)
        return JSONResponse(result.model_dump(mode="json"))

    async def admin_delete_document(request: Any) -> JSONResponse:
        try:
            session = _require_admin_session(auth_provider, request.headers)
            result = services.delete_document(
                workspace_id=session.workspace_id,
                document_id=request.path_params["document_id"],
                actor_user_id=session.user_id,
            )
        except AuthContextError as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        if result is None:
            return JSONResponse({"detail": "document not found"}, status_code=404)
        return JSONResponse(result.model_dump(mode="json"))

    async def admin_audit_logs(request: Any) -> JSONResponse:
        try:
            session = _require_admin_session(auth_provider, request.headers)
        except AuthContextError as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        return JSONResponse(services.list_admin_audit_logs(session.workspace_id).model_dump(mode="json"))

    async def metrics_summary(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, workspace_id)
        if error is not None:
            return error
        return JSONResponse(services.get_metrics_summary(scoped).model_dump(mode="json"))

    async def metrics_trend(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, workspace_id)
        if error is not None:
            return error
        return JSONResponse(services.get_query_trend(scoped).model_dump(mode="json"))

    async def recent_queries(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, workspace_id)
        if error is not None:
            return error
        return JSONResponse(services.list_recent_queries(scoped).model_dump(mode="json"))

    async def query_detail(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, workspace_id)
        if error is not None:
            return error
        result = services.get_query_detail(
            workspace_id=scoped,
            query_id=request.path_params["query_id"],
        )
        if result is None:
            return JSONResponse({"detail": "query not found"}, status_code=404)
        return JSONResponse(result.model_dump(mode="json"))

    async def top_evidence(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, workspace_id)
        if error is not None:
            return error
        return JSONResponse(services.list_top_evidence(scoped).model_dump(mode="json"))

    async def create_eval_run(request: Any) -> JSONResponse:
        try:
            payload = EvalRunRequest.model_validate(await request.json())
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, payload.workspace_id)
        if error is not None:
            return error
        if scoped is not None and scoped != payload.workspace_id:
            payload = payload.model_copy(update={"workspace_id": scoped})
        return JSONResponse(run_eval(services, payload).model_dump(mode="json"))

    async def eval_runs(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        scoped, error = scoped_workspace_or_error(request.headers, workspace_id)
        if error is not None:
            return error
        return JSONResponse(list_eval_runs(services, scoped).model_dump(mode="json"))

    async def retrieve(request: Any) -> JSONResponse:
        try:
            payload = RetrievalQuery.model_validate(await request.json())
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        try:
            scoped = _scoped_search_query(
                require_auth=require_auth,
                auth_provider=auth_provider,
                headers=request.headers,
                payload=payload,
            )
        except AuthContextError as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        return JSONResponse(services.retrieve(scoped).model_dump(mode="json"))

    async def answer(request: Any) -> JSONResponse:
        try:
            payload = AnswerQuery.model_validate(await request.json())
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        try:
            scoped = _scoped_search_query(
                require_auth=require_auth,
                auth_provider=auth_provider,
                headers=request.headers,
                payload=payload,
            )
        except AuthContextError as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        return JSONResponse(services.answer(scoped).model_dump(mode="json"))

    async def auth_retrieve(request: Any) -> JSONResponse:
        try:
            session = _current_auth_session(auth_provider, request.headers)
            payload = SessionSearchQuery.model_validate(await request.json())
            result = services.retrieve(_retrieval_query_from_session(session, payload))
        except AuthContextError as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        return JSONResponse(result.model_dump(mode="json"))

    async def auth_answer(request: Any) -> JSONResponse:
        try:
            session = _current_auth_session(auth_provider, request.headers)
            payload = SessionSearchQuery.model_validate(await request.json())
            result = services.answer(_answer_query_from_session(session, payload))
        except AuthContextError as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        return JSONResponse(result.model_dump(mode="json"))

    return Starlette(
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/workspaces/current", current_workspace, methods=["GET"]),
            Route("/personas", personas, methods=["GET"]),
            Route("/auth/session", auth_session, methods=["GET"]),
            Route("/documents", ingest_document, methods=["POST"]),
            Route("/documents", list_documents, methods=["GET"]),
            Route("/documents/{document_id}", get_document_detail, methods=["GET"]),
            Route("/admin/documents/{document_id}", admin_update_document, methods=["PATCH"]),
            Route("/admin/documents/{document_id}", admin_delete_document, methods=["DELETE"]),
            Route("/admin/audit-logs", admin_audit_logs, methods=["GET"]),
            Route("/metrics/summary", metrics_summary, methods=["GET"]),
            Route("/metrics/trend", metrics_trend, methods=["GET"]),
            Route("/queries/recent", recent_queries, methods=["GET"]),
            Route("/queries/{query_id}", query_detail, methods=["GET"]),
            Route("/evidence/top", top_evidence, methods=["GET"]),
            Route("/eval-runs", create_eval_run, methods=["POST"]),
            Route("/eval-runs", eval_runs, methods=["GET"]),
            Route("/retrieve", retrieve, methods=["POST"]),
            Route("/answer", answer, methods=["POST"]),
            Route("/auth/retrieve", auth_retrieve, methods=["POST"]),
            Route("/auth/answer", auth_answer, methods=["POST"]),
        ]
    )


def _resolve_require_auth(environ: Mapping[str, str]) -> bool:
    # RAG_REQUIRE_AUTH가 명시되면 우선하고, 없으면 인증 모드로 추론한다.
    raw = environ.get("RAG_REQUIRE_AUTH")
    if raw is not None and raw.strip() != "":
        require_auth = raw.strip().lower() in {"1", "true", "yes", "on"}
        if not require_auth:
            logging.warning("RAG auth is not enforced; demo mode trusts request permission context")
        return require_auth
    mode = environ.get("AUTH_CONTEXT_PROVIDER", "demo").strip().lower()
    require_auth = mode not in {"", "demo"}
    if not require_auth:
        logging.warning("RAG auth is not enforced; demo mode trusts request permission context")
    return require_auth


def _configure_cors(app: Any, environ: Mapping[str, str]) -> None:
    # 별도 origin의 웹 콘솔이 API를 호출하는 운영 배포를 위해 허용 origin이 설정된 경우에만 CORS를 켠다.
    raw = environ.get("RAG_CORS_ALLOW_ORIGINS", "").strip()
    if not raw:
        return
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    if not origins:
        return
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _scoped_workspace(
    *,
    require_auth: bool,
    auth_provider: Any,
    headers: Any,
    requested_workspace_id: str | None,
) -> str | None:
    # 인증 비강제 모드에서는 요청값을 그대로 신뢰(데모/테스트), 강제 모드에서는 세션 workspace로 스코프를 고정한다.
    if not require_auth:
        return requested_workspace_id
    session = auth_provider.current_session(headers)
    if requested_workspace_id and requested_workspace_id != session.workspace_id:
        raise AuthContextError(status_code=403, detail="workspace scope mismatch")
    return session.workspace_id


def _scoped_search_query(
    *,
    require_auth: bool,
    auth_provider: Any,
    headers: Any,
    payload: RetrievalQuery,
) -> RetrievalQuery:
    # 인증 강제 모드에서는 본문의 workspace/user/department 권한 컨텍스트를 무시하고 세션 값으로 치환한다.
    if not require_auth:
        return payload
    session = auth_provider.current_session(headers)
    if payload.workspace_id and payload.workspace_id != session.workspace_id:
        raise AuthContextError(status_code=403, detail="workspace scope mismatch")
    return type(payload)(
        workspace_id=session.workspace_id,
        user_id=session.user_id,
        department_ids=session.department_ids,
        query=payload.query,
        top_k=payload.top_k,
        score_threshold=payload.score_threshold,
    )


def _current_auth_session(auth_provider: Any, headers: Any) -> Any:
    """요청 헤더에서 현재 사용자의 인증 세션을 해석해 컨텍스트 바인딩에 사용한다."""
    return auth_provider.current_session(headers)


def _require_admin_session(auth_provider: Any, headers: Any) -> Any:
    """관리 API는 role=admin 조건을 강제해 권한 경계를 중앙에서 선별한다."""
    session = _current_auth_session(auth_provider, headers)
    if session.role != "admin":
        raise AuthContextError(status_code=403, detail="admin role required")
    return session


def _retrieval_query_from_session(session: Any, payload: SessionSearchQuery) -> RetrievalQuery:
    # 관리자/사용자별 질의 필터와 공용 검색 파라미터를 하나의 세션 기반 조회 모델로 정규화한다.
    return RetrievalQuery(
        workspace_id=session.workspace_id,
        user_id=session.user_id,
        department_ids=session.department_ids,
        query=payload.query,
        top_k=payload.top_k,
        score_threshold=payload.score_threshold,
    )


def _answer_query_from_session(session: Any, payload: SessionSearchQuery) -> AnswerQuery:
    # 조회 질의 모델을 답변 질의 모델로 확장해 답변 파이프라인에서 동일한 인증 컨텍스트를 재사용한다.
    return AnswerQuery(**_retrieval_query_from_session(session, payload).model_dump())


app = create_app()
