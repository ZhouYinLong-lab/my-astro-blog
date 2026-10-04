"""Blender 4.5: deterministic courtyard blockout, GLB and two rendered studies.

Run: blender --background --python tools/build-estate.py
No downloaded assets or add-ons. Coordinates: X east, Y north, Z up.
"""
import bpy
import math
import random
import json
import sys
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
PIXEL = '--pixel' in sys.argv
PREFIX = 'estate-pixel' if PIXEL else 'estate'
DATA_NAME = 'regions-pixel.json' if PIXEL else 'regions.json'
OUT = ROOT / 'artifacts' / 'estate'
WEB = ROOT / 'public' / 'world' / 'blender'
OUT.mkdir(parents=True, exist_ok=True)
WEB.mkdir(parents=True, exist_ok=True)
random.seed(514)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.name = 'Estate_Day'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 1440
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
if PIXEL:
    scene.render.resolution_x = 640
    scene.render.resolution_y = 480
    scene.cycles.samples = 256
    scene.cycles.use_denoising = True
    scene.cycles.pixel_filter_type = 'BOX'
    scene.cycles.filter_width = .01
    scene.render.dither_intensity = 0

def mat(name, color, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = .78
    p.inputs['Emission Color'].default_value = (*color, 1)
    p.inputs['Emission Strength'].default_value = emission
    return m

M = {
    'soil': mat('Earth · deep moss', (.16,.23,.16)),
    'grass': mat('Garden · sage', (.32,.43,.26)),
    'stone': mat('Limestone · warm grey', (.51,.54,.43)),
    'paper': mat('Lime plaster · ivory', (.78,.77,.61)),
    'wood': mat('Timber · walnut', (.20,.115,.058)),
    'roof': mat('Tiles · charcoal jade', (.075,.095,.083)),
    'gold': mat('Brass · ochre', (.63,.38,.13)),
    'leaf': mat('Willow · olive', (.28,.40,.12)),
    'leaf2': mat('Bamboo · forest', (.105,.25,.14)),
    'water': mat('Pond · celadon', (.095,.34,.29)),
    'lamp': mat('Lantern · amber', (1,.54,.17), .4),
    'screen': mat('Lab · pale mint', (.15,.8,.61), .45),
    'book': mat('Books · cinnabar', (.48,.16,.09)),
}
regions = [
    dict(id='home', label='主庭院', subtitle='寒柳别苑', href='/', anchor=[0,-6.1,2.1]),
    dict(id='making', label='机杼工坊', subtitle='项目与工具', href='/chores/making/', anchor=[-5.8,-.5,3]),
    dict(id='lab', label='尺蠖实验室', subtitle='算法与智能系统', href='/blog/category/尺蠖/', anchor=[5.7,.5,3.4]),
    dict(id='library', label='留丝书斋', subtitle='博客与阅读', href='/blog/', anchor=[0,4.6,3.8]),
    dict(id='garden', label='语义花园', subtitle='探索内容联系', href='/chores/garden/', anchor=[-4.4,5.8,1.2]),
    dict(id='backyard', label='会客间', subtitle='留言与交流', href='/backyard/', anchor=[5,-3.4,2.5]),
]
parents = {}
for r in regions:
    obj = bpy.data.objects.new('nav_'+r['id'], None)
    scene.collection.objects.link(obj)
    obj['href'] = r['href']
    obj['label'] = r['label']
    parents[r['id']] = obj

def finish(obj, name, material, region=None):
    obj.name = name
    obj.data.materials.append(M[material])
    if region:
        obj.parent = parents[region]
    return obj

def box(name, loc, size, material, region=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, material, region)

def cylinder(name, loc, radius, depth, material, region=None, vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    return finish(bpy.context.object, name, material, region)

def beam(a, b, radius, material, region=None):
    a, b = Vector(a), Vector(b)
    ob = cylinder('Beam', (a+b)/2, radius, (b-a).length, material, region, 8)
    ob.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    return ob

def blob(loc, scale, material, region=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=loc)
    ob = bpy.context.object
    ob.scale = scale
    return finish(ob, 'Foliage / rock', material, region)

def roof(x, y, w, d, z, region):
    # Curved roof profile; raised eaves, steep ridge, gabled cross-section.
    profile = [(-d/2, z+.20),(-d*.35,z+.13),(-d*.20,z+.52),(0,z+1.02),
               (d*.20,z+.52),(d*.35,z+.13),(d/2,z+.20)]
    verts = [(x+side*w/2,y+dy,h) for side in [-1,1] for dy,h in profile]
    faces = [(i,i+1,8+i,7+i) for i in range(6)]
    mesh = bpy.data.meshes.new('Swept roof mesh')
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new('Swept tile roof', mesh)
    scene.collection.objects.link(obj)
    finish(obj, 'Swept tile roof', 'roof', region)
    if PIXEL:
        detail.roof_tiles(x,y,w,d,z,profile,region)
        beam((x-w/2-.08,y,z+1.08),(x+w/2+.08,y,z+1.08),.09,'roof',region)
        return
    for dy,h in profile:
        beam((x-w/2,y+dy,h),(x+w/2,y+dy,h),.045,'roof',region)
    for i in range(int(w/.28)+1):
        xx=x-w/2+i*w/int(w/.28)
        for j in range(6):
            dy,h=profile[j]; dy2,h2=profile[j+1]
            beam((xx,y+dy,h+.02),(xx,y+dy2,h2+.02),.038,'roof',region)
    beam((x-w/2-.08,y,z+1.08),(x+w/2+.08,y,z+1.08),.09,'roof',region)

def building(region,x,y,w,d,h=2.1):
    box('Stone plinth',(x,y,.20),(w+.5,d+.5,.4),'stone',region)
    box('Back plaster',(x,y+d/2-.08,h/2+.4),(w,.16,h),'paper',region)
    for side in [-1,1]:
        box('Side wall',(x+side*(w/2-.08),y,h/2+.4),(.16,d,h),'paper',region)
        for dy in [-d/2,d/2]:
            cylinder('Timber column',(x+side*(w/2-.15),y+dy,h/2+.4),.085,h,'wood',region)
    box('Front lintel',(x,y-d/2,h+.28),(w,.16,.22),'wood',region)
    # Complete front wall assembled around actual door/window openings.
    front=y-d/2
    top=h+.4
    door_w=min(1.12,w*.28)
    door_top=min(2.35,top-.25)
    win_w=w*.18
    win_bottom=1.03
    win_top=min(1.92,top-.28)
    holes=[(-door_w/2,door_w/2,.4,door_top)]
    holes += [(dx-win_w/2,dx+win_w/2,win_bottom,win_top) for dx in [-w*.32,w*.32]]
    xs=sorted(set([-w/2,w/2]+[v for hole in holes for v in hole[:2]]))
    zs=sorted(set([.4,top]+[v for hole in holes for v in hole[2:]]))
    for xa,xb in zip(xs,xs[1:]):
        for za,zb in zip(zs,zs[1:]):
            mx,mz=(xa+xb)/2,(za+zb)/2
            if not any(a<mx<b and c<mz<e for a,b,c,e in holes):
                box('Front masonry',(x+mx,front,mz),(xb-xa,.20,zb-za),'paper',region)
    for dx in [-door_w/2,door_w/2]:
        box('Door jamb',(x+dx,front-.055,(.4+door_top)/2),(.09,.27,door_top-.4),'wood',region)
    box('Door lintel',(x,front-.055,door_top),(door_w+.16,.27,.12),'wood',region)
    box('Door threshold',(x,front,.44),(door_w,.30,.08),'stone',region)
    # Door leaves visibly hinged into the room; other rooms have closed doors.
    angle=math.radians(62 if region in ['library','making'] else 0)
    for side in [-1,1]:
        hinge=Vector((x+side*door_w/2,front-.025,0))
        leaf_width=door_w/2-.025
        direction=Vector((-side*math.cos(angle),math.sin(angle),0))
        center=hinge+direction*leaf_width/2
        ob=box('Timber door leaf',(center.x,center.y,(.48+door_top-.08)/2),
               (leaf_width,.07,door_top-.56),'wood',region)
        ob.rotation_euler[2]=math.atan2(direction.y,direction.x)
        for z in [.70,door_top-.28]:
            ob=box('Door rail',(center.x,center.y-.045,z),(leaf_width,.045,.07),'gold',region)
            ob.rotation_euler[2]=math.atan2(direction.y,direction.x)
    for dx in [-w*.32,w*.32]:
        cx=x+dx
        box('Window sill',(cx,front-.09,win_bottom),(win_w+.20,.38,.10),'stone',region)
        box('Paper window',(cx,front+.035,(win_bottom+win_top)/2),(win_w,.035,win_top-win_bottom),'lamp',region)
        for xx in [cx-win_w/2,cx+win_w/2]:
            box('Window frame',(xx,front-.10,(win_bottom+win_top)/2),(.07,.12,win_top-win_bottom+.08),'wood',region)
        for z in [win_bottom,win_top,(win_bottom+win_top)/2]:
            box('Window rail',(cx,front-.10,z),(win_w,.12,.055),'wood',region)
        for j in range(1,6):
            box('Window lattice',(cx-win_w/2+j*win_w/6,front-.11,(win_bottom+win_top)/2),(.028,.07,win_top-win_bottom),'wood',region)
    # Gable infill and ceiling close the space below the roof on all sides.
    box('Ceiling',(x,y,top+.05),(w,d,.12),'wood',region)
    for side in [-1,1]:
        gx=x+side*(w/2-.04)
        mesh=bpy.data.meshes.new('Closed gable')
        mesh.from_pydata([(gx,y-d/2,top),(gx,y-d/2,top+.24),
                         (gx,y,top+1.02),(gx,y+d/2,top+.24),(gx,y+d/2,top)],[],[(0,1,2,3,4)])
        ob=bpy.data.objects.new('Gable wall',mesh);scene.collection.objects.link(ob)
        finish(ob,'Gable wall','paper',region)
    # Warm rear lattice, visible through the narrow doorway only.
    for dx in [-w*.31,w*.31]:
        box('Luminous lattice window',(x+dx,y+d/2-.18,1.35),(w*.23,.025,.83),'lamp',region)
        for j in range(5):
            box('Window lattice',(x+dx-w*.115+j*w*.0575,y+d/2-.21,1.35),(.025,.04,.87),'wood',region)
        box('Window crossbar',(x+dx,y+d/2-.21,1.35),(w*.23,.04,.025),'wood',region)
    for step in range(3):
        box('Entrance stair',(x,y-d/2-.22-step*.19,.18-step*.045),(w*.55,.3,.18),'stone',region)
    roof(x,y,w+.7,d+.7,h+.4,region)
    if PIXEL:
        detail.facade(x,y,w,d,h,region)

if PIXEL:
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from estate_detail import EstateDetail
    detail = EstateDetail(M,parents)

box('Diorama foundation',(0,0,-.48),(17.4,16,.85),'soil')
box('Moss garden',(0,0,-.025),(17.2,15.8,.12),'grass')
box('Courtyard paving',(0,-1.7,.04),(9,9.1,.13),'stone','home')
for xx in range(-4,5):
    for yy in range(-6,3):
        box('Paving joint',(xx,yy,.112),(.022,.94,.015),'soil','home')
        box('Paving joint',(xx+.5,yy-.48,.112),(.98,.022,.015),'soil','home')
if PIXEL:
    detail.courtyard()
for x in [-8,8]:
    box('Perimeter plaster',(x,0,.58),(.18,15.2,1.15),'paper')
    box('Wall cap',(x,0,1.2),(.36,15.25,.15),'roof')
box('North garden wall',(0,7.5,.58),(16,.18,1.15),'paper')
box('North wall cap',(0,7.5,1.2),(16.2,.36,.15),'roof')
for x in [-4.9,4.9]:
    box('Entry wall',(x,-6.9,.65),(6.2,.20,1.3),'paper','home')
    box('Entry wall cap',(x,-6.9,1.33),(6.35,.4,.18),'roof','home')
for x in [-1.15,1.15]:
    box('Gate pillar',(x,-6.9,1.03),(.26,.35,2.05),'wood','home')
for side in [-1,1]:
    box('Gate masonry',(side*1.48,-6.9,.93),(.65,.24,1.85),'paper','home')
    box('Gate door',(side*.78,-6.86,.95),(.62,.12,1.82),'wood','home')
roof(0,-6.9,3.25,1.6,2.12,'home')
box('Gate sign',(0,-7.09,1.88),(1.40,.07,.30),'gold','home')
for j in range(3):
    box('Gate step',(0,-7.4-j*.15,.11-j*.04),(2.65+j*.2,.4,.15),'stone','home')

building('library',0,4.5,5.2,2.65,2.5)
building('making',-5.65,-.1,3.2,3.4,1.85)
building('lab',5.05,3.25,3.25,2.8,2.1)
building('backyard',5.4,-3.55,3.0,2.25,1.75)

def desk(x,y,region):
    box('Desk top',(x,y,.98),(1.65,.72,.12),'wood',region)
    for dx in [-.65,.65]:
        for dy in [-.25,.25]:
            box('Desk leg',(x+dx,y+dy,.57),(.09,.09,.78),'wood',region)

desk(0,3.6,'library')
for x in [-1.75,1.75]:
    for h in [.55,1.1,1.65,2.2]:
        box('Bookshelf',(x,5.15,h),(1.05,.38,.08),'wood','library')
        for j in range(6):
            box('Book',(x-.40+j*.15,5.13,h+.22),(.10,.29,.34),['book','gold','paper'][j%3],'library')
box('Open book',(0,3.5,1.08),(.65,.42,.05),'paper','library')
desk(-5.65,-1,'making')
for i in range(4):
    box('Workshop tool',(-6.2+i*.36,-1,1.1),(.22,.16,.12),'gold','making')
cylinder('Workshop wheel',(-5.5,.7,1.2),.55,.15,'wood','making',16).rotation_euler[0]=math.pi/2
for i in range(5):
    box('Timber stock',(-6.7,.35+i*.16,.55),(1.1,.11,.11),'wood','making')
desk(5,2.45,'lab')
box('Terminal frame',(5,2.65,1.48),(1.05,.12,.66),'wood','lab')
box('Terminal screen',(5,2.575,1.48),(.92,.015,.54),'screen','lab')
for i in range(3):
    box('Terminal trace',(4.75+i*.19,2.56,1.45+i*.07),(.1,.018,.025),'paper','lab')
for i in range(5):
    for j in range(5):
        box('Search board',(5.05+(i-2)*.26,1.25+(j-2)*.26,.24),(.24,.24,.1),'paper' if (i+j)%2 else 'roof','lab')
desk(5.4,-3.8,'backyard')
for x in [4.95,5.8]:
    cylinder('Tea cup',(x,-3.8,1.09),.08,.10,'paper','backyard')

# Pond, bridge and graph-like beds in the back-left garden.
blob((-5.1,5.2,.10),(2.45,1.72,.12),'water','garden')
for i in range(15):
    a=i*math.tau/15
    blob((-5.1+2.45*math.cos(a),5.2+1.75*math.sin(a),.18),(.33,.25,.23),'stone','garden')
for i in range(9):
    y=3.7+i*.27; z=.35+.35*math.sin(i*math.pi/8)
    box('Bridge plank',(-4.55,y,z),(1.05,.24,.10),'wood','garden')
for x in [-5.08,-4.02]:
    for i in range(5):
        y=3.7+i*.54; z=.4+.35*math.sin(i*math.pi/4)
        beam((x,y,z),(x,y,z+.48),.035,'wood','garden')
        if i<4:
            z2=.4+.35*math.sin((i+1)*math.pi/4)
            beam((x,y,z+.48),(x,y+.54,z2+.48),.035,'gold','garden')

def tree(x,y,s=1,willow=False):
    if PIXEL:
        detail.tree(x,y,s,willow)
        return
    beam((x,y,.1),(x+.15,y,2.35*s),.12*s,'wood')
    for i in range(7):
        a=i*math.tau/7
        tip=(x+math.cos(a)*s,y+math.sin(a)*s,2.5*s+random.uniform(-.1,.3))
        beam((x,y,1.75*s),tip,.045*s,'wood')
        blob(tip,(.85*s,.72*s,.57*s),'leaf' if willow else 'leaf2')
        if willow:
            for j in range(3):
                tx=tip[0]+(j-1)*.28*s; ty=tip[1]
                beam((tx,ty,tip[2]),(tx+.18*s,ty-.12*s,tip[2]-1.25*s),.035*s,'leaf')

tree(-5.8,-4.8,1.15,True)
tree(-6.6,6.25,.85,True)
tree(7.0,.05,.8)
tree(2.2,6.9,.72)
for i in range(24):
    x=random.uniform(-7.6,7.6); y=random.choice([random.uniform(6.5,7.2),random.uniform(-6.5,-5.8)])
    blob((x,y,.2),(.30,.32,.25),'leaf2')

# Central well and meeting stone.
for i in range(12):
    a=i*math.tau/12
    ob=box('Well stone',(-1.3+.63*math.cos(a),-1.6+.63*math.sin(a),.40),(.32,.28,.58),'stone','home')
    ob.rotation_euler[2]=a
cylinder('Well water',(-1.3,-1.6,.17),.51,.02,'water','home',24)
for x in [-2.08,-.52]:
    beam((x,-1.6,.4),(x,-1.6,1.5),.065,'wood','home')
beam((-2.15,-1.6,1.5),(-.45,-1.6,1.5),.08,'wood','home')
beam((-1.3,-1.6,1.5),(-1.3,-1.6,.5),.015,'gold','home')
cylinder('Courtyard table',(1.5,-1.6,.62),.7,.16,'stone','home',16)
cylinder('Table base',(1.5,-1.6,.32),.22,.55,'stone','home')
for dx,dy in [(-1,0),(1,0),(0,1),(0,-1)]:
    cylinder('Stone seat',(1.5+dx,-1.6+dy,.26),.24,.4,'stone','home')

lamps=[]
for x,y in [(-1.85,-6.9),(1.85,-6.9),(-3,2.7),(3,2.7),(-4,-2.2),(4,-4.5),(-3.2,5.8)]:
    cylinder('Lantern foot',(x,y,.16),.21,.3,'stone')
    beam((x,y,.2),(x,y,1.3),.045,'wood')
    box('Lantern glow',(x,y,1.4),(.26,.26,.36),'lamp')
    box('Lantern cap',(x,y,1.63),(.4,.4,.09),'roof')
    for dx in [-.15,.15]:
        for dy in [-.15,.15]:
            beam((x+dx,y+dy,1.2),(x+dx,y+dy,1.6),.018,'wood')
    lamps.append((x,y,1.45))

if PIXEL:
    detail.landscape()

# Turn the side rooms toward the central courtyard, as in the reference map.
for region,cx,cy,angle,tx,ty in [('making',-5.65,-.1,math.pi/2,-5.65,.4),
                                ('lab',5.05,3.25,-math.pi/2,5.7,.5)]:
    c,s=math.cos(angle),math.sin(angle)
    for ob in list(parents[region].children):
        dx,dy=ob.location.x-cx,ob.location.y-cy
        # Roof meshes have world-space vertices and origin zero; moving the
        # object around the same pivot transforms both meshes and primitives.
        ob.location.x=tx+c*dx-s*dy
        ob.location.y=ty+s*dx+c*dy
        ob.rotation_euler=(Matrix.Rotation(angle,3,'Z') @ ob.rotation_euler.to_matrix()).to_euler()

# Merge by navigation owner and material: preserves six semantic roots while
# reducing hundreds of construction pieces to a few dozen draw calls.
groups={}
for obj in list(scene.objects):
    if obj.type=='MESH':
        key=(obj.parent.name if obj.parent else 'landscape',obj.data.materials[0].name)
        groups.setdefault(key,[]).append(obj)
for (owner,material),objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:
        bpy.ops.object.join()
    bpy.context.object.name=owner+' / '+material

bpy.ops.object.camera_add(location=(2,-32,28))
camera=bpy.context.object
camera.name='Camera · courtyard overview'
camera.rotation_euler=(Vector((0,0,.5))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=25.5
scene.camera=camera

def area(name,loc,energy,color,size):
    data=bpy.data.lights.new(name,'AREA'); data.energy=energy; data.color=color; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc
    ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob
key=area('Sunlight',(-8,-10,16),2600,(1,.83,.60),9)
fill=area('Sky',(8,5,12),1600,(.65,.83,1),12)
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.60,.66,.49,1)
bg.inputs['Strength'].default_value=.5
scene.render.film_transparent=True

# Export geometry only. Background/camera/lights belong to the viewer.
bpy.ops.object.select_all(action='DESELECT')
for obj in scene.objects:
    if obj.type in {'MESH','EMPTY'}: obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(WEB/(PREFIX+'.glb')),export_format='GLB',use_selection=True,export_extras=True,
                          export_draco_mesh_compression_enable=PIXEL)
bpy.context.view_layer.update()
for r in regions:
    p=world_to_camera_view(scene,camera,Vector(r['anchor']))
    r['poster']={'x':round(p.x*100,3),'y':round((1-p.y)*100,3)}
metrics={'objects':len([o for o in scene.objects if o.type=='MESH']),
         'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in scene.objects if o.type=='MESH'),
         'glbBytes':(WEB/(PREFIX+'.glb')).stat().st_size}
effects=[]
if PIXEL:
    for kind,points in [('lantern',lamps),('ripple',[(-6.25,4.9,.23),(-5.8,5.7,.23)])]:
        for point in points:
            p=world_to_camera_view(scene,camera,Vector(point))
            effects.append({'kind':kind,'x':round(p.x*100,3),'y':round((1-p.y)*100,3)})
(WEB/DATA_NAME).write_text(json.dumps({'regions':regions,'metrics':metrics,'effects':effects},ensure_ascii=False,indent=2),encoding='utf-8')
print('ESTATE_METRICS',metrics,flush=True)
scene.render.filepath=str(WEB/(PREFIX+'-day.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(PREFIX+'-day.blend')))
bpy.ops.render.render(write_still=True)

scene.name='Estate_Night'
key.data.energy=850; key.data.color=(.48,.68,1)
fill.data.energy=650; fill.data.color=(.24,.62,.55)
bg.inputs['Color'].default_value=(.045,.09,.085,1)
bg.inputs['Strength'].default_value=.25
M['lamp'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=4
M['screen'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=2
for i,loc in enumerate(lamps+[(0,4,1.7),(-5.6,-.5,1.6),(5.4,-3.4,1.6)]):
    data=bpy.data.lights.new('Warm lantern '+str(i),'POINT'); data.energy=28; data.color=(1,.50,.14); data.shadow_soft_size=.5
    ob=bpy.data.objects.new(data.name,data); scene.collection.objects.link(ob); ob.location=loc
scene.render.filepath=str(WEB/(PREFIX+'-night.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(PREFIX+'-night.blend')))
bpy.ops.render.render(write_still=True)
print('ESTATE_DONE',flush=True)
