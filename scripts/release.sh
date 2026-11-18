#!/usr/bin/env bash
# The v1.0 release (human interventions 49: "go ahead and prepare the release"), the way the series' earlier videos made
# theirs: the two upload files with their captions and thumbnail, and the production archive git doesn't hold, in tar
# parts under GitHub's 2 GiB per-asset limit. Staged in release/ (git-ignored; the videos hard-linked), then a draft
# GitHub release of this repository, published once the YouTube links are in its notes.
#
#   all_systems_operational_1920x1080.mp4        the main video, the YouTube upload file (renders/m7/master/)
#   all_systems_operational_short_1080x1920.mp4  the Short (renders/vertical/all-systems-operational-short-A.mp4)
#   all_systems_operational.en.srt               the main video's captions (lyrics/as_sung_lines_video.srt)
#   all_systems_operational_thumbnail.jpg        the thumbnail (review/thumbnail/thumbnail.jpg, option P3)
#   All.Systems.Operational.logicx.zip          the human's Logic Pro project for the master, with Suno's stems (the human
#                added it to the draft by hand, human interventions 50; kept as uploaded in audio/logic/). Apple's clap loop
#                is referenced, not included: Logic offers to install Apple's pack when the project opens
#   inputs.tar   the audio git doesn't hold, none of which can be regenerated: audio/track (the human's Logic master with
#                the hard stops), audio/stems (Suno's stems and the v1.3 repaint's lead), audio/postfilter (the
#                post-filtered master and credits music; the post-filter model is private), audio/credits (the credits
#                music as downloaded and as cut for the end sequence), and the earlier masters (archive/audio/v1.2, v1.3)
#   takes.tar    every generated still and clip, used or not (assets/gen, archive/assets/gen: FLUX.2 stills and plates,
#                LTX-2.3 clips, the textures), less the Remotion frame folders, which regenerate
#   SHA256SUMS   for every file above; the files inside the tars are in MANIFEST.sha256
# Left out: the Apple Logic loop (audio/extra/, used under Apple's terms, not offered); the creator's captures and photo
# (assets/screenshots/, remotion/public/real/); the figure library (assets/figures/, rebuilt from blender/ep/ and
# MakeHuman's CC0 assets); renders, frames and review copies, which regenerate from the logged commands; and the
# Claude Code session transcript, which holds the creator's private captures.
#
# Usage: scripts/release.sh [--draft <notes.md>]   (stages release/; --draft also creates the draft release v1.0 with gh)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
TAG=v1.0
R=release
P=all_systems_operational
mkdir -p "$R"
rm -f "$R"/*.mp4 "$R"/*.srt "$R"/*.jpg "$R"/*.tar "$R"/*.zip "$R"/SHA256SUMS
ln renders/m7/master/all-systems-operational-master.mp4 "$R/${P}_1920x1080.mp4"
ln renders/vertical/all-systems-operational-short-A.mp4 "$R/${P}_short_1080x1920.mp4"
cp lyrics/as_sung_lines_video.srt "$R/$P.en.srt"
cp review/thumbnail/thumbnail.jpg "$R/${P}_thumbnail.jpg"
LOGIC=All.Systems.Operational.logicx.zip
ln "audio/logic/$LOGIC" "$R/$LOGIC"
tar -cf "$R/inputs.tar" audio/track audio/stems audio/postfilter audio/credits archive/audio
tar -cf "$R/takes.tar" --exclude='*/frames' assets/gen archive/assets/gen
(cd "$R" && sha256sum "${P}_1920x1080.mp4" "${P}_short_1080x1920.mp4" "$P.en.srt" "${P}_thumbnail.jpg" "$LOGIC" inputs.tar \
  takes.tar > SHA256SUMS)
for f in "$R"/*; do
  (( $(stat -c %s "$f") < 2147483648 )) || { echo "$f is over 2 GiB" >&2; exit 1; }
done
# every file in the tars as the manifest lists it (or in git, as one small record under archive/ is)
for t in inputs takes; do
  tar -tf "$R/$t.tar" | grep -v '/$' | while IFS= read -r f; do
    grep -qF "  $f" MANIFEST.sha256 || git ls-files --error-unmatch "$f" >/dev/null 2>&1 \
      || { echo "$f: not in MANIFEST.sha256 or git" >&2; exit 1; }
  done
done
(grep -F -e "  renders/m7/master/all-systems-operational-master.mp4" -e "  renders/vertical/all-systems-operational-short-A.mp4" \
  -e "  audio/" -e "  archive/audio/" -e "  assets/gen/" -e "  archive/assets/gen/" MANIFEST.sha256 | grep -v -e '/frames/' \
  -e '^[0-9a-f]*  audio/extra/' -e '^[0-9a-f]*  audio/check/' | sha256sum -c --quiet) || { echo "MANIFEST.sha256 is stale" >&2; exit 1; }
ls -l "$R"
cat "$R/SHA256SUMS"
if [[ ${1:-} == --draft ]]; then
  gh release create "$TAG" --draft --target main --title "All Systems Operational v1.0" --notes-file "$2" \
    "$R/${P}_1920x1080.mp4" "$R/${P}_short_1080x1920.mp4" "$R/$P.en.srt" "$R/${P}_thumbnail.jpg" "$R/$LOGIC" \
    "$R/inputs.tar" "$R/takes.tar" "$R/SHA256SUMS"
fi
