from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers import users, auth
from .security import add_security_headers
from .audit import AuditMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
	# Startup
	init_db()
	yield
	# Shutdown (if needed)

app = FastAPI(
	title="IAM Service",
	description="""
	## IAM Service API
	""",
	version="0.0.1",
	servers=[
		{
			"url": "http://localhost:8000",
			"description": "Development server"
		}
	],
	docs_url="/docs",
	redoc_url="/redoc",
	openapi_url="/openapi.json",
	lifespan=lifespan
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"], # Allows all domains for dev. Limit to specific domains for production.
	allow_credentials=False,
	allow_methods=["GET", "POST", "OPTIONS"],
	allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.middleware("http")(add_security_headers)
app.add_middleware(AuditMiddleware)

@app.get(
    "/healthz",
    tags=["Health"],
    summary="Health check",
    description="Check if the service is running and healthy",
    response_description="Service is healthy"
)
async def healthz():
	return {
		"status": "ok"
	}

app.include_router(auth.router, prefix="")
app.include_router(users.router, prefix="")