from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)

_NOWCAST_STUB: dict[str, Any] = {
    "nowcast_id": "stub-001",
    "issued_at": "2026-09-26T15:00:00Z",
    "valid_until": "2026-09-26T17:00:00Z",
    "horizon_minutes": 120,
    "interval_minutes": 15,
    "timesteps": [15, 30, 45, 60, 75, 90, 105, 120],
    "cells": [
        {
            "cell_id": "TS-001",
            "center": {"lat": 28.61, "lon": 77.23},
            "radius_km": 35.0,
            "severity": "severe",
            "probability": 0.82,
            "hazards": {
                "lightning": {"probability": 0.88, "flash_rate_per_min": 12},
                "hail": {"probability": 0.45, "max_diameter_mm": 25},
                "wind_gust_kmh": 75,
            },
            "motion": {"bearing_deg": 245, "speed_kmh": 42},
            "forecast_positions": [
                {"minutes_ahead": 15, "lat": 28.58, "lon": 77.18, "probability": 0.80},
                {"minutes_ahead": 30, "lat": 28.55, "lon": 77.13, "probability": 0.74},
                {"minutes_ahead": 60, "lat": 28.49, "lon": 77.03, "probability": 0.61},
                {"minutes_ahead": 120, "lat": 28.37, "lon": 76.83, "probability": 0.43},
            ],
        },
    ],
    "model": {"name": "ps72-nowcast-stub", "version": "0.1.0"},
    "data_sources_used": ["radar", "satellite", "lightning"],
}

_MODE: str | None = None


def _detect_mode() -> str:
    try:
        from app.core.config import get_settings
        settings = get_settings()
        if getattr(settings, "ml_force_stub", False):
            return "stub"
    except Exception:
        pass

    try:
        import ml.inference
        return "real"
    except ImportError:
        return "stub"


def _get_mode() -> str:
    global _MODE
    if _MODE is None:
        _MODE = _detect_mode()
    return _MODE


def run_nowcast(
    radar_data: Any | None = None,
    satellite_data: Any | None = None,
    lightning_data: Any | None = None,
    nwp_data: Any | None = None,
) -> dict[str, Any]:
    if _get_mode() == "real":
        try:
            from ml.inference import run_nowcast as _ml_nowcast
            result = _ml_nowcast(
                radar_data=radar_data,
                satellite_data=satellite_data,
                lightning_data=lightning_data,
                nwp_data=nwp_data,
            )
            if isinstance(result, dict) and "cells" in result:
                return result
        except Exception as exc:
            logger.error(f"Inference error: {exc}")

    return dict(_NOWCAST_STUB)


def reset_mode() -> None:
    global _MODE
    _MODE = None
