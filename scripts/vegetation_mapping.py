"""RGB vegetation indices and synthetic-coordinate UAV mapping.

Usage:
    python scripts/vegetation_mapping.py --image data/sample.jpg
    python scripts/vegetation_mapping.py --video data/drone_video.mp4 --interval 0.2

Maps use simulated coordinates, NOT measured GPS or validated plant stress labels.
"""
import argparse
from pathlib import Path
import math
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


def indices(rgb):
    rgb = np.asarray(rgb, dtype=np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    exg = 2 * g - r - b
    denom = g + r - b
    vari = np.divide(g-r, denom, out=np.zeros_like(g), where=np.abs(denom)>1e-6)
    return exg, vari


def clipped(x):
    lo, hi = np.percentile(x[np.isfinite(x)], [2, 98])
    return np.clip(x, lo, hi)


def low_index_mask(exg, vari):
    # Exploratory low-greenness indicator, not a verified stress classifier.
    return (exg < np.percentile(exg, 20)) & (vari < np.percentile(vari, 20))


def save_preview(rgb, out_path):
    exg, vari = indices(rgb)
    mask = low_index_mask(exg, vari)
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    axes[0].imshow(rgb); axes[0].set_title('RGB')
    axes[1].imshow(clipped(exg), cmap='RdYlGn'); axes[1].set_title('ExG')
    axes[2].imshow(clipped(vari), cmap='RdYlGn'); axes[2].set_title('VARI')
    axes[3].imshow(rgb); axes[3].imshow(np.ma.masked_where(~mask, mask), cmap='Reds', alpha=.45, vmin=0, vmax=1)
    axes[3].set_title('Low-index pixels (heuristic)')
    for ax in axes: ax.axis('off')
    fig.tight_layout(); fig.savefig(out_path, dpi=160); plt.close(fig)
    return {'mean_exg':float(np.mean(exg)), 'mean_vari':float(np.mean(vari)), 'low_index_ratio':float(np.mean(mask))}


def extract_video(video, interval, output):
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise ValueError(f'Cannot open video: {video}')
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0: cap.release(); raise ValueError('Video FPS is unavailable')
    step = max(1, round(fps * interval)); frames=[]; idx=0
    while True:
        ok, bgr = cap.read()
        if not ok: break
        if idx % step == 0:
            path=output/'frames'/f'frame_{len(frames):05d}.jpg';path.parent.mkdir(parents=True,exist_ok=True)
            cv2.imwrite(str(path),bgr)
            frames.append((path,idx/fps))
        idx+=1
    cap.release()
    if not frames: raise ValueError('No video frames extracted')
    return frames


def synthetic_coordinates(n, seed=42):
    # Synthetic serpentine survey coordinates; illustrative only.
    rng=np.random.default_rng(seed); rows=[]; k=0; drift=np.zeros(2)
    for row in range(math.ceil(n/8)):
        for col in (range(8) if row%2==0 else range(7,-1,-1)):
            if k>=n: break
            drift += rng.normal(0, 0.0000015, 2)
            lat=23.780600 + row*.000018 + drift[0] + .0000025*np.sin(2*np.pi*k/11) + rng.normal(0,.0000012)
            lon=90.279400 + col*.000022 + drift[1] + .0000020*np.cos(2*np.pi*k/13) + rng.normal(0,.0000012)
            rows.append((lat,lon)); k+=1
    return rows


def run(image=None, video=None, interval=.2, output=Path('outputs')):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if bool(image)==bool(video): raise ValueError('Specify exactly one of --image or --video')
    if image:
        rgb=np.asarray(Image.open(image).convert('RGB'))
        stats=save_preview(rgb,output/'vegetation_preview.png')
        pd.DataFrame([stats]).to_csv(output/'frame_metrics.csv',index=False)
        return
    frames=extract_video(video,interval,output)
    coords=synthetic_coordinates(len(frames)); rows=[]
    for i,((path,t),(lat,lon)) in enumerate(zip(frames,coords)):
        rgb=np.asarray(Image.open(path).convert('RGB'))
        stats=save_preview(rgb,output/f'preview_{i:05d}.png')
        rows.append({'frame':path.name,'time_s':t,'synthetic_lat':lat,'synthetic_lon':lon,**stats})
    df=pd.DataFrame(rows);df.to_csv(output/'frame_metrics.csv',index=False)
    if len(df)>=3:
        fig,ax=plt.subplots(figsize=(7,6))
        sc=ax.scatter(df.synthetic_lon,df.synthetic_lat,c=df.mean_vari,cmap='RdYlGn',s=80)
        fig.colorbar(sc,ax=ax,label='Mean VARI');ax.set(xlabel='Synthetic longitude',ylabel='Synthetic latitude',title='Simulated-coordinate VARI map')
        fig.tight_layout();fig.savefig(output/'synthetic_vari_map.png',dpi=180);plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image',type=Path);group.add_argument('--video',type=Path)
    parser.add_argument('--interval',type=float,default=.2)
    parser.add_argument('--output',type=Path,default=Path('outputs'))
    args=parser.parse_args()
    run(args.image,args.video,args.interval,args.output)
