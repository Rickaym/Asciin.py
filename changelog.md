# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The changelog only keeps track of updates post version **0.1.4**

## [Unreleased]

## [0.2] - 2021-08-30

### Notes

- Upcoming major release

## [Unreleased]

## [0.1.5] - 2021-08-13

### Notes

- This is the last update until major release `0.2`, which is expected to feature 3D elements at first hand and a more concrete structure definition, although there are possibilities of bug fixing releases before it.

### Added

- Concept and Classes on `Line`, made up of two sets of points
- Concept and Classes on `Triangle`, only made possible on derivation of the `Line` class
- Birth of `amath` module in the general scope
- Concept and Classes on `Matrix`, the genesis of all 3D objects and concepts for the future ;) supports all operable actions with and on itself and other compatible types
- An installable extension package which is a code interpolator that condenses any post version **0.1.4** distributions of the library into one singular `.py` file that can be shipped off readily. The condensed python contains version information, resolved relative dependencies, system dependencies and licenses as well ~ it will also support the submodule importing syntax e.g. `from Asciinpy.twod import Plane`; as it makes-up classes under the namespace of the sub packages with their contents defined.

### Changed

- Objects are now appropriately categorized onto their respective sub-packages (`_2D` and `_3D`)if said dimensions are an integral part of differientiating and using them ~ objects lower than 2D are put in the general scope, this is for example why `utils` and `amath` aren't categorized into dimensions.
- 2D specific models are now subclassed under `Plane` which is a renamed class of version _0.1.4_ `Model` ~ while the 3D base model class is named `Model`.
