# Pathfinding Algorithm

This module implements pathfinding algorithms using Python and raylib for visualization.

## Prerequisites

Before running this project, you need to:

1. Install raylib development libraries:

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential git cmake libgl1-mesa-dev libx11-dev libxrandr-dev libxi-dev libxinerama-dev libxcursor-dev
   git clone https://github.com/raysan5/raylib.git /tmp/raylib
   cd /tmp/raylib
   mkdir build && cd build
   cmake -DBUILD_SHARED_LIBS=ON ..
   make
   sudo make install
   sudo ldconfig
   ```

   **Other Operating Systems:**
   - Windows: See [raylib wiki](https://github.com/raysan5/raylib/wiki/Working-on-Windows)
   - macOS: See [raylib wiki](https://github.com/raysan5/raylib/wiki/Working-on-macOS)

2. Set up Python environment:
   ```bash
   # Using uv
   cd algorithms
   uv sync
   ```

## Running the Program

After installing the prerequisites, run:

```bash
uv run Python_Pathfind.py
```

## Troubleshooting

If you get an error about missing `libraylib.so.5.5.0`, ensure that:
1. raylib is properly installed (see Prerequisites)
2. The library is in your system's library path
3. Create the necessary symbolic link:
   ```bash
   mkdir -p .venv/lib/python3.*/site-packages/raylibpy/bin/64bit/
   ln -s /usr/local/lib/libraylib.so.5.5.0 .venv/lib/python3.*/site-packages/raylibpy/bin/64bit/libraylib.so.5.5.0
   ```
