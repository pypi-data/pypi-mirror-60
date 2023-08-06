
from .imports.internal   import *


def mkdir(filepath):
    """
    creates a whole folder structure for a filepath
    
    https://docs.python.org/3/library/os.path.html#os.path.split
    https://docs.python.org/3/library/os.html
    """
    folder = os.path.split(filepath)[0]
    if folder == "":
        folder = "."
    os.makedirs(folder, exist_ok=True)

