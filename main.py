from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.adapters.inbound.controllers.geocode_controller import router as geocode_router
from src.adapters.inbound.controllers.route_controller import router as route_router


app = FastAPI(title="TrafegoPro")
app.include_router(geocode_router)
app.include_router(route_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("static/index.html")


def main() -> None:
    print("TrafegoPro API")


if __name__ == "__main__":
    main()
