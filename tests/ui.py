"""Exercise a real Neovim UI, check composed colors, and save cell-grid renders.

Requires msgpack and Pillow. The captures render Neovim's emitted screen cells;
they are not screenshots of a terminal application.
"""
from pathlib import Path
import copy
import json
import os
import queue
import subprocess
import threading
import time

import msgpack
from PIL import Image, ImageDraw, ImageFont
from contrast import contrast

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'test-results'
OUT.mkdir(exist_ok=True)

class Neovim:
    def __init__(self):
        self.proc = subprocess.Popen(['nvim', '--embed', '--headless', '-u', 'NONE', '-n'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
        self.lock = threading.RLock()
        self.pending = {}
        self.next_id = 0
        self.grid = []
        self.attrs = {0: {}}
        self.defaults = {'foreground': 0xFFFFFF, 'background': 0}
        self.events = []
        self.reader = threading.Thread(target=self.read, daemon=True)
        self.reader.start()

    def read(self):
        unpacker = msgpack.Unpacker(raw=False, strict_map_key=False)
        while True:
            chunk = os.read(self.proc.stdout.fileno(), 65536)
            if not chunk:
                return
            unpacker.feed(chunk)
            for message in unpacker:
                if message[0] == 1:
                    self.pending[message[1]].put(message[2:])
                elif message[0] == 2 and message[1] == 'redraw':
                    with self.lock:
                        for event, *calls in message[2]:
                            for args in calls:
                                self.apply(event, args)

    def apply(self, event, args):
        if event == 'grid_resize':
            _, width, height = args
            self.grid = [[(' ', 0) for _ in range(width)] for _ in range(height)]
        elif event == 'grid_clear':
            self.grid = [[(' ', 0) for _ in row] for row in self.grid]
        elif event == 'default_colors_set':
            self.defaults = {'foreground': args[0], 'background': args[1]}
        elif event == 'hl_attr_define':
            self.attrs[args[0]] = args[1]
        elif event == 'grid_line':
            _, row, start, cells, *_ = args
            attr, col = 0, start
            for cell in cells:
                text = cell[0]
                if len(cell) > 1:
                    attr = cell[1]
                for _ in range(cell[2] if len(cell) > 2 else 1):
                    self.grid[row][col] = (text, attr)
                    col += 1
        elif event == 'grid_scroll':
            _, top, bottom, left, right, rows, _ = args
            old = copy.deepcopy(self.grid)
            for y in range(top, bottom):
                for x in range(left, right):
                    self.grid[y][x] = old[y+rows][x] if top <= y+rows < bottom else (' ', 0)

    def request(self, method, *args):
        self.next_id += 1
        ident = self.next_id
        result = self.pending[ident] = queue.Queue()
        self.proc.stdin.write(msgpack.packb([0, ident, method, list(args)], use_bin_type=True))
        self.proc.stdin.flush()
        error, value = result.get(timeout=15)
        del self.pending[ident]
        if error:
            raise RuntimeError(f'{method}: {error}')
        return value

    def command(self, text):
        return self.request('nvim_command', text)

    def lua(self, code, *args):
        return self.request('nvim_exec_lua', code, list(args))

    def snapshot(self):
        self.command('redraw!')
        self.request('nvim_eval', '1')
        with self.lock:
            return copy.deepcopy(self.grid), copy.deepcopy(self.attrs), self.defaults.copy()

    def stop(self):
        self.proc.terminate()
        self.proc.wait(timeout=5)

def rgb(value):
    return f'#{value:06X}'

def resolved(attr, defaults):
    fg = attr.get('foreground', defaults['foreground'])
    bg = attr.get('background', defaults['background'])
    if attr.get('reverse'):
        fg, bg = bg, fg
    return fg, bg

def font_paths():
    if os.name == 'nt':
        return Path('C:/Windows/Fonts/consola.ttf'), Path('C:/Windows/Fonts/consolab.ttf')
    root = Path('/usr/share/fonts/truetype/dejavu')
    return root / 'DejaVuSansMono.ttf', root / 'DejaVuSansMono-Bold.ttf'

def render(snapshot, path):
    grid, attrs, defaults = snapshot
    regular, bold = (ImageFont.truetype(str(p), 18) for p in font_paths())
    width, height, padding = 11, 25, 22
    image = Image.new('RGB', (len(grid[0])*width+padding*2, len(grid)*height+padding*2), rgb(defaults['background']))
    draw = ImageDraw.Draw(image)
    for row, cells in enumerate(grid):
        for col, (text, ident) in enumerate(cells):
            attr = attrs[ident]
            fg, bg = resolved(attr, defaults)
            x, y = padding+col*width, padding+row*height
            draw.rectangle((x, y, x+width-1, y+height-1), fill=rgb(bg))
            draw.text((x, y), text, font=bold if attr.get('bold') else regular, fill=rgb(fg))
            if attr.get('underline') or attr.get('undercurl'):
                draw.line((x, y+height-3, x+width-1, y+height-3), fill=rgb(attr.get('special', fg)))
    image.save(path)
    assert len(image.getcolors(image.width*image.height)) > 50, 'blank capture'

def find(snapshot, text):
    grid, attrs, defaults = snapshot
    matches = []
    for row in grid:
        line = ''.join(ch if ch else ' ' for ch, _ in row)
        start = line.find(text)
        if start >= 0:
            matches.append([resolved(attrs[ident], defaults) for _, ident in row[start:start+len(text)]])
    return matches

def assert_pair(snapshot, text, fg, bg):
    matches = find(snapshot, text)
    expected = (int(fg[1:], 16), int(bg[1:], 16))
    assert any(all(pair == expected for pair in match) for match in matches), f'{text}: expected {fg}/{bg}; got {matches}'

def run():
    n = Neovim()
    captures = []
    try:
        n.request('nvim_ui_attach', 98, 34, {'rgb': True, 'ext_linegrid': True})
        n.lua("vim.opt.runtimepath:prepend(vim.fn.getcwd()); vim.o.swapfile=false; vim.o.showmode=false; vim.o.laststatus=2; vim.o.statusline=' Verdelle %=%y  %l:%c '; vim.o.number=true; vim.o.cursorline=true; vim.o.signcolumn='yes'; vim.o.shortmess='I'; vim.cmd('filetype on'); vim.cmd('syntax on')")
        for mode in ('dark', 'light'):
            n.command(f'set background={mode}')
            n.command('colorscheme verdelle')
            c = json.loads((ROOT / f'palette/{mode}.json').read_text())['colors']
            for filename in ('library.lua', 'client.ts', 'index.py', 'settings.json', 'notes.md'):
                n.command(f'edit! tests/fixtures/{filename}')
                n.command('normal! gg')
                snapshot = n.snapshot()
                assert find(snapshot, Path(filename).stem) or len(set(ident for row in snapshot[0] for ch, ident in row if ch.strip())) >= 4
                if filename == 'library.lua':
                    assert_pair(snapshot, 'function', c['keyword'], c['bg'])
                    assert n.lua("return vim.fn.synIDattr(vim.fn.synIDtrans(vim.fn.synID(1,17,1)), 'fg#')").upper() == c['punctuation'], 'legacy Lua brace color'
                path = OUT / f'{mode}-{Path(filename).suffix[1:]}.png'
                render(snapshot, path)
                captures.append(path.name)

            # A real visual selection must override the syntax foreground.
            n.command('edit! tests/fixtures/library.lua')
            n.command('normal! gg0v$')
            snapshot = n.snapshot()
            assert_pair(snapshot, 'local Library = {}', c['selection_fg'], c['selection'])
            render(snapshot, OUT / f'{mode}-selection.png')
            n.request('nvim_input', '\x1b')

            # The native popup uses PmenuKindSel/PmenuExtraSel for selected columns.
            n.command('enew!')
            n.lua("vim.api.nvim_buf_set_lines(0,0,-1,false,{'libr'}); vim.api.nvim_win_set_cursor(0,{1,4})")
            n.command('startinsert!')
            n.lua("vim.schedule(function() vim.fn.complete(1, {{word='library',abbr='library',kind='Function',menu='[LSP]'}, {word='libraryRoot',abbr='libraryRoot',kind='Variable',menu='[Buffer]'}}) end)")
            for _ in range(50):
                if n.request('nvim_eval', 'pumvisible()'):
                    break
                time.sleep(.02)
            assert n.request('nvim_eval', 'pumvisible()') == 1, 'completion popup did not open'
            n.request('nvim_input', '\x0e')
            snapshot = n.snapshot()
            assert find(snapshot, 'Function') and find(snapshot, '[LSP]'), 'completion columns missing'
            selected_bg = int(c['menu_selection'][1:], 16)
            assert any(all(bg == selected_bg for fg, bg in match) for label in ('Function', 'Variable') for match in find(snapshot, label)), 'selected completion kind was not tested'
            for label in ('Function', '[LSP]'):
                for match in find(snapshot, label):
                    assert all(contrast(rgb(fg), rgb(bg)) >= 4.5 for fg, bg in match), f'{mode}: unreadable {label}'
            render(snapshot, OUT / f'{mode}-completion.png')
            n.request('nvim_input', '\x1b')
            n.command('stopinsert')

            # Diagnostics retain a shape cue, and all four severity levels render.
            n.command('edit! tests/fixtures/library.lua')
            n.lua("local ns=vim.api.nvim_create_namespace('verdelle-test'); vim.diagnostic.config({virtual_text=true,underline=true,signs=true}); vim.diagnostic.set(ns,0,{{lnum=1,col=0,end_col=7,message='Missing root path',severity=vim.diagnostic.severity.ERROR},{lnum=4,col=0,end_col=8,message='Unused parameter',severity=vim.diagnostic.severity.WARN},{lnum=9,col=0,end_col=6,message='Document title',severity=vim.diagnostic.severity.INFO},{lnum=13,col=0,end_col=7,message='Add a tag',severity=vim.diagnostic.severity.HINT}})")
            snapshot = n.snapshot()
            assert find(snapshot, 'Missing root path'), 'diagnostic text missing'
            render(snapshot, OUT / f'{mode}-diagnostics.png')
            n.lua("vim.diagnostic.reset(vim.api.nvim_create_namespace('verdelle-test'))")

            # Search must be visible on highlighted code and comments.
            n.command('set hlsearch')
            n.request('nvim_input', '/Library\r')
            snapshot = n.snapshot()
            assert find(snapshot, 'Library'), 'search target missing'
            render(snapshot, OUT / f'{mode}-search.png')
            n.command('nohlsearch')

            # Side-by-side real diff buffers exercise added/changed/deleted lines.
            n.command('enew!')
            n.lua("vim.api.nvim_buf_set_lines(0,0,-1,false,{'local title = \"Old title\"','local removed = true','return title'})")
            n.command('diffthis')
            n.command('vnew')
            n.lua("vim.api.nvim_buf_set_lines(0,0,-1,false,{'local title = \"New title\"','local added = 3','local tag = \"notes\"','return title'})")
            n.command('diffthis')
            snapshot = n.snapshot()
            assert find(snapshot, 'New title'), 'diff buffer missing'
            render(snapshot, OUT / f'{mode}-diff.png')
            n.command('diffoff!')
            n.command('only!')

        # Real OptionSet after startup; a ColorScheme event must resolve the new palette.
        n.command('set background=dark')
        for _ in range(50):
            if n.lua("return require('verdelle')._background") == 'dark':
                break
            time.sleep(.02)
        assert n.lua("return vim.api.nvim_get_hl(0,{name='Normal',link=false}).bg") == int('101F20',16)
        (OUT / 'ui-report.json').write_text(json.dumps({'passed': True, 'captures': sorted(p.name for p in OUT.glob('*.png')), 'neovim': n.request('nvim_eval', 'execute("version")')}, indent=2))
        print('Real Neovim UI passed: five languages, selection, completion, diagnostics, search, diff, live switching')
    finally:
        n.stop()

if __name__ == '__main__':
    run()
