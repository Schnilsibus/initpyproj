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


def create_local_directory(
        parent_dir: Path,
        name: str,
        author: str,
        mail: str,
        description: str = "",
        keywords: list = None
) -> None:
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
        file_content = replace_variable(content=file_content, variable="<AUTHOR>", data=author)
        file_content = replace_variable(content=file_content, variable="<MAIL>", data=mail)
        if keywords:
            file_content = replace_variable(content=file_content,
                                            variable="<KEYWORDS>",
                                            data="[" + ", ".join(keywords) + "]")
        else:
            file_content = replace_variable(content=file_content, variable="<KEYWORDS>", data="[]")
        with open(file=parent_dir / name / file_name, mode="x") as fp:
            fp.write(file_content)


def create_local_git_repo(path: Path) -> None:
    try:
        run(["git", "init", "-q"], shell=True, cwd=str(path), check=True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)


def commit_all_changes_local(path: Path) -> None:
    try:
        run(["git", "commit", "-m", '"initial commit by initpyproj"', "-q"], shell=True, cwd=str(path), check=True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)


def add_all_changes_local(path: Path) -> None:
    try:
        run(["git", "add", "-A"], shell=True, cwd=str(path), check=True, capture_output=True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)


def create_git_hub_repo(path: Path, name: str, description: str = None, private: str = False):
    try:
        command = ["gh", "repo", "create", f"{name}", "-r=origin", "-s=.", "--push"]
        if description:
            command.append(f"-d={description}")
        if private:
            command.append("--private")
        else:
            command.append("--public")
        run(command, shell=True, cwd=str(path), check=True, capture_output=True)
    except CalledProcessError as ex:
        raise ChildProcessError(ex.stderr)


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
    p.add_argument("author",
                   help="the author of the new python project",
                   type=str)
    p.add_argument("mail",
                   help="the mail of the author",
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
    git_group = p.add_mutually_exclusive_group()
    git_group.add_argument("--no-git",
                           help="will not create a local git repo (and no GitHub repo)",
                           action="store_false",
                           dest="git")
    git_group.add_argument("--no-GitHub",
                           help="will create a local git repo but no GitHub repo",
                           action="store_false",
                           dest="GitHub")
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
    logging.basicConfig(level=level, format='%(asctime)s %(message)s')
    if disabled:
        logging.disable()


def main(args: Namespace) -> None:
    parent_dir = Path(args.dir) if args.dir else Path.cwd()
    setup_logging(disabled=args.logDisabled, level=args.logLevel)
    create_local_directory(parent_dir=parent_dir,
                           name=args.name,
                           author=args.author,
                           mail=args.mail,
                           description=args.description,
                           keywords=args.keywords)
    logging.info(msg=f"created local dir at: {str(parent_dir / args.name)}")
    if args.git:
        create_local_git_repo(path=parent_dir / args.name)
        add_all_changes_local(path=parent_dir / args.name)
        commit_all_changes_local(path=parent_dir / args.name)
        logging.info(msg=f"created local git repo at: {str(parent_dir / args.name)}")
    if args.git and args.GitHub:
        create_git_hub_repo(path=parent_dir / args.name,
                            name=args.name,
                            description=args.description,
                            private=args.private)
        logging.info(msg=f"created GitHub repo")


if __name__ == "__main__":
    parser = construct_argument_parser()
    main(parser.parse_args())
