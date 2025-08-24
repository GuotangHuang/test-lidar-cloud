import argparse
from pathlib import Path
import numpy as np
import open3d as o3d
from utils_vis import save_xy_scatter

"""
密度調整兩種方式：
1) 體素下採樣（voxel downsample）：以指定體素大小聚合點雲。
2) 目標點數（uniform/random sample）：抽樣到指定點數。
"""

def voxel_downsample(pcd: o3d.geometry.PointCloud, voxel: float) -> o3d.geometry.PointCloud:
    return pcd.voxel_down_sample(voxel)


def random_sample(pcd: o3d.geometry.PointCloud, target_n: int, seed: int | None) -> o3d.geometry.PointCloud:
    n = len(pcd.points)
    if target_n >= n:
        return pcd
    rng = np.random.default_rng(seed)
    idx = rng.choice(n, size=target_n, replace=False)
    out = o3d.geometry.PointCloud()
    out.points = o3d.utility.Vector3dVector(np.asarray(pcd.points)[idx])
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", default="data/plane_raw.ply")
    parser.add_argument("--out", default="data/plane_down.ply")
    parser.add_argument("--voxel", type=float, default=None, help="體素大小（公尺）")
    parser.add_argument("--target", type=int, default=None, help="目標點數（隨機抽樣）")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    pcd = o3d.io.read_point_cloud(args.inp)
    out_pcd = pcd

    steps = []
    if args.voxel and args.voxel > 0:
        out_pcd = voxel_downsample(out_pcd, args.voxel)
        steps.append(f"voxel={args.voxel}")

    if args.target and args.target > 0:
        out_pcd = random_sample(out_pcd, args.target, seed=args.seed)
        steps.append(f"target={args.target}")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    o3d.io.write_point_cloud(args.out, out_pcd)
    print(f"[OK] Saved downsampled to {args.out} with {len(out_pcd.points)} points | steps: {', '.join(steps) if steps else 'none'}")

    # 預覽圖
    pts = np.asarray(out_pcd.points)
    png = Path(args.out).with_suffix(".png")
    save_xy_scatter(pts, str(png), title=f"Downsampled: {len(pts)} pts\n{' + '.join(steps) if steps else 'raw'}")
    print(f"[OK] Saved preview to {png}")

if __name__ == "__main__":
    main()