#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  export FUNCTION_APP_NAME="<your-function-app-name>"
  export FUNCTION_PROJECT_DIR="src/tools"   # optional

The function project directory must contain host.json.
USAGE
}

require_command() {
  local command_name=$1
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Error: required command '$command_name' is not installed or not on PATH." >&2
    exit 1
  fi
}

require_command func

FUNCTION_APP_NAME="${FUNCTION_APP_NAME:-}"
FUNCTION_PROJECT_DIR="${FUNCTION_PROJECT_DIR:-src/tools}"

if [[ -z "$FUNCTION_APP_NAME" ]]; then
  echo "Error: required environment variable 'FUNCTION_APP_NAME' is not set." >&2
  usage >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if [[ "$FUNCTION_PROJECT_DIR" != /* ]]; then
  FUNCTION_PROJECT_DIR="$repo_root/$FUNCTION_PROJECT_DIR"
fi

host_json="$FUNCTION_PROJECT_DIR/host.json"

if [[ ! -f "$host_json" ]]; then
  echo "Error: unable to find project root. Expected host.json at $host_json" >&2
  usage >&2
  exit 1
fi

echo "Publishing Azure Functions project from $FUNCTION_PROJECT_DIR to $FUNCTION_APP_NAME"
(
  cd "$FUNCTION_PROJECT_DIR"
  func azure functionapp publish "$FUNCTION_APP_NAME" --python
)

echo "Function host URL hint: https://${FUNCTION_APP_NAME}.azurewebsites.net/api/<function-name>?code=<function-key>"
