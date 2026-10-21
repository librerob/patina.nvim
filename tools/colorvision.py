"""Generate or verify the versioned before/after color-vision report."""
from pathlib import Path
import argparse
import itertools
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from contrast import contrast
from color_math import SCENARIOS,lab,delta_e

ROLES=('keyword','constant','type','func','string')
BASELINE=ROOT/'tests/fixtures/palette-v1.json'
REPORT=ROOT/'docs/colorvision-report.json'

def variant(palette):
    c=palette['colors']
    cases=[]
    for name,kind,severity in SCENARIOS:
        values={r:lab(c[r],kind,severity) for r in ROLES}
        pairs={'/'.join((a,b)):round(delta_e(values[a],values[b]),6) for a,b in itertools.combinations(ROLES,2)}
        closest=min(pairs,key=pairs.get)
        cases.append({'scenario':name,'minimum_pair':closest,'minimum_distance':pairs[closest],'pairs':pairs})
    worst=min(cases,key=lambda x:x['minimum_distance'])
    return {
        'roles':{r:{'hex':c[r],'contrast_on_base':round(contrast(c[r],c['bg']),6),'Lab_L':round(lab(c[r])[0],6)} for r in ROLES},
        'minimum':{k:worst[k] for k in ('scenario','minimum_pair','minimum_distance')},
        'cases':cases,
    }

def build():
    baseline=json.loads(BASELINE.read_text())
    current={mode:json.loads((ROOT/f'palette/{mode}.json').read_text()) for mode in ('dark','light')}
    report={
        'method':{'simulation':'Machado, Oliveira and Fernandes (2009), published matrices at severities 10 through 100 in steps of 10, plus normal vision','pipeline':'sRGB -> linear RGB -> simulation -> clip to display gamut -> CIELAB D65 -> CIEDE2000, unit parametric factors','scope':'Five chromatic syntax roles, ten pairs, 31 scenarios, two variants: 620 pair/scenario comparisons per palette version. This is a design regression check, not accessibility certification.','baseline':'tests/fixtures/palette-v1.json, published before this revision at d0e2256eeb1ae88d43e32647dd171fc0d4a1921f'},
        'variants':{mode:{'before':variant(baseline[mode]),'after':variant(current[mode])} for mode in ('dark','light')},
    }
    # Deliberate regression bounds, not universal perceptual thresholds.
    for mode,floor in (('dark',7.3),('light',9.0)):
        actual=report['variants'][mode]['after']['minimum']['minimum_distance']
        assert actual>=floor,f'{mode}: minimum {actual} fell below design bound {floor}'
    light=report['variants']['light']['after']['roles']
    assert all(light[a]['contrast_on_base']>light[b]['contrast_on_base'] for a,b in zip(ROLES,ROLES[1:])), 'light hierarchy must run keyword -> constant -> type -> function -> string'
    span=light['string']['Lab_L']-light['keyword']['Lab_L']
    assert span>=10,'light accent lightness span must remain deliberate'
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    report=build()
    text=json.dumps(report,indent=2)+'\n'
    if args.check:
        assert REPORT.read_text(encoding='utf-8')==text,'Regenerate: python tools/colorvision.py'
    else:
        REPORT.write_text(text,encoding='utf-8')
    for mode,values in report['variants'].items():
        before,after=values['before']['minimum'],values['after']['minimum']
        print(f"{mode}: weakest {before['minimum_distance']:.3f} -> {after['minimum_distance']:.3f} ({after['scenario']}, {after['minimum_pair']})")
    print('620 pair/scenario comparisons per version; report is current')

if __name__=='__main__':main()
