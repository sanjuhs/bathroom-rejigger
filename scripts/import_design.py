"""Import a browser JSON proposal into a separate Blender file.
blender --background --factory-startup --python scripts/import_design.py -- design.json output.blend
"""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(args)!=2:raise SystemExit('Expected design.json and output.blend after --')
source,output=map(lambda p:Path(p).resolve(),args)
if output in [ROOT/'blender/bathroom-existing.blend',ROOT/'blender/fixture-alternatives.blend']:raise ValueError('Choose a separate proposal filename')
data=json.loads(source.read_text())
if data.get('schema')!=1 or not isinstance(data.get('objects'),list) or len(data['objects'])>250:raise ValueError('Unsupported design')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/bathroom-existing.blend'))
originals={o['entityId']:o for o in bpy.context.scene.objects if 'entityId' in o}
catalog={a['id'] for a in json.loads((ROOT/'web/public/models/catalog.json').read_text())}
seen=set()
for item in data['objects']:
 id=item.get('id');asset=item.get('asset')
 if not isinstance(id,str) or id in seen:raise ValueError('Duplicate or missing ID')
 seen.add(id)
 if asset:
  if id in originals or not (asset in catalog or asset.startswith('existing:') and asset[9:] in originals):raise ValueError('Invalid asset')
 elif id not in originals:raise ValueError('Unknown original')
 for key,n in [('p',3),('q',4)]:
  if len(item.get(key,[]))!=n or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in item[key]):raise ValueError('Invalid transform')
 if any(abs(v)>20 for v in item['p']) or abs(math.sqrt(sum(v*v for v in item['q']))-1)>.01:raise ValueError('Transform out of range')
 if not isinstance(item.get('visible'),bool):raise ValueError('Invalid visibility')
if not set(originals).issubset(seen):raise ValueError('Missing original objects')
prepared={}
def copy_tree(src,parent=None):
 obj=src.copy()
 if src.data:obj.data=src.data.copy()
 bpy.context.scene.collection.objects.link(obj);obj.parent=parent
 for child in src.children:copy_tree(child,obj)
 return obj
# Prepare copies before moving any originals.
for item in data['objects']:
 asset=item.get('asset')
 if not asset:continue
 if asset.startswith('existing:'):obj=copy_tree(originals[asset[9:]])
 else:
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'web/public/models'/f'{asset}.glb'))
  obj=next(o for o in set(bpy.data.objects)-before if o.get('entityId')==asset)
 obj['entityId']=item['id'];obj['label']=item.get('label',obj.get('label',asset));prepared[item['id']]=obj
basis=Quaternion((1,0,0),math.pi/2)
for item in data['objects']:
 obj=prepared.get(item['id']) or originals[item['id']]
 x,h,s=item['p'];obj.location=(x,-s,h)
 qx,qy,qz,qw=item['q'];obj.rotation_mode='QUATERNION';obj.rotation_quaternion=basis@Quaternion((qw,qx,qy,qz))@basis.inverted()
 for node in [obj,*obj.children_recursive]:node.hide_render=not item['visible'];node.hide_set(not item['visible'])
colors={'limestone':(.56,.55,.45,1),'sage':(.29,.43,.36,1),'terrazzo':(.72,.72,.65,1),'terracotta':(.57,.26,.15,1)}
for surface,finish in data.get('finishes',{}).items():
 if finish=='existing':continue
 if finish not in colors or surface not in {'floor','walls','feature'}:raise ValueError('Invalid finish')
 material=bpy.data.materials.new('Proposal | '+finish);material.diffuse_color=colors[finish];material.use_nodes=True;bsdf=material.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=colors[finish];bsdf.inputs['Roughness'].default_value=.6
 ids=['floor'] if surface=='floor' else ['wall_east'] if surface=='feature' else ['wall_north','wall_south','wall_west']
 for id in ids:
  for child in originals[id].children_recursive:
   if child.type=='MESH':
    for slot in child.material_slots:slot.material=material
bpy.context.scene['design_notes']=str(data.get('notes',''))[:20000]
bpy.context.scene['design_source']=source.name
bpy.context.scene['finish_note']='Proposal finishes use approximate solid colors; browser procedural patterns are not transferred.'
output.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(output))
print(json.dumps({'saved':str(output),'objects':len(data['objects'])}))
