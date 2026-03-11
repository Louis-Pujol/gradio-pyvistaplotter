import gradio as gr
import pytest
from gradio_pyvistaplotter import PyvistaPlotter


def test_component_instantiation(plotter):
    """Component can be created without error."""
    component = PyvistaPlotter(value=plotter)
    assert component is not None


def test_component_instantiation_without_gradio_temp_dir(plotter, monkeypatch):
    """Component falls back gracefully when GRADIO_TEMP_DIR is not set.

    Covers the branch in __init__ where os.getenv('GRADIO_TEMP_DIR') is None
    (line 39 in plottercomponent.py).
    """
    monkeypatch.delenv("GRADIO_TEMP_DIR", raising=False)
    component = PyvistaPlotter(value=plotter)
    assert component is not None


def test_postprocess_returns_none_for_none_value(plotter):
    """postprocess() returns None when called with None (no plotter set).

    Covers the early-return branch at line 87 in plottercomponent.py.
    """
    component = PyvistaPlotter(value=plotter)
    result = component.postprocess(None)
    assert result is None


def test_postprocess_raises_for_invalid_type(plotter):
    """postprocess() raises TypeError for non-Plotter input.

    Covers the error branch at lines 90-94 in plottercomponent.py.
    """
    component = PyvistaPlotter(value=plotter)
    with pytest.raises(
        TypeError, match=r"PyvistaPlotter expects a pyvista.Plotter"
    ):
        component.postprocess("not_a_plotter")


def test_app_launches(plotter):
    """Gradio app starts and stops cleanly using the standard launch."""
    with gr.Blocks() as demo:
        PyvistaPlotter(value=plotter)

    try:
        demo.launch(prevent_thread_lock=True)
    finally:
        demo.close()
