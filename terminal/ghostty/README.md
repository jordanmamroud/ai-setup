# ghostty

Backup / source-of-truth for the Ghostty terminal config. The live file Ghostty actually reads lives at `~/.config/ghostty/config`. This folder mirrors it so changes are tracked in git alongside the rest of the harness.

## Workflow for future changes

1. Edit the live file: `~/.config/ghostty/config`
2. Reload Ghostty: `Cmd+Shift+,` — or **Ghostty → Reload Configuration** in the menu bar if the keybind doesn't fire.
3. Verify the change took effect.
4. Sync the backup:
   ```
   cp ~/.config/ghostty/config ~/mylab/ai-setup/terminal/ghostty/config
   ```

Most options apply on reload. A few (font engine, app runtime) need a full quit — and Ghostty does **not** persist tab/split layouts on restart, so reload over restart whenever possible.

Full option reference: <https://ghostty.org/docs/config/reference>

## What's currently configured

Font, theme (Catppuccin Mocha), padding, opacity, scrollback, plus:

| Setting | Purpose |
|---|---|
| `keybind = super+g=equalize_splits` | Cmd+G evens out pane sizes |
| `split-divider-color = #89b4fa` | Blue line between split panes |
| `unfocused-split-opacity = 0.55` | Dim non-focused panes |
| `unfocused-split-fill = #181825` | Tint color for the dim overlay |

## Known issues

**`unfocused-split-opacity` and `unfocused-split-fill` are broken upstream in Ghostty 1.2.0+** (regression, [Discussion #8732](https://github.com/ghostty-org/ghostty/discussions/8732)). They're left in the config so the dim effect auto-resumes once Ghostty fixes it — until then they are no-ops on macOS Metal.

The visible pane-separation signal today is just `split-divider-color` (the blue divider line).

## Related: per-project prompt color

To compensate for the broken dim feature, the second pane-separation signal lives in zsh: a precmd hook in `~/.zshrc` colors the cwd segment of the prompt by which `~/mylab/<workspace>/<project>` you're in. Color is auto-hashed from the project name (stable: same project = same color forever). One reserved override: `mygeorge` is always mauve.

Source lives in `~/.zshrc` (search for "Per-project prompt color"); the ai-setup backup is at `~/mylab/ai-setup/terminal/zshrc`. To reserve a color for another project, add a line to the `case $project in` block in that function.
