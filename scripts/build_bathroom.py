"""Reproducible, photo-informed Bathroom Rejigger scene. Run in isolated background Blender."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
random.seed(24)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'
W,D,H=2.4,1.5,2.6
scene['dimension_status']='Photo-estimated; not a measured survey'
scene['room_width_m']=W;scene['room_depth_m']=D;scene['room_height_m']=H

def mat(name,color,rough=.45,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
ivory=mat('Existing | warm ivory glazed tile',(.64,.63,.51),.32)
white=mat('Porcelain | warm white',(.88,.9,.87),.22)
paint=mat('White painted plaster',(.83,.84,.8),.85)
grout=mat('Existing | aged grout',(.31,.30,.25),.95)
chrome=mat('Brushed chrome',(.53,.59,.62),.22,.86)
black=mat('Black fittings',(.008,.01,.009),.36)
yellow=mat('Existing | pale yellow laminate',(.73,.69,.34),.6)
edge=mat('Aluminium edging',(.4,.46,.48),.38,.65)
teal=mat('Muted teal bucket',(.18,.34,.32),.44)
tan=mat('Ochre plastic',(.38,.26,.12),.62)
red=mat('Red bottle',(.36,.025,.045),.27)
blue=mat('Blue plastic',(.025,.07,.24),.37)
soap=mat('Amber soap',(.66,.35,.07),.5)
glass=mat('Mirror silver',(.58,.68,.68),.10,.94)
stone=mat('Existing | charcoal stone',(.09,.1,.085),.42)
lightstone=mat('Existing | pale stone',(.6,.59,.52),.4)
wood=mat('Alternative | oak',(.48,.28,.12),.65)
sage=mat('Alternative | sage tile',(.29,.43,.36),.38)
terracotta=mat('Alternative | terracotta',(.57,.26,.15),.8)
# Portable image textures: materials remain textured in glTF.
for m,texture in [(stone,'charcoal'),(lightstone,'limestone')]:
 p=ROOT/'textures'/f'{texture}.png'
 if p.exists():
  n=m.node_tree.nodes.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(str(p));n.image.pack();m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

def group(id,label,cat='fixture',loc=(0,0,0),ref='',fixed=False):
 o=bpy.data.objects.new(id,None);scene.collection.objects.link(o);o.location=loc
 o['entityId']=id;o['label']=label;o['category']=cat;o['reference']=ref;o['fixed']=fixed;o['estimated']=True
 return o

def finish(o,name,material,parent=None):
 o.name=name
 if material:o.data.materials.append(material)
 if parent:o.parent=parent
 return o

def cube(name,loc,size,m,parent=None,bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 finish(o,name,m,parent)
 if bevel:
  b=o.modifiers.new('Soft manufactured edges','BEVEL');b.width=bevel;b.segments=3
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def cyl(name,loc,r,depth,m,parent=None,rot=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=depth,location=loc);o=bpy.context.object
 if rot:o.rotation_euler=rot
 finish(o,name,m,parent)
 for p in o.data.polygons:p.use_smooth=True
 b=o.modifiers.new('Edge radius','BEVEL');b.width=min(.006,r*.14);b.segments=3
 o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o

def sphere(name,loc,scale,m,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.scale=scale;finish(o,name,m,parent)
 for p in o.data.polygons:p.use_smooth=True
 return o

def pipe(name,points,r,m,parent=None):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=r;c.bevel_resolution=3
 s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);finish(o,name,m,parent);return o

def ring(name,loc,rx,ry,r,m,parent=None,vertical=False):
 points=[]
 for i in range(65):
  a=math.tau*i/64
  points.append((loc[0]+rx*math.cos(a),loc[1]+(0 if vertical else ry*math.sin(a)),loc[2]+(ry*math.sin(a) if vertical else 0)))
 return pipe(name,points,r,m,parent)

def lathe(name,loc,profile,m,parent=None,scale=(1,1,1)):
 verts=[];faces=[];n=64
 for radius,z in profile:
  verts.extend([(loc[0]+radius*math.cos(i*math.tau/n)*scale[0],loc[1]+radius*math.sin(i*math.tau/n)*scale[1],loc[2]+z*scale[2]) for i in range(n)])
 for j in range(len(profile)-1):
  for i in range(n): a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);finish(o,name,m,parent)
 for p in mesh.polygons:p.use_smooth=True
 return o

def merge_children(g):
 obs=[o for o in g.children if o.type=='MESH']
 if len(obs)>1:
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=g.name+'_surface'

# Shell is split by wall to support cutaway and independent finish replacement.
floor=group('floor','Existing tiled floor','surface',ref='IMG_0370, 0377, 0380',fixed=True)
cube('Floor substrate',(0,0,-.055),(W+.14,D+.14,.10),grout,floor,0)
for i in range(8):
 for j in range(5):
  tone=random.uniform(.53,.65);m=mat(f'Floor tile variation {i}-{j}',(tone,tone*.98,tone*.85),.65)
  n=m.node_tree.nodes.new('ShaderNodeTexImage');p=ROOT/'textures'/'aged-tile.png'
  if p.exists():n.image=bpy.data.images.load(str(p),check_existing=True);n.image.pack();m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
  o=cube('300 mm floor tile',(-1.05+i*.3,-.6+j*.3,.008),(.295,.295,.016),m,floor,.003)
# Each tile face gets its own full-range UV to preserve edge wear.
for tile in floor.children:
 if tile.type=='MESH' and tile.data.uv_layers.active:
  for face in tile.data.polygons:
   if len(face.loop_indices)==4:
    for k,li in enumerate(face.loop_indices):tile.data.uv_layers.active.data[li].uv=[(0,0),(1,0),(1,1),(0,1)][k]
merge_children(floor)
walls={}
for side in ['north','west','east','south']:
 g=group('wall_'+side,side.title()+' wall','shell',fixed=True);walls[side]=g
 if side in ['north','south']:
  y=.79 if side=='north' else -.79
  if side=='south':
   cube('Entry wall left',(-.675,y,H/2),(1.05,.08,H),paint,g)
   cube('Entry wall right',(1.125,y,H/2),(.15,.08,H),paint,g)
   cube('Entry lintel',(.45,y,2.39),(1.2,.08,.42),paint,g)
  else:
   cube('North backing left',(-1.025,y,H/2),(.35,.08,H),paint,g,0)
   cube('North backing right',(.50,y,H/2),(1.40,.08,H),paint,g,0)
   cube('North backing below window',(-.525,y,.615),(.65,.08,1.23),paint,g,0)
   cube('North backing above window',(-.525,y,2.32),(.65,.08,.56),paint,g,0)
 else:cube(side+' backing',((-1.24 if side=='west' else 1.24),0,H/2),(.08,D,H),paint,g)
 if side=='east':continue
 length=W if side in ['north','south'] else D
 for i in range(round(length/.15)):
  for j in range(11):
   u=-length/2+.075+i*.15;z=.1+j*.2
   if side=='north' and -.83<u<-.23 and 1.18<z<2.02:continue
   if side=='south' and -.15<u<1.05:continue
   if side in ['north','south']:pos=(u,.745 if side=='north' else -.745,z);size=(.147,.015,.197)
   else:pos=(-1.195,u,z);size=(.015,.147,.197)
   cube('Ivory wall tile',pos,size,ivory,g,.0015)
 merge_children(g)
# Striped east shower feature wall, with a dark lower field and four dark bands.
bands=[(0,.60,True),(.60,.70,False),(.70,.77,True),(.77,.87,False),(.87,.94,True),(.94,1.04,False),(1.04,1.11,True),(1.11,1.21,False),(1.21,1.28,True),(1.28,2.20,False)]
for lo,hi,dark in bands:
 cube('Stone band', (1.193,0,(lo+hi)/2),(.018,D-.012,hi-lo-.002),stone if dark else lightstone,walls['east'],.001)
merge_children(walls['east'])
ceiling=group('ceiling','Ceiling and structural beams','shell',fixed=True)
cube('Ceiling',(0,0,H+.04),(W+.18,D+.18,.08),paint,ceiling)
cube('North soffit',(0,.63,2.42),(W,.24,.32),paint,ceiling)
cube('West soffit',(-1.08,0,2.42),(.24,D,.32),paint,ceiling)

# Toilet at the northwest end of the fixture wall. Local front is -Y.
def toilet(id='toilet',label='Existing floor-mounted toilet',loc=(-.67,.34,0),modern=False):
 g=group(id,label,loc=loc,ref='IMG_0369, 0370 / video 24 s')
 lathe('Sculpted pedestal',(0,0,0),[(.0,.025),(.17,.025),(.18,.09),(.12,.22),(.18,.32),(.21,.38)],white,g,scale=(.83,1.2,1))
 lathe('Porcelain bowl',(0,-.06,.22),[(.11,0),(.20,.09),(.23,.18),(.225,.21),(.18,.205),(.145,.12),(.055,.07)],white,g,scale=(1,1.3,1))
 sphere('Closed oval seat lid',(0,-.07,.445),(.224,.285,.022),white,g)
 cube('Seat hinge bridge',(0,.18,.435),(.3,.09,.045),white,g)
 if modern:cube('Integrated cistern',(0,.245,.60),(.39,.17,.36),white,g,.04)
 else:
  cube('Wall mounted cistern',(0,.30,1.03),(.45,.18,.34),white,g,.035)
  cube('Cistern cover',(0,.30,1.208),(.47,.20,.028),white,g)
  pipe('Exposed flush pipe',[(0,.29,.88),(0,.29,.57),(0,.20,.38)],.023,white,g)
  pipe('Yellow supply hose',[(.22,.32,1.04),(.36,.33,.99),(.37,.36,.64),(.37,.38,.56)],.009,tan,g)
 cyl('Flush button',(.155,.198,1.11),.023,.025,white,g,(math.pi/2,0,0))
 return g
wc=toilet()

def basin(id='basin',label='Existing wall-hung basin',loc=(.32,.53,.66),modern=False):
 g=group(id,label,loc=loc,ref='IMG_0379, 0380 / video 16 s')
 lathe('Hollow ceramic basin',(0,-.08,0),[(0,0),(.11,.01),(.23,.06),(.29,.16),(.295,.19),(.255,.19),(.23,.13),(.15,.055),(.035,.038)],white,g,scale=(1,.77,1))
 cube('Basin tap deck',(0,.08,.17),(.48,.15,.065),white,g,.02)
 cyl('Drain',(0,-.08,.046),.027,.005,chrome,g)
 for i in range(5):
  a=i*math.tau/5;cyl('Drain opening',(.016*math.cos(a),-.08+.016*math.sin(a),.05),.004,.002,black,g)
 pipe('Mixer spout',[(0,.07,.20),(0,.07,.32),(0,-.025,.33),(0,-.05,.30)],.017,chrome,g)
 cube('Mixer lever',(0,.07,.34),(.03,.10,.012),chrome,g)
 pipe('Waste pipe',[(0,-.03,.0),(0,-.03,-.24),(0,.07,-.32),(0,.12,-.52)],.021,white,g)
 if modern:
  cube('Floating oak vanity',(0,-.02,-.22),(.65,.42,.4),wood,g,.015)
  for z in [-.30,-.12]:cube('Drawer front',(0,-.24,z),(.62,.015,.16),wood,g);cube('Drawer pull',(0,-.255,z+.035),(.19,.018,.014),black,g)
 return g
sink=basin()
mirror=group('mirror','Silver-framed mirror cabinet',loc=(.32,.715,1.42),ref='IMG_0381, 0382')
cube('Mirror cabinet body',(0,0,0),(.43,.09,.52),edge,mirror,.035)
cube('Mirror outer white rim',(0,-.051,0),(.425,.025,.505),white,mirror,.036)
cube('Reflective glass',(0,-.068,0),(.374,.008,.454),glass,mirror,.027)
# A towel ring on fixture wall.
g=group('towel_ring','Round towel ring',loc=(-.19,.70,1.02),ref='IMG_0381')
cyl('Mount',(0,0,.11),.035,.03,chrome,g,(math.pi/2,0,0));ring('Ring',(0,-.04,0),.095,.105,.008,chrome,g,True)

# Window recess and bars, above cistern.
g=group('window','Recessed barred window',loc=(-.54,.744,1.63),ref='IMG_0369 / video 24 s',fixed=True)
cube('Window dark recess',(0,.046,0),(.59,.028,.78),black,g,0)
cube('Opaque yellow glass',(0,.029,0),(.54,.012,.73),tan,g,0)
for z in [-.38,-.12,.13,.38]:cube('Window horizontal bar',(0,-.035,z),(.61,.035,.025),black,g)
for x in [-.3,.3]:cube('Window frame',(x,-.018,0),(.03,.06,.80),black,g)
cube('Window sill',(0,-.07,-.40),(.64,.18,.04),stone,g)

# Shower along the northeast edge of north wall.
def shower(id='shower',label='Existing exposed shower and mixer',loc=(.94,.69,0),rain=False):
 g=group(id,label,loc=loc,ref='IMG_0378, 0379 / video 4 s')
 pipe('Shower riser',[(0,0,.8),(0,0,2.02),(0,-.06,2.12),(0,-.20,2.12)],.012,chrome,g)
 if rain:cyl('Rain shower head',(0,-.21,2.09),.145,.025,chrome,g)
 else:
  pipe('Shower elbow',[(0,-.20,2.12),(0,-.25,2.07)],.017,chrome,g)
  head=cyl('Bell shower head',(0,-.268,2.052),.044,.052,chrome,g,(.65,0,0))
 pipe('Mixer body',[(-.095,-.015,.82),(.095,-.015,.82)],.026,chrome,g)
 for x in [-.09,.09]:
  cyl('Mixer wall escutcheon',(x,.017,.82),.044,.03,chrome,g,(math.pi/2,0,0))
  sphere('Mixer handle',(x,-.058,.85),(.036,.025,.019),chrome,g)
 pipe('Lower spout',[(0,-.02,.81),(0,-.15,.79),(0,-.17,.73)],.019,chrome,g)
 return g
shower()
g=group('soap_tray','Wall soap tray',loc=(.67,.65,.84),ref='IMG_0380')
cube('Amber tray',(0,0,0),(.14,.15,.015),tan,g);cube('Soap bar',(0,-.025,.022),(.08,.05,.03),soap,g,.013)

# Geyser on west wall, rotated to face into the room.
def geyser(id='geyser',label='Existing cylindrical geyser',loc=(-1.02,.30,1.83),compact=False):
 g=group(id,label,loc=loc,ref='IMG_0371 / video 26 s');g.rotation_euler[2]=math.pi/2
 r=.20 if not compact else .14;h=.67 if not compact else .42
 cyl('Cream insulated tank',(0,0,0),r,h,white,g)
 for z in [-h/2,h/2]:cyl('Black end cap',(0,0,z),r*1.025,.055,black,g)
 cube('Heater badge',(0,-r-.003,.18),(.15,.008,.028),black,g)
 for x in [-.07,0,.07]:
  o=cube('Vintage coloured decal',(x,-r-.009,.05),(.038,.004,.11),red if x<0 else tan if x>0 else black,g);o.rotation_euler[1]=.35
 for x in [-.07,.07]:
  cyl('Heater valve',(x,0,-h/2-.055),.019,.08,chrome,g)
  pipe('Flexible heater hose',[(x,0,-h/2-.10),(x*1.4,-.07,-h/2-.36),(x*2,0,-h/2-.40),(x*2,.06,-h/2-.19)],.009,white,g)
 return g
geyser()
g=group('cabinet','Existing yellow wall cabinet',loc=(-1.05,-.35,1.68),ref='IMG_0372, 0374');g.rotation_euler[2]=math.pi/2
cube('Yellow cabinet carcass',(0,0,0),(.39,.23,.56),yellow,g)
cube('Grey door border',(0,-.125,0),(.38,.026,.55),edge,g)
cube('Yellow inset panel',(0,-.145,0),(.305,.018,.46),yellow,g)
cube('Red cabinet handle',(.13,-.168,-.13),(.014,.027,.1),red,g)
# Long rail on west wall.
g=group('towel_rail','Long towel rail',loc=(-1.12,-.3,1.02),ref='IMG_0373, 0375');g.rotation_euler[2]=math.pi/2
pipe('Rail',[(-.35,-.05,0),(.35,-.05,0)],.012,chrome,g)
for x in [-.35,.35]:cyl('Rail rose',(x,0,0),.031,.035,chrome,g,(math.pi/2,0,0));pipe('Rail bracket',[(x,0,0),(x,-.05,0)],.011,chrome,g)
# Door on south with separate fittings.
g=group('door','Yellow entrance door',loc=(.45,-.765,1.09),ref='IMG_0375, 0376 / video 40 s')
cube('Door slab',(0,0,0),(1.17,.045,2.18),yellow,g,.007)
for z in [i*.2-.98 for i in range(11)]:cube('Horizontal door seam',(0,.026,z),(1.16,.0015,.0015),tan,g,0)
cube('Door kick plate',(0,.031,-.91),(1.16,.015,.34),edge,g,.002)
for x in [-.59,.59]:cube('Door edge',(x,0,0),(.025,.06,2.2),edge,g)
for x in [-.28,.22]:pipe('Black coat hook',[(x,.04,.76),(x,.095,.68),(x,.12,.69),(x,.13,.76)],.012,black,g)
pipe('Door pull',[(.45,.04,.17),(.45,.1,.17),(.45,.1,.37),(.45,.04,.37)],.009,chrome,g)
cube('Slide bolt',(.40,.07,-.11),(.26,.025,.025),chrome,g)
for z in [-.8,.7]:cube('Door hinge',(-.57,.04,z),(.06,.012,.13),chrome,g)
# Overhead storage and drying rods.
g=group('loft','Overhead storage cupboard',loc=(.25,.47,2.42),ref='IMG_0383',fixed=True)
cube('Loft carcass',(0,0,0),(1.65,.5,.36),paint,g)
cube('Dark open loft compartment',(.28,-.257,0),(.56,.009,.26),black,g,0)
for x in [-.52,.63]:cube('Loft sliding panel',(x,-.267,0),(.58,.025,.30),paint,g)
g=group('drying_rods','Two overhead drying rods',ref='IMG_0376, 0378, 0383')
for y in [-.42,.24]:pipe('Drying rod',[(-1.2,y,2.32),(1.2,y,2.32)],.009,chrome,g)
# Light, socket and visible black cable.
g=group('socket','Existing switch and plug point',loc=(-.08,.716,2.04),ref='IMG_0381')
cube('Switch plate',(0,0,0),(.18,.025,.16),white,g)
for x in [-.05,.04]:cube('Rocker switch',(x,-.02,.025),(.035,.014,.053),paint,g)
cyl('Plug',(0,-.035,-.03),.024,.035,black,g,(math.pi/2,0,0))
g=group('bulb','Exposed wall light',loc=(.40,.68,2.09),ref='IMG_0381')
cyl('Light wall rose',(0,0,0),.055,.04,edge,g,(math.pi/2,0,0));pipe('Angled holder',[(0,-.02,0),(0,-.08,-.02)],.023,white,g)
sphere('LED bulb',(0,-.12,-.035),(.035,.058,.035),white,g)
g=group('cable','Exposed geyser cable',ref='IMG_0369, 0381')
pipe('Black cable',[(-1.02,.32,1.93),(-1.15,.55,1.97),(-1.12,.712,1.99),(-.60,.718,1.87),(-.08,.685,2.01)],.006,black,g)
# Bidet sprayer and hose on west wall by toilet.
g=group('bidet','Handheld bidet sprayer and hose',loc=(-1.16,.30,.7),ref='IMG_0370 / video 22 s');g.rotation_euler[2]=math.pi/2
pipe('Flexible steel hose',[(0,0,.09),(0,-.05,-.29),(.12,-.09,-.48),(.30,0,-.38),(.30,0,-.18)],.008,chrome,g)
cube('Sprayer grip',(0,-.035,.16),(.033,.04,.15),chrome,g)
cube('Sprayer head',(0,-.06,.25),(.063,.05,.03),chrome,g)
cyl('Tap mount',(.30,0,-.18),.035,.035,chrome,g,(math.pi/2,0,0))
# Buckets and mugs are hollow, independently movable.
def bucket(id,label,loc,m=teal,r=.17,h=.29):
 g=group(id,label,'accessory',loc,ref='IMG_0373, 0379')
 lathe('Hollow plastic bucket',(0,0,0),[(0,.008),(r*.79,.008),(r,h),(r-.012,h),(r*.79-.012,.025),(0,.025)],m,g)
 for z in [.045,h-.018]:ring('Bucket reinforcing rim',(0,0,z),r*(.8+.2*z/h),r*(.8+.2*z/h),.006,m,g)
 pipe('Wire handle',[(-r,0,h-.045),(-r*1.05,-.07,h*.5),(0,-r*1.02,h*.30),(r*1.05,-.07,h*.5),(r,0,h-.045)],.005,edge,g)
 return g
bucket('teal_bucket','Teal shower bucket',(.94,.38,.02))
bucket('tan_bucket','Ochre utility bucket',(-.96,-.39,.02),tan,.15,.25)
bucket('teal_mug','Teal bath mug',(.96,.36,.18),teal,.055,.10)
bucket('tan_mug','Ochre floor mug',(-.91,.29,.02),tan,.06,.10)
# small mug handles
for id in ['teal_mug','tan_mug']:
 g=bpy.data.objects[id];pipe('Mug handle',[(.052,0,.09),(.095,0,.08),(.095,0,.035),(.052,0,.025)],.006,teal if id=='teal_mug' else tan,g)
g=group('toilet_brush','Toilet brush on floor','accessory',(-.94,.12,.04),ref='IMG_0370 / video 22 s')
sphere('Brush bristles',(0,0,0),(.05,.06,.027),white,g);pipe('Brush handle',[(0,.02,.02),(.13,.28,.035)],.007,blue,g)
g=group('drain','Square floor drain','fixture',(-.96,.05,.02),ref='video 20 s',fixed=True)
cube('Drain plate',(0,0,0),(.10,.10,.004),chrome,g)
for x in range(5):
 for y in range(5):cyl('Drain perforation',((x-2)*.014,(y-2)*.014,.003),.004,.002,black,g)

def bottle(id,label,loc,m=white,h=.15,r=.025,pump=False):
 g=group(id,label,'accessory',loc,ref='IMG_0380 / video 16 s, 24 s')
 cyl('Bottle body',(0,0,h*.44),r,h*.88,m,g);cyl('Bottle neck',(0,0,h*.93),r*.45,h*.1,m,g)
 cyl('Cap',(0,0,h),r*.5,.022,black if m==red else white,g)
 if pump:pipe('Pump spout',[(0,0,h+.014),(0,0,h+.036),(.035,0,h+.036)],.004,white,g)
 cube('Plain label',(0,-r-.001,h*.46),(r*1.2,.002,h*.40),white,g,.002)
 return g
bottle('red_bottle','Red toiletry bottle',(.42,.55,.88),red,.18,.024)
bottle('soap_pump','Hand wash pump',(.12,.58,.88),soap,.14,.029,True)
bottle('white_pump','White pump bottle',(.23,.60,.88),white,.14,.023,True)
bottle('sill_yellow_bottle','Window sill yellow bottle',(-.74,.65,1.255),soap,.20,.03,True)
bottle('sill_white_bottle','Window sill white bottle',(-.56,.65,1.255),white,.16,.025)
bottle('sill_green_bottle','Window sill green bottle',(-.40,.65,1.255),teal,.17,.025)
g=group('toothbrush','Toothbrush','accessory',(.51,.44,.88),ref='IMG_0380');cube('Handle',(0,0,0),(.012,.15,.009),blue,g);cube('Bristles',(0,.065,.012),(.015,.025,.013),white,g)
g=group('toothpaste','Toothpaste tube','accessory',(.50,.59,.91),ref='IMG_0380');o=cube('Tube',(0,0,0),(.045,.13,.026),white,g);o.rotation_euler[2]=-.25;cube('Blue label',(0,-.01,.016),(.027,.07,.002),blue,g)
g=group('small_jar','Small white cosmetic pot','accessory',(.46,.47,.90),ref='IMG_0380');cyl('Pot',(0,0,0),.024,.025,white,g);cyl('Blue pot label',(0,0,.015),.018,.002,blue,g)
g=group('sill_razor','Small toiletry on window sill','accessory',(-.28,.65,1.27),ref='video 24 s');cube('Handle',(0,0,0),(.065,.018,.016),blue,g);cube('Head',(.035,0,0),(.018,.035,.018),white,g)

# Lighting and presentation.
world=bpy.data.worlds.new('Bathroom daylight') if not bpy.data.worlds else bpy.data.worlds[0];scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.78,.83,1);world.node_tree.nodes['Background'].inputs[1].default_value=.22
for name,loc,power,size in [('Ceiling soft light',(0,0,2.48),75,1.3),('Entrance daylight',(.1,-2.3,2.4),120,2),('Basin fill',(.3,.35,2.22),30,.45)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
light=bpy.data.lights.new('Wall bulb illumination','POINT');light.energy=12;light.shadow_soft_size=.09;o=bpy.data.objects.new('Wall bulb illumination',light);scene.collection.objects.link(o);o.location=(.40,.65,2.05)

def camera(name,loc,target,lens=30):
 d=bpy.data.cameras.new(name);d.lens=lens;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
cam=camera('Camera | dollhouse',(3.7,-4.7,3.7),(0,0,1.1),47)
interior=camera('Camera | doorway',(.3,-.73,1.58),(-.25,.72,1.27),17)
scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
# Export complete scene without cameras or lamps; browser supplies dynamic lights.
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
 if o.type not in {'LIGHT','CAMERA'}:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'web/public/models/bathroom-existing.glb'),export_format='GLB',use_selection=True,export_extras=True,export_apply=True,export_cameras=False,export_lights=False)
entities=[{'id':o['entityId'],'label':o['label'],'category':o['category'],'reference':o['reference'],'estimated':True,'fixed':o['fixed']} for o in scene.objects if 'entityId' in o]
(ROOT/'docs/object-inventory.json').write_text(json.dumps(entities,indent=2))
scene.camera=interior
scene.render.filepath=str(ROOT/'renders/existing-interior.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/bathroom-existing.blend'))
scene.camera=cam
# Render a cutaway; full enclosure remains in the saved master and GLB.
def visibility(g,value):
 g.hide_render=not value
 for c in g.children_recursive:c.hide_render=not value
for key in ['wall_south','wall_east','ceiling','door','drying_rods']:visibility(bpy.data.objects[key],False)
scene.render.filepath=str(ROOT/'renders/existing-cutaway.png');bpy.ops.render.render(write_still=True)
for key in ['wall_east','drying_rods']:visibility(bpy.data.objects[key],True)
scene.camera=interior;scene.render.resolution_x=1500;scene.render.resolution_y=1100
scene.render.filepath=str(ROOT/'renders/existing-interior.png');bpy.ops.render.render(write_still=True)
scene.camera=camera('Camera | shower wall',(-.85,-.52,1.55),(.85,.45,1.30),19)
scene.render.filepath=str(ROOT/'renders/existing-shower.png');bpy.ops.render.render(write_still=True)
# Alternatives exported as independent, portable authored assets.
for o in list(scene.objects):bpy.data.objects.remove(o,do_unlink=True)
alternatives=[toilet('modern_toilet','Compact close-coupled toilet',(0,0,0),True),basin('oak_vanity','Floating oak vanity',(0,0,.66),True),shower('rain_shower','Rain shower',(0,0,0),True),geyser('compact_geyser','Compact geyser',(0,0,1.8),True)]
g=group('tall_cabinet','Tall oak storage cabinet',loc=(0,0,0));cube('Cabinet',(0,0,.80),(.45,.32,1.6),wood,g)
for z in [.42,1.20]:cube('Door front',(0,-.168,z),(.43,.025,.75),wood,g);cube('Handle',(.14,-.19,z),(.012,.026,.13),black,g)
alternatives.append(g)
g=group('modern_basin','Rectangular wall basin',loc=(0,0,.85));cube('Basin outer',(0,0,0),(.56,.40,.09),white,g,.035);lathe('Vessel bowl',(0,-.02,.035),[(.08,0),(.20,.07),(.22,.10),(.20,.11),(.16,.055),(.035,.02)],white,g,scale=(1,.75,1));pipe('Tall tap',[(0,.12,.04),(0,.12,.30),(0,-.02,.30)],.013,black,g);alternatives.append(g)
g=group('modern_socket','Modern switched socket',loc=(0,0,1.25));cube('Faceplate',(0,0,0),(.15,.02,.085),white,g)
for x in [-.035,0,.035]:cube('Socket hole',(x,-.012,0),(.008,.008,.018),black,g)
alternatives.append(g)
catalog=[]
for g in alternatives:
 bpy.ops.object.select_all(action='DESELECT');g.select_set(True)
 for o in g.children_recursive:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(ROOT/'web/public/models'/f'{g.name}.glb'),export_format='GLB',use_selection=True,export_extras=True,export_apply=True)
 catalog.append({'id':g.name,'label':g['label'],'file':f'models/{g.name}.glb'})
(ROOT/'web/public/models/catalog.json').write_text(json.dumps(catalog,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/fixture-alternatives.blend'))
print(json.dumps({'status':'complete','entities':len(entities),'alternatives':len(catalog),'dimensions_m':[W,D,H]}))
