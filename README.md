# Indonesia Lidar Archaeology Survey

An open, reproducible workflow for finding possible archaeological earthworks in Indonesian airborne lidar:
point cloud → bare-earth DTM → visualisation tiles → visual review → point-cloud verification → systematic
template search. The approach follows Pietro Miotti's lidar search for Maya sites
(https://pietromiotti.com/latest/maya-site/), adapted to open Indonesian data.

## Key result

- **One moderate candidate, L66:** a ring ditch (radius ≈ 33 m) around a raised interior on a river terrace of the
  upper Kapuas near Putussibau, Kapuas Hulu, West Kalimantan (~0.9, 112.8).
  - It is stable under seven different ground classifications of the raw point cloud and is confirmed by ground
    points alone.
  - Its ditch floor is level, unlike every natural gully ring measured the same way.
  - Estimated about 60% likely to be human-made; it needs a field check.
- **A systematic negative:** a template and morphometric search of all 51 NASA CMS 1 m DTMs (plus the L66 lidar strip)
  found no second L66-like feature. About 3,660 tiles were also reviewed visually; 81 other leads were rejected as
  natural, modern or processing artefacts, and one weak mound lead (L77) remains open.
- **Coarse open data has limits:** DEMNAS 8 m and optical imagery resolve only features wider than about 50 m
  under canopy.

Details: [`docs/RESULTS.md`](docs/RESULTS.md). All leads: [`findings/ALL_LEADS.csv`](findings/ALL_LEADS.csv).

## Data sources (not included in the repository)

| Data | Source | Format | Licence / access |
|---|---|---|---|
| Kalimantan airborne lidar 2014, 410 granules (~148 GB) | NASA ORNL DAAC, CMS LiDAR Indonesia (dataset 1518) | LAZ | Open; free Earthdata login; cite the dataset |
| Kalimantan per-polygon 1 m DTMs | NASA ORNL DAAC, CMS LiDAR products (dataset 1540) | GeoTIFF `*_dtm.idw.tif` | Open; free Earthdata login |
| Jambi lidar DTM 2022, 3 areas (~316 km²) | GRO.data doi:10.25625/ONUBEV | 1 m GeoTIFF | CC0 |
| East Kalimantan lidar 2013, 5 logging concessions | KNB doi:10.5063/F1CN71VP | LAS in .rar | Open; see the dataset page for terms |
| DEMNAS 8 m | Badan Informasi Geospasial (BIG) | GeoTIFF, 0.25° tiles | Free registration; BIG terms of use |
| Optical comparison | Esri World Imagery / Wayback, BIG CTSRT orthophotos | Map tiles | Provider terms; imagery shown for comparison only |

Granule lists: [`data_manifests/kalimantan/`](data_manifests/kalimantan/). DEMNAS tiles scanned:
[`data_manifests/demnas_next.txt`](data_manifests/demnas_next.txt).

## Method

1. **LAZ → DTM** ([`scripts/laz_to_dtm.py`](scripts/laz_to_dtm.py), [`scripts/las_to_dtm.py`](scripts/las_to_dtm.py)):
   ground points (class 2), minimum z per 1 m cell, gap filling.
2. **DTM → tiles** ([`scripts/make_tiles.py`](scripts/make_tiles.py)): multi-direction hillshade plus a 25 m local
   relief model; reviewed by eye following [`docs/REVIEW_GUIDE.md`](docs/REVIEW_GUIDE.md)
   (contact sheets: [`scripts/mosaic.py`](scripts/mosaic.py)).
3. **Lead checks:** DTM zooms ([`scripts/zoom.py`](scripts/zoom.py)), optical comparison ([`scripts/esri.py`](scripts/esri.py),
   [`scripts/lead_multidate.py`](scripts/lead_multidate.py)), and point-cloud checks of ground-return density,
   ground-only TIN, canopy height and profiles ([`scripts/lead_triage.py`](scripts/lead_triage.py),
   [`scripts/lead_pc.py`](scripts/lead_pc.py), [`scripts/pc_check.py`](scripts/pc_check.py),
   [`scripts/mound_detail.py`](scripts/mound_detail.py)).
4. **Ring verification:** re-classify ground with several PDAL filters ([`scripts/ground_variants.sh`](scripts/ground_variants.sh)),
   then compare ring geometry ([`scripts/ring_stability.py`](scripts/ring_stability.py), [`scripts/ring_fit.py`](scripts/ring_fit.py)),
   ditch-floor grade ([`scripts/ring_floor.py`](scripts/ring_floor.py), [`scripts/floor_compare.py`](scripts/floor_compare.py))
   and drainage context ([`scripts/ring_hydro.py`](scripts/ring_hydro.py)).
5. **Systematic search:** ring and rectangle templates with morphometric filters ([`scripts/ring_search.py`](scripts/ring_search.py),
   [`scripts/ring_filter.py`](scripts/ring_filter.py), [`scripts/floor_batch.py`](scripts/floor_batch.py)),
   then contact sheets for visual triage ([`scripts/ring_chips.py`](scripts/ring_chips.py)).
6. **Other tools:** automatic mound detector ([`scripts/detect_mounds.py`](scripts/detect_mounds.py), [`scripts/crops.py`](scripts/crops.py));
   DEMNAS and BIG imagery ([`scripts/demnas_viz.py`](scripts/demnas_viz.py), [`scripts/d8_relief.py`](scripts/d8_relief.py),
   [`scripts/d8_win.py`](scripts/d8_win.py), [`scripts/d8_quads.py`](scripts/d8_quads.py), [`scripts/bj_peaks.py`](scripts/bj_peaks.py),
   [`scripts/big_img.py`](scripts/big_img.py), [`scripts/esri_grid.py`](scripts/esri_grid.py)).

## How to run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # PDAL separately (conda-forge) for ground_variants.sh
cp .env.example .env                     # add your NASA Earthdata token
export $(grep -v '^#' .env | xargs)

# one granule -> DTM -> tiles
curl -L -H "Authorization: Bearer $EARTHDATA_TOKEN" -o g.laz \
  https://data.ornldaac.earthdata.nasa.gov/protected/cms/CMS_LiDAR_Indonesia/data/<granule>.laz
python scripts/laz_to_dtm.py g.laz g.tif
python scripts/make_tiles.py g.tif tiles/ g 750

# template search on any 1 m DTM
python scripts/ring_search.py dtm.tif hits.tsv 2
python scripts/ring_filter.py hits_filtered.tsv hits.tsv
python scripts/floor_batch.py hits_filtered.tsv hits_floor.tsv <dtm_dir>
python scripts/ring_chips.py hits_floor.tsv <dtm_dir> sheets/hits 30
```

For bulk processing, [`scripts/kal_pipeline.sh`](scripts/kal_pipeline.sh) (dataset 1518 LAZ) and
[`scripts/kal1540_pipeline.sh`](scripts/kal1540_pipeline.sh) (dataset 1540 DTMs) are resumable download → DTM → tile
pipelines. They read a list of granule names, one per line, from `data/kalimantan/queue.txt` and
`data/kalimantan/queue1540.txt` respectively; build these from the lists in `data_manifests/kalimantan/`.

## Repository layout

- `scripts/`: processing and analysis code (each script documents its arguments in its docstring)
- `docs/`: results, review guide, next steps, candidate regions, figures
- `findings/ALL_LEADS.csv`: every lead that reached the checking stage, with status and assessment
- `data_manifests/`: granule lists and the DEMNAS tile list

## Coordinate policy

Locations in this repository are rounded to **0.1°** (about 11 km), and tile row/column suffixes and pixel positions
are omitted. Figures use axes in metres from the feature centre. Exact coordinates of candidate sites are withheld
to protect them from disturbance and are shared only with the responsible heritage authorities.
