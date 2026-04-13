"""
FastAPI Application Entry Point
AI-Driven Traffic Congestion Prediction & Adaptive Signal Control
"""
from __future__ import annotations
import asyncio
import sys
import os

# Add backend root to path for ML imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.websocket_manager import ws_manager
from app.services.simulation_service import simulation_loop
from app.services.prediction_service import load_all_models, get_models_status
from app.routers import traffic, prediction, signal, training


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────────────────
    print("[Main] Initializing database …")
    await init_db()

    print("[Main] Loading ML models …")
    load_all_models()

    print("[Main] Starting simulation loop …")
    sim_task = asyncio.create_task(simulation_loop())

    yield  # ← application runs here

    # ── Shutdown ───────────────────────────────────────────────────────────────
    sim_task.cancel()
    print("[Main] Shutdown complete.")


app = FastAPI(
    title       = "AI Traffic Management System",
    description = "Congestion prediction + adaptive signal control API",
    version     = "1.0.0",
    lifespan    = lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins    = ["http://localhost:5173", "http://localhost:3000",
                        "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials= True,
    allow_methods    = ["*"],
    allow_headers    = ["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(traffic.router)
app.include_router(prediction.router)
app.include_router(signal.router)
app.include_router(training.router)


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws/traffic")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    print(f"[WS] Client connected. Total: {ws_manager.count}")
    try:
        # Send current state immediately on connect
        from app.services.simulation_service import get_current_state
        await websocket.send_json({
            "type": "initial_state",
            "data": get_current_state(),
        })
        # Keep alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
        print(f"[WS] Client disconnected. Total: {ws_manager.count}")


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status":        "ok",
        "models_loaded": get_models_status(),
        "db_connected":  True,
        "version":       "1.0.0",
        "ws_clients":    ws_manager.count,
    }


@app.get("/")
async def root():
    return {
        "message": "AI Traffic Management System API",
        "docs":    "/docs",
        "health":  "/health",
    }
