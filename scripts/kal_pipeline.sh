#!/bin/bash
# Resumable NASA CMS Kalimantan pipeline (Nov 2026).
# Parallel downloader (P connections, at most MAXQ LAZ waiting on disk) + one sequential converter
# (memory-safe laz_to_dtm.py + make_tiles.py). Deletes each LAZ after conversion.
# Reads data/kalimantan/queue.txt. A granule is done when tiles/kal2/<prefix>_index.csv exists.
# Usage: nohup bash scripts/kal_pipeline.sh > data/kalimantan/pipeline.log 2>&1 &
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
set -a; . ./.env; set +a
: "${EARTHDATA_TOKEN:?set EARTHDATA_TOKEN in .env}"
. .venv/bin/activate
D=data/kalimantan; mkdir -p $D/laz $D/dtm tiles/kal2 data_manifests/tile_index
P=${P:-3}; MAXQ=${MAXQ:-6}
URL=https://data.ornldaac.earthdata.nasa.gov/protected/cms/CMS_LiDAR_Indonesia/data
pref() { b=${1%.laz}; echo "k$(echo $b | sed 's/Polygon_/k/')"; }
done_g() { [ -f tiles/kal2/$(pref $1)_index.csv ]; }

downloader() {
  for g in $(cat $D/queue.txt); do
    done_g $g && continue
    [ -f $D/laz/$g ] && continue
    while [ $(ls $D/laz | grep -c '\.laz$') -ge $MAXQ ]; do sleep 10; done
    while [ $(ls $D/laz | grep -c "\.part$") -ge $P ]; do sleep 3; done
    touch $D/laz/$g.part
    ( for try in 1 2 3; do
        curl -s -f -L --retry 3 -C - -H "Authorization: Bearer $EARTHDATA_TOKEN" -o $D/laz/$g.part $URL/$g && { mv $D/laz/$g.part $D/laz/$g; echo "$(date +%H:%M) dl ok $g"; exit 0; }
        sleep 20
      done; echo "$(date +%H:%M) DLFAIL $g"; touch $D/laz/$g.dlfail ) &
    sleep 2
  done
  wait
}

downloader &
DLPID=$!
for g in $(cat $D/queue.txt); do
  done_g $g && continue
  while [ ! -f $D/laz/$g ] && [ ! -f $D/laz/$g.dlfail ]; do sleep 10; done
  if [ -f $D/laz/$g.dlfail ]; then echo "SKIP (download failed) $g"; continue; fi
  b=${g%.laz}; out=$D/dtm/$b.tif; p=$(pref $g)
  [ -f $out ] || python scripts/laz_to_dtm.py $D/laz/$g $out 2>&1 | grep -v -i warning
  if [ -f $out ]; then
    python scripts/make_tiles.py $out tiles/kal2 $p 1000 2>&1 | tail -1
    cp tiles/kal2/${p}_index.csv data_manifests/tile_index/ 2>/dev/null
    rm -f $D/laz/$g
    echo "$(date +%H:%M) converted $g"
  else
    echo "$(date +%H:%M) CONVFAIL $g"; mv $D/laz/$g $D/laz/$g.convfail
  fi
done
wait $DLPID
echo DONE
