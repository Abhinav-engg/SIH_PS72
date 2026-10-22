import os
from datetime import datetime, timezone
from typing import Any
import numpy as np

from app.ingestion.base import BaseIngestor
from app.ingestion.satellite.processor import SatelliteProcessor


class INSATClient(BaseIngestor):
    def __init__(self):
        super().__init__(source_name="INSAT_3D_Satellite")
        self.processor = SatelliteProcessor()

    async def fetch(self) -> Any:
        sample_dir = os.path.join("data", "raw", "satellite")
        if os.path.exists(sample_dir):
            files = [f for f in os.listdir(sample_dir) if f.endswith((".h5", ".nc", ".npy"))]
            if files:
                return os.path.join(sample_dir, files[0])

        rng = np.random.RandomState(int(datetime.now(timezone.utc).timestamp()) % 1000)
        tir1 = rng.uniform(210.0, 305.0, (512, 512)).astype(np.float32)
        wv = rng.uniform(200.0, 275.0, (512, 512)).astype(np.float32)

        return {"tir1": tir1, "wv": wv}

    async def process(self, raw_data: Any) -> Any:
        if isinstance(raw_data, dict):
            return self.processor.process(
                tir1=raw_data.get("tir1"),
                wv=raw_data.get("wv"),
            )
        return self.processor.process()
