from pathlib import Path
from os import mkdir
from subprocess import run, CalledProcessError
from argparse import ArgumentParser, Namespace
import logging

_dirs = ["_core", "scripts", "tests", "data"]
_files = {
    "LICENSE": Path(__file__).parent / Path("templates/[template]LICENSE"),
    "CHANGELOG.md": Path(__file__).parent / Path("templates/[template]CHANGELOG"),
    "MANIFEST.in": Path(__file__).parent / Path("templates/[template]MANIFEST"),
    "README.md": Path(__file__).parent / Path("templates/[template]README"),
    "setup.py": Path(__file__).parent / Path("templates/[template]setup"),
    ".gitignore": Path(__file__).parent / Path("templates/[template]gitignore")
}


def replace_variable(content: str, variable: str, data: str) -> str:
    if variable in content:
        content = content.replace(variable, data)
    return content


def create_local_directory(parent_dir: Path, name: str, description: str = "", keywords: list = None) -> None:
    mkdir(path=parent_dir / name)
    for dirName in _dirs:
        full_path = parent_dir / name / dirName
        mkdir(path=full_path)
        if dirName == "_core":
            open(file=full_path / f"{name}.py", mode="x").close()
        open(file=full_path / "__init__.py", mode="x").close()
    for file_name in _files.keys():
        with open(file=_files[file_name], mode="r") as fp:
            file_content = fp.read()
        file_content = replace_variable(content=file_content, variable="<NAME>", data=name)
        file_content = replace_variable(content=file_content, variable="<DESCRIPTION>", data=description)
        if keywords:
            file_content = replace_variable(content=file_content,
                                            variable="<KEYWORDS>",
                                            data="[" + ", ".join(keywords) + "]")
        else:
            file_content = replace_variable(content=file_content, variable="<KEYWORDS>", data="[]")
        with open(file=parent_dir / name / file_name, mode="x") as fp:
            fp.write(file_content)


def write_url_in_local_files(path: Path, url: str) -> None:
    full_path = path / "setup.py"
    with open(file=full_path, mode="r") as fp:
        content = fp.read()
    content = replace_variable(content=content, variable="<URL>", data=url)
    with open(file=full_path, mode="w") as fp:
        fp.write(content)


def create_local_git_repo(path: Path) -> None:
    try:
        run(["git", "init"], shell=True, cwd=str(path), check=True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)


def commit_all_changes_local(path: Path) -> None:
    try:
        run(["git", "commit", "-m", '"initial commit by initpyproj"'], shell=True, cwd=str(path), check=True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)


def add_all_changes_local(path: Path) -> None:
    try:
        run(["git", "add", "-A"], shell=True, cwd=str(path), check=True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)


def push_local_changes(path: Path) -> None:
    try:
        run(["git", "commit", "push"], shell=True, cwd=str(path), check=True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)


def create_git_hub_repo(path: Path, name: str, description: str = None, private: str = False) -> str | None:
    try:
        command = ["gh", "repo", "create", f"{name}", "-r=origin", "-s=."]
        if description:
            command.append(f"-d={description}")
        if private:
            command.append("--private")
        stdout = run(command, shell=True, cwd=str(path), check=True, capture_output=True, text=True).stdout
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)
    protocol = get_git_hub_cli_protocol()
    if protocol == "https":
        start_key = "https://github.com/"
        end_key = ".git"
        start = stdout.find(start_key)
        end = stdout.find(end_key) + len(end_key)
        return stdout[start: end + 1] if not start_key == -1 else None
    else:
        return None


def get_git_hub_cli_protocol() -> str:
    key = "git_protocol="
    try:
        stdout = run(["gh", "config", "list"], shell=True, check=True, capture_output=True, text=True).stdout
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)
    start = stdout.find(key) + len(key)
    end = stdout.find("\n", start)
    return stdout[start: end + 1]


def construct_argument_parser() -> ArgumentParser:
    p = ArgumentParser(
        prog="initpyproj",
        description="Initialize a empty python project; make it a git repo; and sync it with a new github repo",
        add_help=True,
        allow_abbrev=True
    )
    p.add_argument("name",
                   help="the name of the new python project",
                   type=str)
    p.add_argument("-descr",
                   "--description",
                   help="a short description of the python project",
                   type=str,
                   default="")
    p.add_argument("-kw",
                   "--keywords",
                   help="some keywords for the python project",
                   nargs="*")
    p.add_argument("-dir",
                   "--parent-dir",
                   help="the parent dir of the python project, if omitted the current working directory is used",
                   dest="dir")
    git_group = p.add_argument_group()
    git_group.add_argument("--no-git",
                           help="will not create a local git repo (and no GitHub repo)",
                           action="store_true",
                           dest="git")
    git_group.add_argument("--no-GitHub",
                           help="will create a local git repo but no GitHub repo",
                           action="store_true",
                           dest="git_hub")
    git_group.add_argument("--private",
                           help="will create the GitHub as a public repo",
                           action="store_true",
                           default=False)
    verbosity_group = p.add_mutually_exclusive_group()
    verbosity_group.add_argument("-v",
                                 "--verbose",
                                 help="enables verbose output",
                                 action="store_const",
                                 const=logging.INFO,
                                 dest="logLevel")
    verbosity_group.add_argument("-q",
                                 "--quiet",
                                 help="disables any output",
                                 action="store_true",
                                 default=False,
                                 dest="logDisabled")
    verbosity_group.add_argument("-d",
                                 "--debug",
                                 help="disables any output",
                                 action="store_const",
                                 const=logging.DEBUG,
                                 dest="logLevel")

    return p


def setup_logging(disabled: bool, level) -> None:
    logging.basicConfig(level=level)
    if disabled:
        logging.disable()


def main(args: Namespace) -> None:
    parent_dir = Path(args.parent_dir) if args.parent_dir else Path.cwd()
    setup_logging(disabled=args.logDisabeld, level=args.logLevel)
    create_local_directory(parent_dir=parent_dir, name=args.name, description=args.description,
                           keywords=args.keywords)
    if not args.no_git:
        create_local_git_repo(path=parent_dir / args.name)
        add_all_changes_local(path=parent_dir / args.name)
        commit_all_changes_local(path=parent_dir / args.name)
    if not (args.no_git or args.no_GitHub):
        create_git_hub_repo(path=parent_dir / args.name,
                            name=args.name,
                            description=args.description,
                            private=args.private)


if __name__ == "__main__":
    parser = construct_argument_parser()
    main(parser.parse_args())
