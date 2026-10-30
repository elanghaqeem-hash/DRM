"""Generate random credentials for localhost PoC; file is Git-ignored."""
from pathlib import Path
import secrets
import urllib.parse

root = Path(__file__).resolve().parents[2]
target = root / ".env"
if target.exists():
    raise SystemExit(".env exists; refusing to overwrite")
password = secrets.token_urlsafe(30)
admin = secrets.token_urlsafe(30)
minio = secrets.token_urlsafe(30)
app_db_secret = secrets.token_urlsafe(30)
values = (root / ".env.example").read_text()
values = values.replace("POSTGRES_PASSWORD=TBD-LOCAL-SECRET", f"POSTGRES_PASSWORD={password}")
values = values.replace("drm_app:TBD-LOCAL-SECRET@", f"drm_app:{urllib.parse.quote(password)}@")
values = values.replace("KEYCLOAK_ADMIN_PASSWORD=TBD-LOCAL-SECRET",
                        f"KEYCLOAK_ADMIN_PASSWORD={admin}")
values = values.replace("APP_DB_PASSWORD=TBD-LOCAL-SECRET",
                        f"APP_DB_PASSWORD={app_db_secret}")
values = values.replace("edarms_runtime:TBD-LOCAL-SECRET@",
                        f"edarms_runtime:{urllib.parse.quote(app_db_secret)}@")
values = values.replace("MINIO_ROOT_USER=TBD-LOCAL-SECRET", "MINIO_ROOT_USER=pocminio")
values = values.replace("MINIO_ROOT_PASSWORD=TBD-LOCAL-SECRET",
                        f"MINIO_ROOT_PASSWORD={minio}")
target.write_text(values)
target.chmod(0o600)
print("PoC secrets written to local .env (not committed).")
