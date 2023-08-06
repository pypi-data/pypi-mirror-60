import numpy as np
import os
from tqdm import tqdm

import sys
sys.path.append('./')
from BrainRender.scene import Scene, LoadedScene
from BrainRender.settings import *
from BrainRender.variables import *
from BrainRender.ABA_analyzer import ABA
from BrainRender.videomaker import VideoMaker
# from BrainRender.animation import Animator
from BrainRender.settings import update_folders

from vtkplotter import *


# variables
sc_color = [228, 108, 10]
rsp_color = [0, 176, 80]
mos_color = "blue"

rsp_names = ["RSP", "RSPagl", "RSPagl1", "RSPagl2/3", "RSPagl5", "RSPagl6a", "RSPagl6b", "RSPd", "RSPd1", "RSPd2/3",
                    "RSPd4", "RSPd5", "RSPd6a", "RSPd6b", "RSPv", "RSPv1", "RSPv2/3", "RSPv5", "RSPv6a", "RSPv6b"]
main_rsp = ["RSPd", "RSPd"]

# Create scene
aba = ABA()
scene = Scene()
scene.add_brain_regions(["RSPd", "RSPv", ], colors=rsp_color, alpha=.25)
scene.add_brain_regions(["SCm", "SCs" ], colors=sc_color, alpha=.25)


# get some points in sc
npoints = 20
scm, scs = scene.actors['regions']['SCm'], scene.actors['regions']['SCs']
scm_bounds, scs_bounds = scm.bounds(), scs.bounds()
bounds = [[np.min([scm_bounds[0], scs_bounds[0]]), np.max([scm_bounds[1], scs_bounds[1]])], 
            [np.min([scm_bounds[2], scs_bounds[2]]), np.max([scm_bounds[3], scs_bounds[3]])], 
            [np.min([scm_bounds[4], scs_bounds[4]]), np.max([scm_bounds[5], scs_bounds[5]])]]

xmin = scene.get_region_CenterOfMass('root', unilateral=False)[2]

sc_points, niters = [], 0
while len(sc_points) < npoints:
    x, y, z = np.random.randint(bounds[0][0], bounds[0][1]),  np.random.randint(bounds[1][0], bounds[1][1]),  np.random.randint(xmin, bounds[2][1])
    p = [x, y, z]
    if scm.isInside(p) or scs.isInside(p):
        sc_points.append(p)
    niters += 1
    if niters> 1000:
        print("max iters")
        break

# sc_points =[[9051, 2200, 6453], [9051, 2650, 7250], [8900, 1500, 6200], [9051, 1800, 7000]]

for point in tqdm(sc_points):
    tract = aba.get_projection_tracts_to_target(p0=point)
    scene.add_tractography(tract, display_injection_structure=False, verbose=False, extract_region_from_inj_coords=rsp_names, 
                        color_by='target_region', color="ivory", VIP_regions=rsp_names, VIP_color=rsp_color, 
                        include_all_inj_regions=False, others_alpha=0, others_color="ivory")


# scene.render(interactive=False)



vm = VideoMaker(scene=scene)
vm.make_video(videoname="dario_SC2.mp4", duration=15, azimuth=3, nsteps=250)

# deep sc
# print("\ndeep sc\n")
# sc_medial = [9051, 2200, 6453] 
# sc_lateral = [9051, 2650, 7250]
# scene.add_brain_regions(["SCm"], colors=sc_color, alpha=.5)

# superficial sc
# print("superficial sc")
# sc_medial = [8900, 1500, 6200] 
# sc_lateral = [9051, 1800, 7000]
# scene.add_brain_regions(["SCs"], colors=sc_color, alpha=.5)


# print("inferior coll")
# sc_medial = [8900, 1500, 6200] 
# sc_lateral = [9051, 1800, 7000]
# scene.add_brain_regions(["ICc", "ICd", "ICe"], colors=sc_color, alpha=.5)

# # Populate scene SC
# scene.add_sphere_at_point(pos = sc_medial, color="blue", radius=150)
# scene.add_sphere_at_point(pos = sc_lateral, color="green", radius=150)


# medial_tract = aba.get_projection_tracts_to_target(p0=sc_medial)
# lateral_tract = aba.get_projection_tracts_to_target(p0=sc_lateral)

# scene.add_tractography(medial_tract, display_injection_structure=False, 
#                     color_by='target_region', color="blue", VIP_regions=rsp_names, VIP_color=rsp_color, include_all_inj_regions=True)
# scene.add_tractography(lateral_tract, display_injection_structure=False, 
#                     color_by='target_region', color="green", VIP_regions=rsp_names, VIP_color=rsp_color, include_all_inj_regions=True)
# scene.add_tractography(medial_tract, display_injection_structure=False, 
#                     color_by='target_region', color="blue", VIP_regions=['MOs'], VIP_color=mos_color)
# scene.add_tractography(lateral_tract, display_injection_structure=False, 
#                     color_by='target_region', color="green", VIP_regions=['MOs'], VIP_color=mos_color)

# ic_names = ["ICc", "ICd", "ICe"]

# print(scene.get_region_CenterOfMass("ICe"))

# ic_coords = [10351, 1500, 6400]

# for ic in ic_names:
# tract = aba.get_projection_tracts_to_target(p0=ic_coords)
# scene.add_sphere_at_point(pos = ic_coords, color="blue", radius=150)
# scene.add_tractography(tract, display_injection_structure=True, 
#                 color_by='target_region', color="blue", VIP_regions=rsp_names, VIP_color=rsp_color)


# scene.render(interactive=True)
# scene.export_scene(savename="superficial_sc")


# vm = VideoMaker(scene=scene)
# vm.make_video(videoname="deep_sc.mp4", duration=15, azimuth=3, nsteps=250)