import numpy as np


class SatelliteProcessor:
    def __init__(self, target_h=512, target_w=512):
        self.target_h = target_h
        self.target_w = target_w

    def process(self, tir1=None, wv=None):
        h, w = self.target_h, self.target_w

        t1 = self._format_channel(tir1, default_val=280.0)
        w_ch = self._format_channel(wv, default_val=240.0)

        t1_norm = np.clip((t1 - 180.0) / 140.0, 0.0, 1.0)
        w_norm = np.clip((w_ch - 190.0) / 90.0, 0.0, 1.0)

        diff = t1 - w_ch
        diff_norm = np.clip((diff + 30.0) / 60.0, 0.0, 1.0)

        return {
            "tir1": t1_norm.astype(np.float32),
            "wv": w_norm.astype(np.float32),
            "diff": diff_norm.astype(np.float32),
        }

    def _format_channel(self, arr, default_val=250.0):
        if arr is None:
            return np.full((self.target_h, self.target_w), default_val, dtype=np.float32)

        arr = np.nan_to_num(arr, nan=default_val, posinf=default_val, neginf=default_val)

        if arr.ndim == 3:
            arr = arr[0]

        if arr.shape != (self.target_h, self.target_w):
            out = np.full((self.target_h, self.target_w), default_val, dtype=np.float32)
            min_h = min(self.target_h, arr.shape[0])
            min_w = min(self.target_w, arr.shape[1])
            out[:min_h, :min_w] = arr[:min_h, :min_w]
            arr = out

        return arr.astype(np.float32)
