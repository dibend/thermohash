from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

from thermohash_optimized import discover_miners

CONFIG_PATH = Path("config.json")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scan", response_class=HTMLResponse)
async def scan(request: Request, subnet: str = Form(...)):
    miners = discover_miners(subnet)
    return templates.TemplateResponse("scan_results.html", {"request": request, "miners": miners})

@app.post("/save", response_class=HTMLResponse)
async def save(request: Request, address: list[str] = Form([]), os: list[str] = Form([]), lat: str = Form(None), lon: str = Form(None)):
    miners = []
    for a, o in zip(address, os):
        miners.append({"address": a, "os": o})
    config = {}
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())
    if lat and lon:
        config["latitude"] = float(lat)
        config["longitude"] = float(lon)
    if miners:
        config["miners"] = miners
    CONFIG_PATH.write_text(json.dumps(config, indent=4))
    return HTMLResponse("<h2>Configuration saved.</h2>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
