# gradio-pyvistaplotter: Interactive 3D viewer for gradio applications 

A [Gradio](https://www.gradio.app/) custom component that embeds an interactive [PyVista](https://pyvista.org/) plotter in any Gradio app.

## Installation

```bash
pip install gradio-pyvistaplotter
```

## Quick Start

The following minimal example renders an interactive 3D sphere:

```python
import pyvista as pv
import gradio as gr
from gradio_pyvistaplotter import PyvistaPlotter

plotter = pv.Plotter()
plotter.add_mesh(pv.Sphere(), show_edges=True, color="gold")

with gr.Blocks() as demo:
    gr.Markdown("Gradio app with a PyVista plotter")
    viewer = PyvistaPlotter(value=plotter)

demo.launch()
```

A more complete example with a mesh loader is available in `gradio_pyvistaplotter/demo/app.py`.

## Known Issues

### (Linux only) Ctrl+C does not stop the application

When using `PyvistaPlotter` with the standard `gr.Blocks.launch()` method from `gradio`, the application cannot be interrupted from the terminal via `Ctrl+C`. As a workaround, this package provides a custom `launch()` function that wraps `gr.Blocks.launch()` with proper signal handling:

```python
import pyvista as pv
import gradio as gr
from gradio_pyvistaplotter import PyvistaPlotter, launch

plotter = pv.Plotter()
plotter.add_mesh(pv.Sphere(), show_edges=True, color="gold")

with gr.Blocks() as demo:
    gr.Markdown("Gradio app with a PyVista plotter")
    viewer = PyvistaPlotter(value=plotter)

launch(demo)  # custom launch with proper signal handling
```

## Issues / TODO

- [ ] Currently, two files are written to the tmp directory on each render: `static_viewer.html` and `scene_<id>.vtksz`. Investigate whether the HTML can be generated and passed as an in-memory string instead of a file on disk.
- [ ] `static_viewer.html` is currently bundled with this package — should it be imported directly from `trame` instead?
