<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/sprout-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/sprout-light.svg">
    <img alt="" src="assets/sprout-light.svg" width="64" height="64">
  </picture>
</p>

<h1 align="center">Verdelle</h1>

<p align="center">Copper and verdigris, on ink and paper.<br>A dark and light colorscheme for editors and terminals.</p>

<p align="center"><strong>Dark</strong> · deep teal, copper keywords, and soft brass strings.</p>

![Verdelle Dark in Neovim](assets/neovim-dark-lua.png)

<p align="center"><strong>Light</strong> · bone paper, terracotta keywords, and verdigris functions.</p>

![Verdelle Light in Neovim](assets/neovim-light-lua.png)

Previews render Neovim's actual screen cells with the built-in Lua syntax. They are not terminal screenshots. [Palette and interface specimens](docs/PREVIEWS.md).

## Install

### Neovim

Neovim 0.10.4+ and a truecolor terminal. With lazy.nvim:

```lua
{
  "librerob/verdelle",
  lazy = false,
  priority = 1000,
  config = function()
    vim.o.background = "dark" -- or "light"
    vim.cmd.colorscheme("verdelle")
  end,
}
```

For a manual install, copy `colors/verdelle.lua` and `lua/` into the corresponding directories in `vim.fn.stdpath("config")`.

Verdelle follows `background`. Switch with `:set background=light` or `:set background=dark`.

Setup is optional, before loading the theme:

```lua
require("verdelle").setup({
  italic_comments = false,
  bold_control_flow = false, -- true adds weight in light mode
})
```

Includes Vim syntax, Treesitter, LSP, diagnostics, diffs, and terminal colors. There are highlight mappings for Telescope, which-key, blink.cmp, nvim-cmp, neo-tree, Oil, Snacks, gitsigns, and indent-blankline. Plugins and language parsers are installed separately. For lualine, set `options.theme = "verdelle"`.

### Vim

Vim 8.2+ with truecolor support, or gVim. Copy [colors/verdelle.vim](colors/verdelle.vim) to `~/.vim/colors/verdelle.vim`, or install this repository through your Vim plugin manager:

```vim
syntax enable
set termguicolors
set background=dark
colorscheme verdelle
```

Use `set background=light` for paper. Optional settings, before loading: `let g:verdelle_italic_comments = 1` and `let g:verdelle_bold_control_flow = 1`. Control-flow weight applies in light mode. The core UI and syntax groups come from the Neovim definitions; token classification depends on Vim's syntax files.

### Terminals

| App | Dark | Light | Setup |
| --- | --- | --- | --- |
| Kitty | [verdelle-dark.conf](ports/kitty/verdelle-dark.conf) | [verdelle-light.conf](ports/kitty/verdelle-light.conf) | Include your chosen file after other color settings. |
| Alacritty | [verdelle-dark.toml](ports/alacritty/verdelle-dark.toml) | [verdelle-light.toml](ports/alacritty/verdelle-light.toml) | Add your chosen file to the existing `[general]` import array. |
| Ghostty | [Verdelle Dark](ports/ghostty/Verdelle%20Dark) | [Verdelle Light](ports/ghostty/Verdelle%20Light) | Copy to your Ghostty `themes` directory, then set `theme = Verdelle Dark` or `theme = Verdelle Light`. |
| Windows Terminal | [Verdelle Dark.json](ports/windows-terminal/Verdelle%20Dark.json) | [Verdelle Light.json](ports/windows-terminal/Verdelle%20Light.json) | Add either object to `schemes`, then choose it in your profile's Appearance settings. |
| Xfce Terminal | [Verdelle Dark.theme](ports/xfce-terminal/Verdelle%20Dark.theme) | [Verdelle Light.theme](ports/xfce-terminal/Verdelle%20Light.theme) | Copy to `~/.config/xfce4/terminal/colorschemes/`, reopen Preferences → Colors, and choose the preset. |
| foot | [verdelle.ini](ports/foot/verdelle.ini) | Both variants in the same file | Include the file as shown below. |
| Konsole | [Verdelle Dark.colorscheme](ports/konsole/Verdelle%20Dark.colorscheme) | [Verdelle Light.colorscheme](ports/konsole/Verdelle%20Light.colorscheme) | Copy to `~/.local/share/konsole/`, then select under Edit Current Profile → Appearance. |

These files set terminal colors. Editor syntax highlighting needs the editor theme too. Terminal variants switch separately from Neovim.

For foot 1.26+, copy `ports/foot/verdelle.ini` to `~/.config/foot/verdelle.ini`. Add this to the main section of `foot.ini`, before other section headers:

```ini
include=~/.config/foot/verdelle.ini
initial-color-theme=dark
```

Use `initial-color-theme=light` for paper. Older foot versions use [verdelle-legacy.ini](ports/foot/verdelle-legacy.ini) or [verdelle-light-legacy.ini](ports/foot/verdelle-light-legacy.ini), without `initial-color-theme`.

Konsole and Windows Terminal control selected-text rendering themselves. Their schemes use supported color keys; selection behavior can differ from the editor ports.

### VS Code

The [VS Code extension](ports/vscode) includes both variants, workbench colors, TextMate scopes, semantic tokens, and terminal palettes. Copy that directory to `~/.vscode/extensions/librerob.verdelle-theme-0.1.0`, reload VS Code, then select **Verdelle Dark** or **Verdelle Light** in **Preferences: Color Theme**. It is not published on the Marketplace.

### More apps

| App | Dark | Light |
| --- | --- | --- |
| Base16 | [verdelle.yaml](ports/base16/verdelle.yaml) | [verdelle-light.yaml](ports/base16/verdelle-light.yaml) |
| bat | [Verdelle Dark.tmTheme](ports/bat/Verdelle%20Dark.tmTheme) | [Verdelle Light.tmTheme](ports/bat/Verdelle%20Light.tmTheme) |
| colorls | [dark_colors.yaml](ports/colorls/dark_colors.yaml) | [light_colors.yaml](ports/colorls/light_colors.yaml) |
| Emacs | [verdelle-theme.el](ports/emacs/verdelle-theme.el) | [verdelle-light-theme.el](ports/emacs/verdelle-light-theme.el) |
| Doom Emacs | [doom-verdelle-theme.el](ports/doom-emacs/doom-verdelle-theme.el) | [doom-verdelle-light-theme.el](ports/doom-emacs/doom-verdelle-light-theme.el) |

[Setup instructions](docs/APPS.md). Base16 includes current and legacy formats; each builder's template decides how its slots are used. colorls uses the matching terminal preset for its ANSI colors.

## Colors

Copper marks keywords, verdigris marks functions, and brass marks strings. Ordinary text stays neutral. Light mode uses deep terracotta keywords, plum constants, and blue types above the lighter teal and brass accents. Extra weight for light-mode control flow is optional.

Selection has its own readable foreground and stronger teal background. Completion uses a quieter surface so matched text, kind labels, and source labels remain visible.

The checks cover **252 text/background pairs**, all at least **4.5:1**, including comments, diffs, search, and completion states. Selected text exceeds **5:1** in both variants. Passive borders, whitespace, and line numbers are deliberate exceptions.

[Dark palette](palette/dark.json) · [Light palette](palette/light.json) · [Design notes](docs/DESIGN.md) · [Color-vision checks](docs/COLORVISION.md)

## Development

`palette/dark.json` and `palette/light.json` are the sources for every port. The build also reads the shared Neovim definitions for Vim. With Python 3.11+:

```sh
python tools/build.py
python tools/build.py --check
python tests/contrast.py
python tests/ports.py
python tests/bat.py
python tests/color_math_test.py
python tools/colorvision.py --check
nvim --headless -u NONE -l tests/highlights.lua
vim -Nu NONE -n -es -S tests/vim.vim
```

CI also runs a real Neovim UI on 0.10.4 and stable, checking six languages, selection, completion, diagnostics, search, diffs, and live switching. CI loads Vim, VS Code, Emacs, Doom Emacs, bat, and colorls; validates foot and Ghostty with their native parsers; queries the running Linux terminals; and checks Windows Terminal against Microsoft's schema. Kitty and Konsole also have rendered color checks. See [test coverage and limits](docs/TESTING.md). [Configuration and overrides](docs/CONFIGURATION.md).

## License

[MIT](LICENSE).
