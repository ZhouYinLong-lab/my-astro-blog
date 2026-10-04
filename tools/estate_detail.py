"""Mesh-native detail pass for the fixed-camera pixel courtyard.

Adds real geometry; no image processing or downloaded textures. All random
choices use a private seed so day/night and repeat builds remain aligned.
"""
import bpy
import math
import random
from mathutils import Vector


class EstateDetail:
    def __init__(self, materials, parents):
        self.m=materials
        self.parents=parents
        self.r=random.Random(315)
        self.batches={}
        colors={
            'tile0':(.085,.095,.073),'tile1':(.105,.118,.092),'tile2':(.13,.14,.108),
            'slab0':(.36,.37,.28),'slab1':(.46,.45,.33),'slab2':(.55,.53,.40),
            'moss':(.16,.23,.065),'leaflight':(.36,.45,.12),'leafdark':(.09,.19,.05),
            'brick':(.27,.28,.22),'terracotta':(.40,.23,.11),'woodlight':(.37,.23,.10),
        }
        for name,color in colors.items():
            mat=bpy.data.materials.new(name)
            mat.diffuse_color=(*color,1)
            mat.use_nodes=True
            p=mat.node_tree.nodes.get('Principled BSDF')
            p.inputs['Base Color'].default_value=(*color,1)
            p.inputs['Roughness'].default_value=.95
            self.m[name]=mat

    def mesh(self,vertices,faces,mat,region=None):
        key=(mat,region)
        v,f=self.batches.setdefault(key,([],[]))
        offset=len(v)
        v.extend(vertices)
        f.extend(tuple(offset+i for i in face) for face in faces)

    def cube(self,center,size,mat,region=None):
        x,y,z=center;w,d,h=(i/2 for i in size)
        v=[(x+a*w,y+b*d,z+c*h) for a,b,c in
           [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        self.mesh(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,region)

    def twig(self,a,b,width,mat='wood',region=None):
        a,b=Vector(a),Vector(b)
        direction=(b-a).normalized()
        ref=Vector((0,0,1)) if abs(direction.z)<.95 else Vector((1,0,0))
        u=direction.cross(ref).normalized()*width
        v=direction.cross(u).normalized()*width
        verts=[tuple(p+u*math.cos(i*math.tau/5)+v*math.sin(i*math.tau/5)) for p in (a,b) for i in range(5)]
        faces=[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)]
        self.mesh(verts,faces,mat,region)

    def roof_tiles(self,x,y,w,d,z,profile,region):
        def height(dy):
            for (a,ha),(b,hb) in zip(profile,profile[1:]):
                if a<=dy<=b:return ha+(hb-ha)*(dy-a)/(b-a)
            return profile[-1][1]
        cols=math.ceil(w/.18)
        rows=math.ceil(d/.21)
        for i in range(cols):
            xx=x-w/2+(i+.5)*w/cols
            for j in range(rows):
                ya=-d/2+j*d/rows
                yb=min(d/2,ya+d/rows+.045)
                vertices=[]
                for yy in [ya,yb]:
                    for k in range(5):
                        t=k/4
                        vertices.append((xx+(t-.5)*w/cols,y+yy,height(yy)+.025+.045*math.sin(t*math.pi)))
                self.mesh(vertices,[(k,k+1,k+6,k+5) for k in range(4)],'tile'+str(self.r.randrange(3)),region)
        for side in [-1,1]:
            for (ya,ha),(yb,hb) in zip(profile,profile[1:]):
                self.twig((x+side*w/2,y+ya,ha+.03),(x+side*w/2,y+yb,hb+.03),.045,'tile2',region)
        self.flush(region)

    def facade(self,x,y,w,d,h,region):
        front=y-d/2
        # Brick plinth, timber sill, lintels, window surrounds and porch posts.
        for row in range(2):
            for i in range(math.ceil(w/.33)):
                xx=x-w/2+(i+.5)*.33
                if xx>x+w/2-.10:continue
                self.cube((xx,front-.012,.14+row*.13),(.30,.23,.115),'brick',region)
        self.cube((x,front-.12,h+.26),(w+.08,.20,.15),'wood',region)
        for dx in [-w/2+.11,-w*.19,w*.19,w/2-.11]:
            if abs(dx)<.6:continue
            self.cube((x+dx,front-.115,h/2+.4),(.065,.095,h),'wood',region)
        # Small plaque over the entrance, intentionally no rasterized text.
        self.cube((x,front-.14,h+.10),(min(w*.32,1.35),.08,.20),'wood',region)
        self.cube((x,front-.19,h+.10),(min(w*.27,1.20),.025,.105),'gold',region)
        for dx in [-w*.32,w*.32]:
            self.cube((x+dx,front-.16,.87),(w*.22,.13,.12),'wood',region)
        # Irregular weathered plaster patches at the masonry base only.
        for i in range(45):
            xx=x+self.r.uniform(-w/2+.1,w/2-.1)
            if abs(xx-x)<.65:continue
            zz=self.r.uniform(.43,.78)
            self.cube((xx,front-.106,zz),(self.r.uniform(.04,.17),.014,self.r.uniform(.03,.10)),self.r.choice(['moss','slab1','brick']),region)
        self.flush(region)

    def courtyard(self):
        # Individual staggered, slightly uneven slabs replace the huge square grid.
        for row in range(18):
            yy=-6.05+row*.5
            for col in range(12):
                xx=-4.12+col*.72+(.35 if row%2 else 0)
                if xx>4.35:continue
                self.cube((xx,yy,.145+self.r.uniform(-.008,.008)),(.68,.455,.055),'slab'+str(self.r.randrange(3)),'home')
                if self.r.random()<.24:
                    self.cube((xx+self.r.uniform(-.25,.25),yy-.23,.18),(.16,.045,.01),'moss','home')
        self.flush('home')

    def tree(self,x,y,s,willow):
        self.twig((x,y,.1),(x+.16*s,y,2.35*s),.12*s)
        for i in range(10):
            a=i*math.tau/10
            tip=(x+math.cos(a)*1.12*s,y+math.sin(a)*1.12*s,(2.4+self.r.random()*.35)*s)
            self.twig((x+.12*s,y,1.7*s),tip,.045*s)
            for j in range(14 if willow else 9):
                bx=tip[0]+self.r.uniform(-.5,.5)*s
                by=tip[1]+self.r.uniform(-.45,.45)*s
                bz=tip[2]+self.r.uniform(-.12,.28)*s
                # Layer small angular clusters around branch ends to give the
                # hanging foliage a crown, without returning to spherical trees.
                for q in range(4):
                    lx=bx+self.r.uniform(-.18,.18)*s
                    ly=by+self.r.uniform(-.18,.18)*s
                    lz=bz+self.r.uniform(-.05,.12)*s
                    self.mesh([(lx-.18*s,ly,lz),(lx,ly-.16*s,lz+.09*s),
                               (lx+.20*s,ly,lz),(lx,ly+.18*s,lz-.04*s)],[(0,1,2,3)],self.r.choice(['leaf','leaflight','leafdark']))
                # Many small leaf clusters, with long overlapping drooping sprays.
                length=self.r.uniform(.85,1.8)*s if willow else .4*s
                end=(bx+.15*s,by-.08*s,max(.25,bz-length))
                self.twig((bx,by,bz),end,.012*s,'leafdark')
                for k in range(9 if willow else 4):
                    t=k/(9 if willow else 4)
                    cx=bx+.15*s*t;cy=by-.08*s*t;cz=bz-length*t
                    angle=a+k*.8
                    dx=math.cos(angle)*.14*s;dy=math.sin(angle)*.14*s
                    self.mesh([(cx-dx,cy-dy,cz+.07*s),(cx+dy*.4,cy-dx*.4,cz),
                               (cx+dx,cy+dy,cz-.13*s),(cx-dy*.4,cy+dx*.4,cz)],[(0,1,2,3)],self.r.choice(['leaf','leaflight','leafdark']))
        self.flush(None)

    def landscape(self):
        # Exposed wall bases use a few courses of irregular stonework.
        for row in range(3):
            for i in range(40):
                xx=-7.7+i*.39
                if abs(xx)<1.8:continue
                self.cube((xx,-7.025,.15+row*.16),(.36,.035,.14),'slab'+str(self.r.randrange(3)))
        # Bamboo along the northern edge, avoiding the buildings.
        for i in range(45):
            x=self.r.uniform(-7.4,7.4);y=self.r.uniform(6.6,7.2)
            ht=self.r.uniform(1.1,2.9)
            self.twig((x,y,.1),(x+.08,y,ht),.025,'leafdark')
            for j in range(3,int(ht/.25)):
                z=j*.25
                self.cube((x+.08*z/ht,y,z),(.065,.065,.04),'leaflight')
                if j%2:continue
                for side in [-1,1]:
                    self.twig((x,y,z),(x+side*.3,y-.08,z+.20),.018,'leaf')
                    self.mesh([(x,y,z+.12),(x+side*.45,y-.08,z+.26),(x+side*.22,y-.04,z+.10)],[(0,1,2)],'leaflight')
        # Ground cover: bounded to garden margins so paths and doors stay clear.
        for i in range(650):
            x=self.r.uniform(-7.75,7.75);y=self.r.uniform(-6.5,7.2)
            if not (abs(x)>7.0 or y>6.4 or (x<-4.5 and y<-3)):continue
            z=.10;w=self.r.uniform(.025,.06);h=self.r.uniform(.05,.19)
            self.mesh([(x-w,y,z),(x,y,z+h),(x+w,y,z)],[(0,1,2)],self.r.choice(['leaf','moss','leaflight']))
        # Pond highlights and lily pads.
        for i in range(30):
            x=self.r.uniform(-6.8,-3.4);y=self.r.uniform(4.4,6.1)
            if -5.12<x<-3.95:continue
            self.cube((x,y,.22),(self.r.uniform(.1,.32),.018,.012),'leaflight' if i%4==0 else 'water','garden')
        for x,y in [(-6,5),(-5.9,5.7),(-3.65,5.3)]:
            self.cube((x,y,.24),(.20,.15,.018),'leaf','garden')
        # Tea tray and open books on the outdoor stone table.
        self.cube((1.5,-1.6,.74),(.62,.42,.06),'wood','home')
        for x in [1.30,1.65]:
            self.cube((x,-1.6,.81),(.10,.10,.10),'paper','home')
        # Clay planters at front-facing entrances, stacked logs and a notice board.
        for x,y in [(-2.45,2.85),(2.45,2.85),(4.1,-4.65),(6.7,-4.65)]:
            for level in range(3):
                self.cube((x,y,.18+level*.12),(.25+level*.04,.25+level*.04,.11),'terracotta')
            for j in range(9):
                a=j*math.tau/9
                self.twig((x,y,.5),(x+math.cos(a)*.2,y+math.sin(a)*.2,.75+self.r.random()*.2),.025,'leaf')
        for i in range(5):
            self.twig((-6.9,-2.5+i*.16,.3),(-6.0,-2.5+i*.16,.3),.07,'woodlight')
        self.cube((-2.5,-6.3,.65),(.09,.09,1.25),'wood')
        self.cube((-2.5,-6.3,1.17),(.65,.10,.50),'wood')
        self.cube((-2.5,-6.37,1.17),(.48,.025,.34),'paper')
        self.flush_all()

    def flush(self,region):
        for key in list(self.batches):
            if key[1]!=region:continue
            vertices,faces=self.batches.pop(key)
            if not faces:continue
            mesh=bpy.data.meshes.new('Detail '+key[0])
            mesh.from_pydata(vertices,[],faces)
            mesh.update()
            obj=bpy.data.objects.new('Detail '+key[0],mesh)
            bpy.context.scene.collection.objects.link(obj)
            mesh.materials.append(self.m[key[0]])
            if region:obj.parent=self.parents[region]

    def flush_all(self):
        for region in {k[1] for k in self.batches}:self.flush(region)
