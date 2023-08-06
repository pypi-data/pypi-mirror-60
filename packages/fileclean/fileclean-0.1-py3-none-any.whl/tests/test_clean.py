import os
from fileclean import clean


def test_cleanwork():
    filename = "file1.txt"
    fromPath = "./tests/data/from/"
    toPath = "./tests/data/to/"
    filepath = os.path.join(fromPath, filename)
    toFilepath = os.path.join(toPath, filename)
    with open(filepath, "w") as f:
        f.write("from")
    os.remove(toFilepath)
    for i in range(2):
        clean.cleanwork(fromPath, toPath, r".*\.txt", "move")
        # asssert not error if task rerun

