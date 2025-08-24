from typing import Optional
import numpy as np
import matplotlib.pyplot as plt

# 儲存 XY 平面散佈圖（避免 GUI 依賴）
def save_xy_scatter(pts: np.ndarray, out_png: str, title: Optional[str] = None, sample: int = 100_000):
    pts2d = pts[:, :2]
    n = len(pts2d)
    if n > sample:
        idx = np.random.default_rng(0).choice(n, size=sample, replace=False)
        pts2d = pts2d[idx]
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111)
    ax.scatter(pts2d[:,0], pts2d[:,1], s=0.2)
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_title(title or 'XY scatter')
    ax.set_aspect('equal', adjustable='box')
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)