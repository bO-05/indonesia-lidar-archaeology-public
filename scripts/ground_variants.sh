#!/bin/bash
# ground_variants.sh in.laz outdir : re-classify ground with PDAL SMRF/CSF variants, write ground LAZ + 0.5 m TIN DTM per setting
# Set PDAL=/path/to/pdal if pdal is not on PATH (e.g. a conda-forge environment).
P=${PDAL:-pdal}; IN=$1; O=$2; mkdir -p $O; B=$(basename $IN .laz)
run() { # name filterjson
  N=$1; F=$2
  cat > $O/$B.$N.json <<J
[ "$IN",
  {"type":"filters.assign","assignment":"Classification[:]=0"},
  {"type":"filters.elm"},
  {"type":"filters.outlier","method":"statistical","mean_k":8,"multiplier":3.0},
  $F,
  {"type":"filters.range","limits":"Classification[2:2]"},
  {"type":"writers.las","filename":"$O/$B.$N.ground.laz","compression":"laszip"},
  {"type":"filters.delaunay"},
  {"type":"filters.faceraster","resolution":0.5},
  {"type":"writers.raster","filename":"$O/$B.$N.dtm05.tif","gdaldriver":"GTiff","gdalopts":"COMPRESS=DEFLATE,TILED=YES"}
]
J
  t0=$SECONDS; $P pipeline $O/$B.$N.json >> $O/log.txt 2>&1 && echo "OK $N $((SECONDS-t0)) s" >> $O/log.txt || echo "FAIL $N" >> $O/log.txt
}
run smrf_def '{"type":"filters.smrf","ignore":"Classification[7:7]"}' &
run smrf_cons '{"type":"filters.smrf","ignore":"Classification[7:7]","slope":0.10,"window":12,"threshold":0.30,"scalar":1.0}' &
run smrf_perm '{"type":"filters.smrf","ignore":"Classification[7:7]","slope":0.25,"window":30,"threshold":0.80,"scalar":1.5}' &
wait
run csf_flat '{"type":"filters.csf","ignore":"Classification[7:7]","resolution":1.0,"rigidness":3,"threshold":0.5,"smooth":true}' &
run csf_relief '{"type":"filters.csf","ignore":"Classification[7:7]","resolution":0.5,"rigidness":1,"threshold":0.3,"smooth":true}' &
run pmf '{"type":"filters.pmf","ignore":"Classification[7:7]","max_window_size":33,"slope":0.5,"initial_distance":0.15,"max_distance":2.5,"cell_size":1}' &
wait
echo ALLDONE >> $O/log.txt
