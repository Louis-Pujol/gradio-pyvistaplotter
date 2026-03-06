# gradio_pyvistaplotter/launch.py
import signal
import sys
import time

from .plottercomponent import PyvistaPlotter


def launch(demo, **kwargs):
    """Launch a Gradio demo with reliable Ctrl+C support on all platforms.

    This is a drop-in replacement for ``demo.launch()`` that fixes a known
    Gradio issue on Linux where Ctrl+C (SIGINT) is swallowed by uvicorn's
    asyncio event loop and never terminates the server.

    The fix works by:
    - Starting the server in a background thread via ``prevent_thread_lock=True``
    - Blocking the main thread using ``signal.pause()`` (Linux/macOS) or a
      sleep loop (Windows), both of which correctly raise ``KeyboardInterrupt``
      when Ctrl+C is pressed.

    Args:
        demo (gr.Blocks): The Gradio Blocks instance to launch.
        **kwargs: All keyword arguments are forwarded to ``demo.launch()``.
            ``prevent_thread_lock`` is forced to ``True`` and cannot be
            overridden, as the blocking behaviour is handled here instead.

    Example:
        Instead of the standard::

            demo.launch(allowed_paths=viewer.allowed_paths, server_name="0.0.0.0")

        Use::

            from gradio_pyvistaplotter import launch
            launch(demo, allowed_paths=viewer.allowed_paths, server_name="0.0.0.0")

    Note:
        This workaround is necessary because Gradio's built-in signal handling
        relies on uvicorn's asyncio handler on Linux, which defers SIGINT
        indefinitely when the event loop is kept busy by active connections
        (such as those opened by an iframe-based component). See:
        https://github.com/gradio-app/gradio/issues/7051
    """

    plotter_paths = []
    for block in demo.blocks.values():
        if isinstance(block, PyvistaPlotter):
            plotter_paths.extend(block.allowed_paths or [])
    
    # Merge with any user-provided allowed_paths
    user_paths = kwargs.get("allowed_paths", [])
    kwargs["allowed_paths"] = list(set(user_paths + plotter_paths))
    kwargs["prevent_thread_lock"] = True

    demo.launch(**kwargs)

    try:
        if hasattr(signal, "pause"):
            signal.pause()   # Linux/macOS: blocks until any signal is received
        else:
            while True:
                time.sleep(1)  # Windows: no signal.pause(), poll instead
    except KeyboardInterrupt:
        print("\nShutting down...", flush=True)
        sys.exit(0)