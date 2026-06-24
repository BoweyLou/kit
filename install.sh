#!/usr/bin/env sh
set -eu

REPO_URL="${REPO_CONTRACT_KIT_REPO_URL:-https://github.com/BoweyLou/kit.git}"
REF="${REPO_CONTRACT_KIT_REF:-main}"
WORKFLOW_REPO_URL="${AGENT_WORKFLOW_KIT_REPO_URL:-https://github.com/BoweyLou/agent-workflow-kit.git}"
WORKFLOW_REF="${AGENT_WORKFLOW_KIT_REF:-main}"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
INSTALL_DIR="${REPO_CONTRACT_KIT_HOME:-$DATA_HOME/kit/source}"
WORKFLOW_INSTALL_DIR="${AGENT_WORKFLOW_KIT_HOME:-$DATA_HOME/agent-workflow-kit/source}"
BIN_DIR="${REPO_CONTRACT_KIT_BIN_DIR:-$HOME/.local/bin}"
COMMAND_NAME="${KIT_COMMAND:-${REPO_CONTRACT_KIT_COMMAND:-kit}}"
SOURCE_DIR="${REPO_CONTRACT_KIT_SOURCE:-}"
WORKFLOW_SOURCE_DIR="${AGENT_WORKFLOW_KIT_SOURCE:-}"
INSTALL_WORKFLOW=0

usage() {
  cat <<'USAGE'
Usage: install.sh [options]

Install the global kit launcher. The launcher points at a cached kit checkout
outside target repositories. The optional workflow
source checkout is maintainer-only and opt-in.

Options:
  --source PATH              Use an existing local kit checkout.
  --install-dir PATH         Cached kit path. Default: ~/.local/share/kit/source
  --repo-url URL             kit Git URL.
  --ref REF                  kit branch or tag. Default: main
  --with-workflow            Also provision workflow source for maintainer work.
  --workflow-source PATH     Use an existing local workflow source checkout.
  --workflow-install-dir PATH Cached workflow source path. Default: ~/.local/share/agent-workflow-kit/source
  --workflow-repo-url URL    Workflow source Git URL.
  --workflow-ref REF         Workflow source branch or tag. Default: main
  --no-workflow              Compatibility no-op; workflow provisioning is already off by default.
  --bin-dir PATH             Launcher directory. Default: ~/.local/bin
  --command-name NAME        Launcher name. Default: kit
  -h, --help                 Show this help.

After install, run this inside each target repo:
  kit setup
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --source)
      SOURCE_DIR="${2:?missing value for --source}"
      shift 2
      ;;
    --workflow-source)
      WORKFLOW_SOURCE_DIR="${2:?missing value for --workflow-source}"
      INSTALL_WORKFLOW=1
      shift 2
      ;;
    --install-dir)
      INSTALL_DIR="${2:?missing value for --install-dir}"
      shift 2
      ;;
    --workflow-install-dir)
      WORKFLOW_INSTALL_DIR="${2:?missing value for --workflow-install-dir}"
      INSTALL_WORKFLOW=1
      shift 2
      ;;
    --bin-dir)
      BIN_DIR="${2:?missing value for --bin-dir}"
      shift 2
      ;;
    --repo-url)
      REPO_URL="${2:?missing value for --repo-url}"
      shift 2
      ;;
    --workflow-repo-url)
      WORKFLOW_REPO_URL="${2:?missing value for --workflow-repo-url}"
      INSTALL_WORKFLOW=1
      shift 2
      ;;
    --ref)
      REF="${2:?missing value for --ref}"
      shift 2
      ;;
    --workflow-ref)
      WORKFLOW_REF="${2:?missing value for --workflow-ref}"
      INSTALL_WORKFLOW=1
      shift 2
      ;;
    --with-workflow)
      INSTALL_WORKFLOW=1
      shift
      ;;
    --command-name)
      COMMAND_NAME="${2:?missing value for --command-name}"
      shift 2
      ;;
    --no-workflow)
      INSTALL_WORKFLOW=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

need_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

resolve_dir() {
  mkdir -p "$1"
  (cd "$1" && pwd -P)
}

need_command git
need_command python3

checkout_source() {
  label="$1"
  source_dir="$2"
  install_dir="$3"
  repo_url="$4"
  ref="$5"
  marker="$6"
  alternate_marker="$7"

  if [ -n "$source_dir" ]; then
    source_dir="$(cd "$source_dir" && pwd -P)"
    if [ ! -e "$source_dir/$marker" ] && { [ -z "$alternate_marker" ] || [ ! -e "$source_dir/$alternate_marker" ]; }; then
      echo "Source does not look like $label: $source_dir" >&2
      exit 1
    fi
    echo "$source_dir"
  else
    parent_dir="$(dirname "$install_dir")"
    mkdir -p "$parent_dir"
    if [ -d "$install_dir/.git" ]; then
      if ! git -C "$install_dir" diff --quiet || ! git -C "$install_dir" diff --cached --quiet; then
        echo "Cached $label checkout has local changes: $install_dir" >&2
        echo "Commit/stash them, or choose another install directory." >&2
        exit 1
      fi
      git -C "$install_dir" fetch --depth 1 origin "$ref"
      git -C "$install_dir" checkout -q --detach FETCH_HEAD
    elif [ -e "$install_dir" ]; then
      echo "Install directory exists but is not a git checkout: $install_dir" >&2
      exit 1
    else
      git clone --depth 1 --branch "$ref" "$repo_url" "$install_dir"
    fi
    (cd "$install_dir" && pwd -P)
  fi
}

INSTALL_DIR="$(checkout_source "repo-contract-kit" "$SOURCE_DIR" "$INSTALL_DIR" "$REPO_URL" "$REF" "scripts/repo_contract_kit.py" "")"
if [ "$INSTALL_WORKFLOW" = "1" ]; then
  WORKFLOW_INSTALL_DIR="$(checkout_source "agent-workflow-kit" "$WORKFLOW_SOURCE_DIR" "$WORKFLOW_INSTALL_DIR" "$WORKFLOW_REPO_URL" "$WORKFLOW_REF" "workflows/manifest.json" "workflows/prompts")"
else
  WORKFLOW_INSTALL_DIR=""
fi

BIN_DIR="$(resolve_dir "$BIN_DIR")"
launcher="$BIN_DIR/$COMMAND_NAME"

launcher_is_owned() {
  path="$1"
  [ -f "$path" ] && grep -q "repo_contract_kit.py" "$path" 2>/dev/null
}

if [ -e "$launcher" ] && ! launcher_is_owned "$launcher"; then
  echo "Existing launcher is not owned by repo-contract-kit: $launcher" >&2
  echo "Choose another name with --command-name NAME or KIT_COMMAND=NAME." >&2
  exit 1
fi

cat > "$launcher" <<EOF
#!/usr/bin/env sh
AGENT_WORKFLOW_KIT_VALUE="$WORKFLOW_INSTALL_DIR"
if [ -n "\$AGENT_WORKFLOW_KIT_VALUE" ]; then
  export AGENT_WORKFLOW_KIT="\$AGENT_WORKFLOW_KIT_VALUE"
fi
exec python3 "$INSTALL_DIR/scripts/repo_contract_kit.py" "\$@"
EOF
chmod 755 "$launcher"

echo "Installed $COMMAND_NAME -> $launcher"
echo "repo-contract-kit source: $INSTALL_DIR"
if [ -n "$WORKFLOW_INSTALL_DIR" ]; then
  echo "workflow source: $WORKFLOW_INSTALL_DIR"
fi
"$launcher" version
echo ""
echo "Add $BIN_DIR to PATH if needed."
echo "Then, inside each target repo:"
echo "  $COMMAND_NAME setup"
echo "  (two words; not $COMMAND_NAME-setup)"
echo "For agents: resolve the launcher with 'command -v $COMMAND_NAME', then run '$COMMAND_NAME setup'."
echo ""
echo "Later updates use:"
echo "  $COMMAND_NAME update --global"
echo "  $COMMAND_NAME update"
