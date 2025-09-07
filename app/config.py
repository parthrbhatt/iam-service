from typing import Dict

def _get_file_contents(path: str) -> str:
	with open(path, "r") as f:
		return f.read()

AUDIT_LOG_FILE = "audit.log"
# Database configuration
DB_FILENAME = "iam.db"

# JWT configuration
JWT_ALGORITHM = "RS256"
JWT_EXPIRY_SECONDS = 3600
JWT_ISSUER = "iam-service"
JWT_AUDIENCE = (
	"iam-service"
)
JWT_SIGNING_KEY = _get_file_contents("keys/sample/private.pem")
JWT_VERIFICATION_KEYS: Dict[str, str] = { # Supports multiple verification keys to facilitate key rotation.
	"current": _get_file_contents("keys/sample/public.pem"),
	#"previous": _get_file_contents("keys/sample/public_previous.pem"),
}
