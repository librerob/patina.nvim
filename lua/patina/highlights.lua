local M = {}

function M.get(c, opts)
  local groups = {}
  local function hl(name, spec) groups[name] = spec end
  local function link(name, target) groups[name] = { link = target } end
  -- UI
  hl("Normal", { fg = c.variable, bg = c.bg }); link("NormalNC", "Normal")
  hl("NormalFloat", { fg = c.variable, bg = c.float })
  hl("FloatBorder", { fg = c.border, bg = c.float }); hl("FloatTitle", { fg = c.func, bg = c.float, bold = true })
  hl("Cursor", { fg = c.bg, bg = c.cursor }); link("lCursor", "Cursor"); link("CursorIM", "Cursor"); link("TermCursor", "Cursor")
  hl("CursorLine", { bg = c.line }); link("CursorColumn", "CursorLine"); link("ColorColumn", "CursorLine")
  hl("CursorLineNr", { fg = c.func, bold = true }); hl("LineNr", { fg = c.subdued })
  link("LineNrAbove", "LineNr"); link("LineNrBelow", "LineNr")
  hl("SignColumn", { fg = c.subdued }); hl("FoldColumn", { fg = c.subdued }); link("CursorLineFold", "FoldColumn"); link("CursorLineSign", "SignColumn")
  hl("Folded", { fg = c.muted, bg = c.line })
  hl("Visual", { fg = c.selection_fg, bg = c.selection }); link("VisualNOS", "Visual")
  hl("Search", { fg = c.search_fg, bg = c.search_bg })
  hl("CurSearch", { fg = c.search_current_fg, bg = c.search_current_bg, bold = true }); link("IncSearch", "CurSearch"); link("Substitute", "Search")
  hl("MatchParen", { fg = c.func, bg = c.reference, bold = true, underline = true })
  hl("NonText", { fg = c.subdued }); hl("Whitespace", { fg = c.subdued }); hl("SpecialKey", { fg = c.subdued })
  hl("EndOfBuffer", { fg = c.subdued }); hl("Conceal", { fg = c.subdued })
  hl("Directory", { fg = c.func }); hl("Title", { fg = c.func, bold = true })
  hl("ErrorMsg", { fg = c.error, bold = true }); hl("WarningMsg", { fg = c.warning })
  hl("MoreMsg", { fg = c.func }); hl("ModeMsg", { fg = c.variable, bold = true }); hl("Question", { fg = c.func })
  hl("Pmenu", { fg = c.variable, bg = c.float }); hl("PmenuSel", { fg = c.variable, bg = c.menu_selection, bold = true })
  hl("PmenuSbar", { bg = c.line }); hl("PmenuThumb", { bg = c.border }); link("WildMenu", "PmenuSel")
  hl("PmenuMatch", { fg = c.keyword, bg = c.float, bold = true }); hl("PmenuMatchSel", { fg = c.keyword, bg = c.menu_selection, bold = true, underline = true })
  hl("StatusLine", { fg = c.muted, bg = c.panel }); hl("StatusLineNC", { fg = c.comment, bg = c.panel })
  hl("WinSeparator", { fg = c.border }); link("VertSplit", "WinSeparator")
  hl("TabLine", { fg = c.muted, bg = c.panel }); hl("TabLineSel", { fg = c.variable, bg = c.bg, bold = true }); hl("TabLineFill", { bg = c.panel })
  hl("WinBar", { fg = c.muted }); hl("WinBarNC", { fg = c.subdued })
  hl("QuickFixLine", { fg = c.variable, bg = c.menu_selection, bold = true }); hl("Underlined", { fg = c.type, underline = true })
  hl("Ignore", { fg = c.subdued }); hl("Todo", { fg = c.warning, bold = true })
  hl("SpellBad", { sp = c.error, undercurl = true }); hl("SpellCap", { sp = c.warning, undercurl = true })
  hl("SpellRare", { sp = c.type, undercurl = true }); hl("SpellLocal", { sp = c.func, undercurl = true })
  hl("Added", { fg = c.func }); hl("Changed", { fg = c.type }); hl("Removed", { fg = c.error })

  -- Syntax
  hl("Comment", { fg = c.comment, italic = opts.italic_comments })
  hl("Constant", { fg = c.constant }); hl("String", { fg = c.string }); link("Character", "String")
  link("Number", "Constant"); link("Boolean", "Constant"); link("Float", "Constant")
  hl("Identifier", { fg = c.variable }); hl("Function", { fg = c.func })
  hl("Statement", { fg = c.keyword }); for _, g in ipairs({ "Conditional", "Repeat", "Label", "Keyword", "Exception" }) do link(g, "Statement") end
  hl("Operator", { fg = c.operator })
  hl("PreProc", { fg = c.keyword }); for _, g in ipairs({ "Include", "Define", "Macro", "PreCondit" }) do link(g, "PreProc") end
  hl("Type", { fg = c.type }); hl("StorageClass", { fg = c.keyword }); link("Structure", "Type"); link("Typedef", "Type")
  hl("Special", { fg = c.func }); link("SpecialChar", "Special"); hl("Tag", { fg = c.keyword })
  hl("Delimiter", { fg = c.punctuation }); hl("SpecialComment", { fg = c.comment }); hl("Debug", { fg = c.warning })
  hl("Error", { fg = c.error })
  -- The built-in Lua syntax links declarations to Function and braces to Type.
  -- Keep these roles consistent with the Treesitter palette.
  link("luaFunction", "Keyword")
  link("luaTable", "Delimiter")
  link("luaFunc", "Function")

  -- Treesitter
  hl("@variable", { fg = c.variable }); hl("@variable.builtin", { fg = c.type }); hl("@variable.parameter", { fg = c.variable })
  hl("@variable.member", { fg = c.property }); hl("@property", { fg = c.property })
  link("@constant", "Constant"); link("@constant.builtin", "Constant"); link("@constant.macro", "Constant")
  hl("@module", { fg = c.type }); hl("@module.builtin", { fg = c.type }); hl("@label", { fg = c.keyword })
  link("@string", "String"); hl("@string.documentation", { fg = c.comment })
  hl("@string.regexp", { fg = c.func }); hl("@string.escape", { fg = c.func }); hl("@string.special", { fg = c.func })
  hl("@string.special.url", { fg = c.type, underline = true }); link("@character", "String"); hl("@character.special", { fg = c.func })
  link("@boolean", "Constant"); link("@number", "Constant"); link("@number.float", "Constant")
  link("@type", "Type"); link("@type.builtin", "Type"); link("@type.definition", "Type"); hl("@type.qualifier", { fg = c.keyword })
  hl("@attribute", { fg = c.type }); hl("@attribute.builtin", { fg = c.type }); hl("@constructor", { fg = c.type }); hl("@constructor.lua", { fg = c.punctuation })
  for _, g in ipairs({ "@function", "@function.builtin", "@function.call", "@function.macro", "@function.method", "@function.method.call" }) do link(g, "Function") end
  link("@operator", "Operator"); link("@keyword", "Keyword")
  for _, g in ipairs({ "function", "return", "conditional", "repeat", "import", "exception", "operator", "modifier", "type", "coroutine", "directive", "debug" }) do link("@keyword." .. g, "Keyword") end
  hl("@punctuation.delimiter", { fg = c.punctuation }); hl("@punctuation.bracket", { fg = c.punctuation }); hl("@punctuation.special", { fg = c.func })
  link("@comment", "Comment"); link("@comment.documentation", "Comment")
  hl("@comment.error", { fg = c.error, bold = true }); hl("@comment.warning", { fg = c.warning, bold = true })
  hl("@comment.todo", { fg = c.warning, bold = true }); hl("@comment.note", { fg = c.info, bold = true })
  hl("@markup.strong", { bold = true }); hl("@markup.italic", { italic = true }); hl("@markup.strikethrough", { strikethrough = true })
  hl("@markup.underline", { underline = true }); hl("@markup.heading", { fg = c.func, bold = true })
  hl("@markup.link", { fg = c.type, underline = true }); hl("@markup.link.label", { fg = c.type }); hl("@markup.link.url", { fg = c.type, underline = true })
  hl("@markup.raw", { fg = c.string }); hl("@markup.list", { fg = c.keyword }); hl("@markup.quote", { fg = c.comment, italic = true })
  hl("@diff.plus", { fg = c.func }); hl("@diff.minus", { fg = c.error }); hl("@diff.delta", { fg = c.type })
  hl("@tag", { fg = c.keyword }); hl("@tag.attribute", { fg = c.type }); hl("@tag.delimiter", { fg = c.punctuation })
  -- LSP semantic tokens
  for _, g in ipairs({ "class", "enum", "interface", "struct", "type", "typeParameter" }) do link("@lsp.type." .. g, "Type") end
  link("@lsp.type.namespace", "@module"); link("@lsp.type.parameter", "@variable.parameter"); link("@lsp.type.property", "@property")
  link("@lsp.type.function", "Function"); link("@lsp.type.method", "Function"); link("@lsp.type.macro", "@function.macro")
  link("@lsp.type.keyword", "Keyword"); link("@lsp.type.enumMember", "Constant"); link("@lsp.type.decorator", "@attribute")
  hl("@lsp.type.comment", {}); hl("@lsp.type.variable", {}); hl("@lsp.mod.deprecated", { strikethrough = true })

  -- Diagnostics and LSP
  local dg = { Error = c.error, Warn = c.warning, Info = c.info, Hint = c.hint, Ok = c.func }
  for n, col in pairs(dg) do
    hl("Diagnostic" .. n, { fg = col }); hl("DiagnosticVirtualText" .. n, { fg = col }); hl("DiagnosticFloating" .. n, { fg = col })
    hl("DiagnosticSign" .. n, { fg = col }); hl("DiagnosticUnderline" .. n, { sp = col, undercurl = true })
  end
  hl("DiagnosticDeprecated", { strikethrough = true }); hl("DiagnosticUnnecessary", { fg = c.comment })
  hl("LspReferenceText", { bg = c.reference, underline = true }); link("LspReferenceRead", "LspReferenceText"); link("LspReferenceWrite", "LspReferenceText")
  hl("LspInlayHint", { fg = c.comment }); hl("LspCodeLens", { fg = c.comment }); hl("LspCodeLensSeparator", { fg = c.comment })
  hl("LspSignatureActiveParameter", { fg = c.keyword, bold = true, underline = true })

  -- Diff and git
  hl("DiffAdd", { bg = c.diff_add }); hl("DiffChange", { bg = c.diff_change }); hl("DiffDelete", { fg = c.error, bg = c.diff_delete })
  hl("DiffText", { bg = c.diff_text, bold = true })
  hl("diffAdded", { fg = c.func }); hl("diffRemoved", { fg = c.error }); hl("diffChanged", { fg = c.type })
  hl("diffFile", { fg = c.type }); hl("diffLine", { fg = c.comment })
  hl("GitSignsAdd", { fg = c.func }); hl("GitSignsChange", { fg = c.type }); hl("GitSignsDelete", { fg = c.error })

  -- Common plugins
  link("TelescopeNormal", "NormalFloat"); link("TelescopeBorder", "FloatBorder"); hl("TelescopeTitle", { fg = c.func, bold = true })
  hl("TelescopeSelection", { bg = c.menu_selection, bold = true, underline = true }); hl("TelescopeMatching", { fg = c.keyword, bold = true }); hl("TelescopePromptPrefix", { fg = c.keyword })
  hl("WhichKey", { fg = c.func }); hl("WhichKeyDesc", { fg = c.variable }); hl("WhichKeyGroup", { fg = c.type }); hl("WhichKeySeparator", { fg = c.subdued })
  link("BlinkCmpMenu", "Pmenu"); link("BlinkCmpMenuSelection", "PmenuSel"); hl("BlinkCmpLabelMatch", { fg = c.keyword, bold = true, underline = true }); hl("BlinkCmpKind", { fg = c.type })
  hl("CmpItemAbbr", { fg = c.variable }); hl("CmpItemAbbrMatch", { fg = c.keyword, bold = true, underline = true }); hl("CmpItemKind", { fg = c.type }); hl("CmpItemMenu", { fg = c.muted })
  hl("NeoTreeNormal", { fg = c.variable, bg = c.panel }); link("NeoTreeNormalNC", "NeoTreeNormal")
  hl("NeoTreeDirectoryIcon", { fg = c.func }); hl("NeoTreeGitAdded", { fg = c.func }); hl("NeoTreeGitModified", { fg = c.type }); hl("NeoTreeGitDeleted", { fg = c.error })
  hl("IblIndent", { fg = c.border }); hl("IblScope", { fg = c.subdued })


  -- Weight is reserved for control flow; declarations keep the normal weight.
  local control_bold = opts.bold_control_flow and vim.o.background == "light"
  hl("PatinaControlFlow", { fg = c.keyword, bold = control_bold })
  for _, g in ipairs({ "Conditional", "Repeat", "Exception", "@keyword.return", "@keyword.conditional", "@keyword.repeat", "@keyword.exception" }) do
    link(g, "PatinaControlFlow")
  end

  -- Completion uses a quiet selected surface compatible with every item color.
  -- Visual selection has its own stronger pair, independent of syntax colors.
  hl("PmenuKind", { fg = c.type, bg = c.float })
  hl("PmenuKindSel", { fg = c.type, bg = c.menu_selection, bold = true })
  hl("PmenuExtra", { fg = c.muted, bg = c.float })
  hl("PmenuExtraSel", { fg = c.muted, bg = c.menu_selection })
  hl("CmpItemAbbrDeprecated", { fg = c.muted, strikethrough = true })
  link("CmpItemAbbrMatchFuzzy", "CmpItemAbbrMatch")
  for _, g in ipairs({ "BlinkCmpLabel", "BlinkCmpLabelDeprecated", "BlinkCmpLabelDetail", "BlinkCmpLabelDescription", "BlinkCmpSource" }) do
    hl(g, { fg = g == "BlinkCmpLabel" and c.variable or c.muted, strikethrough = g == "BlinkCmpLabelDeprecated" })
  end
  for _, g in ipairs({ "Text", "Method", "Function", "Constructor", "Field", "Variable", "Class", "Interface", "Module", "Property", "Unit", "Value", "Enum", "Keyword", "Snippet", "Color", "File", "Reference", "Folder", "EnumMember", "Constant", "Struct", "Event", "Operator", "TypeParameter" }) do
    hl("BlinkCmpKind" .. g, { fg = c.type })
    hl("CmpItemKind" .. g, { fg = c.type })
  end
  local aliases = {
    BlinkCmpMenuBorder = "FloatBorder", BlinkCmpScrollBarThumb = "PmenuThumb",
    BlinkCmpScrollBarGutter = "PmenuSbar", BlinkCmpDoc = "NormalFloat",
    BlinkCmpDocBorder = "FloatBorder", BlinkCmpDocSeparator = "WinSeparator",
    BlinkCmpDocCursorLine = "CursorLine", BlinkCmpGhostText = "Comment",
    BlinkCmpSignatureHelp = "NormalFloat", BlinkCmpSignatureHelpBorder = "FloatBorder",
    BlinkCmpSignatureHelpActiveParameter = "LspSignatureActiveParameter",
    TelescopePreviewNormal = "NormalFloat", TelescopePromptNormal = "NormalFloat",
    TelescopeResultsNormal = "NormalFloat", TelescopePreviewBorder = "FloatBorder",
    TelescopePromptBorder = "FloatBorder", TelescopeResultsBorder = "FloatBorder",
    NeoTreeFloatNormal = "NormalFloat", NeoTreeFloatBorder = "FloatBorder",
    NeoTreeCursorLine = "QuickFixLine", NeoTreeDirectoryName = "Directory",
    WhichKeyNormal = "NormalFloat", WhichKeyBorder = "FloatBorder",
  }
  for name, target in pairs(aliases) do link(name, target) end
  hl("TelescopeSelectionCaret", { fg = c.func, bg = c.menu_selection, bold = true })
  hl("DiagnosticVirtualTextError", { fg = c.error, underline = true })
  hl("DiagnosticVirtualTextWarn", { fg = c.warning, underline = true })

  return groups
end

return M
