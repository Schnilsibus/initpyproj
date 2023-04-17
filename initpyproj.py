from pathlib import Path
from os import mkdir
from subprocess import run, CalledProcessError
from argparse import ArgumentParser, Namespace

_dirs = ["_core", "scripts", "tests", "data"]
_files = {
    "LICENSE": Path(__file__).parent / Path("templates/[template]LICENSE"),
    "CHANGELOG.md": Path(__file__).parent / Path("templates/[template]CHANGELOG"),
    "MANISFEST.in": Path(__file__).parent / Path("templates/[template]MANIFEST"),
    "README.md": Path(__file__).parent / Path("templates/[template]README"),
    "setup.py": Path(__file__).parent / Path("templates/[template]setup"),
    ".gitginore": Path(__file__).parent / Path("templates/[template]gitignore")
}

def replaceVariable(content: str, variable: str, data: str) -> str:
    if (content.__contains__(variable)):
            content = content.replace(variable, data)
    return content

def createLocalDirectory(parentDir: Path, name: str, description: str = "", keywords: list = None) -> None:
    mkdir(path = parentDir / name)
    for dirName in _dirs:
        fullPath = parentDir / name / dirName
        mkdir(path = fullPath)
        if (dirName == "_core"):
            open(file = fullPath / f"{name}.py",  mode = "x").close()
        open(file = fullPath / "__init__.py",  mode = "x").close()
    for fileName in _files.keys():
        with open(file = _files[fileName], mode = "r") as fp:
            fileContent = fp.read()
        fileContent = replaceVariable(content = fileContent, variable = "<NAME>", data = name)
        fileContent = replaceVariable(content = fileContent, variable = "<DESCRIPTION>", data = description)
        if (keywords):
            fileContent = replaceVariable(content = fileContent, variable = "<KEYWORDS>", data = "[" + ", ".join(keywords) + "]")
        else:
            fileContent = replaceVariable(content = fileContent, variable = "<KEYWORDS>", data = "[]")
        with open(file = parentDir / name / fileName, mode = "x") as fp:
            fp.write(fileContent)

def writeUrlInLocalFiles(path: Path, url: str) -> None:
    fullPath = path / "setup.py"
    with open(file = fullPath, mode = "r") as fp:
        content = fp.read()
    content = replaceVariable(content = content, variable = "<URL>", data = url)
    with open(file = fullPath, mode = "w") as fp:
        fp.write(content)

def createLocalGitRepo(path: Path) -> None:
    try:
        run(["git", "init"], shell = True, cwd = str(path), check = True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)

def commitAllChangesLoacal(path: Path) -> None:
    try:
        run(["git", "commit", "-m", '"initial commit by initpyproj"'], shell = True, cwd = str(path), check = True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)

def addAllChangesLocal(path: Path) -> None:
    try:
        run(["git", "add", "-A"], shell = True, cwd = str(path), check = True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)

def pushLocalChanges(path: Path) -> None:
    try:
        run(["git", "commit", "push"], shell = True, cwd = str(path), check = True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)

def createGitHubRepo(path: Path, name: str, description: str = None) -> str:
    try:
        if (description):
            stdout = run(["gh", "repo", "create", f"{name}", f"-d={description}", "--public", "-r=origin", "-s=."], shell = True, cwd = str(path), check = True, capture_output = True, text = True).stdout
        else:
            stdout = run(["gh", "repo", "create", f"{name}", "--public", "-r=origin", "-s=."], shell = True, cwd = str(path), check = True, capture_output = True, text = True).stdout
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)
    protocoll = getGitHubCLIProtocoll()
    if (protocoll == "https"):
        startKey = "https://github.com/"
        endKey = ".git"
        start = stdout.find(startKey)
        end = stdout.find(endKey) + len(endKey)
        return stdout[start: end + 1] if not startKey == -1 else None
    else:
        return None

def getGitHubCLIProtocoll() -> str:
    key = "git_protocoll="
    try:
        stdout = run(["gh", "config", "list"], shell = True, check = True, capture_output = True, text = True).stdout
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)
    start = stdout.find(key) + len(key)
    end = stdout.find("\n", start)
    return stdout[start: end + 1]

def constructArgumentParser() -> ArgumentParser:
    parser = ArgumentParser(
        prog = "initpyproj",
        description = "Initialize a empty python project; make it a git repo; and sync it with a new github repo",
        add_help = True, 
        allow_abbrev = True
        )
    parser.add_argument("name", help = "the name of the new python project", type = str)
    parser.add_argument("-d", "--description", help = "a short discription of the python project", type = str, default = "")
    parser.add_argument("-kw", "--keywords", help = "some keywords for the python project", nargs = "*")
    parser.add_argument("-dir", "--parent-dir", help = "the parent dir of the python project, if omitted the current working directory is used")
    parser.add_argument("--no-git", help = "will not create a local git repo (and no GitHub repo)", action = "store_true")
    parser.add_argument("--no-GitHub", help = "will create a local git repo but no GitHub repo", action = "store_true")
    verbosityGroup = parser.add_mutually_exclusive_group()
    verbosityGroup.add_argument("-v", "--verbose", help = "enables verbose outupt", action = "store_true")
    verbosityGroup.add_argument("-q", "--quiet", help = "disables any output", action = "store_true")

    return parser

def main(args: Namespace) -> None:
    name = args.name
    parentDir = Path(args.parent_dir) if args.parent_dir else Path.cwd()
    path = parentDir / name
    createLocalDirectory(parentDir = parentDir, name = name, description = args.description, keywords = args.keywords)


if (__name__ == "__main__"):
    parser = constructArgumentParser()
    main(parser.parse_args())
