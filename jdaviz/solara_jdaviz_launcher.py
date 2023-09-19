import solara

from jdaviz.core.launcher import show_launcher


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

        launcher_widget = show_launcher(height='100%')
        display(launcher_widget)