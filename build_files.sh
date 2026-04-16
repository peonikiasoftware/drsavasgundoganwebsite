#!/usr/bin/env bash
# -----------------------------------------------------------------
# Vercel build script — runs inside @vercel/static-build
# -----------------------------------------------------------------
set -e
echo "=== build_files.sh starting ==="
echo "PWD: $(pwd)"
echo "Node: $(node --version 2>&1 || echo MISSING)"
echo "npm:  $(npm --version 2>&1 || echo MISSING)"
echo "ls /usr/bin | grep python:"
ls /usr/bin/ 2>/dev/null | grep -i python || true

# ---------------------------------------------------------------
# 1. Find a usable Python 3.x interpreter (Vercel image has 3.12)
# ---------------------------------------------------------------
PYTHON_BIN=""
for candidate in python3.12 python3.11 python3.10 python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON_BIN=$(command -v "$candidate")
    break
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  echo "FATAL: No Python binary found on PATH"
  exit 1
fi
echo "Using Python: $PYTHON_BIN ($($PYTHON_BIN --version 2>&1))"

# ---------------------------------------------------------------
# 2. Build-time venv + deps
#    (avoids Vercel's uv-managed system Python PEP 668 lock)
# ---------------------------------------------------------------
echo "--- [1/5] create venv + install Python deps ---"
VENV_DIR="$(pwd)/.build_venv"
"$PYTHON_BIN" -m venv "$VENV_DIR"
PY="$VENV_DIR/bin/python"
"$PY" -m pip install --upgrade pip wheel --quiet
"$PY" -m pip install -r requirements.txt --quiet
echo "Django: $("$PY" -c 'import django; print(django.get_version())')"

# ---------------------------------------------------------------
# 3. Frontend (Tailwind)
# ---------------------------------------------------------------
echo "--- [2/5] npm install + build ---"
npm ci --no-audit --no-fund --loglevel=error || npm install --no-audit --no-fund --loglevel=error
npm run build

# ---------------------------------------------------------------
# 4. Django collectstatic → staticfiles_build/static/
# ---------------------------------------------------------------
echo "--- [3/5] collectstatic ---"
export DJANGO_SETTINGS_MODULE=config.settings.prod
mkdir -p staticfiles_build/static
"$PY" manage.py collectstatic --noinput --clear

# ---------------------------------------------------------------
# 5. Migrate + first-run seed (failures are non-fatal — don't
#    break the deploy if DATABASE_URL isn't set yet, etc.)
# ---------------------------------------------------------------
echo "--- [4/5] migrate + seed ---"
"$PY" manage.py migrate --noinput      || echo "WARN: migrate failed — check DATABASE_URL env var."
"$PY" manage.py create_initial_users   || echo "INFO: users already exist or env vars missing."
"$PY" manage.py seed_doctor_data       || echo "WARN: seed failed — run manually later."

# ---------------------------------------------------------------
# 6. compilemessages — gettext missing on Vercel; .mo files are
#    pre-compiled and committed, so this is best-effort.
# ---------------------------------------------------------------
echo "--- [5/5] compilemessages (best-effort) ---"
"$PY" manage.py compilemessages 2>/dev/null || \
  echo "INFO: gettext missing on Vercel — using pre-compiled .mo files from repo."

echo "=== build_files.sh done ==="
