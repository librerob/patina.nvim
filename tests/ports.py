"""Check shared colors and structural validity in the extra ports."""
from pathlib import Path
import json
import configparser
from contrast import contrast

ROOT = Path(__file__).resolve().parents[1]
def ini(path):
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    parser.read(ROOT / path, encoding='utf-8')
    return parser


def verify(variant):
    suffix = '-light' if variant == 'light' else ''
    pdata = json.loads((ROOT / f'palette/{variant}.json').read_text(encoding='utf-8'))
    p, ansi = pdata['colors'], pdata['ansi']
    windows = json.loads((ROOT / f'ports/windows-terminal/{pdata["name"]}.json').read_text(encoding='utf-8'))
    assert windows['background'] == p['bg']
    assert windows['foreground'] == p['fg']
    slots = ['black', 'red', 'green', 'yellow', 'blue', 'purple', 'cyan', 'white',
             'brightBlack', 'brightRed', 'brightGreen', 'brightYellow', 'brightBlue',
             'brightPurple', 'brightCyan', 'brightWhite']
    assert [windows[slot] for slot in slots] == ansi
    ghostty = (ROOT / f'ports/ghostty/{pdata["name"]}').read_text(encoding='utf-8').splitlines()
    assert f'background = {p["bg"]}' in ghostty
    assert [line.split('=', 2)[2] for line in ghostty if line.startswith('palette = ')] == ansi
    xfce = ini(f'ports/xfce-terminal/{pdata["name"]}.theme')['Scheme']
    assert xfce['Name'] == pdata['name']
    assert xfce['ColorPalette'].split(';') == ansi
    for key, role in {'ColorForeground': 'fg', 'ColorBackground': 'bg', 'ColorCursor': 'cursor',
                      'ColorCursorForeground': 'bg', 'ColorSelection': 'selection_fg',
                      'ColorSelectionBackground': 'selection', 'TabActivityColor': 'focus'}.items():
        assert xfce[key] == p[role]
    for key in ('ColorCursorUseDefault', 'ColorSelectionUseDefault', 'ColorUseTheme',
                'ColorBackgroundVary', 'ColorBoldIsBright'):
        assert not xfce.getboolean(key)

    konsole = ini(f'ports/konsole/{pdata["name"]}.colorscheme')
    def hex_color(section):
        values = [int(n) for n in konsole[section]['Color'].split(',')]
        assert len(values) == 3 and all(0 <= n <= 255 for n in values)
        return '#' + ''.join(f'{n:02X}' for n in values)
    assert konsole['General']['Description'] == pdata['name']
    assert konsole['General'].getfloat('Opacity') == 1
    assert not konsole['General'].getboolean('ColorRandomization')
    for name, role in {'Foreground': 'fg', 'ForegroundIntense': 'bright', 'ForegroundFaint': 'muted',
                       'Background': 'bg', 'BackgroundIntense': 'bg', 'BackgroundFaint': 'bg'}.items():
        assert hex_color(name) == p[role]
    for index in range(8):
        assert hex_color(f'Color{index}') == ansi[index]
        assert hex_color(f'Color{index}Intense') == ansi[index + 8]
        assert hex_color(f'Color{index}Faint') == ansi[index]

    modern = ini('ports/foot/verdelle.ini')[f'colors-{variant}']
    legacy = ini(f'ports/foot/verdelle{suffix}-legacy.ini')['colors']
    for section in (modern, legacy):
        for key, role in {'foreground': 'fg', 'background': 'bg',
                          'selection-foreground': 'selection_fg', 'selection-background': 'selection'}.items():
            assert section[key] == p[role][1:]
        assert [section[f'{"regular" if i < 8 else "bright"}{i % 8}'] for i in range(16)] == [c[1:] for c in ansi]
    assert modern['cursor'] == f'{p["bg"][1:]} {p["cursor"][1:]}'
    theme = json.loads((ROOT / f'ports/vscode/themes/verdelle{suffix}-color-theme.json').read_text(encoding='utf-8'))
    package = json.loads((ROOT / 'ports/vscode/package.json').read_text(encoding='utf-8'))
    assert package['version'] == '0.1.0'
    entry = next(t for t in package['contributes']['themes'] if t['label'] == pdata['name'])
    assert (ROOT / 'ports/vscode' / entry['path']).is_file()
    assert entry['uiTheme'] == ('vs' if variant == 'light' else 'vs-dark')
    assert theme['type'] == variant
    assert theme['colors']['editor.background'] == p['bg']
    assert theme['colors']['editor.foreground'] == p['fg']
    ui = theme['colors']
    assert ui['editor.selectionForeground'] == p['selection_fg']
    assert ui['editor.selectionBackground'] == p['selection']
    assert ui['editorSuggestWidget.selectedBackground'] == p['menu_selection']
    assert ui['list.activeSelectionBackground'] == p['menu_selection']
    for foreground, background in (
        ('editor.selectionForeground', 'editor.selectionBackground'),
        ('editorSuggestWidget.selectedForeground', 'editorSuggestWidget.selectedBackground'),
        ('editorSuggestWidget.focusHighlightForeground', 'editorSuggestWidget.selectedBackground'),
        ('list.activeSelectionForeground', 'list.activeSelectionBackground'),
        ('list.focusHighlightForeground', 'list.focusBackground'),
        ('button.foreground', 'button.background'),
        ('button.foreground', 'button.hoverBackground'),
        ('statusBar.debuggingForeground', 'statusBar.debuggingBackground'),
    ):
        assert contrast(ui[foreground], ui[background]) >= 4.5, f'{variant}: {foreground}/{background}'
    assert theme['semanticTokenColors']['function'] == p['func']
    assert theme['semanticTokenColors']['string'] == p['string']
    for index, color in enumerate(ansi):
        slot = ['Black','Red','Green','Yellow','Blue','Magenta','Cyan','White'][index % 8]
        key = 'terminal.ansi' + ('Bright' if index > 7 else '') + slot
        assert theme['colors'][key] == color
    palette_values = set(p.values()) | set(ansi)
    translucent = {'editor.findMatchHighlightBackground': p['search_bg'] + '26',
                   'editor.inactiveSelectionBackground': p['selection'] + '80',
                   **{key: p['bg'] + '00' for key in ('editorInlayHint.background',
                       'editorInlayHint.typeBackground', 'editorInlayHint.parameterBackground')}}
    for key, color in theme['colors'].items():
        if key in translucent:
            assert color == translucent[key]
        else:
            assert color in palette_values, f'Color outside palette: {color}'
    for key in ('editorInlayHint.foreground', 'editorInlayHint.typeForeground',
                'editorInlayHint.parameterForeground', 'editorCodeLens.foreground'):
        assert theme['colors'][key] == p['comment'], f'Unreadable annotation: {key}'
    for token in theme['tokenColors']:
        color = token['settings'].get('foreground')
        assert color is None or color in palette_values


for variant in ('dark', 'light'):
    verify(variant)
print('Dark and light extra terminal ports and VS Code colors agree with their palettes')
