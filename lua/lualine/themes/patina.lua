local c = require("patina").palette().colors
local function mode(accent)
  return {
    a = { fg = c.bg, bg = accent, gui = "bold" },
    b = { fg = c.variable, bg = c.line },
    c = { fg = c.muted, bg = c.panel },
  }
end
return {
  normal = mode(c.func), insert = mode(c.type), visual = mode(c.keyword),
  replace = mode(c.error), command = mode(c.string), terminal = mode(c.func),
  inactive = {
    a = { fg = c.comment, bg = c.panel },
    b = { fg = c.comment, bg = c.panel },
    c = { fg = c.comment, bg = c.panel },
  },
}
