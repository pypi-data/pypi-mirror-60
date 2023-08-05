from pathlib import Path
from unittest.mock import patch
import sys
import os

import pytest

import todofinder
import todofinder.__main__ as cli

TESTVECTOR_DIR: Path = Path(__file__).parent / "testvector"

def test_setup():
    assert TESTVECTOR_DIR.is_dir()
    assert (TESTVECTOR_DIR / "README.md").is_file()


def test_get_files():
    glob_input = str(TESTVECTOR_DIR / "*.md")
    exp_output = str(TESTVECTOR_DIR / "README.md")

    files = todofinder.get_files([glob_input])
    assert list(files) == [exp_output]


def test_scan_line_no_todos():
    context = todofinder.TodoContext(None, None, None, None)
    no_todos = "This is a normal line of text."
    assert todofinder.scan_line(no_todos, context) is None


def test_scan_line_one_todo():
    context = todofinder.TodoContext(None, None, None, None)
    with_todos = "This line of text has a TODO: this one"
    assert todofinder.scan_line(with_todos, context) == todofinder.Todo(
        token="todo",
        text=" this one",
        context=context
    )

def test_scan_line_false_case():
    context = todofinder.TodoContext(None, None, None, None)
    with_todos = "This line has the word autodoc which contains the token"
    assert todofinder.scan_line(with_todos, context) is None


def test_scan_file():
    file = str(TESTVECTOR_DIR / "README.md")
    scan_result = todofinder.scan_file(file)
    todo_list = list(scan_result)
    assert todo_list == [todofinder.Todo(
        token="todo",
        text=" example",
        context=todofinder.TodoContext(
            file=file,
            line_number=0,
            full_line="This is a test-README. TODO: example",
            filetype="md",
        )
    )]


def test_scan_file_nonexistent_file(capsys):
    file = str(TESTVECTOR_DIR / "fakefile.iso")
    scan_result = todofinder.scan_file(file)
    todo_list = list(scan_result)
    assert "while scanning {}".format(str(file)) in capsys.readouterr().err
    assert todo_list == []


def test_integration(capsys):
    real_file = str(TESTVECTOR_DIR / "README.md")
    fake_file = str(TESTVECTOR_DIR / "fakefile.iso")
    outp_file = str(TESTVECTOR_DIR / "todos.csv")
    files = [
        real_file,
        fake_file,
        outp_file,
    ]
    scan_result = todofinder.scan_files(files, output_file=outp_file)
    todofinder.to_csv(scan_result, output_file=outp_file)

    assert "while scanning {}".format(str(fake_file)) in capsys.readouterr().err
    with open(outp_file) as file:
        assert file.read() == """
file,line_number,text,token,full_line,filetype
{real_file},0, example,todo,This is a test-README. TODO: example,md
""".format(real_file=real_file).lstrip()

@pytest.mark.parametrize("plugins,", [["py", "c"], ["all"]])
def test_cli(plugins):
    todos_name = "todos_cli.csv"

    globs = [
        str(TESTVECTOR_DIR / "**/*.py"),
        str(TESTVECTOR_DIR / "**/*.md"),
        str(TESTVECTOR_DIR / "**/*.c"),
        str(TESTVECTOR_DIR / "**/*.unknown"),
    ]

    files = {
        "main_py": str(TESTVECTOR_DIR / "main.py"),
        "readme_md": str(TESTVECTOR_DIR / "README.md"),
        "main_c": str(TESTVECTOR_DIR / "main.c"),
        "unknown": str(TESTVECTOR_DIR / "file.unknown"),
    }

    try:
        # Touch the todos file
        with open(todos_name, "w"):
            pass

        # CLI arguments
        args = ["todofinder", "-g", *globs, "-o", todos_name, "-p", *plugins, "-b"]

        # Make the CLI function think it is running from the command line
        with patch.object(sys, "argv", args):
            with patch.object(todofinder.__main__, "__name__", "__main__"):
                cli.cli()

        #
        with open(todos_name, "r") as file:
            csv_data = file.read()
        assert csv_data == """
file,line_number,text,token,full_line,filetype,author,date,commit,message
{main_py},0, add code,todo,#TODO: add code,py,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,5d2aaa06aa46d995a2f4f23e7509aee21cfa327a,Building blocks for plugin system
{main_py},2, on indented line,todo,# TODO: on indented line,py,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,e7a6affe8feb56c86b41320c341ac2f6629b94b2,Make sure TODOs on indented lines are caught
{main_py},4, this is in a multiline comment,todo,TODO: this is in a multiline comment,py,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,f1072bbda9a1e7b6eff605389951005c7aed72aa,Finish up the Python plugin
{main_py},6, catch this,todo,"another = ""this line has inline comment"" # TODO: catch this",py,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,f1072bbda9a1e7b6eff605389951005c7aed72aa,Finish up the Python plugin
{main_py},8, catch THIS,todo,"yet_another = ""this line has an inline multiline comment"" \"\"\"\"\"\"TODO: catch THIS\"\"\"\"\"\"\",py,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,f1072bbda9a1e7b6eff605389951005c7aed72aa,Finish up the Python plugin
{main_py},10,(someone): this,todo,this = 1 # todo(someone): this,py,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,6e506ea3ac80d5cb297378b39902213ddf4a99aa,Add some trickier test cases
{readme_md},0, example,todo,This is a test-README. TODO: example,md,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,be19df81c86eda6606eb70e265f45f813f5e6bd9,Move most of the code to __init__ and get it tested
{main_c},2, something,todo,"printf(""Hello, World!""); // TODO: something",c,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,5d2aaa06aa46d995a2f4f23e7509aee21cfa327a,Building blocks for plugin system
{main_c},4, catch multline comment,todo,TODO: catch multline comment,c,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,8ded423e8ec2ff304980820f2e70d141f0b88071,Get the C plugin working. Fix potential bug when some scripts have syntax errors
{main_c},7, catch,todo,int x = 1; /* inline multiline-style comment TODO: catch*/,c,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,8ded423e8ec2ff304980820f2e70d141f0b88071,Get the C plugin working. Fix potential bug when some scripts have syntax errors
{main_c},9, catch standalone comment,todo,// TODO: catch standalone comment,c,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,8ded423e8ec2ff304980820f2e70d141f0b88071,Get the C plugin working. Fix potential bug when some scripts have syntax errors
{main_c},10,catch without spaces,todo,//TODO:catch without spaces,c,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,8ded423e8ec2ff304980820f2e70d141f0b88071,Get the C plugin working. Fix potential bug when some scripts have syntax errors
{main_c},11,"catch multiline without spaces ,  another",todo,/*TODO:catch multiline without spaces TODO another*/,c,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,8ded423e8ec2ff304980820f2e70d141f0b88071,Get the C plugin working. Fix potential bug when some scripts have syntax errors
{unknown},0, nothing,todo,".unknown is not associated with any plugins, so it should make the main scanline function run. TODO nothing",unknown,jonathan.gjertsen@disruptive-technologies.com,2020-01-26,5d2aaa06aa46d995a2f4f23e7509aee21cfa327a,Building blocks for plugin system
""".lstrip().format(**files)
    finally:
        os.remove(todos_name)
