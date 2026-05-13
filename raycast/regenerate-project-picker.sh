#!/bin/bash

# Regenerate the @raycast.argument1 dropdown data in claude-open-project.sh
# based on the current contents of ~/mylab/main. Run this after adding (or
# removing) a project in ~/mylab/main so the picker dropdown stays accurate.

set -e

SCRIPT_PATH="/Users/jordanmamroud/mylab/ai-setup/raycast/claude-open-project.sh"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo "Not found: $SCRIPT_PATH"
  exit 1
fi

# Build dropdown data: top-level folders first, then main subfolders alphabetically.
data='[{"title":"main","value":"main"},{"title":"quickies","value":"quickies"}'
for d in /Users/jordanmamroud/mylab/main/*/; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  data+=",{\"title\":\"$name\",\"value\":\"$name\"}"
done
data+=']'

# Replace the existing @raycast.argument1 line in place.
new_line="# @raycast.argument1 { \"type\": \"dropdown\", \"placeholder\": \"project\", \"data\": $data }"
sed -i '' "s|^# @raycast.argument1 .*$|$new_line|" "$SCRIPT_PATH"

count=$(ls -d /Users/jordanmamroud/mylab/main/*/ 2>/dev/null | wc -l | tr -d ' ')
echo "Regenerated picker dropdown: main + quickies + $count subfolders of ~/mylab/main"
