# plotter_html.py
from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import quote
from uuid import uuid4

import gradio as gr
import pyvista as pv

pv.OFF_SCREEN = True  # keep your existing headless setup


class PyvistaPlotter(gr.HTML):
    """
    A gr.HTML component that accepts a pyvista.Plotter (as the component value)
    and renders it via a static HTML viewer + exported .vtksz payload.
    """

    def __init__(
        self,
        value: Any | Callable | None = None,
        *,
        height_px: int = 700,
        **kwargs: Any,
    ):
        self.height_px = int(height_px)

        # Create / manage a temp dir for assets

        if os.getenv("GRADIO_TEMP_DIR") is not None:
            self.tmp_dir = Path(os.getenv("GRADIO_TEMP_DIR"))
        else:
            self._tmp_dir_obj = tempfile.TemporaryDirectory(
                prefix="gradio_pyvista_"
            )
            atexit.register(
                self._tmp_dir_obj.cleanup
            )  # Clean the tmp dir at program exit
            self.tmp_dir = Path(self._tmp_dir_obj.name)

        allowed = os.getenv("GRADIO_ALLOWED_PATHS", "")
        if str(self.tmp_dir.resolve()) not in allowed:
            os.environ["GRADIO_ALLOWED_PATHS"] = str(
                self.tmp_dir.resolve()
            ) + ("," + allowed if allowed else "")

        # Copy the static viewer HTML into tmp dir
        viewer_html = Path(__file__).parent / "static" / "static_viewer.html"
        self.viewer_path = self.tmp_dir / viewer_html.name
        if viewer_html.resolve() != self.viewer_path.resolve():
            shutil.copy(viewer_html, self.viewer_path)

        super().__init__(value=value, **kwargs)

    def _build_iframe(self, vtksz_path: Path) -> str:

        viewer_abs = self.viewer_path.resolve()
        data_abs = vtksz_path.resolve()

        viewer_url = f"/gradio_api/file={quote(str(viewer_abs))}"
        data_url = f"/gradio_api/file={quote(str(data_abs))}"

        iframe_src = f"{viewer_url}?fileURL={data_url}"

        return f"""
        <iframe
            src="{iframe_src}"
            width="100%"
            height="{self.height_px}px"
            style="border:0;"
        ></iframe>
        """

    def postprocess(self, value: Any) -> str | None:
        """
        Accepts a pyvista.Plotter and returns the HTML iframe string.
        """
        if value is None:
            return None

        if not isinstance(value, pv.Plotter):
            msg = (
                f"PyvistaPlotter expects a pyvista.Plotter, got {type(value)!r}. "
                "Return a pv.Plotter from your fn when using this as an output."
            )
            raise TypeError(msg)

        # Export into a unique file to avoid collisions across sessions/
        # if we reuse the same name, the plotter is not updated when a new plotter is passed
        unique_id = str(uuid4())
        vtksz_path = self.tmp_dir / f"scene_{unique_id}.vtksz"
        value.export_vtksz(vtksz_path)
        value.close()

        return self._build_iframe(vtksz_path)

    @property
    def allowed_paths(self) -> list[str]:
        """
        Convenience: pass this to demo.launch(allowed_paths=viewer.allowed_paths).
        """
        return [str(self.tmp_dir)]
