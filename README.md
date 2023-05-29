# GIF_Me_HD
Prototype for the GIF ME HD Project.

# Building

```
git clone https://github.com/GIF-ME-HD/gif_me_hd_proto.git
```

Now create and setup a virtual environment For example,
```
mkdir pyvenv
python -m venv pyvenv
source pyvenv/bin/activate
```

For Windows, you will probably need to run the `Activate.ps1` script.

Now, install the requirements
```
pip install -r gif_me_hd_proto/requirements.txt
```

We have to 
```
python setup.py install
```

Now you can install the library...
```
pip install gif_me_hd_proto
```

And to run it, run the following...
```
cd gif_me_hd_proto
python src/gui.py
```

# Licenses
## Project License
See: [LICENSE.md](LICENSE.md) for the project's license.

## Dependencies
- [PySide6](https://doc.qt.io/qtforpython) - GNU Lesser General Public License (LGPL)
- [randomgen](https://github.com/bashtage/randomgen#license) -  BSD License (BSD-3-Clause)
- [numpy](https://github.com/numpy/numpy/blob/main/LICENSE.txt) - BSD License (BSD-3-Clause)
