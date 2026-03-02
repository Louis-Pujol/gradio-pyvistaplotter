# app.py
from __future__ import annotations

import gradio as gr
import pyvista as pv

from gradio_pyvistaplotter import PyvistaPlotter


pl = pv.Plotter()
pl.add_mesh(pv.Sphere())

def plot_file(file):
    pl = pv.Plotter()
    pl.add_mesh(pv.read(file))
    return pl

with gr.Blocks() as demo:

    with gr.Row():
        with gr.Column():
            file = gr.File()
            button = gr.Button('Show')

        viewer = PyvistaPlotter(value=pl)
    
    button.click(
        fn=plot_file,
        inputs=file,
        outputs=viewer,
    )

demo.launch(
    allowed_paths=viewer.allowed_paths, # Important to have access to scene and viewer files 
    show_error=True,
)