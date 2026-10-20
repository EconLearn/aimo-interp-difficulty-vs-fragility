#!/bin/sh
# Per-case mock tables for the final-shape simulation (lane F2): one fresh mock process per (bundle, configuration, problem,
# speed) on the 50 synthetic new problems at 1.0 / 1.2 / 1.4 / 1.6x (rehearsal/run_per_case.py's per-case mock).
# Run from anywhere; needs calib.json rebuilt (README, first step). PY selects the Python (default: python3).
# With the v95 / v96 code in v95_v96/ (calib.json copied in, README first step) it also builds the v95 / v96 tables;
# V95=DIR points at another folder that holds submission_main/ and submission_small/ (for example ../release_public_v95).
set -e
cd "$(dirname "$0")/../.."
PY=${PY:-python3}
D=rehearsal/final_shape/f2_tables.py
O=${F2_TABLES:-rehearsal/final_shape/tables}
mkdir -p "$O"
"$PY" $D submission_main main "$O/T_v111.json" --workers 5 --new-only
"$PY" $D submission_main main "$O/T_v111nm.json" --set qfin_skip_moot=false --workers 5 --new-only --cfgs Qwen,DeepSeek,low,medium
"$PY" $D submission_small small "$O/T_v112.json" --workers 5 --new-only
"$PY" $D submission_small small "$O/T_v112nm.json" --set qfin_skip_moot=false --workers 5 --new-only --cfgs Qwen,DeepSeek
V95=${V95:-v95_v96}
if [ -f "$V95/submission_main/calib.json" ] && [ -f "$V95/submission_small/calib.json" ]; then
  "$PY" $D "$V95/submission_main" main "$O/T_v95.json" --workers 5 --new-only
  "$PY" $D "$V95/submission_small" small "$O/T_v96.json" --workers 5 --new-only
else
  echo "no calib.json in $V95/submission_main and $V95/submission_small: v95 / v96 tables skipped"
fi
echo "tables in $O"
