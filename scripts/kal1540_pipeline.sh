#!/bin/bash
# Resumable: download NASA ORNL dataset 1540 (CMS LiDAR-derived products, Kalimantan 2014) 1 m DTMs
# (Polygon_NNN_utm_ZZ_dtm.idw.tif, whole polygon; ~5.7 GB for the 51 polygons in data/kalimantan/queue1540.txt)
# and tile them. Much cheaper than the 1518 LAZ (~100 GB); covers all remaining 1518 granules.
# Tiles go to tiles/kal1540/kpNNN_utm_ZZ_rRRR_cCCC.png; index CSVs copied to data_manifests/tile_index/.
# Downloader: P parallel curls with stall detection (abort <20 kB/s for 90 s) and resume (-C -); up to 3 rounds
# over the queue. Tiler: tiles whatever is fully downloaded (any order) until every queue item is tiled or failed.
# Stop it cleanly with: kill -- -$(cat data/kalimantan/pipeline1540.pid)   (it runs in its own process group)
# Usage: setsid nohup bash scripts/kal1540_pipeline.sh > data/kalimantan/pipeline1540.log 2>&1 & echo $! > data/kalimantan/pipeline1540.pid
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
set -a; . ./.env; set +a
. .venv/bin/activate
D=data/kalimantan/dtm1540; mkdir -p $D tiles/kal1540 data_manifests/tile_index
URL=https://data.ornldaac.earthdata.nasa.gov/protected/cms/CMS_LiDAR_Products_Indonesia/data
P=${P:-3}; Q=data/kalimantan/queue1540.txt
rm -f $D/*.dlfail $D/*.tilefail
dl() { g=$1; [ -f $D/$g ] && return; for t in 1 2 3 4 5 6; do
  curl -s -f -L --connect-timeout 30 --speed-limit 20000 --speed-time 90 -C - \
    -H "Authorization: Bearer $EARTHDATA_TOKEN" -o $D/$g.part $URL/$g && {
    if python3 -c "import json,os,sys; d=json.load(open('data_manifests/kalimantan/dtm1540_granules.json')); m={v[0]:v[1] for v in d.values()}; sys.exit(abs(os.path.getsize('$D/$g.part')/1e6-m['$g'])>0.01)"; then
      mv $D/$g.part $D/$g; echo "$(date +%H:%M) dl ok $g"; return
    else echo "$(date +%H:%M) size mismatch $g, restarting"; rm -f $D/$g.part; fi; }
  sleep 15; done
  echo "$(date +%H:%M) DLFAIL $g (partial kept for resume)"; touch $D/$g.dlfail; }
export -f dl; export D URL EARTHDATA_TOKEN
( for round in 1 2 3; do rm -f $D/*.dlfail; xargs -P $P -I{} bash -c 'dl {}' < $Q
    ls $D/*.dlfail >/dev/null 2>&1 || break; echo "$(date +%H:%M) download round $round had failures"; done
  touch $D/.dl_finished ) &
rm -f $D/.dl_finished
while :; do
  left=0
  for g in $(cat $Q); do
    p=kp$(echo $g | sed 's/Polygon_//; s/_dtm.idw.tif//')
    [ -f tiles/kal1540/${p}_index.csv ] && continue
    if [ -f $D/$g ]; then
      python scripts/make_tiles.py $D/$g tiles/kal1540 $p 1000 > /tmp/mt_$p.log 2>&1
      if [ -f tiles/kal1540/${p}_index.csv ]; then tail -1 /tmp/mt_$p.log; cp tiles/kal1540/${p}_index.csv data_manifests/tile_index/; echo "$(date +%H:%M) tiled $g"
      else echo "$(date +%H:%M) TILEFAIL $g (corrupt download? deleted; rerun to refetch)"; tail -1 /tmp/mt_$p.log; rm -f $D/$g; touch $D/$g.tilefail; fi
    elif [ ! -f $D/$g.tilefail ]; then left=$((left+1)); fi
  done
  [ $left -eq 0 ] && break
  [ -f $D/.dl_finished ] && { echo "$(date +%H:%M) $left polygons not downloaded (see DLFAIL lines); rerun later"; break; }
  sleep 30
done
wait
echo DONE
