# app.py
from __future__ import annotations

import gradio as gr
import pyvista as pv
from gradio_pyvistaplotter import PyvistaPlotter, launch

DEFAULT_CODE = """from pyvista import examples
pl.add_mesh(examples.load_ant(), show_edges=True, color="mistyrose")
"""


def run_plot_code(code: str):
    pl = pv.Plotter()
    exec(code, {"pl": pl, "pv": pv})
    return pl


with gr.Blocks() as demo:
    gr.Markdown("# PyvistaComponent: interactive 3D viewer in gradio")
    with gr.Row():
        with gr.Column():
            gr.Markdown("""
        Write Python code in the editor below to build your 3D scene using [PyVista](https://docs.pyvista.org/).

        - A `pv.Plotter()` instance is automatically created and available as **`pl`**
        - The full `pyvista` library is available as **`pv`**
        """)
            code_box = gr.Code(
                value=DEFAULT_CODE,
                language="python",
                lines=5,
            )
            button = gr.Button("Plot")
            gr.Markdown("""

        **Examples:**
        ```python
        # A simple sphere
        pl.add_mesh(pv.Sphere())

        # A colored cube
        pl.add_mesh(pv.Cube(), color="royalblue")

        # Multiple objects
        pl.add_mesh(pv.Sphere(center=(0, 0, 0)), color="red")
        pl.add_mesh(pv.Cylinder(center=(2, 0, 0)), color="green")
        ```
        """)
        viewer = PyvistaPlotter(value=run_plot_code(DEFAULT_CODE))

    button.click(
        fn=run_plot_code,
        inputs=code_box,
        outputs=viewer,
    )

launch(demo, server_name="0.0.0.0")
