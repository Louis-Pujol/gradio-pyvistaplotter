# trame-gradio-component

This repository contains a `gradio` component containing a `PyVista` plotter.

## Installation

Clone the repository and run
```bash
pip install gradio_pyvistaplotter/
```

## Example

There is a minimal gradio app with an interactive plotter:

```python
import pyvista as pv
import gradio as gr

from gradio_pyvistaplotter import PyvistaPlotter

plotter = pv.Plotter()
plotter.add_mesh(pv.Sphere(), show_edges=True, color="gold")

with gr.Blocks() as demo:

    gr.Markdown("Gradio app with a PyVista plotter")
    viewer = PyvistaPlotter(value=plotter)


# Specifying allowed path is necessary
demo.launch(allowed_paths=viewer.allowed_paths)
```

An example app with a mesh loader can be found in `gradio_pyvistaplotter/demo/app.py`


## Issues/TODO

- [ ] The app does not stop with `ctrl+c` (only on linux)
- [ ] Possible to skip the file saving (`static_viewer.html` and `scene.vtksz`) in tmp dir ?
- [ ] Import `static_viewer.html` directly from `trame` ?
- [ ] Possible to update plotter once passed to `PyvistaPlotter` ?
