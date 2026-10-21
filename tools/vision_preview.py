"""Illustrate the light palette before/after at full simulated deficiencies."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from preview import REGULAR,BOLD
from color_math import linear_rgb,simulate_linear,encode_rgb

ROOT=Path(__file__).resolve().parents[1]

def main():
    old=json.loads((ROOT/'tests/fixtures/palette-v1.json').read_text())['light']['colors']
    new=json.loads((ROOT/'palette/light.json').read_text())['colors']
    canvas=Image.new('RGB',(1440,650),'#F6F4EB')
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype(str(REGULAR),18)
    small=ImageFont.truetype(str(REGULAR),15)
    heading=ImageFont.truetype(str(BOLD),24)
    draw.text((24,20),'Verdelle Light / before and after',font=heading,fill='#132B2D')
    scenes=[('Normal',None),('Protan 100','protan'),('Deutan 100','deutan'),('Tritan 100','tritan')]
    samples=[('keyword','if ready then return'),('constant','false  nil  256'),('type','Document  String'),('func','find_document()'),('string','"copper and paper"')]
    for col,(label,kind) in enumerate(scenes):
        x=24+col*354
        draw.text((x,73),label,font=font,fill='#132B2D')
        sim=lambda h:encode_rgb(simulate_linear(linear_rgb(h),kind,100))
        for row,(caption,c) in enumerate((('Before',old),('After',new))):
            y=116+row*248
            draw.rectangle((x,y,x+328,y+222),fill=sim(c['bg']),outline='#BEBBAD')
            draw.text((x+14,y+13),caption,font=small,fill=sim(c['fg']))
            for i,(role,text) in enumerate(samples):
                draw.text((x+14,y+48+i*32),text,font=font,fill=sim(c[role]))
    draw.text((24,621),'Machado 2009 / linear RGB / gamut clipped / simulation is not a user test',font=small,fill='#45676B')
    path=ROOT/'assets/colorvision-light.png'
    canvas.save(path)
    print(path)

if __name__=='__main__':main()
