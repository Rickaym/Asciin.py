from distutils.core import setup
from re import search, MULTILINE

with open("AsciiPy/__init__.py") as fp:
    version = search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fp.read(), MULTILINE
    ).group(1)

packages = ["AsciiPy", "AsciiPy.methods"]
name = "Ascii.py"
setup(
    name=name,
    version=version,
    description="Featherweight 3D / 2D ascii game engine for Python 2.7+ with no external dependencies and written in Python and optimized in C.",
    author="Rickaym",
    url=f"https://github.com/Rickaym/{name}",
    project_urls={
        "Documentation": "...",
        "Issue tracker": f"https://github.com/Rickaym/{name}/issues",
    },
    license="MIT",
    python_requires=">=2.7",
    packages=packages,
)
