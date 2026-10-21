-- Check optional integrations with their actual modules loaded on current Neovim.
vim.opt.runtimepath:prepend(vim.fn.getcwd())
for _, name in ipairs({ "plenary", "oil", "nui", "neo-tree", "which-key", "snacks", "gitsigns", "cmp", "blink" }) do
  vim.opt.runtimepath:append(vim.env.RUNNER_TEMP .. "/" .. name)
end
local ok, err = pcall(function()
  vim.cmd("filetype plugin indent on")
  require("oil").setup({ default_file_explorer = false })
  require("neo-tree").setup({ enable_git_status = false, enable_diagnostics = false })
  require("which-key").setup({ notify = false })
  require("snacks").setup({ picker = { enabled = true } })
  require("gitsigns").setup()
  require("cmp").setup({ sources = {} })
  require("blink.cmp").setup({ fuzzy = { implementation = "lua" }, sources = { default = { "buffer" } } })
  local function number(value) return tonumber(value:sub(2), 16) end
  for _, variant in ipairs({ "dark", "light", "dark" }) do
    vim.o.background = variant
    vim.cmd.colorscheme("verdelle")
    local p = require("verdelle").palette().colors
    for name, role in pairs({
      OilDir = "func", OilFile = "fg", NeoTreeFileName = "fg", WhichKey = "func",
      WhichKeyDesc = "fg", BlinkCmpLabel = "fg", BlinkCmpLabelMatch = "keyword",
      CmpItemAbbr = "fg", CmpItemAbbrMatch = "keyword", GitSignsAdd = "focus", GitSignsDelete = "error",
      SnacksPickerMatch = "keyword", SnacksNormal = "fg",
    }) do
      local attrs = vim.api.nvim_get_hl(0, { name = name, link = false })
      assert(attrs.fg == number(p[role]), name .. " lost its " .. variant .. " foreground")
    end
    require("oil").open(vim.fn.getcwd() .. "/tests/fixtures")
    assert(vim.wait(3000, function() return vim.bo.filetype == "oil" end), "Oil buffer did not open")
    require("oil").close()
    require("neo-tree.command").execute({ action = "show", source = "filesystem", position = "left", dir = vim.fn.getcwd() .. "/tests/fixtures" })
    assert(vim.wait(3000, function()
      for _, win in ipairs(vim.api.nvim_list_wins()) do
        if vim.bo[vim.api.nvim_win_get_buf(win)].filetype == "neo-tree" then return true end
      end
      return false
    end), "Neo-tree window did not open")
    local normal = vim.api.nvim_get_hl(0, { name = "NeoTreeNormal", link = false })
    assert(normal.bg == number(p.panel), "Neo-tree panel color")
    require("neo-tree.command").execute({ action = "close", source = "filesystem" })
    local picker = require("snacks").picker.files({ cwd = vim.fn.getcwd() .. "/tests/fixtures" })
    assert(picker, "Snacks picker did not open")
    vim.wait(300, function() return false end)
    picker:close()
  end
end)
if not ok then
  io.stderr:write(tostring(err) .. "\n")
  vim.cmd("cquit 1")
end
print("Verdelle: explorer rendering and completion/utility plugin colors passed in both variants")
vim.cmd("qa!")
