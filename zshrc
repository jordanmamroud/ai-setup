export PATH="$HOME/bin:$PATH"
export PATH="$HOME/mylab/ai-setup/myshortcuts-shell/bin:$HOME/mylab/ai-setup/myshortcuts-shell/bin/aliases:$PATH"


# ========================================
# ZSHRC QUICK REFERENCE (in my GitHub too.)
# ========================================
# Reload this file after change:
#   source ~/.zshrc
# OR restart shell completely:
#   exec zsh
#
# Git shortcuts (now in myshortcuts-shell/bin — run `mycmds` for the full list):
#   gp "commit message"              - add all, commit, push
#   gdf "folder-name" "message"      - delete folder/file, commit, push
#   gnew "repo-name" ["message"]       - init, add all, commit, create repo, push
#
# ones I use a lot
# 	gh repo create
#
# Common Git Shortcuts:
#   gs    - git status
#   ga    - git add
#   gc    - git commit
#   gl    - git log --oneline --graph
#   gco   - git checkout
#   gb    - git branch
#
#
#
# Common terminal commands
# Create a file: touch FILENAME
# create directory (aka folder): mkdir DIRECTORY NAME
# Delete shit file or folder: rm -r FOLDER_OR_FILENAME
#
# rename file locally & in git: git mv old-name.txt new-name.txt
#
#
#
#
#
# ========================================


# Created by `pipx` on 2026-05-08 09:00:39
export PATH="$PATH:/Users/jordanmamroud/.local/bin"


# Claude launchers — quickies is the default scratchpad/navigator,
# main is the explicit "this is a real project" entry point.
# These stay as aliases (not scripts in myshortcuts-shell/bin) because they cd the
# current shell — a subshell script's cd would evaporate on exit.
alias cquickie='cd ~/mylab/quickies && claude'
alias cq='cd ~/mylab/quickies && claude'
alias chub='cd ~/mylab/main && claude'


# Reloads ~/.zshrc into the current shell. Must be a function/alias (not a
# script) because `source` only affects the shell that runs it.
alias refresh='source ~/.zshrc && echo "↻ zshrc reloaded"'


# Wraps the `clone` script (in myshortcuts-shell/bin) so the shell cds into
# the new repo after cloning. The bare script (used from Claude `!`) just
# clones; this function adds the cd that only an interactive shell can do.
clone() {
  if [ -z "${1:-}" ]; then
    command clone   # delegate to script for usage message
    return 1
  fi
  local url="$1"
  url="${url%%/tree/*}"   # strip GitHub web subfolder paths
  url="${url%%/blob/*}"
  url="${url%/}"
  [[ "$url" != *.git ]] && url="${url}.git"
  local repo_name="${url:t:r}"   # zsh: last path segment, drop .git
  command clone "$1" && cd "$repo_name"
}


# ========================================
# Per-project prompt color
# ========================================
# Colors the cwd segment of the prompt by which ~/mylab/<workspace>/<project> you're in.
# Color auto-hashes from the project name (stable: same project always gets the same color).
# Override map below reserves specific colors for specific projects.
autoload -Uz add-zsh-hook
setopt prompt_subst

typeset -g _PROJECT_PROMPT='%1~'

_set_project_prompt() {
  local mylab=$HOME/mylab
  case $PWD in
    $mylab|$mylab/*) ;;
    *) _PROJECT_PROMPT='%1~'; return ;;
  esac

  local rest=${PWD#$mylab/}
  [[ -z $rest || $rest == $PWD ]] && { _PROJECT_PROMPT='%1~'; return; }

  local first=${rest%%/*} project=""
  case $first in
    main|quickies|studying)
      local after=${rest#$first/}
      if [[ -n $after && $after != $rest ]]; then
        project=${after%%/*}
      else
        project=$first
      fi
      ;;
    *) project=$first ;;
  esac

  local color=""
  case $project in
    mygeorge) color="#cba6f7" ;;   # reserved: mauve
  esac

  if [[ -z $color ]]; then
    local -a palette=("#89b4fa" "#a6e3a1" "#fab387" "#f5c2e7" "#94e2d5" "#b4befe" "#f9e2af" "#74c7ec")
    local sum=0 i ch
    for (( i=1; i<=${#project}; i++ )); do
      ch=${project[i]}
      sum=$(( sum + #ch ))
    done
    color=${palette[$(( sum % ${#palette[@]} + 1 ))]}
  fi

  _PROJECT_PROMPT="%F{$color}%1~%f"
}
add-zsh-hook precmd _set_project_prompt

PROMPT='%n@%m ${_PROJECT_PROMPT} %# '
