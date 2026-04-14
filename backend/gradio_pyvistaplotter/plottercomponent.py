# plotter_html.py
from __future__ import annotations
import atexit
import base64
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

pv.OFF_SCREEN = True


class PyvistaPlotter(gr.HTML):
    """
    A gr.HTML component that renders a pyvista.Plotter as an inline iframe.

    Two modes:
    - inline (default): vtksz embedded as base64, no file serving needed.
    - file: vtksz written to tmp dir and served via /gradio_api/file=
    """

    def __init__(
        self,
        value: Any | Callable | None = None,
        *,
        height_px: int = 700,
        inline: bool = True,
        **kwargs: Any,
    ):
        self.height_px = int(height_px)
        self.inline = inline
        self.tmp_dir = None

        if not inline:
            self._setup_tmp_dir()

        super().__init__(value=value, **kwargs)

    def _setup_tmp_dir(self) -> None:
        if os.getenv("GRADIO_TEMP_DIR") is not None:
            self.tmp_dir = Path(os.getenv("GRADIO_TEMP_DIR"))
        else:
            self._tmp_dir_obj = tempfile.TemporaryDirectory(prefix="gradio_pyvista_")
            atexit.register(self._tmp_dir_obj.cleanup)
            self.tmp_dir = Path(self._tmp_dir_obj.name)

        allowed = os.getenv("GRADIO_ALLOWED_PATHS", "")
        if str(self.tmp_dir.resolve()) not in allowed:
            os.environ["GRADIO_ALLOWED_PATHS"] = (
                str(self.tmp_dir.resolve()) + ("," + allowed if allowed else "")
            )

        viewer_src = Path(__file__).parent / "static" / "static_viewer.html"
        self.viewer_path = self.tmp_dir / viewer_src.name
        if viewer_src.resolve() != self.viewer_path.resolve():
            shutil.copy(viewer_src, self.viewer_path)

    def _viewer_html(self) -> str:
        return (Path(__file__).parent / "static" / "static_viewer.html").read_text()

    def _build_iframe_inline(self, vtksz_path: Path) -> str:
        b64 = base64.b64encode(vtksz_path.read_bytes()).decode()
        html = self._viewer_html()
        html_b64 = base64.b64encode(html.encode()).decode()
        frame_id = f"pv-frame-{uuid4().hex}"

        return f"""
        <iframe
            id="{frame_id}"
            width="100%"
            height="{self.height_px}px"
            style="border:0;"
        ></iframe>
        <script>
        (function() {{
            const b64data = `{b64}`;
            const htmlB64 = `{html_b64}`;
            const html = atob(htmlB64);
            // Patch xh() result so the viewer boots with base64Str instead of fileURL
            const patched = html.replace(
                'n(50)',
                `(function() {{
                    const _xh = window.xh;
                    window.xh = function() {{ return {{ base64Str: b64data }} }};
                }})(); n(50)`
            );
            document.getElementById('{frame_id}').srcdoc = patched;
        }})();
        </script>
        """

    def _build_iframe_file(self, vtksz_path: Path) -> str:
        viewer_url = f"/gradio_api/file={quote(str(self.viewer_path.resolve()))}"
        data_url = f"/gradio_api/file={quote(str(vtksz_path.resolve()))}"
        return f"""
        <iframe
            src="{viewer_url}?fileURL={data_url}"
            width="100%"
            height="{self.height_px}px"
            style="border:0;"
        ></iframe>
        """

    def postprocess(self, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, pv.Plotter):
            raise TypeError(
                f"PyvistaPlotter expects a pyvista.Plotter, got {type(value)!r}."
            )

        tmp = (
            self.tmp_dir
            if not self.inline
            else Path(tempfile.mkdtemp(prefix="gradio_pyvista_inline_"))
        )
        vtksz_path = tmp / f"scene_{uuid4()}.vtksz"
        value.export_vtksz(vtksz_path)
        value.close()

        if self.inline:
            result = self._build_iframe_inline(vtksz_path)
            vtksz_path.unlink(missing_ok=True)
            return result
        else:
            return self._build_iframe_file(vtksz_path)

    @property
    def allowed_paths(self) -> list[str]:
        """Pass to demo.launch(allowed_paths=viewer.allowed_paths). Only relevant in file mode."""
        return [str(self.tmp_dir)] if self.tmp_dir else []
