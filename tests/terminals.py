"""Query the colors actually loaded by Kitty, Alacritty, Xfce and Konsole.

Run under dbus-run-session and xvfb-run on Linux. All application settings and
probe results live in a temporary directory; existing user profiles are unused.
"""
from pathlib import Path
import json
import os
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def probe(destination):
    import termios
    import tty
    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    received = b''
    colors = {}
    pattern = rb'\x1b\](4;\d+|10|11);rgb:([0-9a-fA-F]+)/([0-9a-fA-F]+)/([0-9a-fA-F]+)(?:\x07|\x1b\\)'
    try:
        tty.setraw(fd)
        queries = ['10', '11'] + [f'4;{index}' for index in range(16)]
        os.write(sys.stdout.fileno(), ''.join(f'\x1b]{key};?\x1b\\' for key in queries).encode())
        deadline = time.monotonic() + 8
        while len(colors) < 18 and time.monotonic() < deadline:
            if select.select([fd], [], [], 0.2)[0]:
                received += os.read(fd, 65536)
                for match in re.finditer(pattern, received):
                    key, *channels = match.groups()
                    colors[key.decode()] = '#' + ''.join(
                        f'{round(int(channel, 16) * 255 / (16 ** len(channel) - 1)):02X}'
                        for channel in channels)
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, previous)
        Path(destination).write_text(json.dumps({'colors': colors, 'raw': repr(received)}))
    if os.environ.get('VERDELLE_SWATCH_READY'):
        os.write(sys.stdout.fileno(), b'\x1b[2J\x1b[H\x1b[?25l')
        for row in range(3):
            os.write(sys.stdout.fileno(), b'\x1b[' + str(row + 1).encode() + b';1H')
            for index in range(16):
                code = 40 + index if index < 8 else 100 + index - 8
                os.write(sys.stdout.fileno(), f'\x1b[{code}m    '.encode())
        os.write(sys.stdout.fileno(), b'\x1b[0m')
        Path(os.environ['VERDELLE_SWATCH_READY']).touch()
        deadline = time.monotonic() + 10
        while not Path(os.environ['VERDELLE_SWATCH_READY'] + '.release').exists() and time.monotonic() < deadline:
            time.sleep(0.05)


def rendered_swatches(process, ready, data, variant):
    from collections import Counter
    from PIL import ImageGrab
    deadline = time.monotonic() + 15
    missing = list(data['ansi'])
    while time.monotonic() < deadline and process.poll() is None:
        if ready.exists():
            image = ImageGrab.grab(xdisplay=os.environ['DISPLAY']).convert('RGB')
            counts = Counter(image.getdata())
            missing = [color for color in data['ansi'] if counts[tuple(bytes.fromhex(color[1:]))] < 32]
            if not missing:
                target = ROOT / 'test-results'
                target.mkdir(exist_ok=True)
                image.save(target / f'konsole-{variant}.png')
                Path(str(ready) + '.release').touch()
                return
        time.sleep(0.1)
    Path(str(ready) + '.release').touch()
    raise AssertionError(f'Rendered Konsole ANSI swatches missing: {missing}')


def main():
    failures = []
    for variant in ('dark', 'light'):
        suffix = '-light' if variant == 'light' else ''
        data = json.loads((ROOT / f'palette/{variant}.json').read_text())
        expected = {'10': data['colors']['fg'], '11': data['colors']['bg']}
        expected.update({f'4;{index}': color for index, color in enumerate(data['ansi'])})
        for app in ('kitty', 'alacritty', 'xfce4-terminal', 'konsole'):
            with tempfile.TemporaryDirectory(prefix='verdelle-terminal-') as directory:
                home = Path(directory)
                config, share = home / '.config', home / '.local/share'
                config.mkdir()
                share.mkdir(parents=True)
                env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(config), XDG_DATA_HOME=str(share),
                           LIBGL_ALWAYS_SOFTWARE='1', QT_X11_NO_MITSHM='1')
                result = home / 'colors.json'
                child = [sys.executable, str(Path(__file__).resolve()), '--probe', str(result)]
                if app == 'kitty':
                    command = [app, '--config', str(ROOT / f'ports/kitty/verdelle-{variant}.conf'), *child]
                elif app == 'alacritty':
                    command = [app, '--config-file', str(ROOT / f'ports/alacritty/verdelle-{variant}.toml'), '-e', *child]
                elif app == 'konsole':
                    target = share / 'konsole'
                    target.mkdir()
                    shutil.copyfile(ROOT / f'ports/konsole/{data["name"]}.colorscheme', target / f'{data["name"]}.colorscheme')
                    command = [app, '--separate', '--nofork', '-p', f'ColorScheme={data["name"]}', '-e', *child]
                    env['VERDELLE_SWATCH_READY'] = str(home / 'swatches-ready')
                else:
                    # Xfce's preset importer copies Scheme properties into its
                    # preferences. Exercise those same keys through terminalrc.
                    target = config / 'xfce4/terminal'
                    target.mkdir(parents=True)
                    scheme = (ROOT / f'ports/xfce-terminal/{data["name"]}.theme').read_text()
                    (target / 'terminalrc').write_text(scheme.replace('[Scheme]', '[Configuration]', 1))
                    command = [app, '--disable-server', '--execute', *child]
                try:
                    process = subprocess.Popen(command, env=env, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    try:
                        if app == 'konsole':
                            rendered_swatches(process, Path(env['VERDELLE_SWATCH_READY']), data, variant)
                        _, stderr = process.communicate(timeout=25)
                    finally:
                        if process.poll() is None:
                            process.kill()
                            process.communicate()
                    assert result.is_file(), f'No probe result; exit {process.returncode}: {stderr}'
                    actual = json.loads(result.read_text())
                    if app == 'konsole':
                        # Konsole's OSC 4 fallback reports its built-in default
                        # table, not the profile palette (Vt102Emulation.cpp).
                        # Check rendered ANSI pixels above; OSC 10/11 is valid.
                        assert all(actual['colors'].get(key) == expected[key] for key in ('10', '11')), actual
                    else:
                        assert actual['colors'] == expected, f'Expected {expected}, received {actual}'
                    assert process.returncode == 0, stderr
                    assert not re.search(r'(?i)(unused config key|unknown config key|invalid configuration)', stderr), stderr
                    print(f'{app} {variant}: foreground, background and all 16 ANSI colors passed', flush=True)
                except (AssertionError, subprocess.TimeoutExpired) as error:
                    failures.append(f'{app} {variant}: {error}')
    if failures:
        raise AssertionError('\n'.join(failures))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--probe':
        probe(sys.argv[2])
    else:
        main()
