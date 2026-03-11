import signal
from unittest.mock import patch

import gradio as gr
from gradio_pyvistaplotter import PyvistaPlotter, launch


def test_custom_launch_is_callable():
    """Custom launch() is importable and callable.

    We do not invoke launch() directly in this test because it installs custom
    signal handlers (SIGINT/SIGTERM) to fix Ctrl+C on Linux. Running it inside
    pytest would override pytest's own signal handlers, causing the test suite
    to hang and become impossible to interrupt. The actual behavior of launch()
    should be validated manually or in a dedicated integration test run outside
    of pytest.
    """
    assert callable(launch)


def test_custom_launch_calls_demo_launch(plotter):
    """launch() forwards kwargs to demo.launch() with prevent_thread_lock=True.

    We mock demo.launch() and signal.pause() so the function returns immediately
    without blocking or touching signal handlers in a way that would interfere
    with pytest.
    """
    with gr.Blocks() as demo:
        PyvistaPlotter(value=plotter)

    port = 7861

    with (
        patch.object(demo, "launch") as mock_launch,
        patch("signal.signal"),
        patch("signal.pause", side_effect=KeyboardInterrupt),
        patch("sys.exit"),
    ):
        launch(demo, server_port=port)

    mock_launch.assert_called_once()
    call_kwargs = mock_launch.call_args[1]
    assert call_kwargs.get("prevent_thread_lock") is True
    assert call_kwargs.get("server_port") == port


def test_custom_launch_handles_keyboard_interrupt_on_linux(plotter):
    """launch() catches KeyboardInterrupt from signal.pause() and calls sys.exit(0).

    Covers the signal.pause() branch on Linux/macOS, where the
    blocking call raises KeyboardInterrupt when SIGINT is received.
    """
    with gr.Blocks() as demo:
        PyvistaPlotter(value=plotter)

    with (
        patch.object(demo, "launch"),
        patch("signal.signal"),
        patch("signal.pause", side_effect=KeyboardInterrupt),
        patch("sys.exit") as mock_exit,
    ):
        launch(demo)

    mock_exit.assert_called_once_with(0)


def test_custom_launch_handles_keyboard_interrupt_on_windows(
    plotter, monkeypatch
):
    """launch() catches KeyboardInterrupt from the Windows polling loop and calls sys.exit(0).

    Covers the Windows fallback branch by temporarily hiding
    signal.pause so the code falls back to the time.sleep() polling loop.
    """
    with gr.Blocks() as demo:
        PyvistaPlotter(value=plotter)

    monkeypatch.delattr(signal, "pause", raising=False)

    with (
        patch.object(demo, "launch"),
        patch("signal.signal"),
        patch("time.sleep", side_effect=KeyboardInterrupt),
        patch("sys.exit") as mock_exit,
    ):
        launch(demo)

    mock_exit.assert_called_once_with(0)
