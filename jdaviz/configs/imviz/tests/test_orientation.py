import pytest
from astropy.table import Table
from numpy.testing import assert_allclose

from glue.core.roi import EllipticalROI

from jdaviz.configs.imviz.tests.utils import BaseImviz_WCS_WCS


class TestDefaultOrientation(BaseImviz_WCS_WCS):
    def test_affine_reset_and_linktype(self):
        lc_plugin = self.imviz.plugins['Orientation']

        lc_plugin.link_type = 'WCS'
        lc_plugin.wcs_use_affine = False
        assert self.imviz.get_link_type("Default orientation", "has_wcs_2[SCI,1]") == "wcs"

        # wcs_use_affine should revert/default to True when change back to Pixels.
        lc_plugin.link_type = 'Pixels'
        assert lc_plugin.wcs_use_affine is True
        assert self.imviz.get_link_type("has_wcs_1[SCI,1]", "has_wcs_2[SCI,1]") == "pixels"

        assert self.imviz.get_link_type("has_wcs_1[SCI,1]", "has_wcs_1[SCI,1]") == "self"

        with pytest.raises(ValueError, match=".*combo not found"):
            self.imviz.get_link_type("has_wcs_1[SCI,1]", "foo")

    def test_astrowidgets_markers_disable_relinking(self):
        lc_plugin = self.imviz.plugins['Orientation']
        lc_plugin.link_type = 'Pixels'

        # Adding markers should disable changing linking from both UI and API.
        assert lc_plugin._obj.need_clear_astrowidget_markers is False
        tbl = Table({'x': (0, 0), 'y': (0, 1)})
        self.viewer.add_markers(tbl, marker_name='xy_markers')

        assert lc_plugin._obj.need_clear_astrowidget_markers is True
        with pytest.raises(ValueError, match="cannot change linking"):
            lc_plugin.link_type = 'WCS'
        assert lc_plugin.link_type == 'Pixels'

        lc_plugin._obj.vue_reset_astrowidget_markers()

        assert lc_plugin._obj.need_clear_astrowidget_markers is False
        lc_plugin.link_type = 'WCS'

    def test_markers_plugin_recompute_positions_pixels_to_wcs(self):
        lc_plugin = self.imviz.plugins['Orientation']
        lc_plugin.link_type = 'Pixels'

        # Blink to second image, if we have to.
        if self.viewer.top_visible_data_label != "has_wcs_2[SCI,1]":
            self.viewer.blink_once()

        label_mouseover = self.imviz.app.session.application._tools['g-coords-info']
        mp = self.imviz.plugins['Markers']

        with mp.as_active():
            # (1, 0) on second image but same sky coordinates as (0, 0) on first.
            label_mouseover._viewer_mouse_event(
                self.viewer, {'event': 'mousemove', 'domain': {'x': 1, 'y': 0}})
            mp._obj._on_viewer_key_event(self.viewer, {'event': 'keydown', 'key': 'm'})

            # (0, 0) on first image.
            self.viewer.blink_once()
            label_mouseover._viewer_mouse_event(
                self.viewer, {'event': 'mousemove', 'domain': {'x': 0, 'y': 0}})
            mp._obj._on_viewer_key_event(self.viewer, {'event': 'keydown', 'key': 'm'})

            lc_plugin.link_type = 'WCS'

            # Both marks stay the same in sky, so this means X and Y w.r.t. reference
            # same on both entries.
            # FIXME: 0.25 offset introduced by fake WCS layer (remove AssertionError).
            #        https://jira.stsci.edu/browse/JDAT-4256
            with pytest.raises(AssertionError):
                assert_allclose(mp._obj.marks["imviz-0"].x, 0)
            with pytest.raises(AssertionError):
                assert_allclose(mp._obj.marks["imviz-0"].y, 0)

            mp.clear_table()

    def test_markers_plugin_recompute_positions_wcs_to_pixels(self):
        lc_plugin = self.imviz.plugins['Orientation']
        lc_plugin.link_type = 'WCS'

        # Blink to second image, if we have to.
        if self.viewer.top_visible_data_label != "has_wcs_2[SCI,1]":
            self.viewer.blink_once()

        label_mouseover = self.imviz.app.session.application._tools['g-coords-info']
        mp = self.imviz.plugins['Markers']

        with mp.as_active():
            # (0, 0) on second image, but linked by WCS.
            label_mouseover._viewer_mouse_event(
                self.viewer, {'event': 'mousemove', 'domain': {'x': 0, 'y': 0}})
            mp._obj._on_viewer_key_event(self.viewer, {'event': 'keydown', 'key': 'm'})

            # (0, 0) on first image.
            self.viewer.blink_once()
            label_mouseover._viewer_mouse_event(
                self.viewer, {'event': 'mousemove', 'domain': {'x': 0, 'y': 0}})
            mp._obj._on_viewer_key_event(self.viewer, {'event': 'keydown', 'key': 'm'})

            lc_plugin.link_type = 'Pixels'

            # Both marks now get separated, so this means X and Y w.r.t. reference
            # are different on both entries.
            # FIXME: 0.25 offset introduced by fake WCS layer (remove AssertionError).
            #        https://jira.stsci.edu/browse/JDAT-4256
            with pytest.raises(AssertionError):
                assert_allclose(mp._obj.marks["imviz-0"].x, [1, 0])
            with pytest.raises(AssertionError):
                assert_allclose(mp._obj.marks["imviz-0"].y, 0)

            mp.clear_table()


class TestNonDefaultOrientation(BaseImviz_WCS_WCS):
    def test_N_up_multi_viewer(self):
        lc_plugin = self.imviz.plugins['Orientation']
        lc_plugin.link_type = 'WCS'

        # Should automatically be applied as reference to first viewer.
        lc_plugin._obj.create_north_up_east_left(set_on_create=True)

        # This would set a different reference to second viewer.
        viewer_2 = self.imviz.create_image_viewer()
        self.imviz.app.add_data_to_viewer("imviz-1", "has_wcs_1[SCI,1]")
        lc_plugin.viewer = "imviz-1"
        lc_plugin._obj.create_north_up_east_right(set_on_create=True)

        assert self.viewer.state.reference_data.label == "North-up, East-left"
        assert viewer_2.state.reference_data.label == "North-up, East-right"

        # Both viewers should revert back to same reference when pixel-linked.
        lc_plugin.link_type = 'Pixels'
        assert self.viewer.state.reference_data.label == "has_wcs_1[SCI,1]"
        assert viewer_2.state.reference_data.label == "has_wcs_1[SCI,1]"

        # FIXME: spacetelescope/jdaviz#2724 (remove AssertionError)
        lc_plugin.link_type = 'WCS'
        with pytest.raises(AssertionError):
            assert self.viewer.state.reference_data.label == "Default orientation"
        with pytest.raises(AssertionError):
            assert viewer_2.state.reference_data.label == "Default orientation"

    def test_custom_orientation(self):
        lc_plugin = self.imviz.plugins['Orientation']
        lc_plugin.link_type = 'WCS'
        lc_plugin.viewer = "imviz-0"
        lc_plugin.rotation_angle = 42  # Triggers auto-label
        lc_plugin._obj.add_orientation(rotation_angle=None, east_left=True, label=None,
                                       set_on_create=True, wrt_data=None)
        assert self.viewer.state.reference_data.label == "CCW 42.00 deg (E-left)"

    def test_delete_orientation_with_subset(self):
        lc_plugin = self.imviz.plugins['Orientation']
        lc_plugin.link_type = 'WCS'

        # Should automatically be applied as reference to first viewer.
        lc_plugin._obj.create_north_up_east_left(set_on_create=True)

        # Create rotated ellipse
        self.imviz.app.get_viewer("imviz-0").apply_roi(EllipticalROI(3, 5, 1.2, 0.6, 0.5))

        # Switch to N-up E-right
        lc_plugin._obj.create_north_up_east_right(set_on_create=True)

        self.imviz.app.vue_data_item_remove({"item_name": "North-up, East-left"})

        # Check that E-right still linked to default
        assert len(self.imviz.app.data_collection.external_links) == 3
        assert self.imviz.app.data_collection.external_links[2].data1.label == "North-up, East-right"  # noqa
        assert self.imviz.app.data_collection.external_links[2].data2.label == "Default orientation"

        # Check that the subset got reparented and the angle is correct
        subset_group = self.imviz.app.data_collection.subset_groups[0]
        nuer_data = self.imviz.app.data_collection['North-up, East-right']
        assert subset_group.subset_state.xatt in nuer_data.components
        assert_allclose(subset_group.subset_state.roi.theta, 2.641593, rtol=1e-5)
