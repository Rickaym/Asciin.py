# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The changelog only keeps track of updates post version **0.1.4**

## [Unreleased]

## [0.2.0] - 2021-08-30

### Major
- Dropped python `2.7` support as there is no further reason to with a complete rewrite of typehints.


### Changed
- `amath` module is renamed to `geometry`
- `PixelPainter` class is renamed to `mask`
- `geometry` - `Matrix` classes now supports attribute and index fetching `m.x` or `m[0]` or `m["x"]` as part of the `__getitem__` routine.
- `screen` - `DispWindow` renamed to `screen.WindowsControl`, `screen.DispMacOS` and `screen.DispLinux` is generalized to `screen.UnixControl`. `Displayable` is renamed to `Screen`.
- Built-in render and collision methods provided acquires color from `object.color` and acquires texture from `object.texture`
- Rendering methods are completely re-written in a way optimized for coloring

### Added

- `utils` - Added a `Profiler` class which utilizes a tiny wrapper class that uses `cProfile` and `pstats` from the stdlib and allows a form of context manager to gather the statistics of the application and dump it elsewhere. `Color` - general means of coloring components of the console
- `geometry` - Projection and rotational matrixes, `geometry.X_ROTO_MATRIX`, `geometry.Y_ROTO_MATRIX`, `geometry.Z_ROTO_MATRIX`, `geometry.PROJE_MATRIX`. these are further implemented by `geometry.project_3D` and `geometry.rotate_3D`
- `screen` - `Screen.refresh` used to write directly in a low level operation onto stdout with cursor at the origin (the frame system remains the same)
- `values` - `ANSI` provides variou ANSI escape code as hex code for chaning escape sequences to will
- `devices` - `Keyboard` and `Mouse` module provides handling input and output on those devices ~ `Mic` and `Audio` will be implemented later down the line.
- `planes` - `Rasterizer`, `Collidable` implemented (they used to be generalized as part of `Plane`)

### Removed

- `planes.Rectangle`
- `utils.caches` - use `functools.lru_cache`
- `_2D.methods` directory is removed and specific methods are now stitched to relevant objects, this includes collision physics and rasturizing.

## [0.1.5] - 2021-08-13

### Notes

- This is the last update until major release `0.2`, which is expected to feature 3D elements at first hand and a more concrete structure definition, although there are possibilities of bug fixing releases before it.

### Added

- `amath.Line` - a simple abstract representation of a mathemathical line from two points, this isn't subclassed under `Plane` because it isn't a graphical model
- `planes.Triangle` - simple class that implements `amath.Line` classes
- `amath` - module in the general scope for optimized arithmetic
- `amath.Matrix` - the genesis of all 3D objects and concepts for the future ;) supports all operable actions with and on itself and other compatible types
- An installable extension package which is a code interpolator that condenses any post version **0.1.4** distributions of the library into one singular `.py` file that can be shipped off readily. The condensed python contains version information, resolved relative dependencies, system dependencies and licenses as well ~ it will also support the submodule importing syntax e.g. `from Asciinpy._2D import Plane`; as it makes-up classes under the namespace of the sub packages with their contents defined.

### Changed

- Objects are now appropriately categorized onto their respective sub-packages (`_2D` and `_3D`)if said dimensions are an integral part of differientiating and using them ~ objects lower than 2D are put in the general scope, this is for example why `utils` and `amath` aren't categorized into dimensions.
- 2D specific models are now subclassed under `Plane` which is a renamed class of version _0.1.4_ `Model` ~ while the 3D base model class is named `Model`.
