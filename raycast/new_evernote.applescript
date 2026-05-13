#!/usr/bin/osascript

# @raycast.schemaVersion 1
# @raycast.title Create Focused Evernote
# @raycast.mode silent
# @raycast.packageName Evernote

tell application "System Events"
    tell process "Evernote"
        set frontmost to true
        click menu item "New Note" of menu "File" of menu bar 1
    end tell
end tell

# This delay ensures the window is open before focusing
delay 0.3

tell application "System Events"
    tell process "Evernote"
        set frontmost to true
    end tell
end tell