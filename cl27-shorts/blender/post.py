# Post-process Blender frames: upscale to 1080x1920, bloom, star streaks, anamorphic streak, lens-flare ghosts, vignette.
# python3 post.py <indir> <outdir> [workers]
import sys, os, glob, cv2, numpy as np
from concurrent.futures import ProcessPoolExecutor
W, H = 1080, 1920
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); VIG = (1 - 0.42 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)).clip(0.55, 1)[..., None]
def line_kernel(n, ang):
    k = np.zeros((n, n), np.float32); c = n // 2; d = np.array([np.cos(ang), np.sin(ang)])
    for i in range(-c, c + 1):
        x, y = int(round(c + d[0] * i)), int(round(c + d[1] * i)); k[y, x] = np.exp(-abs(i) / (c * 0.35))
    return k / k.sum()
KS = [line_kernel(61, a) for a in (0.26, 0.26 + np.pi / 3, 0.26 + 2 * np.pi / 3)]
HUSS = {'parkirbus': ([11.95, 17.85, 29.45, 40.62, 51.45], 'huss_inter'), 'tikitaka': ([11.45, 22.9, 30.75, 37.55, 53.7], 'huss_barca')}
ROOT = os.path.dirname(os.path.abspath(__file__))
def overlay_huss(out, f, story):
    times, d = HUSS[story]; t = f / 30.0
    for h in times:
        k = int(round((t - h) * 30))
        if 0 <= k < 66:
            hp = os.path.join(ROOT, d, 'h%03d.png' % k)
            if not os.path.exists(hp): return out
            o = cv2.imread(hp, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.0; x0 = W - o.shape[1] + 30; o = o[:, :W - x0]; oh, ow = o.shape[:2]; y0 = H - oh - 40
            a = o[..., 3:4]; out[y0:y0 + oh, x0:x0 + ow] = out[y0:y0 + oh, x0:x0 + ow] * (1 - a) + o[..., :3] * a
    return out
def proc(args):
    src, dst, story = args
    if os.path.exists(dst): return
    im = cv2.imread(src).astype(np.float32) / 255.0
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4).clip(0, 1)
    lin = np.where(im <= 0.04045, im / 12.92, ((im + 0.055) / 1.055) ** 2.4)                 # rendered at -0.5 EV
    lum = lin[..., 0:1] * 0.0722 + lin[..., 1:2] * 0.7152 + lin[..., 2:3] * 0.2126
    br = np.clip(lin - 0.86, 0, None) * np.clip((lum - 0.86) * 12, 0, 1) * 6.0               # only what clipped at -0.5 EV: lights
    lin = np.clip(lin * 1.414, 0, 1); im = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)
    q = cv2.resize(br, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bloom = np.zeros_like(q)
    for s in (2, 6, 14): bloom += cv2.GaussianBlur(q, (0, 0), s)
    star = sum(cv2.filter2D(q, -1, k) for k in KS) * 1.6
    ana = cv2.blur(q, (151, 3)) * np.array([1.3, 0.85, 0.55], np.float32) * 1.4      # BGR: bluish horizontal streak
    gh = np.zeros_like(q); g8 = cv2.GaussianBlur(q, (0, 0), 3)
    for k, tint in ((-0.55, (1.0, 0.6, 0.9)), (-1.15, (0.6, 1.0, 0.7)), (0.45, (0.5, 0.8, 1.0))):
        M = np.float32([[k, 0, (1 - k) * q.shape[1] / 2], [0, k, (1 - k) * q.shape[0] / 2]])
        gh += cv2.warpAffine(g8, M, (q.shape[1], q.shape[0])) * np.array(tint, np.float32) * 0.5
    fx = cv2.resize(bloom * 0.22 + star * 0.5 + ana * 0.35 + gh * 0.35, (W, H), interpolation=cv2.INTER_LINEAR)
    out = (im + fx) * VIG
    if story: out = overlay_huss(out, int(os.path.basename(src)[1:5]), story)
    cv2.imwrite(dst, (out.clip(0, 1) * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
if __name__ == '__main__':
    ind, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True); n = int(sys.argv[3]) if len(sys.argv) > 3 else 2; story = sys.argv[4] if len(sys.argv) > 4 else None
    fs = sorted(glob.glob(os.path.join(ind, 'f*.jpg'))); jobs = [(f, os.path.join(outd, os.path.basename(f)), story) for f in fs]
    with ProcessPoolExecutor(n) as ex: list(ex.map(proc, jobs, chunksize=4))
    print('POST', len(jobs))
