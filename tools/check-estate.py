"""Read-only round-trip verification: blender -b --python tools/check-estate.py."""
import bpy
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
web = root / 'public/world/blender'
pixel='--pixel' in sys.argv
prefix='estate-pixel' if pixel else 'estate'
data = json.loads((web/('regions-pixel.json' if pixel else 'regions.json')).read_text(encoding='utf-8'))
expected = {'nav_'+r['id'] for r in data['regions']}
for name in [prefix+'-day.blend', prefix+'-night.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(root/'artifacts/estate'/name))
    assert bpy.context.scene.camera, 'Missing camera'
    assert expected.issubset(bpy.data.objects.keys()), 'Missing navigation roots'
    print('BLEND_OK', name, flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(web/(prefix+'.glb')))
assert expected.issubset(bpy.data.objects.keys()), 'GLB lost navigation roots'
for r in data['regions']:
    obj=bpy.data.objects['nav_'+r['id']]
    assert obj.get('href')==r['href'], 'GLB lost navigation extras'
    assert len(obj.children)>0, 'Empty navigation region'
    assert 0<r['poster']['x']<100 and 0<r['poster']['y']<100, 'Offscreen label'
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.data.objects if o.type=='MESH')
assert triangles==data['metrics']['triangles'], 'Geometry changed during export'
assert (web/(prefix+'.glb')).stat().st_size<3_000_000, 'Model exceeds budget'
print('GLB_ROUNDTRIP_OK', triangles, 'triangles;', len(expected), 'navigation roots', flush=True)
