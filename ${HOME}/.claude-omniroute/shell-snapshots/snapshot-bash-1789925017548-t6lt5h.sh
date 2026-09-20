# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
shopt -s expand_aliases
# Check for rg availability
if ! (unalias rg 2>/dev/null; command -v rg) >/dev/null 2>&1; then
  function rg {
  local _cc_bin="${CLAUDE_CODE_EXECPATH:-}"
  [[ -x $_cc_bin ]] || _cc_bin=/c/Users/devr8/.local/bin/claude.exe
  if [[ ! -x $_cc_bin ]]; then command rg ${1+"$@"}; return; fi
  if [[ -n ${ZSH_VERSION:-} ]]; then
    ARGV0=rg "$_cc_bin" ${1+"$@"}
  elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    ARGV0=rg "$_cc_bin" ${1+"$@"}
  else
    (exec -a rg "$_cc_bin" ${1+"$@"})
  fi
}
fi
# Shadow pkill to refuse patterns matching the CLI process
unalias pkill 2>/dev/null || true
function pkill {
  if [ -n "${CLAUDE_PID:-}" ] && [ -r "/proc/${CLAUDE_PID}/comm" ]; then
    local _cc_skip="" _cc_a
    local -a _cc_probe=()
    for _cc_a in ${1+"$@"}; do
      if [ -n "$_cc_skip" ]; then _cc_skip=""; continue; fi
      case "$_cc_a" in
        --signal) _cc_skip=1 ;;
        --signal=*|-e|--echo) ;;
        -[0-9]*) ;;
        -[PUGOF]?*) _cc_probe+=("$_cc_a") ;;
        -[ABCDEFGHIJKLMNOPQRSTUVWXYZ][ABCDEFGHIJKLMNOPQRSTUVWXYZ0-9]*) ;;
        *) _cc_probe+=("$_cc_a") ;;
      esac
    done
    if command pgrep ${_cc_probe[@]+"${_cc_probe[@]}"} 2>/dev/null | command grep -qx "${CLAUDE_PID}"; then
      printf 'pkill: refusing to run — this pattern matches the Claude CLI process (PID %s). Narrow the pattern, or target your own children with `pkill -P $$ ...`.\n' "${CLAUDE_PID}" >&2
      return 1
    fi
  fi
  command pkill ${1+"$@"}
}
export PATH='/c/Users/devr8/bin:/mingw64/bin:/usr/local/bin:/usr/bin:/bin:/mingw64/bin:/usr/bin:/c/Users/devr8/bin:/c/Users/devr8/Downloads/expense-tracker/expense-tracker/venv/Scripts:/c/Users/devr8/AppData/Roaming/Code/User/globalStorage/github.copilot-chat/debugCommand:/c/Users/devr8/AppData/Roaming/Code/User/globalStorage/github.copilot-chat/copilotCli:/c/Program Files/Python314/Scripts:/c/Program Files/Python314:/c/Program Files/Common Files/Oracle/Java/javapath:/c/Windows/system32:/c/Windows:/c/Windows/System32/Wbem:/c/Windows/System32/WindowsPowerShell/v1.0:/c/Windows/System32/OpenSSH:/c/Program Files (x86)/NVIDIA Corporation/PhysX/Common:/cmd:/c/MinGW/bin:/d/bin:/c/Program Files/dotnet:/c/Program Files/NVIDIA Corporation/NVIDIA app/NvDLISR:/c/Program Files/MongoDB/Server/8.2/bin:/c/Program Files/R/R-4.x.x/bin:/c/ProgramData/chocolatey/bin:/c/Program Files/nodejs:/c/Users/devr8/AppData/Local/Android/Sdk/platforms:/c/Users/devr8/AppData/Local/Android/Sdk/platform-tools:/c/Users/devr8/AppData/Local/Android/Sdk:/c/Users/devr8/AppData/Local/Android/Sdk/build-tools:/c/Users/devr8/AppData/Local/Android/Sdk/emulator:/c/Program Files/MySQL/MySQL Server 8.0/bin:/c/Program Files/Docker/Docker/resources/bin:/c/Users/devr8/.local/bin:/d/Anaconda:/d/Anaconda/Library/mingw-w64/bin:/d/Anaconda/Library/usr/bin:/d/Anaconda/Library/bin:/d/Anaconda/Scripts:/c/Users/devr8/AppData/Local/Programs/Trae/bin:/c/Users/devr8/AppData/Local/Programs/Python/Python313/Scripts:/c/Users/devr8/AppData/Local/Programs/Python/Python313:/c/Users/devr8/AppData/Local/Programs/Python/Launcher:/c/Users/devr8/AppData/Local/Microsoft/WindowsApps:/d/Microsoft VS Code/bin:/c/Users/devr8/AppData/Local/Programs/cursor/resources/app/bin:/c/Users/devr8/AppData/Local/Programs/Antigravity/bin:/c/Users/devr8/AppData/Roaming/npm:/c/Program Files/Java/jdk-17/bin:/c/Users/devr8/AppData/Local/Programs/Ollama:/c/Users/devr8/AppData/Local/Programs/Antigravity IDE/bin:/c/Users/devr8/AppData/Local/PowerToys/DSCModules:/c/Users/devr8/.vscode/extensions/ms-python.debugpy-2026.6.0-win32-x64/bundled/scripts/noConfigScripts:/usr/bin/vendor_perl:/usr/bin/core_perl'
