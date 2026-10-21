"""Validate bat themes; pass --bat PATH to check cache loading and real rendering."""
from pathlib import Path
import argparse
import json
import os
import plistlib
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bat')
    args = parser.parse_args()
    palettes = []
    for variant in ('dark', 'light'):
        data = json.loads((ROOT / f'palette/{variant}.json').read_text(encoding='utf-8'))
        p = data['colors']
        theme = plistlib.loads((ROOT / f'ports/bat/{data["name"]}.tmTheme').read_bytes())
        assert theme['name'] == data['name']
        global_settings = theme['settings'][0]['settings']
        assert global_settings['foreground'] == p['fg']
        assert global_settings['background'] == p['bg']
        assert global_settings['selectionForeground'] == p['selection_fg']
        assert global_settings['selection'] == p['selection']
        for rule in theme['settings']:
            for key, value in rule['settings'].items():
                if key != 'fontStyle':
                    assert value in p.values(), f'Off-palette bat setting: {key}={value}'
        palettes.append(data)
    if args.bat:
        with tempfile.TemporaryDirectory(prefix='verdelle-bat-') as directory:
            config = Path(directory)
            (config / 'themes').mkdir()
            for path in (ROOT / 'ports/bat').glob('*.tmTheme'):
                shutil.copyfile(path, config / 'themes' / path.name)
            env = dict(os.environ, BAT_CONFIG_DIR=str(config), XDG_CACHE_HOME=str(config / 'cache'),
                       BAT_CONFIG_PATH=str(config / 'config'), COLORTERM='truecolor', TERM='xterm-256color')
            (config / 'config').write_text('')
            def run(*arguments):
                return subprocess.run([args.bat, *arguments], env=env, cwd=ROOT, check=True,
                                      capture_output=True, text=True).stdout
            run('cache', '--build')
            themes = run('--list-themes', '--color=never')
            for data in palettes:
                assert data['name'] in themes.splitlines(), f'bat did not register {data["name"]}'
                rendered = ''.join(run('--theme', data['name'], '--color=always', '--style=plain',
                                       '--paging=never', str(path))
                                   for path in sorted((ROOT / 'tests/fixtures').glob('*'))
                                   if path.suffix in ('.py', '.ts', '.rs', '.lua', '.md'))
                actual = {tuple(map(int, match)) for match in re.findall(r'38;2;(\d+);(\d+);(\d+)', rendered)}
                for role in ('keyword', 'string', 'func', 'comment'):
                    color = data['colors'][role]
                    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                    assert rgb in actual, f'bat did not render {data["name"]} {role} in truecolor'
    print('bat plist settings passed; native cache and rendering passed when requested')


if __name__ == '__main__':
    main()
