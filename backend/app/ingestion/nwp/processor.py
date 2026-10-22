import numpy as np


class NWPProcessor:
    def __init__(self, target_h=512, target_w=512):
        self.target_h = target_h
        self.target_w = target_w

    def process(self, cape=None, cin=None):
        h, w = self.target_h, self.target_w

        c_arr = self._clean_field(cape, default_val=1500.0)
        cin_arr = self._clean_field(cin, default_val=80.0)

        cape_norm = np.clip(c_arr / 5000.0, 0.0, 1.0)
        cin_norm = np.clip(cin_arr / 500.0, 0.0, 1.0)

        return {
            "cape": cape_norm.astype(np.float32),
            "cin": cin_norm.astype(np.float32),
        }

    def _clean_field(self, arr, default_val=0.0):
        if arr is None:
            return np.full((self.target_h, self.target_w), default_val, dtype=np.float32)

        arr = np.nan_to_num(arr, nan=default_val, posinf=default_val, neginf=0.0)

        if arr.ndim == 3:
            arr = arr[0]

        if arr.shape != (self.target_h, self.target_w):
            out = np.full((self.target_h, self.target_w), default_val, dtype=np.float32)
            min_h = min(self.target_h, arr.shape[0])
            min_w = min(self.target_w, arr.shape[1])
            out[:min_h, :min_w] = arr[:min_h, :min_w]
            arr = out

        return arr.astype(np.float32)
