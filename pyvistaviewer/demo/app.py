import os
import time
import pyvista as pv
import gradio as gr
from pathlib import Path
from urllib.parse import quote

# ---- Force headless rendering ----
os.environ["PYOPENGL_PLATFORM"] = "osmesa"
os.environ["VTK_DEFAULT_RENDER_WINDOW_OFFSCREEN"] = "1"
os.environ["PYVISTA_OFF_SCREEN"] = "true"

pv.OFF_SCREEN = True

HERE = Path(__file__).parent.resolve()
STATIC_DIR = HERE / "static"
STATIC_DIR.mkdir(exist_ok=True)

VIEWER_HTML = STATIC_DIR / "static_viewer.html"
VTKSZ_FILE = STATIC_DIR / "scene.vtksz"


# ---- Core export function ----
def export_scene(user_code: str | None = None):
    pl = pv.Plotter()

    # Provide plotter in execution namespace
    local_ns = {"pv": pv, "pl": pl}

    if user_code and user_code.strip():
        try:
            exec(user_code, {}, local_ns)
        except Exception as e:
            return f"<pre style='color:red;'>Error:\n{e}</pre>"

    else:
        pl.add_mesh(pv.Sphere())
        pl.add_axes()

    pl.export_vtksz(VTKSZ_FILE)

    # ---- Cache busting ----
    timestamp = int(time.time() * 1000)

    viewer_abs = VIEWER_HTML.resolve()
    data_abs = VTKSZ_FILE.resolve()

    viewer_url = f"/gradio_api/file={quote(str(viewer_abs))}"
    data_url = f"/gradio_api/file={quote(str(data_abs))}?t={timestamp}"

    iframe_src = f"{viewer_url}?fileURL={data_url}"

    return f"""
    <iframe
        src="{iframe_src}"
        width="100%"
        height="700px"
        style="border:0;"
    ></iframe>
    """


# ---- Initial export ----
initial_iframe = export_scene(None)


with gr.Blocks() as demo:

    with gr.Row():
        with gr.Column(scale=1):
            code = gr.Code(
                value="pl.add_mesh(pv.Sphere())",
                language="python"
            )
            plot_button = gr.Button("Plot!")

        viewer = gr.HTML(initial_iframe, scale=2)

    plot_button.click(
        fn=export_scene,
        inputs=code,
        outputs=viewer,
    )


demo.launch(
    allowed_paths=[str(STATIC_DIR)],
    show_error=True
)
