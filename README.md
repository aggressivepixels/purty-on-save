# Purty on Save

Copy of [Elm Format on Save](https://github.com/evancz/elm-format-on-save) for
[Purty](https://gitlab.com/joneshf/purty).

As the name implies, this plugin runs `purty` whenever you save a PureScript
file. Also, this plugin adds the keyboard shortcut `Alt+Shift+F` to run `purty`
manually.

This plugin will attempt to find a local `purty` installation (i.e. one made
with `npm install [--save|--save-dev] purty`) if an absolute path is not 
specified in it's settings. If a local installation is not found, it will
also check in the directories specified in your `PATH` environment variable.
