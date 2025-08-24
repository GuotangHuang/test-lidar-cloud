import argparse
from pathlib import Path
import numpy as np
import open3d as o3d
from utils_vis import save_xy_scatter

"""
離群點過濾（去噪）兩種常用方法：
1) 統計式離群點過濾（Statistical Outlier Removal, SOR）：
   - 以 K 鄰近的平均距離作為統計量，移除超過 threshold_sigma 標準差的點。
2) 半徑式離群點過濾（Radius Outlier Removal, ROR）：
   - 在 radius 半徑內鄰居數少於 min_neighbors 的點視為離群。
可單獨或串接使用。
"""

def sor(pcd: o3d.geometry.PointCloud, k: int, sigma: float):
    cl, ind = pcd.remove_statistical_outlier(nb_neighbors=k, std_ratio=sigma)
    return cl, ind


def ror(pcd: o3d.geometry.PointCloud, radius: float, min_neighbors: int):
    cl, ind = pcd.remove_radius_outlier(nb_points=min_neighbors, radius=radius)
    return cl, ind


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", default="data/plane_raw.ply")
    parser.add_argument("--out", default="data/plane_denoised.ply")
    # SOR 參數
    parser.add_argument("--sor-k", type=int, default=None, help="SOR：K 鄰近數，例如 20~50")
    parser.add_argument("--sor-sigma", type=float, default=2.0, help="SOR：標準差倍率（越小越嚴格）")
    # ROR 參數
    parser.add_argument("--ror-radius", type=float, default=None, help="ROR：半徑（公尺）")
    parser.add_argument("--ror-min", type=int, default=8, help="ROR：最少鄰居數")
    args = parser.parse_args()

    pcd = o3d.io.read_point_cloud(args.inp)
    orig_n = len(pcd.points)
    steps = []

    out = pcd
    if args.sor_k:
        out, _ = sor(out, k=args.sor_k, sigma=args.sor_sigma)
        steps.append(f"SOR(k={args.sor_k},σ={args.sor_sigma})")

    if args.ror_radius:
        out, _ = ror(out, radius=args.ror_radius, min_neighbors=args.ror_min)
        steps.append(f"ROR(r={args.ror_radius},min={args.ror_min})")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    o3d.io.write_point_cloud(args.out, out)

    cur_n = len(out.points)
    print(f"[OK] Denoised {args.inp} -> {args.out} | {orig_n} -> {cur_n} points | steps: {', '.join(steps) if steps else 'none'}")

    pts = np.asarray(out.points)
    png = Path(args.out).with_suffix(".png")
    save_xy_scatter(pts, str(png), title=f"Denoised: {cur_n} pts{' + '.join(steps) if steps else 'none'}")
    print(f"[OK] Saved preview to {png}")

if __name__ == "__main__":
    main()