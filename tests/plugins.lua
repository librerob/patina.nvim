-- Exercise the real plugin consumers rather than just requiring our palette table.
vim.opt.runtimepath:prepend(vim.fn.getcwd())
for _, name in ipairs({ "lualine", "plenary", "telescope" }) do
  vim.opt.runtimepath:append(vim.env.RUNNER_TEMP .. "/" .. name)
end
local ok, err = pcall(function()
  require("telescope").setup({ defaults = { layout_config = { width = 0.8, height = 0.8 } } })
  require("lualine").setup({ options = { theme = "verdelle", icons_enabled = false } })
  local function number(value) return tonumber(value:sub(2), 16) end
  for _, variant in ipairs({ "dark", "light", "dark" }) do
    vim.o.background = variant
    vim.cmd.colorscheme("verdelle")
    vim.wait(100, function() return false end)
    local p = require("verdelle").palette().colors
    for _, mode in ipairs({ "normal", "insert", "visual", "replace", "command" }) do
      local expected = ({ normal = p.func, insert = p.type, visual = p.keyword, replace = p.error, command = p.string })[mode]
      local attrs = vim.api.nvim_get_hl(0, { name = "lualine_a_" .. mode, link = false })
      assert(attrs.bg == number(expected), "lualine stale " .. variant .. " " .. mode)
      assert(attrs.fg == number(p.bg), "lualine foreground " .. mode)
    end
    require("lualine").refresh({ force = true })
    require("telescope.builtin").find_files({ cwd = vim.fn.getcwd() .. "/tests/fixtures" })
    vim.wait(500, function() return false end)
    local picker = require("telescope.actions.state").get_current_picker(vim.api.nvim_get_current_buf())
    assert(picker and picker.results_win, "Telescope picker did not open")
    local normal = vim.api.nvim_get_hl(0, { name = "TelescopeNormal", link = false })
    local selection = vim.api.nvim_get_hl(0, { name = "TelescopeSelection", link = false })
    assert(normal.bg == number(p.float), "Telescope float background")
    assert(selection.bg == number(p.menu_selection), "Telescope selection background")
    local matching = vim.api.nvim_get_hl(0, { name = "TelescopeMatching", link = false })
    assert(matching.fg ~= selection.bg, "Matched text disappears on the selected Telescope result")
    require("telescope.actions").close(vim.api.nvim_get_current_buf())
  end
end)
if not ok then
  io.stderr:write(tostring(err) .. "\n")
  vim.cmd("cquit 1")
end
print("Verdelle: real lualine mode colors and Telescope pickers passed across variant switches")
vim.cmd("qa!")
