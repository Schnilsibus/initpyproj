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
_variables = ["<NAME>", "<URL>", "<DESCRIPTION>", "<KEYWORDS>"]

def replaceVariables(content: str, data: list) -> str:
    for i in range(len(_variables)):
        if (content.__contains__(_variables[i])):
            if (not i == len(_variables) - 1):
                content = content.replace(_variables[i], data[i])
            elif (not type(data[i]) == type(None)):
                content = content.replace(_variables[i], "[" + ", ".join(data[i]) + "]")
            else:
                content = content.replace(_variables[i], "[]")
    return content

def createLocalDirectory(path: Path, name: str, url: str, description: str = "", keywords: list = None) -> None:
    mkdir(path = path / name)
    for dirName in _dirs:
        fullPath = path / name / dirName
        mkdir(path = fullPath)
        open(file = fullPath / "__init__.py",  mode = "x").close()
    for fileName in _files.keys():
        with open(file = _files[fileName], mode = "r") as fp:
            fileContent = fp.read()
        fileContent = replaceVariables(content = fileContent, data = [name, url, description, keywords])
        with open(file = path / name / fileName, mode = "x") as fp:
            fp.write(fileContent)

if (__name__ == "__main__"):
    createLocalDirectory(path = Path("D:\Desktop"), name = "sampleproj", url = "notaurl", description = "notadescr", keywords = ["one", "two", "three"])