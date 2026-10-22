import math
import numpy as np


class LightningProcessor:
    def __init__(
        self,
        target_h=512,
        target_w=512,
        lat_min=20.0,
        lat_max=35.0,
        lon_min=68.0,
        lon_max=92.0,
    ):
        self.target_h = target_h
        self.target_w = target_w
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max

    def process(self, strokes=None, sigma_pixels=8.0):
        grid = np.zeros((self.target_h, self.target_w), dtype=np.float32)

        if not strokes or not isinstance(strokes, list):
            return grid

        dlat = self.lat_max - self.lat_min
        dlon = self.lon_max - self.lon_min

        for s in strokes:
            if not isinstance(s, dict):
                continue
            lat = s.get("lat")
            lon = s.get("lon")
            if lat is None or lon is None:
                continue

            if not (self.lat_min <= lat <= self.lat_max and self.lon_min <= lon <= self.lon_max):
                continue

            py = int((self.lat_max - lat) / dlat * (self.target_h - 1))
            px = int((lon - self.lon_min) / dlon * (self.target_w - 1))

            py = max(0, min(self.target_h - 1, py))
            px = max(0, min(self.target_w - 1, px))

            rad = int(sigma_pixels * 2)
            y0 = max(0, py - rad)
            y1 = min(self.target_h, py + rad + 1)
            x0 = max(0, px - rad)
            x1 = min(self.target_w, px + rad + 1)

            for gy in range(y0, y1):
                for gx in range(x0, x1):
                    dist_sq = (gy - py) ** 2 + (gx - px) ** 2
                    val = math.exp(-dist_sq / (2.0 * (sigma_pixels**2)))
                    grid[gy, gx] += val

        max_val = grid.max()
        if max_val > 0.0:
            grid = grid / max_val

        return np.clip(grid, 0.0, 1.0).astype(np.float32)
