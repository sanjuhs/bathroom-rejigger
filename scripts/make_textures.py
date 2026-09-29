from PIL import Image,ImageFilter
import random,math
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'textures';root.mkdir(exist_ok=True)
r=random.Random(14);size=512
for kind in ['charcoal','limestone','aged-tile']:
 im=Image.new('RGB',(size,size));p=im.load()
 for y in range(size):
  for x in range(size):
   n=r.gauss(0,1);wave=math.sin(x*.10+math.sin(y*.04)*3)*math.cos(y*.08+x*.04)
   if kind=='charcoal':
    v=max(24,min(138,64+n*21+wave*25));c=(v,v+3,v)
   elif kind=='limestone':
    v=max(140,min(218,184+n*10+wave*9));c=(v+3,v+1,v-7)
   else:
    edge=min(x,y,size-1-x,size-1-y)/size
    stain=math.exp(-edge*25)*(25+14*math.sin(x*.03+y*.024))+max(0,math.sin(x*.014+2)*math.sin(y*.019))*8
    v=int(max(95,min(240,207-stain+n*3)));c=(v,v-2,v-16)
   p[x,y]=tuple(int(max(0,min(255,a))) for a in c)
 im.save(root/f'{kind}.png')
