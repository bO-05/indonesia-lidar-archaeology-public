# Results

Coordinates are rounded to 0.1°. Lead IDs (`L<n>`) refer to rows of [`findings/ALL_LEADS.csv`](../findings/ALL_LEADS.csv).
Figures use axes in metres from the feature centre.

## Summary

- About 3,660 lidar DTM tiles were reviewed visually (NASA CMS Kalimantan 2014, GRO.data Jambi 2022, KNB East
  Kalimantan 2013), and every open lead was re-checked against the raw point cloud, optical imagery and the literature.
- **One moderate candidate remains: L66**, a ring ditch around a raised interior on a river terrace of the upper
  Kapuas near Putussibau, Kapuas Hulu, West Kalimantan (~0.9, 112.8). We estimate it is about 60% likely to be
  human-made (plausible range 45–70%). Only a field check can confirm it.
- One weak lead remains: L77, a smooth floodplain dome near Loa Janan, Kutai Kartanegara (~-0.8, 116.9).
- A systematic template search of all 1 m DTMs found **no second L66-like feature**. All other leads (82) were
  rejected as natural landforms, modern earthworks or data artefacts.
- Coarser open data (DEMNAS 8 m, optical imagery) passed control tests only for features wider than about 50 m and
  produced no lead.

## 1. Data sources

| Source | What | Access | Verdict |
|---|---|---|---|
| NASA ORNL DAAC CMS datasets 1518 / 1540 | 2014 airborne lidar, Kalimantan (LAZ + 1 m DTM) | Free, Earthdata login | Fully reviewed; mostly logging and peat areas |
| KNB doi:10.5063/F1CN71VP | 2013 lidar, 5 logging concessions, East Kalimantan | Free | Fully reviewed |
| GRO.data ONUBEV / ZFPSYJ | Jambi lidar DTM 2022 / 2020 | ONUBEV open (CC0); ZFPSYJ restricted | ONUBEV reviewed (315 tiles + mound detector) |
| OpenTopography | Indonesian point clouds | Open | Only two small UAS volcano sets |
| BIG DEMNAS public ImageServer | DEM | Open; full 8 m returns NoData, overviews ~16.8 m (Java) / ~67 m (Sumatra) | Too coarse |
| BIG DEMNAS 8 m tiles | Per-tile GeoTIFF, 0.25° tiles | Free registration on the BIG portal | A DSM (IFSAR/TerraSAR-X); resolves features > ~50 m only |
| BIG imagery (CTSRT 0.5 m orthos, 1981–82 aerial photos) | Optical | Open exportImage | Useful on open farmland; fails under canopy |
| BIG RBI 1:5,000 lidar DTM | DTM | Formal data request | Not requested |
| Esri World Imagery + Wayback | Optical, multi-date | Open tiles | Used to screen every lead |
| Planet NICFI | 4.7 m monthly mosaics | Programme ended Jan 2025 | Not usable |
| TanDEM-X 12 m (DLR) | Global DEM | Free for science via proposal | Not used |

## 2. Control tests (does the data show known sites?)

A region was scanned only if known features of the target type were visible.

| Region / data | Control | Result |
|---|---|---|
| Lampung, Esri / CTSRT | Pugung Raharjo ditched enclosure | FAIL (haze) |
| Batujaya, Esri | Known *unur* as tree islands in paddy | PASS (optical); 25 sheets scanned |
| Trowulan, Esri | Canal grid, buried walls | FAIL (only restored monuments show) |
| Palembang, Esri | Karanganyar canals | FAIL (urban) |
| Batujaya, DEMNAS 8 m | 9 *unur* / temples | PARTIAL: only the largest stand out |
| Trowulan, DEMNAS 8 m | Segaran, Tikus, Brahu, canal grid | FAIL (only the 375 × 175 m Segaran pond) |
| Penanggungan, DEMNAS 8 m | Terraced sanctuaries | FAIL (speckle ± 1.5 m, striping) |
| Muara Jambi, DEMNAS 8 m | 17 temples / *menapo* | FAIL (canopy DSM; cleared temples read low) |
| Palembang, DEMNAS 8 m | Karanganyar moated complex | **PASS** for features > ~50 m |
| Kota Kapur, DEMNAS 8 m | Earthen ramparts (~10 m wide) | FAIL / inconclusive |

Figures: [`figures/controls/`](figures/controls/).

## 3. Negative results

- **Visual lidar review:** NASA CMS 1518/1540 (~3,230 tiles), KNB (113 tiles) and GRO.data Jambi (315 tiles). The
  moderate and best weak leads were downgraded after zooms, imagery and point-cloud checks: roads and skid trails,
  canals, a bauxite mine, plantation grids, natural knolls and karst, and vegetation or interpolation artefacts.
  Examples: [`figures/leads/`](figures/leads/).
- **Optical:** at Batujaya, 11 tree islands were checked; all were farmsteads, cemeteries, pond bunds or artefacts.
  Trowulan, Palembang, Air Sugihan and Lampung were closed because their controls failed.
- **DEMNAS 8 m:** 23 tiles (Batujaya, Palembang and 12 further lowland tiles; list in
  [`data_manifests/demnas_next.txt`](../data_manifests/demnas_next.txt)). Only modern drainage and plantation grids,
  natural levees, beach ridges, meanders and valley heads. No lead.
- **Point-cloud triage of all 80 open weak leads** ([`scripts/lead_triage.py`](../scripts/lead_triage.py)): a 0.5 m
  ground-only TIN with local relief, ground-return density, canopy height, profiles and Esri at the same scale.
  78 were rejected: skid trails, roads, drains, borrow pits, settling ponds, houses, natural knolls, valley heads,
  landslips, meander cores (e.g. L32, [`figures/leads/L32_natural_meander_core_analogue.png`](figures/leads/L32_natural_meander_core_analogue.png)),
  TIN spikes, swath edges, and 5 leads outside the lidar coverage.

## 4. L66: verification from the raw point cloud

Data: NASA CMS dataset 1518, granule `Polygon_212_utm_49N_0` (21.3 M points, 7.8 pts/m² around L66) and the adjacent
granule `_1`. The vendor ground classification was replaced by six PDAL ground filters (SMRF default/conservative/permissive,
CSF flat/relief, PMF; [`scripts/ground_variants.sh`](../scripts/ground_variants.sh)), each gridded as a 0.5 m TIN DTM,
and compared with [`scripts/ring_stability.py`](../scripts/ring_stability.py).

| Ground filter | Ground pts | Ditch radius (m) | Closure | Interior above ditch (m) | Outer above ditch (m) | Cut / fill (m³) |
|---|---|---|---|---|---|---|
| Vendor | 15,607 | 32.9 ± 6.2 | 96% | 2.45 | 1.39 | 2,513 / 801 |
| SMRF default | 30,234 | 31.6 ± 5.2 | 100% | 2.63 | 1.45 | 1,861 / 1,162 |
| SMRF conservative | 25,922 | 33.6 ± 5.9 | 100% | 2.60 | 1.47 | 1,987 / 1,169 |
| SMRF permissive | 34,854 | 31.8 ± 6.0 | 100% | 2.59 | 2.18* | 1,467 / 1,094 |
| CSF flat | 25,901 | 32.9 ± 5.4 | 100% | 2.64 | 1.25 | 2,203 / 1,222 |
| CSF relief (1 km crop) | 27,520 | 33.3 ± 6.3 | 100% | 2.63 | 1.43 | 2,265 / 1,169 |
| PMF | 21,931 | 32.7 ± 7.2 | 96% | 2.57 | 2.10* | 1,622 / 978 |

\*Permissive settings admit low vegetation into the ground class, which inflates the outer values.

**Evidence for an earthwork**
- **Stable under every ground filter**; the centre moves less than 1.5 m between versions
  ([`l66_ground_filter_stability.png`](figures/l66/l66_ground_filter_stability.png),
  [`l66_radial_profiles.png`](figures/l66/l66_radial_profiles.png)).
- **Not an interpolation artefact:** using ground points alone, the ditch is lower than both sides in 8–10 of 12
  30° sectors and the interior is higher in all 12. The ditch has real returns (0.2–0.5 pts/m²); 84–95% of ditch
  cells lie within 4 m of a ground point.
- **Level ditch floor:** no grade toward any outlet (amplitude 0.06–0.11 m, permutation p = 0.46–0.75), and about half
  of the ring is a closed depression up to 1.2 m deep. Natural gully rings and interfluves measured the same way all
  slope toward an outlet: a rounded island 250 m away (0.59 m), a gully-ringed knob elsewhere (0.18 m) and two
  interfluves (0.85 m), all p ≤ 0.002 ([`l66_ditch_floor_vs_analogues.png`](figures/l66/l66_ditch_floor_vs_analogues.png);
  [`scripts/ring_floor.py`](../scripts/ring_floor.py)). Given the noise, a grade weaker than about 0.25 m cannot be
  excluded.
- **Raised interior:** the interior stands above the terrace, and the ditch volume is at least the mound volume.
- **Isolated form:** it is the only clean ring in about 45 km² of the same lidar strip (Section 5).
- **Open interior canopy in 2014:** median 8.8 m against 17 m around it, 39% of cells under 3 m
  ([`l66_canopy_context.png`](figures/l66/l66_canopy_context.png)); consistent with an old clearing, though other
  fallow patches nearby look similar.

**Evidence against**
- Gullies of the terrace's dendritic network meet the ring on its east and north-west sides
  ([`l66_drainage.png`](figures/l66/l66_drainage.png); [`scripts/ring_hydro.py`](../scripts/ring_hydro.py)).
- There is no outer bank, and the dome is not flat-topped.
- Ground returns under the forest are sparse.
- Gully-ringed knobs are a common natural form elsewhere (Section 5).

Earlier figures: [`l66_ring_ditch_pointcloud.png`](figures/l66/l66_ring_ditch_pointcloud.png),
[`l66_ring_ditch_detail.png`](figures/l66/l66_ring_ditch_detail.png), [`l66_context_1km.png`](figures/l66/l66_context_1km.png).

Context: ditched and palisaded settlements (*kuta*) are documented for Dayak groups elsewhere in Kalimantan, for
example Kuta Hantapang in Central Kalimantan (14th–19th century). No site is recorded at this location in the
Kapuas Hulu cultural-heritage (*cagar budaya*) lists we consulted.

**Assessment: moderate candidate, about 60% likely human-made.** Recommended next step: a field check with a hand
auger or small test pit across the ditch (ditch-fill profile, interior fill versus natural terrace sediment, any
sherds or charcoal), carried out with the regional heritage authority.

## 5. Systematic search for L66-like features

- **Detector** ([`scripts/ring_search.py`](../scripts/ring_search.py)): annular templates (ring radius 15–60 m) and
  rotated square-annulus templates (half-side 15–60 m) at 2 m resolution, followed by per-ray morphometry (closure,
  radius CV, interior and outer height above the ditch, an outward-channel "leak" test, cut/fill, slope, relief).
  Run on our own DTM, it recovers L66 (radius 33 m, closure 0.96, radius CV 0.12).
- **Filters** ([`scripts/ring_filter.py`](../scripts/ring_filter.py)) calibrated on L66, then the ditch-floor grade
  test ([`scripts/floor_batch.py`](../scripts/floor_batch.py)), then visual triage
  ([`scripts/ring_chips.py`](../scripts/ring_chips.py)).
- **All 51 dataset-1540 DTMs plus 3 earlier 1518 DTMs:** 109,902 raw peaks → 131 filtered hits → 10 with a level floor.
  The top 30 ([`dtm1540_top30_*.png`](figures/search/)), the 15 most L66-like hits on flat ground
  ([`dtm1540_flat_*.png`](figures/search/)) and the 10 level-floor hits
  ([`dtm1540_level_floor.png`](figures/search/dtm1540_level_floor.png)) were all natural or modern: gully-encircled
  knobs and interfluves in dissected terrain, meander loops, channel banks, a canal junction, peat-swamp DTM speckle
  and interpolation facets. The rectangular templates found no rectilinear enclosure.
- **The L66 lidar strip** (granules 212_0 to 212_4, about 45 km² along the Kapuas): in granules 0 and 1 the only clean
  ring is L66 ([`same_terrace_hits_*.png`](figures/search/)). Granules 2–4 gave 16 filtered hits, 2 with a level floor;
  both were checked in the point cloud and rejected (a branching gully network and a meander scar;
  [`l66_strip_level_floor_rejects.png`](figures/search/l66_strip_level_floor_rejects.png),
  [`l66_strip_hits_*.png`](figures/search/)).

**No new candidate.** L66 is the only feature that passes every automatic filter and the level-floor test and
survives visual checks.

## 6. Open leads

| ID | Location (0.1°) | Status | Summary |
|---|---|---|---|
| L66 | Putussibau Utara, Kapuas Hulu (~0.9, 112.8) | Moderate | Ring ditch (r ≈ 33 m) around a raised interior; level ditch floor; field check recommended |
| L77 | Loa Janan, Kutai Kartanegara (~-0.8, 116.9) | Weak | Smooth dome ~30 m across, 2.3 m high, on real ground; natural bar remnant equally plausible ([figure](figures/leads/open_lead_loa_janan_mound_detail.png)) |
