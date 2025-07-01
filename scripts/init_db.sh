#!/usr/bin/env bash
# scripts/init_db.sh
set -euo pipefail

docker compose exec -T db bash -c '
psql -U postgres -v ON_ERROR_STOP=1 <<SQL
-- ① роль
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '\''jobint_user'\'') THEN
    CREATE ROLE jobint_user LOGIN PASSWORD '\''Karen_2003'\'';
  END IF;
END
\$\$;

-- ② база
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '\''jobint'\'') THEN
    CREATE DATABASE jobint OWNER jobint_user;
  END IF;
END
\$\$;

-- ③ привилегии (на случай, если база уже была, но права сняли)
GRANT ALL PRIVILEGES ON DATABASE jobint TO jobint_user;
SQL
'
echo "✓ DB & role ok"
