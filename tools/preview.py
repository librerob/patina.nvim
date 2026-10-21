"""Render designed palette specimens. These are not application screenshots."""
from pathlib import Path
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path('C:/Windows/Fonts') if os.name == 'nt' else Path('/usr/share/fonts/truetype/dejavu')
REGULAR = FONTS / ('consola.ttf' if os.name == 'nt' else 'DejaVuSansMono.ttf')
BOLD = FONTS / ('consolab.ttf' if os.name == 'nt' else 'DejaVuSansMono-Bold.ttf')

def render(mode):
    c = json.loads((ROOT / f'palette/{mode}.json').read_text())['colors']
    image = Image.new('RGB', (1440, 1030), c['bg'])
    d = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(REGULAR), 20)
    small = ImageFont.truetype(str(REGULAR), 16)
    bold = ImageFont.truetype(str(BOLD), 20)
    title = ImageFont.truetype(str(BOLD), 38)
    def text(x, y, value, role='variable', f=font):
        d.text((x, y), value, fill=c.get(role, role), font=f)
    def rule(y):
        d.line((42, y, 1398, y), fill=c['border'])
    text(42, 29, 'Patina', 'variable', title)
    text(1210, 45, mode.upper(), 'func', small)
    text(42, 88, 'Copper / verdigris / ' + ('ink' if mode == 'dark' else 'bone paper'), 'muted')
    rule(132)
    text(42, 155, 'library.lua', 'muted', small)
    text(997, 155, 'INTERFACE STATES', 'muted', small)
    d.line((958, 155, 958, 867), fill=c['border'])
    lines = (ROOT / 'tests/fixtures/library.lua').read_text().splitlines()
    # The excerpt preserves real source lines and their line numbers.
    selected = list(enumerate(lines[:20], 1)) + [(0, '')] + list(enumerate(lines[21:28], 22))
    keywords = {'local', 'function', 'return', 'if', 'then', 'end', 'for', 'in', 'do', 'or'}
    controls = {'return', 'if', 'then', 'end', 'for', 'in', 'do'}
    pattern = re.compile(r'--.*|"[^"\n]*"|\b\d+\b|[A-Za-z_][A-Za-z_0-9]*|\s+|.')
    char = font.getlength('M')
    for row, (lineno, line) in enumerate(selected):
        y = 197+row*23
        if lineno == 14:
            d.rectangle((38,y-1,934,y+22), fill=c['line'])
        if lineno:
            text(43,y,f'{lineno:2}', 'func' if lineno == 14 else 'subdued', small)
        x = 93
        for match in pattern.finditer(line):
            value = match.group()
            if value.startswith('--'):
                role = 'comment'
            elif value.startswith('"'):
                role = 'string'
            elif value in keywords:
                role = 'keyword'
            elif value in ('true', 'false', 'nil') or value.isdigit():
                role = 'constant'
            elif re.match(r'^\s*\(', line[match.end():]):
                role = 'func'
            elif value in ('self',):
                role = 'type'
            elif match.start() and line[match.start()-1] == '.':
                role = 'property'
            elif re.fullmatch(r'[^\w\s]+', value):
                role = 'punctuation'
            else:
                role = 'variable'
            text(x,y,value,role,bold if mode == 'light' and value in controls else font)
            x += len(value)*char
    right = 997
    text(right,207,'Selection', 'muted', small)
    d.rectangle((right,242,1396,284), fill=c['selection'])
    text(right+14,250,'return document.title','selection_fg')
    text(right,322,'Completion', 'muted', small)
    d.rectangle((right,358,1396,496), fill=c['float'], outline=c['border'])
    d.rectangle((right+1,365,1395,405), fill=c['menu_selection'])
    text(right+13,373,'library', 'variable', bold)
    text(right+203,374,'Function', 'type', small)
    d.line((right+13,398,right+59,398), fill=c['keyword'])
    text(right+13,419,'libraryRoot', 'variable')
    text(right+203,420,'Variable', 'type', small)
    text(right+13,460,'[LSP]', 'muted', small)
    text(right,535,'Search', 'muted', small)
    d.rectangle((right,570,right+110,605), fill=c['search_bg'])
    text(right+10,576,'match', 'search_fg')
    d.rectangle((right+130,570,1396,605), fill=c['search_current_bg'])
    text(right+140,576,'current match', 'search_current_fg')
    text(right,645,'Diagnostics', 'muted', small)
    text(right,683,'E  Missing root path', 'error')
    d.line((right+36,708,right+240,708), fill=c['error'])
    text(right,726,'W  Unused parameter', 'warning')
    d.line((right+36,751,right+240,751), fill=c['warning'])
    text(right,793,'+  document added', 'func', small)
    text(right,827,'-  duplicate removed', 'error', small)
    rule(891)
    roles = ('keyword','func','string','type','constant','comment','punctuation','variable')
    for i, role in enumerate(roles):
        x = 42+i*170
        d.rectangle((x,915,x+26,941), fill=c[role])
        text(x+36,919,{'func':'function','variable':'text'}.get(role,role),'muted',small)
    text(42,978,'DESIGNED PALETTE SPECIMEN', 'comment', small)
    text(1042,978,'NEOVIM / TRUE COLOR', 'comment', small)
    path = ROOT / f'assets/patina-{mode}.png'
    path.parent.mkdir(exist_ok=True)
    image.save(path)
    print(path)

if __name__ == '__main__':
    for variant in ('dark','light'):
        render(variant)
