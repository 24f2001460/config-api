from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# DEFAULT CONFIG
# ------------------------

config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000"
}

# ------------------------
# YAML
# ------------------------
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
yaml_file = BASE_DIR / "config.development.yaml"

if yaml_file.exists():
    with open(yaml_file) as f:
        y = yaml.safe_load(f)
        if y:
            config.update(y)

# ------------------------
# .env
# ------------------------

env_map = {
    "APP_PORT": "port",
    "APP_WORKERS": "workers",
    "APP_DEBUG": "debug",
    "APP_LOG_LEVEL": "log_level",
    "APP_API_KEY": "api_key",
    "NUM_WORKERS": "workers"
}

for k, v in env_map.items():
    if os.getenv(k) is not None:
        config[v] = os.getenv(k)

# ------------------------
# OS ENV (same APP_* vars)
# ------------------------

for k, v in env_map.items():
    if k in os.environ:
        config[v] = os.environ[k]


def to_bool(x):
    return str(x).lower() in ["true", "1", "yes", "on"]


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    final = config.copy()

    # CLI overrides
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            final[key] = value

    # type coercion
    final["port"] = int(final["port"])
    final["workers"] = int(final["workers"])
    final["debug"] = to_bool(final["debug"])
    final["log_level"] = str(final["log_level"])

    # mask secret
    final["api_key"] = "****"

    return final