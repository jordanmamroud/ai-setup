export PATH="$HOME/bin:$PATH"


# ========================================
# ZSHRC QUICK REFERENCE (in my GitHub too.)
# ========================================
# Reload this file after change:
#   source ~/.zshrc
# OR restart shell completely:
#   exec zsh
#
# Git Functions (defined below):
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


# ========================================
# commands for working on .ZSHRC file
# ========================================


#opens .zshrc file in text edit
alias zopen="open -a TextEdit ~/.zshrc"


# Copies your live ~/.zshrc into your GitHub backup file, then stages,
# commits, and pushes that updated file to the ai-setup repo.
zsync() {
  local target="/Users/jordanmamroud/github/ai-setup/zshrc"
  local repo="/Users/jordanmamroud/github/ai-setup"
  local message="${1:-Update zshrc}"

  cp ~/.zshrc "$target" &&
  cd "$repo" &&
  git add zshrc &&
  git commit -m "$message" &&
  git push
}

# ========================================
# commands for working vs code
# ========================================

# Opens VS Code by itself if no repo name is given.
# If you pass a folder name, it opens that folder inside /Users/jordanmamroud/github.
vopen() {
  local repo_name="$1"
  local base_dir="/Users/jordanmamroud/github"

  if [[ -z "$repo_name" ]]; then
    code
  else
    code "$base_dir/$repo_name"
  fi
}



# ========================================
# commands for working working with github
# ========================================

# Adds only changed files, commits, and pushes.
# Usage: gp "commit message"
gp() {
  if [ -z "$1" ]; then
    echo 'Usage: gp "commit message"'
    return 1
  fi

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Not inside a git repository."
    return 1
  fi

  if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "No changed files to commit."
    return 0
  fi

  echo "Changed files:"
  git status --short

  git add -A

  if git diff --cached --quiet; then
    echo "No staged changes to commit."
    return 0
  fi

  git commit -m "$1" && git push
}



#adds all files commits and pushes to git.
gpa() {
  git add . && git commit -m "$1" && git push
}

# Deletes folder from git, commits and pushes. Commit msg optional. ex:gdf subfolder-name "Removed subfolder-name"
gdf() {
  if [ -z "$1" ]; then
    echo 'Usage: gdf <file-or-folder> [commit-message]'
    echo 'Example: gdf "My Folder" "Removed old folder"'
    return 1
  fi

  git rm -r "$1" || return 1

  if [ -n "$2" ]; then
    git commit -m "$2" && git push
  else
    git commit && git push
  fi
}


# Creates a new local git repo, creates the matching GitHub repo, connects them, and pushes main
gnew() {
  # Stop and show help if no repo name was provided
  if [ -z "$1" ]; then
    echo 'Usage: gnew <repo-name> [commit-message]'
    echo 'Example: gnew my-new-repo "Initial commit"'
    return 1
  fi

  # Save the repo name from the first argument
  local repo_name="$1"

  # Build the GitHub URL automatically using your username
  local repo_url="https://github.com/jordanmamroud/$repo_name.git"

  # Initialize git in the current folder
  git init || return 1

  # Rename the current branch to main
  git branch -M main || return 1

  # Stage all files in the current folder
  git add .

  # Only create a commit if there are staged changes
  # This avoids failing with "nothing to commit, working tree clean"
  if ! git diff --cached --quiet; then
    git commit -m "${2:-Initial commit}" || return 1
  fi

  # Create the repo on GitHub
  # This only creates the remote repo; it does not always safely replace an existing origin
  gh repo create "$repo_name" --public || return 1

  # If origin already exists, update it to the new repo URL
  # If origin does not exist yet, add it
  git remote set-url origin "$repo_url" 2>/dev/null || git remote add origin "$repo_url"

  # Push your local main branch to GitHub and set upstream tracking
  git push -u origin main
}


# Renames a tracked file or folder with git mv, auto-detects whether it is a file or folder,
# creates a matching commit message, then commits and pushes the change to GitHub.
grename() {
  # Require exactly 2 arguments: the current path and the new path
  if [ "$#" -ne 2 ]; then
    echo "Usage: g <old-path> <new-path>"
    return 1
  fi

  # Save the two arguments into readable variable names
  local old="$1"
  local new="$2"
  local oldbase newbase kind msg

  # Stop if the original file or folder does not exist
  if [ ! -e "$old" ]; then
    echo "Source not found: $old"
    return 1
  fi

  # Stop if Git is not tracking this path
  if ! git ls-files --error-unmatch "$old" >/dev/null 2>&1; then
    echo "Git is not tracking: $old"
    echo "Run: git add \"$old\" && git commit -m \"Track $old\""
    return 1
  fi

  # Detect whether the source is a folder or a file
  if [ -d "$old" ]; then
    kind="folder"
  else
    kind="file"
  fi

  # Grab just the last part of each path for a clean commit message
  oldbase=$(basename "$old")
  newbase=$(basename "$new")

  # Rename it through Git so the change is tracked properly
  git mv "$old" "$new" || return 1

  # Build the commit message automatically
  if [ "$kind" = "folder" ]; then
    msg="Rename folder $oldbase to $newbase"
  else
    msg="Rename file $oldbase to $newbase"
  fi

  # Commit and push the rename
  git commit -m "$msg"
  git push
}


