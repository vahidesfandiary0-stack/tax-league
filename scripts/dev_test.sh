#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="raqtiva-payment-test:dfc85a8"
DB_CONTAINER="raqtiva-db-rehearsal"
NETWORK="raqtiva-rehearsal-net"
DB_NAME="taxleague_devtest_$(date +%s)_$$"
CREATED=0

cleanup() {
  if [[ "$CREATED" -eq 1 ]]; then
    docker exec "$DB_CONTAINER" dropdb -U postgres --if-exists "$DB_NAME" >/dev/null
    echo "دیتابیس موقت اختصاصی پاک‌سازی شد."
  fi
}
trap cleanup EXIT

echo "=== RAQTIVA ISOLATED BACKEND TEST ==="

for tool in docker python3; do
  command -v "$tool" >/dev/null || { echo "خطا: $tool موجود نیست."; exit 1; }
done

docker image inspect "$IMAGE" >/dev/null
docker inspect "$DB_CONTAINER" >/dev/null
docker network inspect "$NETWORK" >/dev/null

STATUS="$(docker inspect "$DB_CONTAINER" --format '{{.State.Status}}')"
[[ "$STATUS" == "running" ]] || { echo "خطا: دیتابیس آزمایشی روشن نیست."; exit 1; }

DBPASS="$(docker exec "$DB_CONTAINER" printenv POSTGRES_PASSWORD)"
[[ -n "$DBPASS" ]] || { echo "خطا: رمز دیتابیس دریافت نشد."; exit 1; }

EXISTS="$(docker exec "$DB_CONTAINER" psql -U postgres -d postgres -tAc \
  "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")"
[[ -z "$EXISTS" ]] || { echo "خطا: نام دیتابیس از قبل وجود دارد."; exit 1; }

docker exec "$DB_CONTAINER" createdb -U postgres "$DB_NAME"
CREATED=1

echo "دیتابیس موقت ساخته شد: $DB_NAME"
echo "اجرای آزمون‌ها در کانتینر ایزوله..."

docker run --rm \
  --tmpfs /app/media:rw,nosuid,size=64m,mode=1777 \
  --network "$NETWORK" \
  -v "$ROOT/backend:/app" \
  -w /app \
  -e DJANGO_SETTINGS_MODULE=config.settings.base \
  -e DATABASE_URL="postgresql://postgres:${DBPASS}@${DB_CONTAINER}:5432/${DB_NAME}" \
  "$IMAGE" \
  python manage.py test --verbosity 1

echo "نتیجه: آزمون‌های Backend با موفقیت پایان یافتند."
