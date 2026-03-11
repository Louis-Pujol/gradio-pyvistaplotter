import pytest
import pyvista as pv


@pytest.fixture
def plotter():
    """A minimal off-screen PyVista plotter shared across tests."""
    p = pv.Plotter(off_screen=True)
    p.add_mesh(pv.Sphere())
    return p
