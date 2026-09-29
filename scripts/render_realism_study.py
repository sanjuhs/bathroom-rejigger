"""Non-destructive lighting/material study; retains the editable room master.
Run in background Blender. Procedural shaders in this study are not exported to the web app.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/bathroom-existing.blend'))
scene=bpy.context.scene

def pbr(name,color=None,rough=None,metal=None):
 m=bpy.data.materials.get(name)
 if not m:return None
 p=m.node_tree.nodes.get('Principled BSDF')
 if color is not None:p.inputs['Base Color'].default_value=(*color,1)
 if rough is not None:p.inputs['Roughness'].default_value=rough
 if metal is not None:p.inputs['Metallic'].default_value=metal
 return m

def surface_detail(m,scale=200,depth=.00015,rough_min=.2,rough_max=.3):
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 tex=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.65;l.new(tex.outputs['Object'],noise.inputs['Vector'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=depth;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
 ramp=n.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.15;ramp.inputs['From Max'].default_value=.85;ramp.inputs['To Min'].default_value=rough_min;ramp.inputs['To Max'].default_value=rough_max;l.new(noise.outputs['Fac'],ramp.inputs['Value']);l.new(ramp.outputs['Result'],p.inputs['Roughness'])

ceramic=pbr('Porcelain | warm white',(.72,.745,.72),.13)
ceramic.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.28
ceramic.node_tree.nodes['Principled BSDF'].inputs['Coat Roughness'].default_value=.09
surface_detail(ceramic,360,.000035,.12,.20)
wall=pbr('Existing | warm ivory glazed tile',(.47,.465,.365),.23)
surface_detail(wall,150,.00011,.19,.32)
plaster=pbr('White painted plaster',(.64,.65,.60),.85);surface_detail(plaster,180,.00028,.76,.88)
g=pbr('Existing | aged grout',(.19,.19,.145),.92);surface_detail(g,250,.0005,.8,.96)
metal=pbr('Brushed chrome',(.63,.67,.69),.11,1);surface_detail(metal,900,.000015,.08,.18)
pbr('Aluminium edging',(.44,.49,.51),.28,1)
pbr('Mirror silver',(.96,.97,.98),.018,1)
pbr('Black fittings',(.006,.006,.005),.29)
laminate=pbr('Existing | pale yellow laminate',(.65,.57,.24),.43);surface_detail(laminate,200,.000045,.34,.48)
for name in ['Muted teal bucket','Ochre plastic','Red bottle','Blue plastic','Amber soap']:
 m=pbr(name,rough=.3);surface_detail(m,250,.00008,.25,.40)
# World-space tile mottling and patchy floor staining instead of a repeating image.
for m in bpy.data.materials:
 if not m.name.startswith('Floor tile variation'):continue
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 for link in list(p.inputs['Base Color'].links):l.remove(link)
 coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5.5;noise.inputs['Detail'].default_value=4.5;noise.inputs['Roughness'].default_value=.75;l.new(coord.outputs['Object'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.27;ramp.color_ramp.elements[0].color=(.10,.105,.061,1);ramp.color_ramp.elements[1].position=.69;ramp.color_ramp.elements[1].color=(.62,.61,.47,1)
 middle=ramp.color_ramp.elements.new(.43);middle.color=(.38,.37,.25,1);l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
 surface_detail(m,230,.00035,.33,.64)
# Granular stone at physical scale, with sparse light crystalline flecks.
for name,dark in [('Existing | charcoal stone',True),('Existing | pale stone',False)]:
 m=bpy.data.materials[name];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
 for link in list(p.inputs['Base Color'].links):l.remove(link)
 coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=145;noise.inputs['Detail'].default_value=3;l.new(coord.outputs['Object'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.30;ramp.color_ramp.elements[1].position=.72
 ramp.color_ramp.elements[0].color=(.016,.022,.017,1) if dark else (.34,.335,.29,1)
 ramp.color_ramp.elements[1].color=(.31,.34,.31,1) if dark else (.68,.67,.60,1)
 l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color']);surface_detail(m,270,.00013,.18,.33)
# Give the window a translucent, aged pane in this test.
window=bpy.data.objects['window']
for o in window.children:
 if o.name.startswith('Opaque yellow glass'):
  mat=bpy.data.materials.new('Study | aged translucent window');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.40,.37,.19,1);p.inputs['Transmission Weight'].default_value=.35;p.inputs['Roughness'].default_value=.48;o.data.materials.clear();o.data.materials.append(mat)
# Fully enclose the room: realistic indirect illumination needs the ceiling and walls.
for o in scene.objects:o.hide_render=False
# Door is open for the doorway camera and corridor illumination; do not alter the master.
for o in [bpy.data.objects['door'],*bpy.data.objects['door'].children_recursive]:o.hide_render=True
for o in list(scene.objects):
 if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.48,.57,.70,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.06

def area(name,loc,target,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Study | corridor bounce',(.25,-1.75,1.75),(.25,.55,1),95,1.45,(1,.86,.68))
# The area stands in for diffuse corridor bounce, not a visible studio softbox.
bpy.data.objects['Study | corridor bounce'].visible_glossy=False
bpy.ops.mesh.primitive_cube_add(size=1,location=(.25,-2.40,1.3));back=bpy.context.object;back.name='Study | neutral corridor backdrop';back.dimensions=(3,.08,2.6);back.data.materials.append(bpy.data.materials['White painted plaster'])
area('Study | window daylight',(-.54,1.06,1.62),(-.54,-.3,1.2),32,.48,(.80,.88,1))
d=bpy.data.lights.new('Study | actual wall bulb','POINT');d.energy=22;d.color=(.93,.96,1);d.shadow_soft_size=.032;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(.40,.535,2.055)
# Visible bulb receives its own emissive material, leaving all other white items unlit.
for o in bpy.data.objects['bulb'].children:
 if o.name.startswith('LED bulb'):
  m=bpy.data.materials.new('Study | luminous LED diffuser');m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.85,.90,1,1);p.inputs['Emission Color'].default_value=(.93,.96,1,1);p.inputs['Emission Strength'].default_value=4;o.data.materials.clear();o.data.materials.append(m);o.visible_shadow=False
# Preserve physically meaningful detail but improve curve silhouette smoothness.
for o in scene.objects:
 if o.type=='CURVE':o.data.resolution_u=24;o.data.bevel_resolution=4
scene.camera=bpy.data.objects['Camera | doorway'];scene.camera.data.lens=18
scene.camera.location=(.22,-.715,1.54);target=Vector((-.14,.60,1.23));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.dof.use_dof=False
scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.018;scene.cycles.use_denoising=True
scene.cycles.max_bounces=12;scene.cycles.diffuse_bounces=6;scene.cycles.glossy_bounces=6;scene.cycles.transmission_bounces=8
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.5
scene.render.resolution_x=1200;scene.render.resolution_y=975;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene['study_note']='Lighting and procedural material study, not a measured/photo-calibrated reconstruction. Entry door omitted to represent open doorway. Web materials unchanged.'
scene.render.filepath=str(ROOT/'renders/realism-study.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/bathroom-realism-study.blend'))
bpy.ops.render.render(write_still=True)
print(json.dumps({'blend':str(ROOT/'blender/bathroom-realism-study.blend'),'render':scene.render.filepath,'samples':scene.cycles.samples}))
