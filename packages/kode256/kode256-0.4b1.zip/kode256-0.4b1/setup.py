
from setuptools import setup, find_packages
from os import path
import codecs
try:
    import py2exe
except ImportError:
    pass

here = path.abspath(path.dirname(__file__))
with codecs.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_descr = f.read()

setup(
    name        = "kode256",
    version     = "0.4b1",
    description = "Create code128 barcodes",
    long_description = long_descr,
    url         = "https://gitlab.com/bhowell/kode256",
    author      = "Brendan Howell, Felix Knopf",
    author_email = "brendan-soc@howell-ersatz.com",
    license     = "LGPLv2+",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: "
            "GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities"
    ],
    keywords    = "barcode",
    packages=find_packages(exclude=[]),
    package_data= {"kode256" : ["Inconsolata-Regular.ttf"]},
    #install_requires = []
    extras_require = { "PIL" : ["Pillow>=2.7.0"] },
    entry_points={
        "console_scripts": [
            "code128 = kode256.tool:main",
        ],
        "gui_scripts": [
            "code128w = kode256.tool:gui_main",
        ]
    },
    console = [
        {"script":"kode256/__main__.py", "dest_base":"code128"}
    ],
    windows = [
        {"script":"kode256/tool/gui.py", "dest_base":"code128w"}
    ],
)

