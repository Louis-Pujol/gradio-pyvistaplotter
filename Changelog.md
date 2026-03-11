#Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.1.0] - 2026-03-11

Added

PyvistaPlotter: a Gradio custom component that embeds an interactive PyVista plotter in any Gradio app.
launch(): a wrapper around gr.Blocks.launch() with proper SIGINT/SIGTERM signal handling, fixing Ctrl+C not stopping the application on Linux.
