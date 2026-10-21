"""sRGB/D65 color math and Machado (2009) color-vision simulations.

Simulation matrices are published numerical data, reproduced in Colorspacious:
https://github.com/njsmith/colorspacious/blob/master/colorspacious/cvd.py
CIEDE2000 follows Sharma, Wu and Dalal (2005), kL=kC=kH=1:
https://hajim.rochester.edu/ece/sites/gsharma/ciede2000/
"""
import math
import json
from pathlib import Path

MATRICES = {kind:{int(severity):matrix for severity,matrix in rows.items()} for kind,rows in json.loads((Path(__file__).resolve().parent/'data/machado2009.json').read_text()).items()}
SCENARIOS = [('normal', None, 0)] + [(f'{kind}-{severity}',kind,severity) for kind in MATRICES for severity in range(10,101,10)]

def linear_rgb(color):
    rgb = [int(color[i:i+2],16)/255 for i in (1,3,5)]
    return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb)

def encode_rgb(rgb):
    values = [max(0.,min(1.,v)) for v in rgb]
    return '#' + ''.join(f'{round(255*(12.92*v if v <= .0031308 else 1.055*v**(1/2.4)-.055)):02X}' for v in values)

def simulate_linear(rgb, kind=None, severity=100):
    if kind is None:
        return tuple(rgb)
    # Clip to the display gamut before computing displayed Lab values.
    return tuple(max(0.,min(1.,sum(a*b for a,b in zip(row,rgb)))) for row in MATRICES[kind][severity])

def lab_from_linear(rgb):
    r,g,b = rgb
    xyz = ((.4124564*r+.3575761*g+.1804375*b)/.95047,
           .2126729*r+.7151522*g+.0721750*b,
           (.0193339*r+.1191920*g+.9503041*b)/1.08883)
    x,y,z = (v**(1/3) if v > 216/24389 else (24389/27*v+16)/116 for v in xyz)
    return (116*y-16,500*(x-y),200*(y-z))

def lab(color, kind=None, severity=100):
    return lab_from_linear(simulate_linear(linear_rgb(color),kind,severity))

def delta_e(a,b):
    l1,a1,b1 = a
    l2,a2,b2 = b
    cbar = (math.hypot(a1,b1)+math.hypot(a2,b2))/2
    g = .5*(1-math.sqrt(cbar**7/(cbar**7+25**7)))
    ap1,ap2 = (1+g)*a1,(1+g)*a2
    c1,c2 = math.hypot(ap1,b1),math.hypot(ap2,b2)
    h1 = math.degrees(math.atan2(b1,ap1)) % 360 if c1 else 0.
    h2 = math.degrees(math.atan2(b2,ap2)) % 360 if c2 else 0.
    dl,dc = l2-l1,c2-c1
    dh = h2-h1
    if c1*c2 == 0:
        dh = 0.
    elif dh > 180:
        dh -= 360
    elif dh < -180:
        dh += 360
    dhp = 2*math.sqrt(c1*c2)*math.sin(math.radians(dh/2))
    lbar,cpbar = (l1+l2)/2,(c1+c2)/2
    if c1*c2 == 0:
        hbar = h1+h2
    elif abs(h1-h2) <= 180:
        hbar = (h1+h2)/2
    elif h1+h2 < 360:
        hbar = (h1+h2+360)/2
    else:
        hbar = (h1+h2-360)/2
    cos = lambda angle: math.cos(math.radians(angle))
    t = 1-.17*cos(hbar-30)+.24*cos(2*hbar)+.32*cos(3*hbar+6)-.20*cos(4*hbar-63)
    sl = 1+.015*(lbar-50)**2/math.sqrt(20+(lbar-50)**2)
    sc,sh = 1+.045*cpbar,1+.015*cpbar*t
    theta = 30*math.exp(-((hbar-275)/25)**2)
    rt = -2*math.sqrt(cpbar**7/(cpbar**7+25**7))*math.sin(math.radians(2*theta))
    x,y,z = dl/sl,dc/sc,dhp/sh
    return math.sqrt(max(0.,x*x+y*y+z*z+rt*y*z))
