"""Validate saved CAD and print meshes, including the motor-seat datum."""
from pathlib import Path
import json
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from cadgen import read_step
from cadgen import build123d as bd

ROOT = Path(__file__).resolve().parents[1]
results = {}
for name, expected in [("pendulum_pedestal_55mm",[46,46,64]),("motor_fit_test",[46,46,12])]:
    cad = read_step(ROOT/"STEP"/(name+".step"))
    assert cad.is_valid and len(cad.solids()) == 1
    mesh = trimesh.load(ROOT/"STL"/(name+".stl"), force="mesh")
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert np.allclose(mesh.extents,expected,atol=.02), mesh.extents
    edges = mesh.face_adjacency
    graph = coo_matrix((np.ones(len(edges)), (edges[:,0],edges[:,1])), shape=(len(mesh.faces),len(mesh.faces)))
    count = connected_components(graph,directed=False,return_labels=False)
    assert count == 1, count
    results[name] = {"bounds_mm":mesh.bounds.tolist(),"watertight":True,"consistent_normals":True,"connected_bodies":int(count),"volume_mm3":round(mesh.volume,2),"triangles":len(mesh.faces)}

pedestal = read_step(ROOT/"STEP/pendulum_pedestal_55mm.step")
# A flat motor support face exists at z=55; the clips rise to z=64.
seat_faces = [f for f in pedestal.faces() if abs(f.center().Z-55)<1e-5 and abs(f.normal_at().Z-1)<1e-5]
assert sum(f.area for f in seat_faces)>900
# Nominal 42 mm NEMA17 body with >=3.5 mm chamfered corners clears the socket.
h=21; k=h-3.5
profile=bd.Polygon((-k,-h),(k,-h),(h,-k),(h,k),(k,h),(-k,h),(-h,k),(-h,-k),align=None)
motor=bd.Pos(0,0,55.001)*bd.extrude(profile,amount=23)
intersection=pedestal.intersect(motor)
assert intersection is None or intersection.volume<1e-5
# Verify actual socket flats in the saved STEP, not just source constants.
flats=[f for f in pedestal.faces() if f.geom_type==bd.GeomType.PLANE and 55.1<f.center().Z<63.5 and abs(abs(f.center().X)-21.1)<1e-5 and abs(f.normal_at().X)>.99]
assert len(flats)>=4, len(flats)
results["interface"]={"motor_underside_z_mm":55,"grip_top_z_mm":64,"socket_parallel_flats_mm":42.2,"nominal_motor_mm":42,"nominal_side_clearance_mm":.1,"corner_chamfer_mm":3.5,"seat_upward_face_area_mm2":round(sum(f.area for f in seat_faces),2),"motor_interference_mm3":round(intersection.volume if intersection else 0,8),"physical_fit_test":"required; printer tolerance and motor variation unmeasured"}
out=ROOT/"review/verification.json"
out.write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results,indent=2))
