# Next steps

1. **Field check of L66 and L77.** Lidar alone cannot separate a dug ring ditch or mound from a natural island or bar
   remnant. A site visit with a hand auger or a small test pit (ditch-fill profile, interior fill versus natural
   terrace or levee sediment, sherds or charcoal) would settle it. Fieldwork should be done with the regional heritage
   authority, and exact locations should not be published.
   To regenerate the evidence from the raw point cloud: download the covering 1518 granule, then run
   `scripts/ground_variants.sh`, `scripts/ring_stability.py`, `scripts/ring_floor.py`, `scripts/ring_hydro.py`,
   `scripts/lead_pc.py`, `scripts/mound_detail.py` and `scripts/ring_fit.py` (see the docstrings for arguments).
2. **Existing lidar held by institutions** (Penanggungan / Arjuno-Welirang, Muara Jambi, Trowulan). The
   review and triage pipeline in this repository can be applied directly to a shared DTM. See
   [`NEXT_REGIONS.md`](NEXT_REGIONS.md).
3. **TanDEM-X 12 m** (free for science via a DLR proposal). Still a DSM, but better than DEMNAS for large earthworks
   under uniform cover; worthwhile only for lowland moat and canal landscapes (Palembang, Air Sugihan, Batanghari),
   where DEMNAS passed its control for features wider than about 50 m.
4. **Other routes:** BIG RBI 1:5,000 lidar DTM through a formal data request, drone lidar over a known landscape with
   a partner institution, and multi-date optical imagery over newly cleared plantations.
5. **Method extensions:** apply `scripts/ring_search.py` (with the level-floor test) to any new 1 m DTM; add templates
   for linear causeways and terrace sequences.
