# PyPrism

![Build & Test](https://github.com/manorajesh/pyprism/actions/workflows/python-app.yml/badge.svg)
![Lines of Code](https://tokei.rs/b1/github/manorajesh/pyprism)

**PyPrism** is a comprehensive 3D modeling and rendering toolkit entirely in Python, rendered with the `cmu_graphics` library. The project will implement everything from scratch from matrix operations, to perspective projection, to path tracing. The goal is to provide a simple and intuitive interface for creating and manipulating 3D objects in a virtual space, as well as a path-traced rendering engine for realistic lighting effects.

In addition to a functional 3D modeling environment that allows users to create and manipulate objects in a virtual space, PyPrism will include a path-traced rendering engine. This will simulate realistic lighting effects, such as reflections, refractions, and global illumination, using a physically accurate approach to light transport.

## Installation

Clone the repository and create the virtual environment:

```bash
git clone https://github.com/manorajesh/pyprism.git && cd pyprism
```

Create a virtual environment:

```bash
python -m venv env/ && source env/bin/activate
```

```bash
pip install -r requirements.txt
```

## Usage

Run the main script:

```bash
python src/main.py
```

This will open a window displaying the 3D modeling environment.

### Controls

#### Camera Controls

- Hold `Space` and move mouse to orbit the camera around the scene.
- Hold `q` and move mouse to zoom camera
- Press `x`, `y`, or `z` to snap the camera to the x, y, or z axis, respectively.
- Press `5` to toggle between orthographic and perspective projection.

#### Object Controls

- Press `tab` to switch between object selection and edit mode.

##### Object Mode

- In object selection mode, right click with the mouse on an object to select it. It will highlight in orange.
- Hold `g` and move the mouse to translate the selected object.
- Hold `r` and move the mouse to rotate the selected object.
- Hold `s` and move the mouse to scale the selected object.
  - For any of the above transformations, press `x`, `y`, or `z` to constrain the transformation to the x, y, or z axis, respectively.
- Press `delete` to delete the selected object.

##### Edit Mode

- Press `1` for vertex selection mode and `2` for face selection mode.
- In edit mode, right click with the mouse on a vertex/face to select it. It will highlight in orange.
- Hold `g` and move the mouse to translate the selected vertex.
  - Press `x`, `y`, or `z` to constrain the transformation to the x, y, or z axis, respectively.
- Press `e` to extrude the selected face.
