export PATH="$HOME/bin:$PATH"


# ========================================
# ZSHRC QUICK REFERENCE
# ========================================
# Reload this file after changes:
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
