import argparse
import numpy as np
import open3d as o3d
from pathlib import Path
from utils_vis import save_xy_scatter

"""
生成一個 Z≈0 的平面點雲，可選擇：
- 高斯雜訊（模擬量測誤差）
- 挖洞（模擬稀疏區塊）
- 離群點（outliers）：在指定範圍內隨機撒點，Z 可偏離平面
"""

def gen_plane(n_points: int, size: float, noise_sigma: float, hole_ratio: float, seed: int | None):
    rng = np.random.default_rng(seed)
    # 均勻分布在 [-size/2, size/2]
    x = rng.uniform(-size/2, size/2, n_points)
    y = rng.uniform(-size/2, size/2, n_points)
    z = np.zeros_like(x)

    # 高斯雜訊（模擬量測誤差）
    if noise_sigma > 0:
        z += rng.normal(0, noise_sigma, n_points)

    # 人為挖洞（模擬稀疏區域）
    if 0 < hole_ratio < 1:
        mask = rng.random(n_points) > hole_ratio
        x, y, z = x[mask], y[mask], z[mask]

    pts = np.stack([x, y, z], axis=1)
    return pts


def gen_outliers(n_out: int, box_xy: float, z_min: float, z_max: float, seed: int | None):
    rng = np.random.default_rng(seed)
    xo = rng.uniform(-box_xy/2, box_xy/2, n_out)
    yo = rng.uniform(-box_xy/2, box_xy/2, n_out)
    zo = rng.uniform(z_min, z_max, n_out)
    return np.stack([xo, yo, zo], axis=1)


def to_o3d_pcd(pts: np.ndarray) -> o3d.geometry.PointCloud:
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)
    return pcd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/plane_raw.ply")
    parser.add_argument("--n", type=int, default=200_000, help="平面點數")
    parser.add_argument("--size", type=float, default=10.0, help="平面邊長")
    parser.add_argument("--noise", type=float, default=0.005, help="Z 噪聲 sigma")
    parser.add_argument("--hole", type=float, default=0.0, help="挖洞比例 0~1")
    # 離群點參數
    parser.add_argument("--outliers", type=int, default=0, help="離群點數量")
    parser.add_argument("--outlier-box", type=float, default=None, help="離群點散佈的 XY 正方形邊長，預設等於 size")
    parser.add_argument("--outlier-z-min", type=float, default=0.3, help="離群點 Z 最小值（遠離平面）")
    parser.add_argument("--outlier-z-max", type=float, default=1.0, help="離群點 Z 最大值（遠離平面）")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    pts = gen_plane(args.n, args.size, args.noise, args.hole, args.seed)

    if args.outliers and args.outliers > 0:
        box_xy = args.outlier_box if args.outlier_box else args.size
        outlier_pts = gen_outliers(args.outliers, box_xy, args.outlier_z_min, args.outlier_z_max, args.seed+1)
        pts = np.concatenate([pts, outlier_pts], axis=0)

    pcd = to_o3d_pcd(pts)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    o3d.io.write_point_cloud(str(out), pcd)
    print(f"[OK] Saved raw plane(+outliers) to {out} with {len(pcd.points)} points")

    # 存 XY 散佈圖（可快速看密度/離群分布）
    png = out.with_suffix(".png")
    save_xy_scatter(pts, str(png), title=f"Raw plane (+outliers): {len(pts)} pts")
    print(f"[OK] Saved preview to {png}")

if __name__ == "__main__":
    main()