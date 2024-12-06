# PyPrism

![Build & Test](https://github.com/manorajesh/pyprism/actions/workflows/python-app.yml/badge.svg)

**PyPrism** is a comprehensive 3D modeling and rendering toolkit entirely in Python, rendered with the `cmu_graphics` library. The project will implement everything from scratch from matrix operations to perspective projection. The goal is to provide a simple and intuitive interface for creating and manipulating 3D objects in a virtual space. The project will include a scene graph, object properties, and a camera system for navigating the 3D space. Based around edit and object modes, users can create, select, and manipulate objects in the scene. Users can select faces and vertices, being able to translate them and extrude faces. Users can dynamically add and delete objects to the scene. The project can also read obj files so that users can import 3D models into the scene (e.g. `sphere.obj`, `suzanne.obj`, etc.). The project will also include a simple rendering engine that can render the scene with a camera and lighting system using Lambertian shading. The project has a simple panel UI to display various object and program statistics.

Key features of the project include:

- **3D Object Rendering:** Ability to render primative 3D objects like planes and cubes. Also be able to import `.obj` files.
- **3D Modeling:** Ability to create and manipulate 3D objects in a 3D space.
- **Interactive Camera Control:** Users can navigate/interact with the 3D space using the keyboard and mouse.
- **Lamberian Shading:** Implement a simple shading model to render objects in the scene.

## Similar Projects

1. **Three.js**

   - **Key Features:**
     - Comprehensive scene graph for managing 3D objects.
     - Advanced shading and lighting.
     - Support for various 3D file formats and textures.

2. **Blender 3D**

   - **Key Features:**
     - Comprehensive modeling and animation tools.
     - Realistic rendering with physics-based shading.

3. **Unity Engine**

   - **Key Features:**
     - Editor for scene management and object manipulation.
     - Real-time lighting and shading features.

## Version Control

**Git** will be the main version control for this project. All project files will be hosted on **GitHub** alongside local backups. Regular commits will be made to track project progress and ease development.

![Github Screenshot](https://github.com/manorajesh/pyprism/blob/master/images/repo.png?raw=true)

## Tech List

No external libraries are planned for this project other than the `cmu_graphics` library and Python 3.\*.

## Storyboard

![Storyboard](https://github.com/manorajesh/pyprism/blob/master/images/storyboard.jpg?raw=true)

---
