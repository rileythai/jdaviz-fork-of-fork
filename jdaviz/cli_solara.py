import solara

from jdaviz import Imviz, Cubeviz, Specviz, Mosviz, Specviz2d

viz_helpers = {"imviz": Imviz,
               "cubeviz": Cubeviz,
               "specviz": Specviz,
               "mosviz": Mosviz,
               "specviz2d": Specviz2D}

@solara.component
def Page(layout):
    with solara.Column():
        import ipysplitpanes
        import ipygoldenlayout
        from jdaviz.app import custom_components
        import os
        import ipyvue
        import jdaviz

        # Hack to make sure the necessary widgets are registered with vue
        ipysplitpanes.SplitPanes()
        ipygoldenlayout.GoldenLayout()
        for name, path in custom_components.items():
            ipyvue.register_component_from_file(None, name,
                                                os.path.join(os.path.dirname(jdaviz.__file__), path))

        ipyvue.register_component_from_file('g-viewer-tab', "container.vue", jdaviz.__file__)

        viz = viz_helpers[layout]
        viz.load_data(f'{data_dir}/{fn}')
        display(viz.app)