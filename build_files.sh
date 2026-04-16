#!/usr/bin/env bash
# -----------------------------------------------------------------
# Vercel build script (Python 3.12 + Node 20+)
#
# NOTE: Vercel's build image uses uv-managed Python where global pip
# is blocked by PEP 668. We create our own venv at build time; the
# @vercel/python runtime still installs requirements.txt into the
# lambda independently.
# -----------------------------------------------------------------
set -euo pipefail
echo "--- build_files.sh starting ---"

# 1. Build-time Python venv + deps
echo "[1/5] create build venv + install Python deps"
python3.12 -m venv /tmp/build_venv
PY="/tmp/build_venv/bin/python"
$PY -m pip install --upgrade pip wheel
$PY -m pip install -r requirements.txt

# 2. Frontend build (Tailwind)
echo "[2/5] npm install + build"
npm ci --no-audit --no-fund --loglevel=error || npm install --no-audit --no-fund
npm run build

# 3. collectstatic into the directory Vercel routes /static/ to
echo "[3/5] collectstatic"
export DJANGO_SETTINGS_MODULE=config.settings.prod
mkdir -p staticfiles_build
$PY manage.py collectstatic --noinput --clear

# 4. Migrate the Supabase database
echo "[4/5] migrate + first-run seed"
$PY manage.py migrate --noinput || {
  echo "WARN: migrate failed — continuing, you may need to run it manually."
}
$PY manage.py create_initial_users || echo "INFO: users already exist."
$PY manage.py seed_doctor_data || echo "WARN: seed failed — run manually."

# 5. compilemessages is optional; .mo files are pre-compiled and committed.
echo "[5/5] compilemessages (best-effort)"
$PY manage.py compilemessages 2>/dev/null || \
  echo "INFO: gettext missing on Vercel — using pre-compiled .mo files from repo."

echo "--- build_files.sh done ---"
