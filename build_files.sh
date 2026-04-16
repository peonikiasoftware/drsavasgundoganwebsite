#!/usr/bin/env bash
# -----------------------------------------------------------------
# Vercel build script (Python 3.12 + Node 20+)
#
# Runs on every deploy:
#   1. Install Python deps
#   2. Install Node deps + build Tailwind CSS
#   3. Django collectstatic (into ./staticfiles_build/static)
#   4. Django migrate   (Supabase Postgres)
#   5. Django compilemessages — best-effort (gettext may be missing)
# -----------------------------------------------------------------
set -euo pipefail
echo "--- build_files.sh starting ---"

# 1. Python dependencies
echo "[1/5] pip install"
python3.12 -m pip install --upgrade pip
python3.12 -m pip install -r requirements.txt

# 2. Frontend
echo "[2/5] npm install + build"
npm ci --no-audit --no-fund --loglevel=error || npm install --no-audit --no-fund
npm run build

# 3. collectstatic into the directory Vercel routes static/ to
echo "[3/5] collectstatic"
export DJANGO_SETTINGS_MODULE=config.settings.prod
mkdir -p staticfiles_build
python3.12 manage.py collectstatic --noinput --clear

# 4. Migrate the Supabase database
echo "[4/5] migrate"
python3.12 manage.py migrate --noinput || {
  echo "WARN: migrate failed — continuing, you may need to run it manually."
}

# 5. compilemessages is optional; .mo files are pre-compiled and committed.
echo "[5/5] compilemessages (best-effort)"
python3.12 manage.py compilemessages 2>/dev/null || \
  echo "INFO: gettext missing on Vercel — using pre-compiled .mo files from repo."

echo "--- build_files.sh done ---"
