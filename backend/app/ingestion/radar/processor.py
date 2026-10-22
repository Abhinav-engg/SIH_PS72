import os
import numpy as np


class RadarProcessor:
    def __init__(self, target_h=512, target_w=512):
        self.target_h = target_h
        self.target_w = target_w

    def process(self, raw_data=None):
        h, w = self.target_h, self.target_w

        if raw_data is None:
            return np.zeros((h, w), dtype=np.float32)

        if isinstance(raw_data, str) and os.path.exists(raw_data):
            try:
                if raw_data.endswith(".npy"):
                    arr = np.load(raw_data)
                    return self._clean_and_resize(arr)
            except Exception:
                pass

        if isinstance(raw_data, np.ndarray):
            return self._clean_and_resize(raw_data)

        return np.zeros((h, w), dtype=np.float32)

    def _clean_and_resize(self, arr):
        arr = np.nan_to_num(arr, nan=0.0, posinf=70.0, neginf=0.0)
        arr = np.clip(arr, 0.0, 75.0)

        if arr.max() > 1.0:
            arr = arr / 70.0
            arr = np.clip(arr, 0.0, 1.0)

        if arr.ndim == 3:
            arr = arr[0]
        elif arr.ndim > 3:
            arr = arr.reshape(-1, arr.shape[-2], arr.shape[-1])[0]

        if arr.shape != (self.target_h, self.target_w):
            from scipy.ndimage import zoom
            zy = self.target_h / max(1, arr.shape[0])
            zx = self.target_w / max(1, arr.shape[1])
            try:
                arr = zoom(arr, (zy, zx), order=1)
            except Exception:
                out = np.zeros((self.target_h, self.target_w), dtype=np.float32)
                min_h = min(self.target_h, arr.shape[0])
                min_w = min(self.target_w, arr.shape[1])
                out[:min_h, :min_w] = arr[:min_h, :min_w]
                arr = out

        return arr.astype(np.float32)
