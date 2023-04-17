from pathlib import Path
from os import mkdir

_dirs = ["_core", "scripts", "tests", "data"]
_files = {
    "LICENSE": Path(__file__).parent / Path("templates/[template]LICENSE"),
    "CHANGELOG.md": Path(__file__).parent / Path("templates/[template]CHANGELOG"),
    "MANISFEST.in": Path(__file__).parent / Path("templates/[template]MANIFEST"),
    "README.md": Path(__file__).parent / Path("templates/[template]README"),
    "setup.py": Path(__file__).parent / Path("templates/[template]setup"),
    ".gitginore": Path(__file__).parent / Path("templates/[template]gitignore")
}

def createLocalDirectory(path: Path, name: str, url: str):
    mkdir(path = path / name)
    for dirName in _dirs:
        fullPath = path / name / dirName
        mkdir(path = fullPath)
        open(file = fullPath / "__init__.py",  mode = "x").close()
    for fileName in _files.keys():
        with open(file = _files[fileName], mode = "r") as fp:
            fileContent = fp.read()
        if (fileName == "setup.py"):
            # TODO insert name; url etc in setup.py
            pass
        with open(file = path / name / fileName, mode = "x") as fp:
            fp.write(fileContent)

if (__name__ == "__main__"):
    pathInput = input("input a path: ")
    createLocalDirectory(path = Path(pathInput), name = "sampleproj", url = "notaurl")