"""Render both generated Kitty themes in a real terminal under Xvfb."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import time
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'test-results'
OUT.mkdir(exist_ok=True)

def run():
    for mode in ('dark','light'):
        palette=json.loads((ROOT/f'palette/{mode}.json').read_text())
        c=palette['colors']
        script = ['import time', 'print("\\033[2J\\033[H",end="")',f'print("  VERDELLE / {mode.upper()}\\n")']
        for i,role in enumerate(('keyword','string','func','type','constant','comment','error','warning')):
            rgb=';'.join(str(int(c[role][j:j+2],16)) for j in (1,3,5))
            script.append(f'print("  \\033[38;2;{rgb}m{role:12}  The quick brown fox 0123456789\\033[0m")')
        script += ['print("\\n  ANSI palette\\n")']
        for row in (0,8):
            text='  '+''.join(f'\x1b[{40+i if row==0 else 100+i}m    {i+row:02}    \x1b[0m' for i in range(8))
            script.append('print('+repr(text)+')')
        script += ['print("\\n  Generated Kitty theme / DejaVu Sans Mono")','time.sleep(30)']
        with tempfile.TemporaryDirectory() as temp:
            child=Path(temp)/'specimen.py'
            child.write_text('\n'.join(script),encoding='utf-8')
            process=subprocess.Popen(['kitty','--config',str(ROOT/f'ports/kitty/verdelle-{mode}.conf'),
                '--override','font_family=DejaVu Sans Mono','--override','font_size=15',
                '--override','initial_window_width=1050','--override','initial_window_height=620',
                '--override','remember_window_size=no','--override','confirm_os_window_close=0',
                '--title',f'Verdelle terminal test {mode}',sys.executable,str(child)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            try:
                window=None
                deadline=time.monotonic()+25
                while time.monotonic()<deadline:
                    found=subprocess.run(['xdotool','search','--onlyvisible','--name',f'^Verdelle terminal test {mode}$'],capture_output=True,text=True)
                    if found.returncode==0 and found.stdout.strip():
                        window=found.stdout.splitlines()[-1];break
                    if process.poll() is not None:
                        raise RuntimeError(process.stderr.read().decode())
                    time.sleep(.1)
                assert window,'Kitty window not found'
                path=OUT/f'kitty-{mode}.png'
                for _ in range(40):
                    subprocess.run(['import','-window',window,str(path)],check=True,capture_output=True)
                    pixels=Image.open(path).convert('RGB')
                    counts=dict((color,count) for count,color in pixels.getcolors(pixels.width*pixels.height))
                    color=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5))
                    # Check the actual background, truecolor text and every ANSI slot.
                    required=[c['bg']]+[c[k] for k in ('keyword','string','func','type','constant')]+palette['ansi']
                    if all(counts.get(color(h),0)>=3 for h in required):
                        break
                    time.sleep(.1)
                else:
                    raise AssertionError(f'{mode}: terminal capture did not contain the configured palette')
                assert counts[color(c['bg'])]>pixels.width*pixels.height*.35
                print(f'Kitty {mode}: real background, five truecolor roles and all 16 ANSI slots verified')
            finally:
                process.terminate()
                process.wait(timeout=5)

if __name__=='__main__':run()
