"""Reopen and validate the independently saved Blender high-detail scene."""
import bpy
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parents[1]
out=root/'artifacts/estate-highpoly'
bpy.ops.wm.open_mainfile(filepath=str(out/'hanliu-garden-highpoly.blend'))
expected=json.loads((out/'model-stats.json').read_text(encoding='utf-8'))
scene=bpy.context.scene
assert scene.camera and scene.camera.type=='CAMERA'
assert len([o for o in scene.objects if o.type=='CAMERA'])==4
assert len(expected['regions'])==8
for entry in expected['regions']:
    obj=bpy.data.objects['nav_'+entry['id']]
    assert obj['href']==entry['href'] and obj['label']==entry['label']
    assert len(obj.children)>0, entry['id']
meshes=[o for o in scene.objects if o.type=='MESH']
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
assert triangles==expected['triangles'] and triangles>1_000_000
assert any(o.name.startswith('bridge') for o in meshes)
assert any(o.name.startswith('birds') for o in meshes)
assert bpy.data.images['estate-garden.webp'].packed_file
for font in bpy.data.fonts:
    if font.filepath and not font.filepath.startswith('<'):
        assert font.packed_file, font.name
for mesh in meshes:
    assert all(math.isfinite(c) for v in mesh.data.vertices for c in v.co), mesh.name
    assert not mesh.data.validate(verbose=False), mesh.name
print('PASS: reopened .blend; 8 navigation roots and destinations; 4 cameras; packed reference/font; finite and valid meshes;',triangles,'triangles.')
