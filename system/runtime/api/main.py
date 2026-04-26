from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from system.runtime.config import settings

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TREE_ROOT = REPO_ROOT / "tree"
STATIC_ROOT = Path(__file__).resolve().parent / "static"

from .dependencies import build_runtime
from .routers.agent_surface import router as agent_router
from .routers.authoring import router as authoring_router
from .routers.governance import router as governance_router
from .routers.pipelines import router as pipelines_router
from .routers.read import router as read_router
from .routers.surface import router as surface_router


def create_app(db_path: str | Path | None = None, tree_root: str | Path | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.runtime = build_runtime(db_path)
        yield

    app = FastAPI(title="Nexus Runtime", version=settings.version, lifespan=lifespan)
    app.state.runtime = None
    app.state.runtime_db_path = db_path
    app.state.tree_root = Path(tree_root) if tree_root is not None else DEFAULT_TREE_ROOT

    @app.get("/health", tags=["system"])
    async def health(request: Request) -> dict[str, str]:
        runtime = request.app.state.runtime
        if runtime is not None:
            db_runtime_path = runtime.db_path
        else:
            configured_path = getattr(request.app.state, "runtime_db_path", None)
            db_runtime_path = str(configured_path) if configured_path is not None else str(settings.db_path)
        return {
            "status": "ok",
            "environment": settings.env,
            "version": settings.version,
            "db_path": db_runtime_path,
        }

    app.include_router(read_router)
    app.include_router(authoring_router)
    app.include_router(governance_router)
    app.include_router(pipelines_router)
    app.include_router(surface_router)
    app.include_router(agent_router)
    app.mount("/static", StaticFiles(directory=STATIC_ROOT), name="static")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> Response:
        return Response(status_code=204)

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {
            "service": "nexus-runtime",
            "status": "ready",
            "environment": settings.env,
            "surface": "/surface",
            "agent_surface": "/agent",
        }

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("system.runtime.api.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
