local M = {}

local defaults = {
  italic_comments = false,
  bold_control_flow = true,
  overrides = {},
}
M.options = vim.deepcopy(defaults)

function M.setup(opts)
  opts = opts or {}
  assert(type(opts) == "table", "patina.setup expects a table")
  local next_opts = vim.tbl_deep_extend("force", {}, defaults, opts)
  for _, name in ipairs({ "italic_comments", "bold_control_flow" }) do
    assert(type(next_opts[name]) == "boolean", "patina: " .. name .. " must be boolean")
  end
  assert(type(next_opts.overrides) == "table" or type(next_opts.overrides) == "function", "patina: overrides must be a table or function")
  M.options = next_opts
  if vim.g.colors_name == "patina" then M.load() end
end

function M.palette(variant)
  variant = variant or vim.o.background
  assert(variant == "dark" or variant == "light", "patina: variant must be dark or light")
  return vim.deepcopy(require("patina.palette")[variant])
end

function M.load()
  local variant = vim.o.background
  local palette = M.palette(variant)
  local groups = require("patina.highlights").get(palette.colors, M.options)
  local overrides = M.options.overrides
  if type(overrides) == "function" then overrides = overrides(vim.deepcopy(palette.colors)) or {} end
  assert(type(overrides) == "table", "patina: overrides callback must return a table")
  for name, spec in pairs(overrides) do groups[name] = spec end

  vim.cmd("highlight clear")
  if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end
  vim.o.termguicolors = true
  vim.g.colors_name = "patina"
  for name, spec in pairs(groups) do vim.api.nvim_set_hl(0, name, spec) end
  for i, color in ipairs(palette.ansi) do vim.g["terminal_color_" .. (i - 1)] = color end
  M._background = variant
  package.loaded["lualine.themes.patina"] = nil

  local group = vim.api.nvim_create_augroup("PatinaBackground", { clear = true })
  vim.api.nvim_create_autocmd("OptionSet", {
    group = group,
    pattern = "background",
    callback = function()
      vim.schedule(function()
        if vim.g.colors_name == "patina" and vim.o.background ~= M._background then
          vim.cmd.colorscheme("patina")
        end
      end)
    end,
  })
end

return M
