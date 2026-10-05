# Shared setup for the orchestration scripts (source it). They run either from Windows (Git Bash,
# reaching WSL through wsl.exe) or directly inside WSL; nothing depends on where the repo is cloned.
#   ROOT      project root as this shell sees it
#   WSL_ROOT  the same folder as WSL sees it (/c/Users/... -> /mnt/c/Users/...)
#   C_DRIVE   where the Windows C: drive (holding WSL's virtual disk) is mounted
#   wslrun "<cmd>"         run a shell command in WSL (output without \0 and \r)
#   wsl_exec <cmd> [args]  run a program in WSL
#   start_keepalive        keep WSL from shutting down while we work (sets KEEPALIVE)
#   bootstrap              install the WSL helpers into /tmp, start MinIO
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WSL_DISTRO=${WSL_DISTRO:-Ubuntu-22.04}
if [ -n "${WSL_DISTRO_NAME:-}" ]; then   # already inside WSL
  WSL_ROOT=$ROOT; C_DRIVE=/mnt/c
  wsl_exec() { "$@"; }
  wslrun() { timeout "${WSLRUN_TIMEOUT:-120}" bash -c "$1" | tr -d '\0\r'; }
  # WSL stays up while this terminal is open; only an extra Windows-side process can outlive it
  start_keepalive() {
    if wsl.exe --version > /dev/null 2>&1; then
      wsl.exe -d "$WSL_DISTRO" -- bash -c 'exec sleep infinity' > /dev/null 2>&1 &
    else
      sleep infinity &   # Windows interop unavailable: keep this terminal open
    fi
    KEEPALIVE=$!
  }
else
  WSL_ROOT="/mnt/$(echo "${ROOT:1:1}" | tr '[:upper:]' '[:lower:]')${ROOT:2}"; C_DRIVE=/c
  wsl_exec() { MSYS_NO_PATHCONV=1 wsl.exe -d "$WSL_DISTRO" -- "$@"; }
  wslrun() { MSYS_NO_PATHCONV=1 timeout "${WSLRUN_TIMEOUT:-120}" wsl.exe -d "$WSL_DISTRO" -- bash -c "$1" | tr -d '\0\r'; }
  start_keepalive() {
    MSYS_NO_PATHCONV=1 wsl.exe -d "$WSL_DISTRO" -- bash -c 'exec sleep infinity' > /dev/null 2>&1 &
    KEEPALIVE=$!
  }
fi
bootstrap() { wslrun "sed 's/\r$//' '$WSL_ROOT/tools/wsl/bootstrap.sh' | bash -s '$WSL_ROOT'"; }
