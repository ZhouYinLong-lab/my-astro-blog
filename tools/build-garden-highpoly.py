"""Editable high-detail reconstruction of the approved eight-place garden.

Blender 4.5: blender -b --python tools/build-garden-highpoly.py
Use -- --draft for a quick render, --no-render to build only.
All geometry and procedural materials are authored here; no AI depth extrusion.
"""
import bpy
import bmesh
import math
import random
import json
import sys
import time
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/estate-highpoly'
OUT.mkdir(parents=True, exist_ok=True)
R = random.Random(9182026)
DRAFT = '--draft' in sys.argv
START = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'Hanliu_Garden_Highpoly'
scene.unit_settings.system = 'METRIC'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32 if DRAFT else 96
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.cycles.transparent_max_bounces = 8
scene.render.resolution_x = 1500 if DRAFT else 2400
scene.render.resolution_y = 1125 if DRAFT else 1800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
scene.render.film_transparent = False
scene.render.threads_mode = 'FIXED'
scene.render.threads = 12
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == 'OPTIX'
    scene.cycles.device = 'GPU'
except Exception:
    scene.cycles.device = 'CPU'

def log(message):
    print(f'GARDEN [{time.time()-START:.1f}s] {message}', flush=True)

M = {}
def material(name, color, rough=.7, noise=0, scale=7, wood=False, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    bs = nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metallic
    if noise:
        coord = nodes.new('ShaderNodeTexCoord')
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = scale
        tex.inputs['Detail'].default_value = 3
        if wood:
            mapping = nodes.new('ShaderNodeVectorMath')
            mapping.operation = 'MULTIPLY'
            mapping.inputs[1].default_value = (5, 5, .2)
            links.new(coord.outputs['Object'], mapping.inputs[0])
            links.new(mapping.outputs[0], tex.inputs['Vector'])
        else:
            links.new(coord.outputs['Object'], tex.inputs['Vector'])
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (*(c*(1-noise) for c in color), 1)
        ramp.color_ramp.elements[1].color = (*(min(1,c*(1+noise)) for c in color), 1)
        links.new(tex.outputs['Fac'], ramp.inputs[0])
        links.new(ramp.outputs[0], bs.inputs['Base Color'])
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .16
        bump.inputs['Distance'].default_value = .045 if not wood else .012
        links.new(tex.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs[0], bs.inputs['Normal'])
    M[name] = m
    return m

material('Plaster', (.84,.80,.68), noise=.10, scale=14)
material('Earth', (.36,.32,.20), noise=.38, scale=1.4)
material('Moss', (.21,.29,.105), noise=.28, scale=4)
material('Wood', (.145,.064,.027), noise=.35, scale=8, wood=True)
material('WoodLight', (.31,.16,.065), noise=.23, scale=9, wood=True)
material('Stone', (.48,.48,.40), noise=.18, scale=18)
material('StoneLight', (.65,.64,.53), noise=.13, scale=16)
material('Mortar', (.30,.32,.28), noise=.15)
material('Brass', (.54,.32,.09), rough=.28, metallic=.65)
material('Paper', (.80,.73,.53), noise=.08)
material('Ink', (.035,.038,.027))
material('Ceramic', (.18,.33,.29), rough=.23)
for i,c in enumerate([(.055,.07,.072),(.068,.083,.081),(.084,.092,.087),(.095,.105,.10)]):
    material('Tile'+str(i), c, rough=.58, noise=.16, scale=24)
for i,c in enumerate([(.22,.35,.09),(.32,.42,.13),(.39,.48,.17),(.13,.26,.085),(.22,.32,.14),(.42,.44,.19)]):
    m = material('Leaf'+str(i),c, rough=.58)
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Subsurface Weight'].default_value = .055
for name,c in [('Pink',(.76,.31,.39)),('PalePink',(.91,.64,.63)),('White',(.89,.86,.73)),('Purple',(.36,.23,.47)),('Yellow',(.81,.55,.14)),('Burgundy',(.29,.065,.06)),('BirdWhite',(.87,.88,.79)),('BirdGrey',(.25,.31,.31)),('DuckBrown',(.29,.17,.08)),('DuckGreen',(.045,.18,.10)),('Orange',(.61,.29,.045))]:
    material(name,c,rough=.55)
water = material('Water',(.075,.27,.22),rough=.18)
wp = water.node_tree.nodes.get('Principled BSDF')
wp.inputs['Transmission Weight'].default_value = .35
wp.inputs['IOR'].default_value = 1.333
tex = water.node_tree.nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value = 8
water_coords=water.node_tree.nodes.new('ShaderNodeTexCoord')
water.node_tree.links.new(water_coords.outputs['Object'],tex.inputs['Vector'])
bump = water.node_tree.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .13
bump.inputs['Distance'].default_value = .035
water.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
water.node_tree.links.new(bump.outputs[0],wp.inputs['Normal'])
material('PondBed',(.07,.16,.12),noise=.3)
material('Backdrop',(.78,.74,.64),rough=1)
lamp = material('Lantern',(.98,.63,.24),rough=.5)
lp = lamp.node_tree.nodes.get('Principled BSDF')
lp.inputs['Emission Color'].default_value = (1,.54,.18,1)
lp.inputs['Emission Strength'].default_value = .65

REGIONS = [
    ('home','首页','/',(-10,-11,1.7)),
    ('blog','博客','/blog/',(1,8,3)),
    ('chores','别苑杂务','/chores/',(-13,-5,1.8)),
    ('making','造物录','/chores/making/',(-13,0,2.5)),
    ('garden','语义花园','/chores/garden/',(-11,8,1)),
    ('about','居士自序','/about/',(12.5,8,2.8)),
    ('friends','友链','/friend/',(-13,-12,1.3)),
    ('backyard','会客间','/backyard/',(11,-4,2.5)),
]
parents={}
collections={}
for rid,label,href,anchor in REGIONS:
    col = bpy.data.collections.new(label+' | '+rid)
    scene.collection.children.link(col)
    ob = bpy.data.objects.new('nav_'+rid,None)
    col.objects.link(ob)
    ob['label'],ob['href'],ob['anchor']=label,href,anchor
    parents[rid]=ob
    collections[rid]=col
for rid in ['site','bridge','planting','birds','lighting']:
    col=bpy.data.collections.new(rid.title())
    scene.collection.children.link(col)
    collections[rid]=col

class Geometry:
    def __init__(self):
        self.batches={}
        self.region='site'
        self.transform=Matrix.Identity(4)
    def context(self,region,x=0,y=0,yaw=0):
        self.region=region
        self.transform=Matrix.Translation((x,y,0)) @ Matrix.Rotation(yaw,4,'Z')
    def add(self,verts,faces,mat,smooth=False):
        key=(self.region,mat,smooth)
        vs,fs=self.batches.setdefault(key,([],[]))
        off=len(vs)
        vs.extend(tuple(self.transform @ Vector(v)) for v in verts)
        fs.extend(tuple(off+i for i in f) for f in faces)
    def flush(self):
        for (region,mat,smooth),(vs,fs) in self.batches.items():
            mesh=bpy.data.meshes.new(region+'_'+mat)
            mesh.from_pydata(vs,[],fs)
            mesh.materials.append(M[mat])
            mesh.update()
            if smooth:
                mesh.polygons.foreach_set('use_smooth',[True]*len(mesh.polygons))
            ob=bpy.data.objects.new(region+' · '+mat,mesh)
            collections[region].objects.link(ob)
            if region in parents: ob.parent=parents[region]
        self.batches.clear()

G=Geometry()

# Reusable genuinely bevelled solid box, not a smooth-shaded block.
bm=bmesh.new()
bmesh.ops.create_cube(bm,size=1)
bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.035,segments=2,affect='EDGES')
bm.verts.ensure_lookup_table()
BV=[tuple(v.co) for v in bm.verts]
BF=[tuple(v.index for v in f.verts) for f in bm.faces]
bm.free()

def box(loc,size,mat='Stone',angle=0,bevel=True):
    x,y,z=loc; w,d,h=size
    verts=BV if bevel else [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
    faces=BF if bevel else [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    co,si=math.cos(angle),math.sin(angle)
    G.add([(x+a*w*co-b*d*si,y+a*w*si+b*d*co,z+c*h) for a,b,c in verts],faces,mat)

def tube(points,radii,mat='Wood',sides=12):
    if isinstance(radii,(float,int)): radii=[radii]*len(points)
    pts=[Vector(p) for p in points];vs=[]
    for j,(p,r) in enumerate(zip(pts,radii)):
        axis=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
        ref=Vector((0,0,1)) if abs(axis.z)<.95 else Vector((1,0,0))
        u=axis.cross(ref).normalized();v=axis.cross(u).normalized()
        vs.extend(tuple(p+r*(u*math.cos(k*math.tau/sides)+v*math.sin(k*math.tau/sides))) for k in range(sides))
    fs=[(j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k) for j in range(len(pts)-1) for k in range(sides)]
    fs += [tuple(range(sides-1,-1,-1)),tuple((len(pts)-1)*sides+k for k in range(sides))]
    G.add(vs,fs,mat,True)

def beam(a,b,r=.045,mat='Wood',sides=12): tube([a,b],r,mat,sides)

def ellipsoid(loc,size,mat,segments=18,rings=10):
    x,y,z=loc;sx,sy,sz=size
    vs=[]
    for j in range(rings+1):
        phi=math.pi*j/rings
        for i in range(segments):
            theta=math.tau*i/segments
            vs.append((x+sx*math.sin(phi)*math.cos(theta),y+sy*math.sin(phi)*math.sin(theta),z+sz*math.cos(phi)))
    fs=[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(rings) for i in range(segments)]
    G.add(vs,fs,mat,True)

def stone(loc,size,seed=None):
    # Smooth irregular rock with a dense watertight spherical topology.
    x,y,z=loc;sx,sy,sz=size;segments=20;rings=12
    phase=R.random()*6
    vs=[]
    for j in range(rings+1):
        p=math.pi*j/rings
        for i in range(segments):
            t=math.tau*i/segments
            n=1+.10*math.sin(3*t+phase)*math.sin(4*p)+.06*math.sin(7*t-2*p)
            vs.append((x+sx*n*math.sin(p)*math.cos(t),y+sy*n*math.sin(p)*math.sin(t),z+sz*n*math.cos(p)))
    fs=[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(rings) for i in range(segments)]
    G.add(vs,fs,R.choice(['Stone','StoneLight','Mortar']),True)

def leaf(center,length,width,angle,mat='Leaf1',droop=.12):
    # Folded lanceolate blade: real geometry, visible from either side.
    c=Vector(center);u=Vector((math.cos(angle),math.sin(angle),-droop)).normalized()
    v=Vector((-math.sin(angle),math.cos(angle),0))
    vs=[]
    for j in range(5):
        t=j/4
        base=c+u*length*t+Vector((0,0,-length*droop*t*t))
        w=width*math.sin(math.pi*t)
        vs += [tuple(base-v*w),tuple(base+Vector((0,0,w*.25))),tuple(base+v*w)]
    fs=[]
    for j in range(4):
        fs.extend([(j*3,j*3+1,j*3+4,j*3+3),(j*3+1,j*3+2,j*3+5,j*3+4)])
    G.add(vs,fs,mat,True)

def plaque(text,loc,width,region,angle=0):
    box(loc,(width,.11,.45),'Wood')
    box((loc[0],loc[1]-.065,loc[2]),(width-.09,.025,.35),'Paper')
    font=bpy.data.curves.new('Inscription '+text,'FONT')
    font.body=text;font.align_x='CENTER';font.align_y='CENTER';font.size=.27
    font.extrude=.003;font.bevel_depth=.001
    font.font=bpy.data.fonts.load('C:/Windows/Fonts/simkai.ttf',check_existing=True)
    ob=bpy.data.objects.new(text,font);collections[region].objects.link(ob)
    ob.matrix_world=G.transform @ Matrix.Translation((loc[0],loc[1]-.087,loc[2])) @ Matrix.Rotation(math.pi/2,4,'X')
    ob.data.materials.append(M['Ink'])
    if region in parents:ob.parent=parents[region]

def roof(w,d,z,rise=1.55):
    # Curved roof field, individually modelled overlapping half-cylinder tiles.
    half=d/2
    def height(x,y):
        t=min(1,abs(y)/half)
        return z+rise*(1-t)**1.55+.18*t**7+.17*(abs(x)/(w/2))**10*t**5
    cols=math.ceil(w/.20);rows=math.ceil(half/.27)
    for side in [-1,1]:
        # Solid continuous underside, trimmed fascia, and visible rafters.
        for i in range(cols):
            x=-w/2+(i+.5)*w/cols
            points=[(x,side*half*t/16,height(x,side*half*t/16)-.13) for t in range(17)]
            if i%2==0:tube(points,.055,'Wood',8)
            for j in range(rows):
                y0=side*j*half/rows;y1=side*min(half+.055,(j+1)*half/rows+.055)
                vs=[]
                for q in range(4):
                    y=y0+(y1-y0)*q/3
                    for k in range(9):
                        t=k/8
                        xx=x+(t-.5)*w/cols
                        vs.append((xx,y,height(xx,y)+.055*math.sin(t*math.pi)))
                fs=[(q*9+k,q*9+k+1,(q+1)*9+k+1,(q+1)*9+k) for q in range(3) for k in range(8)]
                G.add(vs,fs,'Tile'+str(R.choices([0,1,2,3],[3,5,2,1])[0]),True)
        tube([(-w/2+i*w/64,side*half,height(-w/2+i*w/64,side*half)-.06) for i in range(65)],.10,'Tile1',12)
    tube([(-w/2-.1+i*(w+.2)/48,0,z+rise+.12+.18*(abs(-1+2*i/48)**10)) for i in range(49)],.115,'Tile1',16)
    # Verge tiles on both gables follow the same section without intersecting roofs.
    for x in [-w/2,w/2]:
        tube([(x,-half+2*half*i/40,height(x,-half+2*half*i/40)+.055) for i in range(41)],.065,'Tile2',12)

def window(x,y,z,w=1.05,h=1.25):
    box((x,y+.05,z),(w,.05,h),'Paper')
    for dx in [-w/2,w/2]:box((x+dx,y-.03,z),(.075,.12,h+.15),'WoodLight')
    for dz in [-h/2,h/2]:box((x,y-.03,z+dz),(w+.12,.12,.075),'WoodLight')
    for i in range(1,8):box((x-w/2+i*w/8,y-.06,z),(.025,.05,h),'Wood')
    for j in range(1,7):box((x,y-.06,z-h/2+j*h/7),(w,.05,.025),'Wood')

def furniture_table(x,y,z,w=1.4,d=.8):
    box((x,y,z+.76),(w,d,.11),'WoodLight')
    for a in [-1,1]:
        for b in [-1,1]:box((x+a*(w/2-.09),y+b*(d/2-.09),z+.36),(.09,.09,.72),'Wood')
    box((x,y,z+.63),(w-.08,d-.08,.13),'Wood')

def books(x,y,z,count=14):
    for i in range(count):
        h=R.uniform(.22,.38);w=R.uniform(.055,.095)
        box((x+i*.09,y,z+h/2),(w,.22,h),R.choice(['Paper','WoodLight','Burgundy','Ceramic']))

def building(rid,x,y,w,d,h=3.0,yaw=0,cottage=False):
    G.context(rid,x,y,yaw)
    base=.65; front=-d/2
    box((0,0,.39),(w+.65,d+.8,.48),'Stone')
    box((0,0,.65),(w+.55,d+.72,.10),'StoneLight')
    box((0,d/2,base+h/2),(w,.20,h),'Plaster')
    for sx in [-1,1]:
        box((sx*w/2,0,base+h/2),(.20,d,h),'Plaster')
        # Triangular gable filling the true roof profile.
        G.add([(sx*w/2,-d/2,base+h),(sx*w/2,d/2,base+h),(sx*w/2,0,base+h+1.45)],[(0,1,2)],'Plaster')
    doorx=-w*.23 if cottage else 0
    holes=[(doorx-.59,doorx+.59,base,base+2.24)]
    centers=[w*.22] if cottage else [-w*.32,w*.32]
    wh=.84 if cottage else 1.32;ww=.8 if cottage else 1.45
    for cx in centers:holes.append((cx-ww/2,cx+ww/2,1.5,1.5+wh))
    xs=sorted(set([-w/2,w/2]+[v for hole in holes for v in hole[:2]]))
    zs=sorted(set([base,base+h]+[v for hole in holes for v in hole[2:]]))
    for a,b in zip(xs,xs[1:]):
        for c,e in zip(zs,zs[1:]):
            if not any(l<(a+b)/2<r and lo<(c+e)/2<hi for l,r,lo,hi in holes):
                box(((a+b)/2,front,(c+e)/2),(b-a,.20,e-c),'Plaster' if cottage else 'Wood')
    for cx in centers:window(cx,front-.11,1.5+wh/2,ww,wh)
    for cx in [-w/2+.05,w/2-.05,doorx-.66,doorx+.66]:
        beam((cx,front-.18,.66),(cx,front-.18,base+h),.075,'Wood',20)
        box((cx,front-.18,.72),(.24,.24,.20),'StoneLight')
    box((0,front-.16,base+h-.05),(w+.15,.20,.20),'WoodLight')
    if cottage:
        box((doorx,front-.10,1.73),(1.12,.12,2.15),'WoodLight')
        for q in range(8):box((doorx-.5+q*.14,front-.18,1.73),(.018,.015,2.1),'Wood')
        ellipsoid((doorx+.33,front-.22,1.6),(.035,.025,.045),'Brass')
    else:
        for side in [-1,1]:
            box((doorx+side*.56,front+.30,1.7),(.15,.75,2.1),'WoodLight',angle=side*.18)
            box((doorx+side*.56,front+.29,2.18),(.17,.5,.8),'Paper',angle=side*.18)
    for i in range(3):
        box((doorx,front-.4-i*.31,.58-i*.12),(1.7,.36,.16),'StoneLight')
    roof(w+1.05,d+1.3,base+h+.10,rise=1.5 if not cottage else 1.0)
    label=next(row[1] for row in REGIONS if row[0]==rid)
    plaque(label,(doorx,front-.23,base+h-.36),1.7 if len(label)>2 else 1.1,rid)
    if rid=='blog':
        # Shelf bays and individual volumes, visible through the open middle bay.
        for xx in [-2.5,-.9,.9,2.5]:
            box((xx,d/2-.3,1.9),(1.45,.38,2.5),'Wood')
            for zz in [1,1.5,2,2.5,3]:
                box((xx,d/2-.62,zz),(1.42,.58,.07),'WoodLight')
                books(xx-.62,d/2-.65,zz+.05,13)
        furniture_table(0,0,.68,2.2,.9)
        box((0,-.05,1.50),(.65,.4,.025),'Paper')
        for xx in [-w*.43,w*.43]:
            beam((xx,front-.7,.68),(xx,front-.7,base+h),.10,'Wood',20)
    if rid=='making':
        furniture_table(0,-.1,.68,2.7,1.0)
        for i in range(8):
            beam((-1+i*.28,0,1.52),(-1+i*.28,.20,1.57),.023,'WoodLight')
            box((-1+i*.28,.22,1.58),(.18,.08,.045),'Ink')
        box((-w*.30,front-.7,.73),(.5,.5,.14),'WoodLight')
        for zz in [1.2,1.7,2.2]:
            beam((-w*.32,front+.15,zz),(-w*.32+.40,front+.15,zz),.025,'Brass')
    G.flush()

log('Materials and mesh generators ready')

OUTLINE=[(-18,-11),(12,-11),(18,-5),(17,12),(-17,12),(-19,3)]
def pond(t,extra=0):
    r=1+.055*math.sin(3*t+.3)+.035*math.cos(5*t)
    return (1+(10.0*r+extra)*math.cos(t),-1+(6.8*r+extra)*math.sin(t))

def boundary(t):
    origin=Vector((1,-1));ray=Vector((math.cos(t),math.sin(t)))
    for a,b in zip(OUTLINE,OUTLINE[1:]+OUTLINE[:1]):
        a,b=Vector(a),Vector(b);edge=b-a
        cross=lambda u,v:u.x*v.y-u.y*v.x
        den=cross(ray,edge)
        if abs(den)<1e-8:continue
        distance=cross(a-origin,edge)/den;u=cross(a-origin,ray)/den
        if distance>0 and 0<=u<=1:return tuple(origin+ray*distance)
    raise ValueError('Boundary ray missing')

G.context('site')
count=192
inner=[(*pond(i*math.tau/count),.28) for i in range(count)]
outer=[(*boundary(i*math.tau/count),.35) for i in range(count)]
G.add(inner+outer,[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)],'Earth')
G.add(outer+[(x,y,-.5) for x,y,z in outer],[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)],'Stone')
G.add([(1,-1,-.12)]+[(x,y,-.12) for x,y,z in inner],[(0,i+1,(i+1)%count+1) for i in range(count)],'PondBed')
G.add([(1,-1,.10)]+[(x,y,.10) for x,y,z in inner],[(0,i+1,(i+1)%count+1) for i in range(count)],'Water')
# A connected left-bank promontory supports the willow's roots above water.
bank=[(-9,4.7),(-8,2.8),(-6.1,2.7),(-4.9,3),(-4.6,3.8),(-5.3,4.5),(-7,5.7)]
G.add([(x,y,.39) for x,y in bank],[tuple(range(len(bank)))],'Moss')
for a,b in zip(bank[1:5],bank[2:6]):
    for i in range(4):
        x=a[0]+(b[0]-a[0])*(i+.5)/4;y=a[1]+(b[1]-a[1])*(i+.5)/4
        stone((x,y,.20),(.33,.30,.32))
box((0,0,-.65),(200,200,.20),'Backdrop',bevel=False)

def path(points,width=1.2):
    for a,b in zip(points,points[1:]):
        a,b=Vector(a),Vector(b);length=(b-a).length
        angle=math.atan2((b-a).y,(b-a).x)
        n=max(1,math.ceil(length/.45));side=Vector((-math.sin(angle),math.cos(angle)))
        for i in range(n):
            mid=a+(b-a)*(i+.5)/n
            for k in [-1,1]:
                pos=mid+side*k*width/4
                box((pos.x,pos.y,.405),(length/n-.025,width/2-.025,.105),R.choice(['Stone','StoneLight']),angle)

ring=[pond(i*math.tau/180,1.15) for i in range(181)]
path(ring,1.1)
path([(-10,-11),(-10,-8.5),(-11,-6),(-12,-3),(-12,.2)],1.45)
path([(-12,3),(-12,4.2),(-13,6),(-13,8),(-11,9.7),(-8,9),(-7,6),(0,5.4)],1.15)
path([(-12,4.2),(-9,5),(-6,4.3)],1.15)
path([(10,5),(12.5,5),(13,7)],1.2)
for row in range(3):
    for col in range(22):
        box((-4.3+col*.49,5.3+row*.40,.43),(.46,.38,.12),'StoneLight')
for i in range(100):
    t=i*math.tau/100
    if .35<t<1.6:continue
    x,y=pond(t,.08)
    if R.random()<.74:stone((x,y,.31),(R.uniform(.25,.60),R.uniform(.25,.52),R.uniform(.23,.48)))

def wall(a,b,height=1.55):
    a,b=Vector(a),Vector(b);mid=(a+b)/2;length=(b-a).length;angle=math.atan2((b-a).y,(b-a).x)
    box((mid.x,mid.y,.35+height/2),(length,.28,height),'Plaster',angle)
    for row in range(2):
        n=math.ceil(length/.56)
        for i in range(n):
            p=a+(b-a)*(i+.5)/n
            box((p.x,p.y,.44+row*.15),(length/n-.02,.34,.13),'Stone',angle)
    n=math.ceil(length/.22)
    side=Vector((-math.sin(angle),math.cos(angle)))
    for i in range(n):
        p=a+(b-a)*(i+.5)/n
        tube([(p.x-side.x*.23,p.y-side.y*.23,height+.36),(p.x,p.y,height+.50),(p.x+side.x*.23,p.y+side.y*.23,height+.36)],.065,'Tile1',8)

wall((-18,-11),(-11.55,-11),1.3)
wall((-8.45,-11),(12,-11),1.3)
for a,b in zip(OUTLINE[1:],OUTLINE[2:]+OUTLINE[:1]):wall(a,b,1.8 if a[1]>0 else 1.3)
G.flush()
log('Ground, pond, paving and boundary walls built')

building('blog',1.0,8.0,8.0,4.8,3.15)
building('making',-13,0.4,5.0,3.5,2.6,yaw=-.12)
building('about',12.6,8.5,4.6,3.1,2.6,yaw=-.08,cottage=True)

# Light covered gallery between study and dwelling, above solid accessible paving.
G.context('about',7.6,8.0)
box((0,0,.48),(5.9,1.5,.20),'StoneLight')
for x in [-2.7,-1.35,0,1.35,2.7]:
    for y in [-.60,.60]:beam((x,y,.58),(x,y,3.05),.07,'Wood',16)
roof(6.15,1.9,3.02,.45)
for y in [-.60,.60]:beam((-2.9,y,2.65),(2.9,y,2.65),.07,'WoodLight')
G.flush()

def pavilion():
    G.context('backyard',12,-4)
    box((0,0,.47),(4.7,4.4,.52),'Stone')
    box((0,0,.76),(4.85,4.5,.13),'StoneLight')
    for x in [-1.8,1.8]:
        for y in [-1.6,1.6]:
            beam((x,y,.82),(x,y,3.6),.10,'Wood',24)
            box((x,y,.93),(.30,.30,.22),'StoneLight')
            for a in [-1,1]:
                beam((x,y,2.97),(x-a*.42,y,3.5),.055,'Wood')
    for y in [-1.6,1.6]:box((0,y,3.50),(3.8,.16,.22),'WoodLight')
    for x in [-1.8,1.8]:box((x,0,3.50),(.16,3.3,.22),'WoodLight')
    # Four swept tiled hip faces, each tapering into the small central ridge.
    for face in range(4):
        rotation=face*math.pi/2
        co,si=math.cos(rotation),math.sin(rotation)
        for row in range(15):
            t0=row/15;t1=(row+1.10)/15
            n=math.ceil(30*(1-.74*t0))
            for col in range(n):
                vs=[]
                for q in range(4):
                    t=min(1,t0+(t1-t0)*q/3)
                    half=2.62*(1-.76*t)
                    for k in range(9):
                        u=-1+2*(col+k/8)/n
                        x=u*half;y=-half
                        z=3.55+1.4*t**1.35+.26*(1-t)**7+.16*abs(u)**8*(1-t)**5+.045*math.sin(k*math.pi/8)
                        vs.append((x*co-y*si,x*si+y*co,z))
                G.add(vs,[(q*9+k,q*9+k+1,(q+1)*9+k+1,(q+1)*9+k) for q in range(3) for k in range(8)],'Tile'+str(R.randrange(3)),True)
        tube([(u*2.62*co+2.62*si,u*2.62*si-2.62*co,3.81+.16*abs(u)**8) for u in [-1+i/16 for i in range(33)]],.07,'Tile1')
    ellipsoid((0,0,5.04),(.16,.16,.24),'Tile1')
    # Close the four hip fields with a tiled crown; no open skylight at the apex.
    half=.635
    G.add([(-half,-half,4.95),(half,-half,4.95),(half,half,4.95),(-half,half,4.95),(0,0,5.24)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'Tile1')
    for x,y in [(-half,-half),(half,-half),(half,half),(-half,half)]:
        tube([(x,y,4.97),(x*.5,y*.5,5.11),(0,0,5.26)],.045,'Tile2')
    furniture_table(0,0,.84,1.55,1)
    box((0,0,1.66),(.8,.52,.055),'Wood')
    ellipsoid((-.12,0,1.83),(.13,.13,.13),'Ceramic')
    beam((-.12,0,1.91),(-.30,0,1.91),.035,'Ceramic')
    for x in [-.3,.05,.30]:ellipsoid((x,-.16,1.73),(.065,.065,.045),'White')
    for x,y in [(-1,0),(1,0),(0,-1),(0,1)]:
        box((x,y,1.16),(.45,.45,.11),'WoodLight')
        for a in [-.16,.16]:
            for b in [-.16,.16]:box((x+a,y+b,.98),(.055,.055,.30),'Wood')
    for y in [-1.6,1.6]:
        beam((-.8,y,1.2),(1.75,y,1.2),.045,'Wood')
    plaque('会客间',(0,-1.75,3.20),1.5,'backyard')
    G.flush()

pavilion()

G.context('chores',-13,-5)
box((0,0,.45),(3.6,2.0,.20),'StoneLight')
for x in [-1.6,1.6]:beam((x,.7,.55),(x,.7,2.65),.085,'Wood',18)
box((0,.75,1.60),(3.4,.15,2.1),'Plaster')
roof(3.9,2.4,2.6,.6)
furniture_table(0,-.05,.55,2.35,.75)
for x in [-.65,0,.65]:box((x,-.05,1.4),(.43,.33,.065),'Paper')
plaque('别苑杂务',(0,-.95,2.3),1.7,'chores')
G.flush()

G.context('home',-10,-11)
for x in [-1.38,1.38]:box((x,0,1.9),(.40,.58,3.1),'Plaster')
box((0,0,3.35),(3.18,.58,.34),'Plaster')
roof(3.7,1.55,3.50,.70)
for s in [-1,1]:box((s*1.13,.4,1.8),(.14,.92,2.8),'WoodLight',angle=s*.2)
for i in range(3):box((0,-.45-i*.35,.34-i*.10),(3.15,.45,.14),'StoneLight')
plaque('寒柳别苑',(0,-.36,3.15),1.85,'home')
G.flush()
G.context('friends',-13,-12)
box((0,0,1.0),(.12,.12,1.3),'Wood')
box((0,0,1.60),(.68,.44,.65),'WoodLight')
box((0,-.23,1.75),(.46,.03,.05),'Ink')
roof(.85,.70,1.95,.22)
plaque('友链',(0,-.27,1.46),.55,'friends')
G.flush()
log('Eight destination structures and interiors built')

def bridge():
    G.context('bridge')
    a=Vector((2.4,5.45));b=Vector((9.63,-3.65));direction=(b-a).normalized()
    normal=Vector((-direction.y,direction.x));length=(b-a).length;width=1.48
    def point(t,side,z):
        p=a+(b-a)*t+normal*side
        return (p.x,p.y,z)
    def deck(t):return .75+1.35*math.sin(math.pi*t)**.95
    def underside(t):return .22+1.23*math.sin(math.pi*t)**.8
    n=64
    # Visible voussoir units, arch intrados, spandrels and watertight sides.
    for i in range(n):
        t0=i/n+.0005;t1=(i+1)/n-.0005
        vs=[point(t,s,z(t)) for t in [t0,t1] for s in [-width/2,width/2] for z in [underside,deck]]
        G.add(vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(1,3,7,5),(0,4,6,2)],'StoneLight')
    for i in range(48):
        t=(i+.5)/48;pos=a+(b-a)*t
        box((pos.x,pos.y,deck(t)+.035),(length/48-.01,width+.07,.09),'StoneLight',math.atan2(direction.y,direction.x))
    for s in [-1,1]:
        for i in range(15):
            t=i/14;p=point(t,s*(width/2+.06),deck(t)+.42)
            box(p,(.13,.13,.84),'StoneLight')
            ellipsoid((p[0],p[1],p[2]+.44),(.11,.11,.09),'StoneLight')
        tube([point(i/64,s*(width/2+.06),deck(i/64)+.72) for i in range(65)],.06,'StoneLight',12)
        tube([point(i/64,s*(width/2+.06),deck(i/64)+.30) for i in range(65)],.042,'StoneLight',10)
    G.flush()
bridge()
log('Segmented masonry arch bridge complete')

def moon_gate():
    G.context('garden',-12,4.6)
    radius=1.08;cz=1.62;half=3.15;top=3.05;bottom=.34;n=96
    vs=[]
    for y in [-.16,.16]:
        for i in range(n):
            t=math.tau*i/n;dx,dz=math.cos(t),math.sin(t)
            limit=min(half/max(abs(dx),1e-8),(top-cz)/dz if dz>0 else (bottom-cz)/dz if dz<0 else 1e9)
            vs.extend([(radius*dx,y,cz+radius*dz),(limit*dx,y,cz+limit*dz)])
    fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.extend([(i*2,j*2,j*2+1,i*2+1),(2*n+i*2+1,2*n+j*2+1,2*n+j*2,2*n+i*2),(i*2,2*n+i*2,2*n+j*2,j*2)])
    G.add(vs,fs,'Plaster')
    tube([(radius*math.cos(i*math.tau/n),-.18,cz+radius*math.sin(i*math.tau/n)) for i in range(n+1)],.06,'StoneLight')
    roof(6.5,.70,top,.18)
    plaque('语义花园',(2.2,-.24,2.3),1.7,'garden')
    G.flush()
moon_gate()

def tree(x,y,height=5,spread=2,flower=None,willow=False):
    G.context('planting')
    lean=.15*height if willow else .05*height
    trunk=[(x+lean*(j/15)**1.3,y+.14*math.sin(j/15*3),.35+height*.72*j/15) for j in range(16)]
    tube(trunk,[.35*(1-j/18)**1.2*(height/6) for j in range(16)],'Wood',20)
    branches=38 if willow else 8
    for i in range(branches):
        ang=i*2.39996+R.uniform(-.2,.2)
        reach=spread*R.uniform(.60,1)
        tip=Vector((x+lean+math.cos(ang)*reach,y+math.sin(ang)*reach,height*R.uniform(.74,1)))
        base=Vector(trunk[R.randrange(7,15)])
        pts=[tuple(base.lerp(tip,j/10)+Vector((0,0,.35*math.sin(math.pi*j/10)))) for j in range(11)]
        tube(pts,[.12*(1-j/12) for j in range(11)],'Wood',12)
        if willow:
            for q in range(13):
                start=tip+Vector((R.uniform(-.7,.7),R.uniform(-.7,.7),R.uniform(-.2,.35)))
                length=R.uniform(2.1,4.5)
                curve=[]
                for j in range(15):
                    t=j/14
                    curve.append(tuple(start+Vector((math.cos(ang)*.45*t,math.sin(ang)*.45*t,-length*t*t))))
                tube(curve,[.014*(1-.7*j/14) for j in range(15)],'WoodLight',6)
                for j in range(48):
                    t=(j+.3)/48
                    c=start+Vector((math.cos(ang)*.45*t,math.sin(ang)*.45*t,-length*t*t))
                    for s in [-1,1]:leaf(c,R.uniform(.20,.34),.025,ang+s*1.2+j*.3,R.choice(['Leaf0','Leaf1','Leaf2']),.95)
        else:
            for q in range(240):
                theta=R.random()*math.tau;u=R.uniform(-1,1);r=R.random()**(1/3)
                c=tip+Vector((math.cos(theta)*math.sqrt(1-u*u)*spread*.42*r,math.sin(theta)*math.sqrt(1-u*u)*spread*.42*r,u*spread*.38*r))
                leaf(c,R.uniform(.15,.28),.06,R.random()*math.tau,R.choice(['Leaf0','Leaf3','Leaf4']),.15)
                if flower and q%3==0:
                    for pet in range(5):
                        aa=pet*math.tau/5
                        ellipsoid(c+Vector((.065*math.cos(aa),.065*math.sin(aa),0)),(.055,.042,.026),flower,8,5)
    G.flush()

tree(-5.9,3.7,8.8,3.25,willow=True)
log('Hero willow: branching trunk, hanging twigs and individual folded leaves')
for args in [(-15,8.2,4.2,2,'PalePink'),(-15.5,11,5.5,2,None),(-9.6,11,4.4,1.6,None),(-17,1.8,4.0,1.8,None),(15,-5,3.8,1.7,'Pink'),(14,11,4.3,1.4,None),(-5,-9.3,2.5,1.3,None),(8,-9.8,2.7,1.4,None)]:
    tree(*args)

def shrub(x,y,r=.6,flower=None):
    # Individual leaves on a non-spherical branching crown.
    for i in range(5):
        ang=i*2.4
        end=(x+math.cos(ang)*r*.6,y+math.sin(ang)*r*.6,.40+r*.72)
        beam((x,y,.34),end,.018,'Wood')
    for i in range(100):
        ang=R.random()*math.tau;rr=r*math.sqrt(R.random())
        p=(x+math.cos(ang)*rr,y+math.sin(ang)*rr,.38+r*.60*(1-rr/r)+R.uniform(0,.24))
        leaf(p,.20,.055,ang,R.choice(['Leaf0','Leaf3','Leaf4']),.1)
        if flower and i%7==0:
            for j in range(5):
                a=j*math.tau/5
                ellipsoid((p[0]+.047*math.cos(a),p[1]+.047*math.sin(a),p[2]+.045),(.045,.035,.025),flower,8,5)

G.context('garden')
for i in range(52):
    x=R.uniform(-16,-7.2);y=R.uniform(5.2,11)
    if (x+12)**2+(y-7.8)**2<1.7:continue
    if -13.5<x<-12 and y<8.8:continue
    shrub(x,y,R.uniform(.35,.72),R.choice(['White','PalePink','Purple',None,None]))
for i in range(18):
    x=R.uniform(-15.3,-12.5);y=R.uniform(9.0,11.1)
    stone((x,y,R.uniform(.45,1.1)),(R.uniform(.35,.7),R.uniform(.4,.7),R.uniform(.5,1.2)))
# Stone tea table and four drum stools within an actual garden clearing.
tube([(-10.5,7.4,.35),(-10.5,7.4,1.0)],.18,'Stone',24)
tube([(-10.5,7.4,1.0),(-10.5,7.4,1.13)],.65,'StoneLight',48)
for i in range(4):
    a=i*math.pi/2;x=-10.5+math.cos(a)*1.15;y=7.4+math.sin(a)*1.15
    ellipsoid((x,y,.62),(.28,.28,.32),'Stone',20,12)
G.flush()

G.context('planting')
for i in range(46):
    t=i*math.tau/46
    x,y=pond(t,2.25+R.random()*.7)
    if y>4.5 or (-14<x<-9 and -7<y<3):continue
    if 9<x<15 and -6<y<-1:continue
    if R.random()<.70:shrub(x,y,R.uniform(.35,.6),R.choice([None,None,'White','Yellow']))
for i in range(850):
    t=R.random()*math.tau;x,y=pond(t,R.uniform(.25,.65))
    if .8<t<1.65:continue
    # Sparse upright grass blades along selected stone joints and shore pockets.
    if math.sin(5*t)>.15:
        for k in range(5):leaf((x+R.uniform(-.1,.1),y+R.uniform(-.1,.1),.32),R.uniform(.16,.45),.015,R.random()*math.tau,'Leaf2',-1.2)
for cluster in [(15.3,9.0),(-16,10.5)]:
    for i in range(18):
        x=cluster[0]+R.uniform(-.7,.7);y=cluster[1]+R.uniform(-.7,.7);h=R.uniform(2.5,4.5)
        beam((x,y,.35),(x+.12,y,h),.035,'Leaf3',10)
        for j in range(5,int(h/.35)):
            z=j*.35
            tube([(x,y,z-.015),(x,y,z+.02)],.047,'Leaf1',10)
            end=(x+.55*math.sin(j),y+.55*math.cos(j),z+.25)
            beam((x,y,z),end,.012,'Leaf3',6)
            for k in range(7):leaf((end[0]+k*.045,end[1],end[2]),.32,.025,j+k*.7,'Leaf3',.1)
G.flush()
log('Garden beds, rockery, bamboo and perimeter planting complete')

G.context('site')
for cluster in [(-5,-4),(5,2),(3,-5),(7,-.5)]:
    for i in range(18):
        x=cluster[0]+R.uniform(-1.3,1.3);y=cluster[1]+R.uniform(-.9,.9);radius=R.uniform(.12,.31)
        n=32
        vs=[(x,y,.13)]+[(x+radius*math.cos(.15+j*(math.tau-.30)/(n-1)),y+radius*math.sin(.15+j*(math.tau-.30)/(n-1)),.13+.025*math.sin(j*5/n)) for j in range(n)]
        G.add(vs,[(0,j+1,j+2) for j in range(n-1)],R.choice(['Leaf0','Leaf2']),True)
        if i%9==0:
            beam((x,y,.10),(x,y,.35),.012,'Leaf3')
            for layer in range(2):
                for k in range(7):
                    a=k*math.tau/7+layer*.4
                    ellipsoid((x+.08*math.cos(a),y+.08*math.sin(a),.36+layer*.035),(.065,.065,.09),R.choice(['Pink','PalePink']),12,8)
G.flush()

def bird(x,y,kind,angle=0):
    G.context('birds',x,y,angle)
    duck=kind in ['male','female'];night=kind=='night'
    if duck:
        body='DuckBrown' if kind=='female' else 'BirdGrey'
        ellipsoid((0,0,.23),(.38,.21,.19),body,28,16)
        ellipsoid((.26,0,.46),(.13,.11,.13),'DuckGreen' if kind=='male' else 'DuckBrown',24,14)
        tube([(.14,0,.26),(.21,0,.40)],.08,body,16)
        tube([(.34,0,.46),(.52,0,.43)],[.07,.025],'Yellow' if kind=='male' else 'DuckBrown',12)
        for side in [-1,1]:
            ellipsoid((0,side*.15,.28),(.28,.08,.12),'DuckBrown',24,12)
            ellipsoid((.29,side*.094,.49),(.018,.012,.018),'Ink',12,8)
        for i in range(4):
            ellipsoid((-.27-i*.035,0,.29+i*.014),(.12,.055,.025),body,16,8)
    else:
        z=.75 if not night else .56;mat='BirdWhite' if not night else 'BirdGrey'
        ellipsoid((0,0,z),(.22,.14,.32 if not night else .22),mat,28,18)
        neck=[(.02,0,z+.18),(.13,0,z+.38),(.05,0,z+.52),(.18,0,z+.63)] if not night else [(.10,0,z+.12),(.18,0,z+.26)]
        tube(neck,[.065]*len(neck),'BirdWhite',16)
        hx,hy,hz=neck[-1]
        ellipsoid((hx,0,hz),(.10,.085,.105),'Ink' if night else 'BirdWhite',24,16)
        tube([(hx+.08,0,hz),(hx+.34,0,hz-.035)],[.033,.002],'Ink' if not night else 'Orange',12)
        for side in [-1,1]:
            ellipsoid((hx+.02,side*.078,hz+.025),(.013,.008,.014),'Orange' if night else 'Ink',12,8)
            legz=.14 if not night else .36
            tube([(-.03,side*.085,z-.2),(.015,side*.085,legz)],.015,'Ink' if not night else 'Orange',10)
            for toe in [-1,0,1]:beam((.015,side*.085,legz),(.12,side*.085+toe*.05,legz-.01),.007,'Ink',8)
            for k in range(7):ellipsoid((-.06-k*.012,side*.13,z-.05-k*.018),(.13,.04,.21),mat,18,10)
    G.flush()

bird(-7.0,-1.8,'egret',.3)
bird(8,-6.2,'night',2.4)
bird(-1.6,-3.3,'male',.2)
bird(-.5,-3.8,'female',.4)
log('Four waterbirds and lotus geometry complete')

def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name)
    ob=bpy.data.objects.new(name,data);collections['lighting'].objects.link(ob)
    ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=scale;data.lens=50;data.clip_end=500
    return ob

main_cam=camera('01 · Garden overview',(16,-44,40),(0,1.3,1.1),43)
bridge_cam=camera('02 · Stone arch and tea pavilion',(25,-23,20),(5,-.3,1.1),22)
garden_cam=camera('03 · Willow, flower garden and craftsmanship',(-27,-20,22),(-8,5,2),25)
plan_cam=camera('04 · Plan',(0,0,70),(0,0,0),41)
scene.camera=main_cam
world=bpy.data.worlds.new('Warm daylight');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.82,.91,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.65
scene.world=world
sun_data=bpy.data.lights.new('Soft afternoon sun','SUN');sun_data.energy=3.0;sun_data.angle=.14
sun_data.color=(1.0,.91,.78)
scene.view_settings.exposure=.25
sun=bpy.data.objects.new('Soft afternoon sun',sun_data);collections['lighting'].objects.link(sun)
sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-36))
area_data=bpy.data.lights.new('Large sky fill','AREA');area_data.energy=1800;area_data.shape='DISK';area_data.size=20
area=bpy.data.objects.new('Large sky fill',area_data);collections['lighting'].objects.link(area)
area.location=(0,-6,20)
for name,x,y in [('Library desk light',1,6.0),('Workshop light',-13,-.5)]:
    ld=bpy.data.lights.new(name,'AREA');ld.energy=45;ld.color=(1,.73,.43);ld.size=1.5
    lo=bpy.data.objects.new(name,ld);collections['lighting'].objects.link(lo)
    lo.location=(x,y,2.8)

# Pack the approved reference for convenient visual comparison inside Blender.
reference=bpy.data.images.load(str(ROOT/'public/world/estate-garden.webp'),check_existing=True)
reference.use_fake_user=True
reference.pack()
bpy.ops.file.pack_all()
scene['reference_image']='estate-garden.webp'
scene['asset_type']='High-detail editable geometry; not optimized for web delivery'
scene['construction']='Procedural reconstruction from approved 2D concept; dimensions are interpretive'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.clip_end=500

meshes=[o for o in scene.objects if o.type=='MESH']
stats={'vertices':sum(len(o.data.vertices) for o in meshes),'polygons':sum(len(o.data.polygons) for o in meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'mesh_objects':len(meshes),'materials':len(M),'regions':[]}
for rid,label,href,anchor in REGIONS:
    p=world_to_camera_view(scene,main_cam,Vector(anchor))
    stats['regions'].append({'id':rid,'label':label,'href':href,'anchor':anchor,'projection':[p.x,1-p.y]})
(OUT/'model-stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hanliu-garden-highpoly.blend'),compress=True)
log('Saved editable model: '+json.dumps({k:v for k,v in stats.items() if k!='regions'}))
if '--no-render' not in sys.argv:
    for cam,name in [(main_cam,'overview'),(bridge_cam,'bridge-detail'),(garden_cam,'garden-detail')]:
        if DRAFT and cam!=main_cam:continue
        scene.camera=cam
        scene.render.filepath=str(OUT/('draft.png' if DRAFT else name+'.png'))
        bpy.ops.render.render(write_still=True)
        log('Rendered '+name)
    scene.camera=main_cam
log('Complete')
