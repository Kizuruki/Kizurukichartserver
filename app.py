import os, importlib, asyncio
from urllib.parse import urlparse

from concurrent.futures import ThreadPoolExecutor

import yaml

with open("config.yml", "r") as f:
    config = yaml.load(f, yaml.Loader)

from fastapi import FastAPI, Request
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
# near other imports
from db import init_db, engine
import crud
from helpers.storage import init_storage, save_chart_file
from models import User, Song, UserUnlock, SQLModel
from fastapi import Depends, UploadFile, File
from jose import JWTError, jwt
from passlib.context import CryptContext

from helpers.repository_map import repo

debug = False


class SonolusFastAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = kwargs["debug"]

        self.executor = ThreadPoolExecutor(max_workers=16)

        self.config = kwargs["config"]
        self.base_url = kwargs["base_url"]

        self.repository = repo

        self.exception_handlers.setdefault(HTTPException, self.http_exception_handler)

        # do NOT compile all static assets at startup for dynamic mode.
        # We'll still allow a small compile-on-demand but avoid blocking startup.
        
    async def reload_dynamic_repo(self):
        # scan dynamic storage and update internal repo mapping or DB
        # (For now, rely on DB; this method can be used to rebuild in-memory caches)
        pass

    async def compile_and_register(self, uid: str, filename: str, title: str, default_locked=False):
        # called when file uploaded
        # Save DB record and optionally run compile logic in a background thread
        # Save record to DB (sync helper for simplicity)
        path = f"{init_storage}"  # placeholder - actual path was returned by save_chart_file
        # We'll instead call crud.create_song_sync in background tasks where appropriate
        return


        compile_static_levels_list(
            self.base_url
        )  # this might take time, maybe compile now?

    async def run_blocking(self, func, *args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, lambda: func(*args, **kwargs)
        )

    def get_items_per_page(self, route: str) -> int:
        return self.config["items-per-page"].get(
            route, self.config["items-per-page"].get("default")
        )

    async def http_exception_handler(self, request: Request, exc: HTTPException):
        if exc.status_code < 500:
            return JSONResponse(
                content={"message": exc.detail}, status_code=exc.status_code
            )
        else:
            return JSONResponse(status_code=exc.status_code)


VERSION_REGEX = r"^\d+\.\d+\.\d+$"


class SonolusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.localization = request.query_params.get("localization", "en")
        response = await call_next(request)
        response.headers["Sonolus-Version"] = request.app.config[
            "required-client-version"
        ]
        return response


app = SonolusFastAPI(
    debug=debug, config=config["sonolus"], base_url=config["server"]["base-url"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SonolusMiddleware)
if not debug:
    domain = urlparse(config["server"]["base-url"]).netloc
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*", "charts.kizuruki.com"])


@app.middleware("http")
async def force_https_redirect(request, call_next):
    response = await call_next(request)

    if config["server"]["force-https"] and not debug:
        if response.headers.get("Location"):
            response.headers["Location"] = response.headers.get("Location").replace(
                "http://", "https://", 1
            )

    return response


# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")


import os
import importlib


def loadRoutes(folder, cleanup: bool = True):
    global app
    """Load Routes from the specified directory."""

    routes = []

    def traverse_directory(directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for file in files:
                if not "__pycache__" in root and os.path.join(root, file).endswith(
                    ".py"
                ):
                    route_name: str = (
                        os.path.join(root, file)
                        .removesuffix(".py")
                        .replace("\\", "/")
                        .replace("/", ".")
                    )

                    # Check if the route is dynamic or static
                    if "{" in route_name and "}" in route_name:
                        routes.append(
                            (route_name, False)
                        )  # Dynamic route (priority lower)
                    else:
                        routes.append(
                            (route_name, True)
                        )  # Static route (priority higher)

    traverse_directory(folder)

    # Sort the routes: static first, dynamic last. Deeper routes (subdirectories) have higher priority.
    # We are sorting by two factors:
    # 1. Whether the route is static (True first) or dynamic (False second).
    # 2. Depth of the route (deeper subdirectory routes come first).
    routes.sort(key=lambda x: (not x[1], x[0]))  # Static first, dynamic second

    for route_name, is_static in routes:
        route = importlib.import_module(route_name)
        if hasattr(route, "donotload") and route.donotload:
            continue

        route_version = route_name.split(".")[0]
        route_name_parts = route_name.split(".")

        # it's the index for the route
        if route_name.endswith(".index"):
            del route_name_parts[-1]

        route_name = ".".join(route_name_parts)

        route.router.prefix = "/" + route_name.replace(".", "/")
        route.router.tags = (
            route.router.tags + [route_version]
            if isinstance(route.router.tags, list)
            else [route_version]
        )

        route.setup()
        app.include_router(route.router)

        print(f"[API] Loaded Route {route_name}")


async def startup_event():
    # init DB
    await init_db()

    # init dynamic storage
    init_storage(config["server"])

    # optionally load existing songs into repo or a cache
    print("Database and dynamic storage initialized.")
    # load routes as before:
    folder = "sonolus"
    if len(os.listdir(folder)) == 0:
        print("[WARN] No routes loaded.")
    else:
        loadRoutes(folder)
        print("Routes loaded!")


app.add_event_handler("startup", startup_event)

# uvicorn.run("app:app", port=port, host="0.0.0.0")


async def start_fastapi(args):
    config_server = uvicorn.Config(
        "app:app",
        host="0.0.0.0",
        port=config["server"]["port"],
        workers=8,
        # log_level="critical",
    )
    server = uvicorn.Server(config_server)
    await server.serve()


if __name__ == "__main__":
    raise SystemExit("Please run main.py")
    
from routes import auth as auth_routes, charts as chart_routes
app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
app.include_router(chart_routes.router, prefix="/api/charts", tags=["charts"])
