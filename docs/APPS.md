# More apps

Each port has a dark and light variant generated from the same palettes as Neovim and the terminals.

## Base16

Use [verdelle.yaml](../ports/base16/verdelle.yaml) or [verdelle-light.yaml](../ports/base16/verdelle-light.yaml) with a builder that accepts Tinted Theming's Base16 scheme format. For older builders that expect top-level `base00`–`base0F` keys, use the matching file in [legacy/](../ports/base16/legacy).

The mapping keeps teal ink or bone paper at `base00`, readable comments at `base03`, ordinary text at `base05`, strings at `base0B`, functions at `base0D`, and keywords at `base0E`. `base06` and `base07` share the brightest foreground. A builder's application template decides how these slots are used; this is a semantic Base16 scheme, rather than a copy of the terminal's ANSI slot order.

The files are not yet included in the upstream Tinted scheme collection. Add them as local schemes through your chosen builder.

## bat

From a checkout of this repository:

```sh
mkdir -p "$(bat --config-dir)/themes"
cp ports/bat/*.tmTheme "$(bat --config-dir)/themes/"
bat cache --build
bat --theme="Verdelle Dark" tests/fixtures/index.py
bat --theme="Verdelle Light" tests/fixtures/index.py
```

Use `BAT_THEME="Verdelle Dark"` or `BAT_THEME="Verdelle Light"` to choose a default, or put `--theme="Verdelle Dark"` in bat's config file. Some distributions name the command `batcat`; substitute it in the commands above. Rebuild the cache after updating the files. See [bat's custom-theme instructions](https://github.com/sharkdp/bat#adding-new-themes).

## colorls

Copy the two color files into colorls's config directory:

```sh
mkdir -p ~/.config/colorls
cp ports/colorls/dark_colors.yaml ports/colorls/light_colors.yaml ~/.config/colorls/
colorls --dark
colorls --light
```

Back up existing color files before replacing them. Use the matching Verdelle terminal preset: directories use ANSI cyan, executables use green, errors use red, and ordinary files use the terminal's default foreground. Dark metadata uses ANSI white; light metadata uses the default dark foreground.

colorls 1.5 uses Rainbow 3, which converts HEX colors to its 256-color cube even on a truecolor terminal. This port uses ANSI names so the terminal supplies Verdelle's actual ANSI colors instead. Both the foreground colors and the background therefore depend on your terminal preset. See [colorls's configuration guide](https://github.com/athityakumar/colorls#custom-configurations) and [Rainbow's color handling](https://github.com/ku1ik/rainbow#color-specification).

## Emacs

Emacs 27.1+ with a GUI or truecolor terminal. Copy both files in [ports/emacs](../ports/emacs) to a directory such as `~/.emacs.d/themes/`, then add:

```elisp
(add-to-list 'custom-theme-load-path "~/.emacs.d/themes/")
(load-theme 'verdelle t)
```

For light, use `(load-theme 'verdelle-light t)`. Disable the previous theme when switching, so settings from unrelated themes do not remain layered:

```elisp
(mapc #'disable-theme custom-enabled-themes)
(load-theme 'verdelle-light t)
```

The standalone themes require no theme framework. They include core Font Lock, newer syntax faces, Org, diffs, Magit, completion, inlay hints, and ANSI/vterm colors. Mappings for optional packages take effect when those packages are installed. Comments and inlay hints stay upright. Text rendering and token classification depend on the display and major mode.

## Doom Emacs

The separate [Doom themes](../ports/doom-emacs) use the `doom-themes` framework's palette API and base integrations. Copy both files into your Doom configuration's `themes/` directory, such as `~/.config/doom/themes/` or `~/.doom.d/themes/`. In `config.el`:

```elisp
(add-to-list 'custom-theme-load-path (expand-file-name "themes/" doom-user-dir))
(setq doom-theme 'doom-verdelle)
```

For light, set `doom-theme` to `doom-verdelle-light`. Restart Doom or load the selected theme. The Doom variants share the standalone theme's core faces and add the named colors expected by `doom-color` and Doom integrations. `doom-themes` is the only theme-library dependency; it is normally supplied by Doom's theme module. Exact RGB colors require a GUI or truecolor terminal.

## Validation

The workflow checks both variants through Ruby's YAML parser, bat's native cache and renderer, colorls 1.5.0, and Emacs. Doom tests load the actual `doom-themes` framework at a pinned upstream revision. The Emacs checks cover core faces, readable inlay hints, selections, diffs, ANSI colors, repeated variant switching, and Python Font Lock. The ports have not been visually tested across every application, terminal, major mode, or plugin.

## Port sources

The generators and native application tests were adapted from [Morello](https://github.com/librerob/morello/tree/eaeceaef461a8c3aeaf5ac8d610f005f7bc58038) under the MIT license. Verdelle keeps its own palettes, syntax choices, selection foregrounds, and completion surfaces. Copyright notices are retained in [LICENSE](../LICENSE).
