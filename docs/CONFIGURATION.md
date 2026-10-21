# Configuration

Call `require("verdelle").setup()` before `colorscheme verdelle`. Defaults:

```lua
require("verdelle").setup({
  italic_comments = false,
  bold_control_flow = true,
  overrides = {},
})
```

Control-flow emphasis applies in light mode to distinct conditional, loop, return, and exception groups. Exact token coverage follows the syntax engine: some built-in syntax files group returns with other statements.

Override individual highlights with a table or a function:

```lua
require("verdelle").setup({
  overrides = function(colors)
    return { Comment = { fg = colors.comment, italic = true } }
  end,
})
```

Read a defensive copy of either palette with `require("verdelle").palette("dark")` or `palette("light")`. With no argument it returns the active variant. The table has `colors` and a one-indexed `ansi` array; terminal slots 0–15 correspond to array entries 1–16.

Calling `setup()` again resets unspecified options to defaults and reapplies an active Verdelle theme. Palette overrides can change the tested contrast relationships.

For lualine:

```lua
require("lualine").setup({ options = { theme = "verdelle" } })
```
