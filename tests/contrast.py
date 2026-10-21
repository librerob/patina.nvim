"""Test the actual foreground/background contracts, including selected states."""
from pathlib import Path
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]

def luminance(color):
    values = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
    linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
    return sum(a*b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))

def contrast(a, b):
    x, y = sorted((luminance(a), luminance(b)))
    return (y+0.05)/(x+0.05)

def check():
    count = 0
    report = {}
    roles = ('keyword', 'string', 'func', 'type', 'constant', 'variable', 'operator', 'punctuation', 'property', 'comment', 'error', 'warning')
    surfaces = ('bg', 'panel', 'line', 'float', 'reference', 'diff_add', 'diff_change', 'diff_delete', 'diff_text')
    for mode in ('dark', 'light'):
        data = json.loads((ROOT / f'palette/{mode}.json').read_text())
        c = data['colors']
        assert all(re.fullmatch(r'#[0-9A-F]{6}', v) for v in list(c.values()) + data['ansi'])
        assert len(data['ansi']) == 16
        checks = [(f'{role}/{surface}', c[role], c[surface]) for role in roles for surface in surfaces]
        checks += [(f'menu:{role}/{surface}', c[role], c[surface]) for role in ('keyword', 'type', 'func', 'variable', 'muted') for surface in ('float', 'menu_selection')]
        checks += [('Visual', c['selection_fg'], c['selection']), ('Search', c['search_fg'], c['search_bg']), ('CurSearch', c['search_current_fg'], c['search_current_bg'])]
        checks += [(f'lualine:{accent}', c['bg'], c[accent]) for accent in ('keyword', 'func', 'type', 'string', 'error')]
        ratios = [(label, contrast(fg, bg)) for label, fg, bg in checks]
        for label, ratio in ratios:
            assert ratio >= 4.5, f'{mode} {label}: {ratio:.4f}:1'
        assert contrast(c['selection'], c['bg']) >= 3, f'{mode}: visual selection is too subtle'
        assert luminance(c['fg']) > luminance(c['operator']) > luminance(c['punctuation']) > luminance(c['comment']) if mode == 'dark' else luminance(c['fg']) < luminance(c['operator']) < luminance(c['punctuation']) < luminance(c['comment'])
        # ANSI black is a utility slot; the remaining slots must read on the default background.
        for i, color in enumerate(data['ansi'][1:], 1):
            assert contrast(color, c['bg']) >= 4.5, f'{mode}: ANSI {i} is unreadable'
        # Independently parse the emitted terminal formats and compare every color.
        alacritty = tomllib.loads((ROOT / f'ports/alacritty/patina-{mode}.toml').read_text())['colors']
        assert alacritty['selection'] == {'text': c['selection_fg'], 'background': c['selection']}
        names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
        assert [alacritty[group][name] for group in ('normal', 'bright') for name in names] == data['ansi']
        kitty = dict(line.split() for line in (ROOT / f'ports/kitty/patina-{mode}.conf').read_text().splitlines() if line and not line.startswith('#'))
        assert kitty['selection_foreground'] == c['selection_fg'] and kitty['selection_background'] == c['selection']
        assert [kitty[f'color{i}'] for i in range(16)] == data['ansi']
        ghostty = [line.split(' = ', 1) for line in (ROOT / f'ports/ghostty/Patina {mode.title()}').read_text().splitlines() if line and not line.startswith('#')]
        ghost_palette = [v.split('=', 1) for k, v in ghostty if k == 'palette']
        assert [value for _, value in ghost_palette] == data['ansi']
        ghost_options = dict((k, v) for k, v in ghostty if k != 'palette')
        assert ghost_options['selection-foreground'] == c['selection_fg'] and ghost_options['selection-background'] == c['selection']
        minimum = min(ratios, key=lambda pair: pair[1])
        report[mode] = {'checks': len(checks), 'minimum': {'pair': minimum[0], 'ratio': round(minimum[1], 4)}, 'selection_text': round(contrast(c['selection_fg'], c['selection']), 4), 'selection_surface': round(contrast(c['selection'], c['bg']), 4), 'completion_kind_selected': round(contrast(c['type'], c['menu_selection']), 4)}
        count += len(checks)
    print(json.dumps({'total_pairs': count, 'variants': report}, indent=2))
    return report

if __name__ == '__main__':
    check()
