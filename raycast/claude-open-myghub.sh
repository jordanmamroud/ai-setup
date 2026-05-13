#!/bin/bash

# Required Raycast metadata:
# @raycast.schemaVersion 1
# @raycast.title Claude → main
# @raycast.mode silent

# Optional Raycast metadata:
# @raycast.icon 🤖
# @raycast.packageName Claude
# @raycast.description If an iTerm window for main already exists, focus it. Otherwise open a new iTerm window in ~/mylab/main and start Claude Code.

osascript <<'EOF'
tell application "iTerm"
  set tagValue to "claude-main"
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
    -- Window already exists: select that session and bring iTerm forward.
    tell foundSession to select
    activate
  else
    -- No existing window: make a new one, tag it, and start Claude.
    activate
    create window with default profile
    tell current session of current window
      set variable named "user.claudeTag" to tagValue
      write text "cd /Users/jordanmamroud/mylab/main && claude"
    end tell
  end if
end tell
EOF
