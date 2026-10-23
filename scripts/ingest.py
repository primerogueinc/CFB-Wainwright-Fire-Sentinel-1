"""Ingest a raw Copernicus Browser Sentinel-1 export (zip) into sentinel-1/<date>/<mode>_<pols>/.
Usage: python3 scripts/ingest.py EXPORT.zip [--acq "2026-10-19T01:05Z ascending, orbit 12345"]
Copies files unchanged; writes manifest.json (SHA-256 per file, frame, pixel size, coverage of reference points) and a preview."""
import sys, os, re, json, hashlib, zipfile, tempfile, glob, shutil
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (-110.96, 52.74, -110.85, 52.80)
POINTS = {"origin": (-110.9214, 52.7764), "A_range2": (-110.90632, 52.77279), "B_road_head": (-110.89965, 52.77045)}
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def main(zin, acq):
    import rasterio
    from rasterio.windows import from_bounds
    from PIL import Image
    tmp = tempfile.mkdtemp(); zipfile.ZipFile(zin).extractall(tmp)
    files = sorted(f for f in glob.glob(tmp + "/**/*", recursive=True) if os.path.isfile(f))
    groups = {}
    for f in files:
        m = re.match(r"(\d{4}-\d{2}-\d{2})-\d{2}_\d{2}_\d{4}-\d{2}-\d{2}-\d{2}_\d{2}_Sentinel-1_([A-Z]{2})_(VV_VH|HH_HV|VV|VH|HH|HV)_(.+)\.(tiff?|jpe?g|png)$", os.path.basename(f), re.I)
        if not m: print("skip", os.path.basename(f)); continue
        groups.setdefault((m.group(1), m.group(2), m.group(3)), []).append(f)
    for (date, mode, pols), fs in groups.items():
        dest = os.path.join(REPO, "sentinel-1", date, f"{mode}_{pols}"); os.makedirs(dest, exist_ok=True)
        qa = {}
        raw = next((f for f in fs if "VV_(Raw)" in f), None) or next((f for f in fs if f.lower().endswith((".tif", ".tiff"))), None)
        if raw:
            r = rasterio.open(raw); a = r.read(1)
            qa = {"georeferenced": r.crs is not None, "crs": str(r.crs), "pixel_deg": list(r.res),
                  "pixel_m_approx": [round(r.res[0] * 111320 * np.cos(np.radians(52.77)), 1), round(r.res[1] * 110950, 1)],
                  "bounds": [round(v, 5) for v in r.bounds], "covers_points": {}}
            for k, (lo, la) in POINTS.items():
                i, j = r.index(lo, la); qa["covers_points"][k] = bool(0 <= i < a.shape[0] and 0 <= j < a.shape[1] and a[i, j] > 0)
            box = r.read(1, window=from_bounds(*BOX, r.transform), boundless=True, fill_value=0)
            qa["fire_box_valid_frac"] = round(float((box > 0).mean()), 3)
            qa["usable"] = bool(all(qa["covers_points"].values()) and qa["fire_box_valid_frac"] > 0.95)
        vis = next((f for f in fs if "Enhanced_visualization" in f), None)
        prev = []
        if vis:
            r = rasterio.open(vis); x = r.read([1, 2, 3], window=from_bounds(*BOX, r.transform), boundless=True).astype("float32")
            x = np.moveaxis(x, 0, -1); p = np.percentile(x[x > 0], 99.5) if (x > 0).any() else 1
            im = Image.fromarray((np.clip(x / p, 0, 1) * 255).astype("uint8")); im.thumbnail((1200, 1200)); im.save(os.path.join(dest, "preview_enhanced.jpg"), quality=85); prev.append("preview_enhanced.jpg")
        for f in fs: shutil.copy2(f, os.path.join(dest, os.path.basename(f)))
        man = {"source": "Copernicus Browser export (Sentinel Hub), received from Prime Rogue", "date_utc": date, "mode": mode, "polarisations": pols.replace("_", "+"),
               "acquisition": acq or "Not recorded in the export. Sentinel-1 passes over the base near 01:00 UTC (ascending, evening of the previous local day) or 13:30 UTC (descending, morning).",
               "layers": sorted(re.sub(r".*Sentinel-1_[A-Z]{2}_(?:VV_VH|HH_HV|VV|VH|HH|HV)_", "", os.path.splitext(os.path.basename(f))[0]) for f in fs),
               "n_files": len(fs), "qa": qa, "previews": prev, "original_upload": os.path.basename(zin), "original_upload_sha256": sha(zin),
               "files": {os.path.basename(f): {"bytes": os.path.getsize(f), "sha256": sha(f)} for f in fs},
               "licence": "Contains modified Copernicus Sentinel data [2026]"}
        json.dump(man, open(os.path.join(dest, "manifest.json"), "w"), indent=1)
        print(date, mode, pols, len(fs), qa.get("usable"), qa.get("pixel_m_approx"))
    shutil.rmtree(tmp)
if __name__ == "__main__":
    acq = sys.argv[sys.argv.index("--acq") + 1] if "--acq" in sys.argv else None
    main(sys.argv[1], acq)
