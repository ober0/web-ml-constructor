import os
import pathlib

path = pathlib.Path(os.path.join(pathlib.Path(__file__).parent.absolute(), 'static/datasets'))
path.mkdir(exist_ok=True)

path = pathlib.Path(os.path.join(pathlib.Path(__file__).parent.absolute(), 'static/graphics'))
path.mkdir(exist_ok=True)

path = pathlib.Path(os.path.join(pathlib.Path(__file__).parent.absolute(), 'static/models'))
path.mkdir(exist_ok=True)
