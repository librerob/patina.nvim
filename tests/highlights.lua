-- Run from repository root: nvim --headless -u NONE -l tests/highlights.lua
vim.opt.runtimepath:prepend(vim.fn.getcwd())
local api = vim.api
local function hl(name) return api.nvim_get_hl(0, { name = name, link = false }) end
local function hex(color) return tonumber(color:sub(2), 16) end
local function eq(actual, expected, label)
  assert(vim.deep_equal(actual, expected), label .. ': ' .. vim.inspect(actual) .. ' ~= ' .. vim.inspect(expected))
end
local theme = require('verdelle')
eq(vim.g.colors_name, nil, 'require has no theme side effects')
theme.setup({ italic_comments = true })

for _, mode in ipairs({ 'dark', 'light', 'dark', 'light' }) do
  vim.o.background = mode
  vim.cmd.colorscheme('verdelle')
  local p = theme.palette(mode)
  local c = p.colors
  eq(vim.g.colors_name, 'verdelle', 'theme loaded')
  eq(hl('Normal').bg, hex(c.bg), 'background')
  eq(hl('Comment').italic, true, 'setup before colorscheme')
  eq(hl('Visual').fg, hex(c.selection_fg), 'selection foreground')
  eq(hl('Visual').bg, hex(c.selection), 'selection background')
  eq(hl('PmenuKindSel').fg, hex(c.type), 'selected kind')
  eq(hl('PmenuKindSel').bg, hex(c.menu_selection), 'selected menu surface')
  eq(hl('BlinkCmpKindFunction').fg, hex(c.type), 'blink function kind')
  eq(hl('CmpItemMenu').fg, hex(c.muted), 'cmp source')
  eq(hl('@constructor.lua').fg, hex(c.punctuation), 'Lua braces')
  eq(hl('luaTable').fg, hex(c.punctuation), 'legacy Lua braces')
  eq(hl('luaFunction').fg, hex(c.keyword), 'legacy Lua declaration')
  eq(hl('@keyword.conditional').bold or false, false, 'quiet control-flow default')
  eq(hl('@keyword.function').bold or false, false, 'declaration weight')
  eq(hl('DiagnosticUnderlineError').undercurl, true, 'diagnostic shape cue')
  eq(hl('PmenuMatchSel').underline, true, 'completion match cue')
  local lualine = require('lualine.themes.verdelle')
  eq(lualine.normal.a.bg, c.func, 'lualine follows background')
  for i, value in ipairs(p.ansi) do eq(vim.g['terminal_color_' .. (i-1)], value, 'terminal slot') end
  p.colors.bg = '#FFFFFF'
  assert(theme.palette(mode).colors.bg ~= '#FFFFFF', 'palette must be a defensive copy')
  for name, spec in pairs(require('verdelle.highlights').get(c, theme.options)) do
    if spec.link then assert(next(hl(name)), 'unresolved highlight: ' .. name) end
  end
end

theme.setup({ bold_control_flow = true })
eq(hl('@keyword.conditional').bold, true, 'optional light control-flow emphasis')
eq(hl('@keyword.function').bold or false, false, 'emphasis preserves declaration weight')
theme.setup({ overrides = function(c) return { Comment = { fg = c.string, italic = true } } end })
eq(hl('Comment').fg, hex(theme.palette().colors.string), 'callback override reapplies')
theme.setup({ bold_control_flow = false, overrides = { Function = { fg = '#123456' } } })
eq(hl('Function').fg, hex('#123456'), 'table override')
eq(hl('@keyword.return').bold or false, false, 'control-flow opt-out')
theme.setup()
eq(hl('Comment').italic or false, false, 'reset defaults')
assert(not pcall(theme.setup, { italic_comments = 'yes' }), 'invalid option must fail')
assert(not pcall(theme.palette, 'sepia'), 'invalid variant must fail')

-- OptionSet is disabled during startup. Exercise the installed callback explicitly,
-- then use the UI test for a real post-startup :set background switch.
vim.o.background = 'dark'
api.nvim_exec_autocmds('OptionSet', { pattern = 'background' })
vim.wait(1000, function() return theme._background == 'dark' end)
eq(hl('Normal').bg, hex(theme.palette('dark').colors.bg), 'live background update')
vim.cmd.colorscheme('default')
local old_name = vim.g.colors_name
vim.o.background = 'light'
api.nvim_exec_autocmds('OptionSet', { pattern = 'background' })
vim.wait(30)
eq(vim.g.colors_name, old_name, 'inactive Verdelle does not restore itself')
print('Verdelle module, highlights, options, terminal slots, switching and lualine passed')
vim.cmd('qa!')
