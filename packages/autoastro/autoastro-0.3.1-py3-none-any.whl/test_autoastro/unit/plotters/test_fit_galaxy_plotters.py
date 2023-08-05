import autoastro as aast
import os

import pytest


@pytest.fixture(name="galaxy_fitting_plotter_path")
def make_galaxy_fitting_plotter_setup():
    return "{}/../../../test_files/plotting/galaxy_fitting/".format(
        os.path.dirname(os.path.realpath(__file__))
    )


def test__fit_sub_plot__all_types_of_galaxy_fit(
    gal_fit_7x7_image,
    gal_fit_7x7_convergence,
    gal_fit_7x7_potential,
    gal_fit_7x7_deflections_y,
    gal_fit_7x7_deflections_x,
    positions_7x7,
    plot_patch,
    galaxy_fitting_plotter_path,
):
    aast.plot.fit_galaxy.subplot_fit_galaxy(
        fit=gal_fit_7x7_image,
        positions=positions_7x7,
        cb_tick_values=[1.0],
        cb_tick_labels=["1.0"],
        output_path=galaxy_fitting_plotter_path,
        format="png",
    )

    assert galaxy_fitting_plotter_path + "galaxy_fit.png" in plot_patch.paths

    aast.plot.fit_galaxy.subplot_fit_galaxy(
        fit=gal_fit_7x7_convergence,
        positions=positions_7x7,
        cb_tick_values=[1.0],
        cb_tick_labels=["1.0"],
        output_path=galaxy_fitting_plotter_path,
        format="png",
    )

    assert galaxy_fitting_plotter_path + "galaxy_fit.png" in plot_patch.paths

    aast.plot.fit_galaxy.subplot_fit_galaxy(
        fit=gal_fit_7x7_potential,
        positions=positions_7x7,
        cb_tick_values=[1.0],
        cb_tick_labels=["1.0"],
        output_path=galaxy_fitting_plotter_path,
        format="png",
    )

    assert galaxy_fitting_plotter_path + "galaxy_fit.png" in plot_patch.paths

    aast.plot.fit_galaxy.subplot_fit_galaxy(
        fit=gal_fit_7x7_deflections_y,
        positions=positions_7x7,
        cb_tick_values=[1.0],
        cb_tick_labels=["1.0"],
        output_path=galaxy_fitting_plotter_path,
        format="png",
    )

    assert galaxy_fitting_plotter_path + "galaxy_fit.png" in plot_patch.paths

    aast.plot.fit_galaxy.subplot_fit_galaxy(
        fit=gal_fit_7x7_deflections_x,
        positions=positions_7x7,
        cb_tick_values=[1.0],
        cb_tick_labels=["1.0"],
        output_path=galaxy_fitting_plotter_path,
        format="png",
    )

    assert galaxy_fitting_plotter_path + "galaxy_fit.png" in plot_patch.paths
