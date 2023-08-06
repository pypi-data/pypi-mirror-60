import os

import sys
sys.path.append('./')

from BrainRender.scene import Scene, LoadedScene, DualScene, MultiScene
from BrainRender.settings import *
from BrainRender.variables import *
from BrainRender.ABA_analyzer import ABA
from BrainRender.videomaker import VideoMaker
# from BrainRender.animation import Animator
from BrainRender.settings import update_folders
from BrainRender.colors import get_n_shades_of
from BrainRender.Utils.mouselight_parser import NeuronsParser
from BrainRender.Utils.data_manipulation import *

from vtkplotter import *

# create classes
ds = DualScene()
parser = NeuronsParser(scene=ds.scenes[0])


# render neurons
neurons, regions = [], []
neuron_files = ['axons_in_GRN_a.json', 'axons_in_GRN_b.json']
for nf in neuron_files:
    n, r = parser.render_neurons( os.path.join(folders_paths['neurons_fld'], nf), render_neurites=True, 
                        color_neurites=False, force_to_hemisphere='left',  color_by_region=True,
                        neurite_radius=18)
    neurons.extend(n)
    regions.extend(r)


effe_regions = set([r['soma'] for r in regions])
ROI = [['TH', 'VM'], [ 'HY', 'ZI'], ['SSp-m5', 'MOs5', 'MOp5']]

ms = MultiScene(len(ROI)+1)
# ['MOs', 'MOp', 'MOs5', 'MOp5', 'SSp-m5']
for i, region in enumerate(ROI):
    # if not isinstance(region, list): region = [region]
    selected_neurons = parser.filter_neurons_by_region(neurons, region, neurons_regions=regions)
    ms.scenes[i+1].add_neurons(selected_neurons)
    ms.scenes[i+1].edit_neurons(mirror='soma', copy=True) 

    ms.scenes[i+1].add_brain_regions(['GRN'], colors="ivory", alpha=.5)
    # ms.scenes[i+1].add_brain_regions(region, use_original_color=True, alpha=.15)
    ms.scenes[i+1].add_brain_regions(['SCs', 'SCm', 'PAG'], colors="salmon", alpha=.15)
    ms.scenes[i+1].add_brain_regions(['CUN', 'PPN', 'MRN'], colors="orange", alpha=.15)


ms.scenes[0].add_neurons(neurons)
ms.scenes[0].edit_neurons(mirror='soma', copy=True)

ms.render()

