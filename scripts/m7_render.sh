#!/usr/bin/env bash
# M7: the full Eevee render at 1920x1080 (production log 58+): every Blender sub-shot of the cut at the M7 look
# (blender/coverage_m7.py: M7a-M7d and the v1.3 bridge, config/look_m7.json), JPEG q92 -> renders/m7/frames/<sub>/.
# O22d is the generated clip (m7c.clip_subs), not rendered. One Blender process per build, so a failure costs only that
# build; a build whose log already ends in "done" is skipped, so rerunning the script resumes.
# Logs: log/render_logs/m7_<build>.log (with /usr/bin/time -v), m7_pose_check_<build>.log (the pose report).
# Usage: scripts/m7_render.sh [build ...]   (no args: every build, in coverage.py's order)
#        M7_PASS=m7e scripts/m7_render.sh   (a later pass: its own logs, log/render_logs/<pass>_<build>.log, so the
#        resume check doesn't skip builds the earlier pass finished; move the earlier frames to archive/ first)
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
BUILDS=("$@")
[ ${#BUILDS[@]} -eq 0 ] && BUILDS=(O03 O04 O07 O08 O08c O09 O10 O11 O12 O14 O15 O16 O17 O18 O19a O19b O20 O21 O22)
mkdir -p renders/m7/frames log/render_logs
t0=$(date +%s)
tag=${M7_PASS:-m7}
for b in "${BUILDS[@]}"; do
  lg=log/render_logs/${tag}_$b.log
  if [ -f "$lg" ] && grep -q "M5b build $b done" "$lg"; then echo "$b: done before, skipped"; continue; fi
  tb=$(date +%s)
  /usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7/frames --only "$b" \
    --size 1920x1080 --log "log/render_logs/${tag}_pose_check_$b.log" > "$lg" 2>&1
  rc=$?
  echo "$b: exit $rc, $(( $(date +%s) - tb )) s, $(grep -c '^M5b O' "$lg") sub-shots; $(grep 'Maximum resident' "$lg" | sed 's/^\s*//')"
done
echo "M7 render ($tag): $(( $(date +%s) - t0 )) s; $(find renders/m7/frames -name '*.jpg' | wc -l) frames, $(du -sh renders/m7/frames | cut -f1)"
