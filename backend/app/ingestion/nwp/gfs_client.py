import os
from datetime import datetime, timezone
from typing import Any
import numpy as np

from app.ingestion.base import BaseIngestor
from app.ingestion.nwp.processor import NWPProcessor


class GFSClient(BaseIngestor):
    def __init__(self):
        super().__init__(source_name="GFS_NWP")
        self.processor = NWPProcessor()

    async def fetch(self) -> Any:
        sample_dir = os.path.join("data", "raw", "nwp")
        if os.path.exists(sample_dir):
            files = [f for f in os.listdir(sample_dir) if f.endswith((".grib2", ".grb2", ".nc", ".npy"))]
            if files:
                return os.path.join(sample_dir, files[0])

        rng = np.random.RandomState(int(datetime.now(timezone.utc).timestamp()) % 1000)
        cape = rng.uniform(500.0, 4200.0, (512, 512)).astype(np.float32)
        cin = rng.uniform(10.0, 250.0, (512, 512)).astype(np.float32)

        return {"cape": cape, "cin": cin}

    async def process(self, raw_data: Any) -> Any:
        if isinstance(raw_data, dict):
            return self.processor.process(
                cape=raw_data.get("cape"),
                cin=raw_data.get("cin"),
            )
        return self.processor.process()
