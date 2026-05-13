#!/bin/bash

# Required Raycast metadata:
# @raycast.schemaVersion 1
# @raycast.title raypicker
# @raycast.mode compact

# Optional Raycast metadata:
# @raycast.icon 🤖
# @raycast.packageName Claude
# @raycast.argument1 { "type": "dropdown", "placeholder": "project", "data": [{"title":"main","value":"main"},{"title":"quickies","value":"quickies"},{"title":"coding-agent-workflow","value":"coding-agent-workflow"},{"title":"gahelper","value":"gahelper"},{"title":"jm-writer","value":"jm-writer"},{"title":"mybrain","value":"mybrain"},{"title":"mycli","value":"mycli"},{"title":"prompt-tester","value":"prompt-tester"},{"title":"researcher","value":"researcher"}] }
# @raycast.description Open a Claude session in main, quickies, or any main subproject. Run regenerate-project-picker.sh after adding a new project to refresh the dropdown.

input="$1"

# Build candidates: the two top-level folders + every main subfolder
candidates=("main" "quickies")
for d in /Users/jordanmamroud/mylab/main/*/; do
  candidates+=("$(basename "$d")")
done

# Resolve: exact match first, then first prefix match
target_name=""
for name in "${candidates[@]}"; do
  if [ "$name" = "$input" ]; then target_name="$name"; break; fi
done
if [ -z "$target_name" ]; then
  for name in "${candidates[@]}"; do
    if [[ "$name" == "$input"* ]]; then target_name="$name"; break; fi
  done
fi
if [ -z "$target_name" ]; then
  echo "No match: $input"
  exit 1
fi

# Map name to path and per-window tag.
# Matching tags with the dedicated scripts means the picker reuses their windows.
case "$target_name" in
  main)     target_path="/Users/jordanmamroud/mylab/main";     tag="claude-main" ;;
  quickies) target_path="/Users/jordanmamroud/mylab/quickies"; tag="claude-quickies" ;;
  *)        target_path="/Users/jordanmamroud/mylab/main/$target_name"; tag="claude-main-$target_name" ;;
esac

echo "Opening: $target_name"

osascript <<EOF
tell application "iTerm"
  set tagValue to "$tag"
  set foundSession to missing value

  repeat with w in windows
    repeat with t in tabs of w
      repeat with s in sessions of t
        try
          if (variable named "user.claudeTag" of s) is tagValue then
            set foundSession to s
            exit repeat
          end if
        end try
      end repeat
      if foundSession is not missing value then exit repeat
    end repeat
    if foundSession is not missing value then exit repeat
  end repeat

  if foundSession is not missing value then
    tell foundSession to select
    activate
  else
    activate
    create window with default profile
    tell current session of current window
      set variable named "user.claudeTag" to tagValue
      write text "cd $target_path && claude"
    end tell
  end if
end tell
EOF
