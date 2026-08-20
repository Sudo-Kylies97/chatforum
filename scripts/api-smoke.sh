#!/usr/bin/env sh
set -eu
API_URL="${API_URL:-http://localhost:8000/api/v1}"
COOKIE_FILE="$(mktemp)"
trap 'rm -f "$COOKIE_FILE"' EXIT
CSRF_JSON="$(curl -fsS -c "$COOKIE_FILE" "$API_URL/auth/csrf/")"
CSRF_TOKEN="$(printf '%s' "$CSRF_JSON" | sed -n 's/.*"csrfToken":"\([^"]*\)".*/\1/p')"
curl -fsS -b "$COOKIE_FILE" -c "$COOKIE_FILE" -H "X-CSRFToken: $CSRF_TOKEN" -H 'Content-Type: application/json' -d '{"username":"sam","password":"VerityDemo123!"}' "$API_URL/auth/login/" >/dev/null
RESULT="$(curl -fsS -b "$COOKIE_FILE" -H "X-CSRFToken: $CSRF_TOKEN" -H 'Content-Type: application/json' -d '{"title":"Automated smoke check","body":"This post verifies the documented API from end to end."}' "$API_URL/posts/")"
printf '%s' "$RESULT" | grep -q 'Automated smoke check'
printf 'Verity API smoke test passed.\n'

