# Lidar tile review guide (Indonesia)

Guide for visual review of DTM visualisation tiles produced by `scripts/make_tiles.py`.

Each PNG is a 750 m x 750 m tile of a 1 m bare-earth lidar DTM (trees removed). Black bar bottom-left = 100 m.
Colouring: grey multi-direction hillshade (2x vertical exaggeration) + local relief: RED = higher than its ~25 m surroundings, BLUE = lower. White = no data.

## What to flag (possible archaeology)
Examples are drawn from Sumatra lowland (Jambi, Batanghari basin) archaeology of the Malayu/Sriwijaya era (7th-14th c.) and earlier/later:
- **Menapo**: small isolated mounds of collapsed brick temples, typically 10-40 m across, 1-5 m high, often roughly square/rectangular, sometimes with a surrounding ditch or low enclosure wall. Usually on levees or slightly raised ground near rivers/old channels.
- **Rectangular enclosures / walls / moats** (parit): straight-sided ditches or banks forming squares/rectangles 30-300 m a side.
- **Kolam / tanks**: regular rectangular hollows (flat bottom, straight edges), e.g. Kolam Telago Rajo at Muara Jambi.
- **Canals**: long, very straight or gently curving linear channels not following natural drainage, sometimes linking rivers.
- **Clusters** of several regular mounds or platforms, causeways, raised paths.
- Hilltop terracing, fortified ridges (benteng) with cross-ditches.
Key cue: straight edges, right angles, regular geometry, repetition – nature rarely makes these.

## What to IGNORE (modern / natural)
- Oil palm & rubber plantation: dense regular grids of small dots/rows, contour terraces, harvesting paths (very common here!).
- Roads, logging tracks, skid trails, field boundaries, drainage ditches in grids, fishponds connected to modern roads, house plots in villages, mining pits (gold mining PETI along rivers), quarries.
- Natural: dendritic valleys, meander scars, oxbows, levees, termite mounds (tiny 1-3 m bumps everywhere), tree-throw pits, sandbars, sinkholes.
- Data artefacts: stripes along flight lines, triangulation facets in data gaps, tile edges.

## Output per tile
For each tile you open, record: tile name, verdict (none / weak / moderate / strong), and for weak+ a short description with approximate pixel position (x,y from top-left, 0-750) and size in metres. Be sceptical: most tiles will be "none". Only "strong" for clear geometric anthropogenic non-modern-looking features.
