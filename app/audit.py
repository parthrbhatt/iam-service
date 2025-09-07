import time
import logging
import json
import os
from jose import jwt
from typing import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .config import AUDIT_LOG_FILE

logging.basicConfig(
    filename=AUDIT_LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("audit")

class AuditMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next: Callable):
		client_ip = client_port = req_id = user_id = jti = role = "<NA>"
		if request.client:
		    client_ip = request.client.host
		    client_port = request.client.port

		req_id = request.headers.get("X-Request-ID", "<NA>")
		auth = request.headers.get("Authorization", "")
		if auth.lower().startswith("bearer "):
			try:
				token = auth.split(" ", 1)[1]
				claims = jwt.get_unverified_claims(token)
				user_id = str(claims.get("sub", "<NA>"))
				jti = str(claims.get("jti", "<NA>"))
				role = str(claims.get("role", "<NA>"))
			except Exception:
				pass
		response = await call_next(request)
		logger.info(f"method={request.method} path={request.url.path} status={response.status_code} client_ip={client_ip} client_port={client_port} request_id={req_id} user_id={user_id} role={role} jti={jti}")
		return response