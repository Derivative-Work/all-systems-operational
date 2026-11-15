#!/usr/bin/env bash
# M2 in one command: the timing map, the shot times, the SRTs and the review video, from the current master.
# Rerun after any change to the master (it isn't locked yet: M1), lyrics/as_sung.txt, config/timing.json or
# config/shot_cues.json. WhisperX alignment needs the GPU for a few seconds (under 1 GB).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
export NLTK_DATA=$PWD/.venv/nltk_data
.venv/bin/python -I scripts/timing_map.py 2>&1 | grep -v -i -e warn -e mel_basis | tee timing/timing_map.log
.venv/bin/python -I scripts/shot_times.py | tee timing/shot_times.log
.venv/bin/python -I scripts/export_srt.py
.venv/bin/python -I scripts/export_srt.py --video
.venv/bin/python -I scripts/m2_review.py
