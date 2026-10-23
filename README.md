# CFB Wainwright fire: Sentinel-1 radar imagery

Raw, unmodified Copernicus Sentinel-1 radar exports covering the Oct. 17, 2026 fire at CFB Wainwright, Alberta, kept so anyone can check the analysis in the [CFB Wainwright fire archive](https://github.com/primerogueinc/cfb-wainwright-fire-archive). Optical (Sentinel-2) exports are in the [full Copernicus data repository](https://github.com/primerogueinc/CFB-Wainwright---Full-Satellite-Data---Copernicus-).

Radar sees through cloud and smoke, and burned grass returns a weaker signal than unburned grass, so Sentinel-1 can map the burn on days when optical satellites can't.

Each folder `sentinel-1/<date UTC>/<mode>_<polarisations>/` holds the files exactly as exported from [Copernicus Browser](https://browser.dataspace.copernicus.eu/), a `manifest.json` (SHA-256 of every file, frame, pixel size, coverage of the fire's origin, the Range 2 point and the road head), and a preview.

## Exports

| Date (UTC) | Mode | Polarisations | Files | Covers fire area | Folder |
|---|---|---|---|---|---|
| 2026-10-19 | IW | VV + VH | 8 | Yes, about 10 m pixels | [`sentinel-1/2026-10-19/IW_VV_VH/`](sentinel-1/2026-10-19/IW_VV_VH/) |

**Acquisition time.** Browser exports carry the UTC date, not the time or orbit direction. Over Wainwright, Sentinel-1 passes near 01:00 UTC (ascending; that is the previous evening, local time) or near 13:30 UTC (descending; morning). Where known, the manifest records it.

**First reading, Oct. 19.** Against the burn mapped from Sentinel-2 (Oct. 4 vs Oct. 19), burned ground is darker in radar than unburned ground: median VV −18.7 dB vs −16.8 dB, VH −28.3 dB vs −24.6 dB. Comparing passes with the same orbit before and after the fire will map the burn more sharply.

## Adding an export

```
python3 scripts/ingest.py path/to/Browser_images.zip [--acq "2026-10-19T01:05Z ascending"]
```

## Licence

Scripts and documentation: MIT (see LICENSE). Data: Copernicus Sentinel data are free and open under the [Copernicus data policy](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice); credit "Contains modified Copernicus Sentinel data [2026]" when reusing.

Maintained by Prime Rogue Inc.
