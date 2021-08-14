from setuptools import setup
from re import search, MULTILINE

pkg_name = "Asciinpy"
prj_name = "Asciin.py"
with open(f"{pkg_name}/__init__.py") as fp:
    version = search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fp.read(), MULTILINE
    ).group(1)

with open(f"readme.md", encoding="utf-8") as f:
    long_description = f.read()
packages = [pkg_name, "Asciinpy._2D", "Asciinpy._2D.methods","Asciinpy._3D"]

setup(
    name=prj_name,
    version=version,
    description="Featherweight 3D / 2D ascii game engine for Python 2.7+ with no external dependencies and written purely in Python.",
    author="Rickaym",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/Rickaym/{prj_name}",
    project_urls={
        "Documentation": "https://asciipy.readthedocs.io/en/latest/",
        "Issue tracker": f"https://github.com/Rickaym/{prj_name}/issues",
    },
    license="MIT",
    python_requires=">=2.7",
    packages=packages,
)
