# plotter_html.py
from __future__ import annotations
import atexit
import base64
import logging
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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", force=True)


class PyvistaPlotter(gr.HTML):
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
        logger.debug("PyvistaPlotter init — inline=%s height_px=%s", inline, height_px)

        if not inline:
            self._setup_tmp_dir()

        super().__init__(value=value, **kwargs)

    def _setup_tmp_dir(self) -> None:
        if os.getenv("GRADIO_TEMP_DIR") is not None:
            self.tmp_dir = Path(os.getenv("GRADIO_TEMP_DIR"))
            logger.debug("Using GRADIO_TEMP_DIR: %s", self.tmp_dir)
        else:
            self._tmp_dir_obj = tempfile.TemporaryDirectory(prefix="gradio_pyvista_")
            atexit.register(self._tmp_dir_obj.cleanup)
            self.tmp_dir = Path(self._tmp_dir_obj.name)
            logger.debug("Created tmp dir: %s", self.tmp_dir)

        allowed = os.getenv("GRADIO_ALLOWED_PATHS", "")
        if str(self.tmp_dir.resolve()) not in allowed:
            os.environ["GRADIO_ALLOWED_PATHS"] = (
                str(self.tmp_dir.resolve()) + ("," + allowed if allowed else "")
            )
        logger.debug("GRADIO_ALLOWED_PATHS: %s", os.getenv("GRADIO_ALLOWED_PATHS"))

        viewer_src = Path(__file__).parent / "static" / "static_viewer.html"
        self.viewer_path = self.tmp_dir / viewer_src.name
        logger.debug("Copying viewer HTML: %s -> %s", viewer_src, self.viewer_path)
        if viewer_src.resolve() != self.viewer_path.resolve():
            shutil.copy(viewer_src, self.viewer_path)

    def _viewer_html(self) -> str:
        viewer_src = Path(__file__).parent / "static" / "static_viewer.html"
        logger.debug("Reading viewer HTML from: %s (exists=%s)", viewer_src, viewer_src.exists())
        content = viewer_src.read_text()
        logger.debug("Viewer HTML length: %d chars", len(content))
        return content

    def _build_iframe_inline(self, vtksz_path: Path) -> str:
        logger.debug("Building inline iframe from vtksz: %s (size=%d bytes)",
                     vtksz_path, vtksz_path.stat().st_size)

        raw = vtksz_path.read_bytes()
        data_url = "data:application/octet-stream;base64," + base64.b64encode(raw).decode()
        logger.debug("data URL length: %d chars", len(data_url))

        html = self._viewer_html()
        if "__VTKSZ_URL__" not in html:
            logger.error("Placeholder __VTKSZ_URL__ NOT found in static_viewer.html — inline mode will not work")
        else:
            logger.debug("__VTKSZ_URL__ placeholder found, replacing")
        html = html.replace("__VTKSZ_URL__", data_url)

        html_b64 = base64.b64encode(html.encode()).decode()
        logger.debug("Final base64 HTML length: %d chars", len(html_b64))

        iframe = f"""
        <iframe
            src="data:text/html;base64,{html_b64}"
            width="100%"
            height="{self.height_px}px"
            style="border:0;"
        ></iframe>
        """
        logger.debug("iframe HTML snippet (first 200 chars): %s", iframe[:200])
        return iframe

    def _build_iframe_file(self, vtksz_path: Path) -> str:
        viewer_url = f"/gradio_api/file={quote(str(self.viewer_path.resolve()))}"
        data_url = f"/gradio_api/file={quote(str(vtksz_path.resolve()))}"
        logger.debug("Building file iframe — viewer_url=%s data_url=%s", viewer_url, data_url)
        return f"""
        <iframe
            src="{viewer_url}?fileURL={data_url}"
            width="100%"
            height="{self.height_px}px"
            style="border:0;"
        ></iframe>
        """

    def postprocess(self, value: Any) -> str | None:
        logger.debug("postprocess called — value type: %s", type(value))
        if value is None:
            logger.debug("value is None, returning None")
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
        logger.debug("Exporting vtksz to: %s", vtksz_path)
        value.export_vtksz(vtksz_path)
        value.close()
        logger.debug("Export done — file exists=%s size=%d",
                     vtksz_path.exists(), vtksz_path.stat().st_size if vtksz_path.exists() else -1)

        if self.inline:
            result = self._build_iframe_inline(vtksz_path)
            vtksz_path.unlink(missing_ok=True)
            logger.debug("Inline: deleted tmp vtksz, returning iframe HTML")
            return result
        else:
            return self._build_iframe_file(vtksz_path)

    @property
    def allowed_paths(self) -> list[str]:
        return [str(self.tmp_dir)] if self.tmp_dir else []
