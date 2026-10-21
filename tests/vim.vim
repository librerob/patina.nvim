" Run from the repository root: vim -Nu NONE -n -es -S tests/vim.vim
set nocompatible
execute 'set runtimepath^=' . fnameescape(getcwd())
syntax enable

for s:variant in ['dark', 'light', 'dark']
  let &background = s:variant
  let s:suffix = s:variant ==# 'light' ? '-light' : ''
  let s:data = json_decode(join(readfile('palette/' . s:variant . '.json'), "\n"))
  let s:p = s:data.colors
  let g:verdelle_italic_comments = 1
  colorscheme verdelle
  call assert_equal('verdelle', g:colors_name)
  call assert_equal(s:variant, &background)
  call assert_equal(1, &termguicolors)
  for [s:group, s:role] in items({'Normal': 'fg', 'Comment': 'comment',
        \ 'Keyword': 'keyword', 'Function': 'func', 'String': 'string',
        \ 'Constant': 'constant', 'Type': 'type', 'Operator': 'operator',
        \ 'Delimiter': 'punctuation', 'Error': 'error', 'LspInlayHint': 'comment'})
    call assert_equal(tolower(s:p[s:role]), synIDattr(synIDtrans(hlID(s:group)), 'fg#', 'gui'), s:group)
  endfor
  call assert_equal(tolower(s:p.bg), synIDattr(hlID('Normal'), 'bg#', 'gui'))
  call assert_equal(tolower(s:p.selection_fg), synIDattr(hlID('Visual'), 'fg#', 'gui'))
  call assert_equal(tolower(s:p.selection), synIDattr(hlID('Visual'), 'bg#', 'gui'))
  call assert_equal(tolower(s:p.diff_text), synIDattr(hlID('DiffText'), 'bg#', 'gui'))
  call assert_equal(s:data.ansi, g:terminal_ansi_colors)
  call assert_equal('1', synIDattr(hlID('Comment'), 'italic', 'gui'))
  call assert_equal('', synIDattr(hlID('LspInlayHint'), 'italic', 'gui'))
  let g:verdelle_bold_control_flow = 1
  colorscheme verdelle
  call assert_equal(s:variant ==# 'light' ? '1' : '', synIDattr(synIDtrans(hlID('Conditional')), 'bold', 'gui'))
  let g:verdelle_bold_control_flow = 0
  let g:verdelle_italic_comments = 0
  colorscheme verdelle
  call assert_equal('', synIDattr(hlID('Comment'), 'italic', 'gui'))
endfor

" Changing 'background' reloads the active Vim colorscheme too.
set background=light
call assert_equal('#f6f4eb', synIDattr(hlID('Normal'), 'bg#', 'gui'))
set background=dark
call assert_equal('#101f20', synIDattr(hlID('Normal'), 'bg#', 'gui'))

if !empty(v:errors)
  call writefile(v:errors, '/dev/stderr')
  cquit 1
endif
qa!
