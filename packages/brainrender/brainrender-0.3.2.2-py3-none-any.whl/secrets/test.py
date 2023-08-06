import os

import sys
sys.path.append('./')

from BrainRender.scene import Scene, LoadedScene
from BrainRender.settings import *
from BrainRender.variables import *
from BrainRender.ABA_analyzer import ABA
from BrainRender.videomaker import VideoMaker
# from BrainRender.animation import Animator
from BrainRender.settings import update_folders
from BrainRender.colors import get_n_shades_of

from vtkplotter import *

# aba = ABA()

scene = Scene()

neuron_files = ['neurons_in_MOp_axons_in_VAL.json', 'neurons_in_MOs_axons_in_VAL.json', 'neurons_in_VAL.json', 'neurons_in_VM.json']
hemispheres = ['left', 'left', 'right', 'right']
for nf, hemi in zip(neuron_files, hemispheres):
    scene.add_neurons(os.path.join(folders_paths['neurons_fld'], nf), 
            color_neurites=False, dendrites_color="red", force_to_hemisphere=hemi,  color_by_region=True, 
            soma_color="darkred", )

# scene.edit_neurons(mirror=True, copy=True)


# vm = VideoMaker(scene = scene)
# vm.make_video(videoname="spinning_neurons_3.mp4", duration=15, nsteps=500, azimuth=0.5)

scene.render(interactive=True)
