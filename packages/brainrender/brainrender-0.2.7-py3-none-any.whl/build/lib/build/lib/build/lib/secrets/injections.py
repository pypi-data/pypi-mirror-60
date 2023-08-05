# from brainrender import *

import sys
sys.path.append('./')
from brainrender.scene import Scene
import pandas as pd
import os
from tqdm import tqdm
from brainrender.Utils.actors_funcs import edit_actor

sc = ['SCdg', 'SCdw', 'SCig', 'SCiw', 'SCm', 'SCop', 'SCs', 'SCsg', 'SCzo']


scene = Scene()

inj_files = ['/Users/federicoclaudi/Desktop/CC134_1_injsite.obj',
             '/Users/federicoclaudi/Desktop/CC134_2_injsite.obj']
colors=['lightgreen', 'aqua']

for fl, c in zip(inj_files, colors): 
    act = scene.add_from_file(fl, c=c, alpha=.6)
    edit_actor(act, smooth=True, line=False, line_kwargs=dict(lw=.25, c='blackboard'))
    act.flipNormals()

scene.add_brain_regions(['SCm'], use_original_color=True, wireframe=False, alpha=.4)
scene.add_brain_regions(['PAG', 'SCs'], use_original_color=True, wireframe=True, alpha=.4)

scene.render() 
