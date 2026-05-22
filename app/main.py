from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.demo_data import seed_demo_state
from app.evaluation import list_eval_runs, run_eval
from app.models import AnswerQuery, DocumentCreate, EvalRunRequest, RetrievalQuery
from app.personas import DEMO_PERSONAS, DEMO_WORKSPACE
from app.runtime import build_services_from_env


def create_app(seed_demo: bool = True) -> Any:
    services = build_services_from_env()
    if seed_demo:
        seed_demo_state(services)
    try:
        from fastapi import FastAPI, HTTPException

        app = FastAPI(title="Enterprise Policy RAG", version="0.1.0")

        @app.get("/health")
        def health() -> dict[str, str]:
            return {"status": "ok"}

        @app.get("/workspaces/current")
        def current_workspace() -> dict[str, Any]:
            return DEMO_WORKSPACE.model_dump(mode="json")

        @app.get("/personas")
        def personas() -> dict[str, Any]:
            return {"personas": [persona.model_dump(mode="json") for persona in DEMO_PERSONAS]}

        @app.post("/documents", status_code=201)
        def ingest_document(payload: DocumentCreate) -> dict[str, Any]:
            try:
                return services.ingest_document(payload).model_dump(mode="json")
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

        @app.get("/documents")
        def list_documents(workspace_id: str) -> dict[str, Any]:
            return services.list_documents(workspace_id).model_dump(mode="json")

        @app.get("/documents/{document_id}")
        def get_document_detail(document_id: str, workspace_id: str) -> dict[str, Any]:
            result = services.get_document_detail(workspace_id=workspace_id, document_id=document_id)
            if result is None:
                raise HTTPException(status_code=404, detail="document not found")
            return result.model_dump(mode="json")

        @app.get("/metrics/summary")
        def metrics_summary(workspace_id: str) -> dict[str, Any]:
            return services.get_metrics_summary(workspace_id).model_dump(mode="json")

        @app.get("/metrics/trend")
        def metrics_trend(workspace_id: str) -> dict[str, Any]:
            return services.get_query_trend(workspace_id).model_dump(mode="json")

        @app.get("/queries/recent")
        def recent_queries(workspace_id: str) -> dict[str, Any]:
            return services.list_recent_queries(workspace_id).model_dump(mode="json")

        @app.get("/queries/{query_id}")
        def query_detail(query_id: str, workspace_id: str) -> dict[str, Any]:
            result = services.get_query_detail(workspace_id=workspace_id, query_id=query_id)
            if result is None:
                raise HTTPException(status_code=404, detail="query not found")
            return result.model_dump(mode="json")

        @app.get("/evidence/top")
        def top_evidence(workspace_id: str) -> dict[str, Any]:
            return services.list_top_evidence(workspace_id).model_dump(mode="json")

        @app.post("/eval-runs")
        def create_eval_run(payload: EvalRunRequest) -> dict[str, Any]:
            return run_eval(services, payload).model_dump(mode="json")

        @app.get("/eval-runs")
        def eval_runs(workspace_id: str) -> dict[str, Any]:
            return list_eval_runs(services, workspace_id).model_dump(mode="json")

        @app.post("/retrieve")
        def retrieve(payload: RetrievalQuery) -> dict[str, Any]:
            return services.retrieve(payload).model_dump(mode="json")

        @app.post("/answer")
        def answer(payload: AnswerQuery) -> dict[str, Any]:
            return services.answer(payload).model_dump(mode="json")

        return app
    except ModuleNotFoundError as exc:
        if exc.name != "fastapi":
            raise
        return _create_starlette_fallback(services)


def _create_starlette_fallback(services: PolicyRagServices) -> Any:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    async def health(_request: Any) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    async def current_workspace(_request: Any) -> JSONResponse:
        return JSONResponse(DEMO_WORKSPACE.model_dump(mode="json"))

    async def personas(_request: Any) -> JSONResponse:
        return JSONResponse({"personas": [persona.model_dump(mode="json") for persona in DEMO_PERSONAS]})

    async def ingest_document(request: Any) -> JSONResponse:
        try:
            payload = DocumentCreate.model_validate(await request.json())
            result = services.ingest_document(payload)
        except (ValidationError, ValueError) as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        return JSONResponse(result.model_dump(mode="json"), status_code=201)

    async def list_documents(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        result = services.list_documents(workspace_id)
        return JSONResponse(result.model_dump(mode="json"))

    async def get_document_detail(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        result = services.get_document_detail(
            workspace_id=workspace_id,
            document_id=request.path_params["document_id"],
        )
        if result is None:
            return JSONResponse({"detail": "document not found"}, status_code=404)
        return JSONResponse(result.model_dump(mode="json"))

    async def metrics_summary(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        return JSONResponse(services.get_metrics_summary(workspace_id).model_dump(mode="json"))

    async def metrics_trend(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        return JSONResponse(services.get_query_trend(workspace_id).model_dump(mode="json"))

    async def recent_queries(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        return JSONResponse(services.list_recent_queries(workspace_id).model_dump(mode="json"))

    async def query_detail(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        result = services.get_query_detail(
            workspace_id=workspace_id,
            query_id=request.path_params["query_id"],
        )
        if result is None:
            return JSONResponse({"detail": "query not found"}, status_code=404)
        return JSONResponse(result.model_dump(mode="json"))

    async def top_evidence(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        return JSONResponse(services.list_top_evidence(workspace_id).model_dump(mode="json"))

    async def create_eval_run(request: Any) -> JSONResponse:
        try:
            payload = EvalRunRequest.model_validate(await request.json())
            result = run_eval(services, payload)
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        return JSONResponse(result.model_dump(mode="json"))

    async def eval_runs(request: Any) -> JSONResponse:
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return JSONResponse({"detail": "workspace_id is required"}, status_code=422)
        return JSONResponse(list_eval_runs(services, workspace_id).model_dump(mode="json"))

    async def retrieve(request: Any) -> JSONResponse:
        try:
            payload = RetrievalQuery.model_validate(await request.json())
            result = services.retrieve(payload)
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        return JSONResponse(result.model_dump(mode="json"))

    async def answer(request: Any) -> JSONResponse:
        try:
            payload = AnswerQuery.model_validate(await request.json())
            result = services.answer(payload)
        except ValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)
        return JSONResponse(result.model_dump(mode="json"))

    return Starlette(
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/workspaces/current", current_workspace, methods=["GET"]),
            Route("/personas", personas, methods=["GET"]),
            Route("/documents", ingest_document, methods=["POST"]),
            Route("/documents", list_documents, methods=["GET"]),
            Route("/documents/{document_id}", get_document_detail, methods=["GET"]),
            Route("/metrics/summary", metrics_summary, methods=["GET"]),
            Route("/metrics/trend", metrics_trend, methods=["GET"]),
            Route("/queries/recent", recent_queries, methods=["GET"]),
            Route("/queries/{query_id}", query_detail, methods=["GET"]),
            Route("/evidence/top", top_evidence, methods=["GET"]),
            Route("/eval-runs", create_eval_run, methods=["POST"]),
            Route("/eval-runs", eval_runs, methods=["GET"]),
            Route("/retrieve", retrieve, methods=["POST"]),
            Route("/answer", answer, methods=["POST"]),
        ]
    )


app = create_app()
