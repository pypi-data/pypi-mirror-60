import os

from BrainRender.scene import Scene, LoadedScene
from BrainRender.settings import *
from BrainRender.variables import *
from BrainRender.ABA_analyzer import ABA
from BrainRender.videomaker import VideoMaker
# from BrainRender.animation import Animator
from BrainRender.settings import update_folders
from BrainRender.colors import colors

from vtkplotter import *
from random import choices
from BrainRender.colors import colors, getColor, get_n_shades_of

# neuron_file = os.path.join(folders_paths['neurons_fld'], 'neurons_in_M2_axons_in_PPN_CUN.JSON')


aba = ABA()
vm = VideoMaker()
# print(aba.other_sets['Summary structures of the thalamus'])
# VAL
# VM

val_neuronsf = os.path.join(folders_paths['neurons_fld'], "neurons_in_VAL.json")
vm_neuronsf = os.path.join(folders_paths['neurons_fld'], "neurons_in_VM.json")

val_neuronsf

scene = Scene()
scene.add_brain_regions(["MOp"], colors="ivory", alpha=.5, use_original_color=False)

val_colors, vm_colors = get_n_shades_of("green", n=20), get_n_shades_of("red", n=12)



# ? Neurons
scene.add_neurons(val_neuronsf, display_soma_region=True, soma_regions_kwargs={"alpha":0.5, "colors":"green"},
                            color_neurites=False, soma_color=val_colors)
scene.add_neurons(vm_neuronsf, display_soma_region=True, soma_regions_kwargs={"alpha":0.5, "colors":"red"},
                            color_neurites=False, soma_color=vm_colors)


# ? Tractography
# mop_points = [[4438, 2301, 7771], [5000, 1750, 7250], [5250, 1500, 7000], 
#                     [4000, 2800, 8000], [3800, 3000, 8250], [3600, 3500, 8250]]
# colors = ["aliceblue", 'cadetblue', 'cornflowerblue', 'dodgerblue', 'deepskyblue', 'dodgerblue']
# for p, c in zip(mop_points, colors):
#     scene.add_sphere_at_point(pos = p, color=c, radius=150)
#     tract = aba.get_projection_tracts_to_target(p0=p)
#     scene.add_tractography(tract, display_injection_structure=True, display_onlyVIP_injection_structure=True,
#                     VIP_regions=['VAL'], VIP_color="green", others_alpha=0, 
#                     color_by='target_region', color="green",)

#     scene.add_tractography(tract, display_injection_structure=True, display_onlyVIP_injection_structure=True,
#                     VIP_regions=['VM'], VIP_color="red", others_alpha=0, 
#                     color_by='target_region', color="red",)


scene.render(interactive=True)
scene.export_scene(savename="josh_neurons")
vm.add_scene(scene)
vm.make_video(videoname="forjoshneurons_2.mp4", duration=15, azimuth=3, nsteps=250)