import brainrender
brainrender.SHADER_STYLE = 'cartoon'

from brainrender.scene import Scene

import pandas as pd

cells = pd.read_hdf('secrets/CC_134_1_ch1_cells.h5', key='hdf')


color = 'salmon'

show = 'schematic'

# ------------------------------ INJECTION SCENE ----------------------------- #
if show == 'inj':
    scene = Scene(add_root=False)
    inj = scene.add_from_file('secrets/CC_134_1_ch1inj.obj')
    inj.color(color)
    inj.lighting(
            style='plastic',
            specular=0,
            enabled=False)

    scene.add_brain_regions(['SCm'], use_original_color=True, wireframe=True)


# ------------------------- INJECTION SCHEMATIC SCENE ------------------------ #
if show == 'schematic':
    if brainrender.SHADER_STYLE != 'cartoon':
        raise ValueError('Set cartoon style at imports')
    scene = Scene()
    scene.add_brain_regions(['SCm'], use_original_color=True, alpha=1)



# -------------------------------- CELLS SCENE ------------------------------- #
if show == 'cells':
    scene = Scene()

    scene.add_brain_regions(['MOs', 'MOp'], use_original_color=True, alpha=1)

    scene.actors['root'].lighting(style='plastic', enabled=False)
    scene.actors['regions']['MOs'].lighting(style='plastic', 
        enabled=False
    )
    scene.actors['regions']['MOp'].lighting(style='plastic', 
        enabled=False
    )


scene.render()
