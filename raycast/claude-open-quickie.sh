#!/bin/bash

# Required Raycast metadata:
# @raycast.schemaVersion 1
# @raycast.title Claude → quickies
# @raycast.mode silent

# Optional Raycast metadata:
# @raycast.icon 🤖
# @raycast.packageName Claude
# @raycast.description If an iTerm window for quickies already exists, focus it. Otherwise open a new iTerm window in ~/mylab/quickies and start Claude Code.

# To make a version for another repo, copy this file and change:
#   - the @raycast.title line
#   - the tagValue (must be unique per script — that's how we find the right window)
#   - the path inside `write text`
# Then re-point Raycast at this folder and assign the new script its own hotkey.

osascript <<'EOF'
tell application "iTerm"
  set tagValue to "claude-quickie"
  set foundSession to missing value

  -- Look through every window/tab/session for one we previously tagged.
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
    -- Window already exists: select that session (which selects its tab + window) and bring iTerm forward.
    tell foundSession to select
    activate
  else
    -- No existing window: make a new one, tag it, and start Claude.
    activate
    create window with default profile
    tell current session of current window
      set variable named "user.claudeTag" to tagValue
      write text "cd /Users/jordanmamroud/mylab/quickies && claude"
    end tell
  end if
end tell
EOF
