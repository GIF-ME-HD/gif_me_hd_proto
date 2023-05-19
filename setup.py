# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages

__version__ = "0.0.1"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

ext_modules = [
    Pybind11Extension("lzw_gif_cpp",
        [
                      "gif_me_hd/cpp/lzw_gif_cpp.cpp"
         ],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        ),
]

setup(
    name="gif_me_hd_proto",
    version=__version__,
    author="Gif Me HD Team",
    author_email="",
    url="https://github.com/pybind/python_example",
    description="A program for encrypting GIFs",
    long_description="",
    ext_modules=ext_modules,
    install_requires=[
        "autopep8==2.0.2",
        "imageio==2.28.1",
        "Jinja2==3.1.2",
        "MarkupSafe==2.1.2",
        "numpy==1.24.3",
        "Pillow==9.5.0",
        "pybind11==2.10.4",
        "pycodestyle==2.10.0",
        "PySide6==6.5.0",
        "PySide6-Addons==6.5.0",
        "PySide6-Essentials==6.5.0",
        "qt-material==2.14",
        "randomgen==1.23.1",
        "shiboken6==6.5.0"
    ],
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # py_modules=["gif_me_hd"],
    extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)
