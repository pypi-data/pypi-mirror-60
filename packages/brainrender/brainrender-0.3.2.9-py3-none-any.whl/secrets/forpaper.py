import brainrender
brainrender.SHADER_STYLE = 'cartoon'

from brainrender.scene import Scene

from vtkplotter.analysis import surfaceIntersection
import pandas as pd

cells = pd.read_hdf('secrets/CC_134_1_ch1_cells.h5', key='hdf')


color = 'salmon'

show = 'cells'

# ------------------------------ INJECTION SCENE ----------------------------- #
if show == 'inj':
    scene = Scene(add_root=True)

    scene.add_brain_regions(['SCm'], use_original_color=True, wireframe=False)

    inj = scene.add_from_file('secrets/CC_134_1_ch1inj.obj')
    inj.color(color).alpha(.7)
    inj.lighting(
            style='plastic',
            ambient=0,
            diffuse=.1,
            specular=0,
            enabled=False)   
    scene.edit_actors(inj, smooth=True)

    inters = surfaceIntersection(scene.actors['regions']['SCm'], inj)
    scene.edit_actors(inters, smooth=True)
    scene.edit_actors(inters, line=True, line_kwargs=dict(lw=10))

    scene.add_vtkactor(inters)


# ------------------------- INJECTION SCHEMATIC SCENE ------------------------ #
if show == 'schematic':
    if brainrender.SHADER_STYLE != 'cartoon':
        raise ValueError('Set cartoon style at imports')
    scene = Scene()
    scene.add_brain_regions(['SCm'], use_original_color=True, alpha=1)



# -------------------------------- CELLS SCENE ------------------------------- #
if show == 'cells':
    scene = Scene()

    # scene.add_brain_regions(['MOs', 'MOp'], use_original_color=True, alpha=1)

    scene.add_cells(cells.loc[cells.])

scene.render()
