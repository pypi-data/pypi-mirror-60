import csv
from collections import namedtuple
import glob
import re
import sys
from typing import Iterable, Optional, Tuple

LOWERCASE_CHARS = { chr(x) for x in range(ord('a'), ord('z')) }
UPPERCASE_CHARS = { char.upper() for char in LOWERCASE_CHARS }
DIGITS = { chr(x) for x in range(ord('0'), ord('9')) }
VARNAME_CHARS = LOWERCASE_CHARS | UPPERCASE_CHARS | DIGITS | { '_' }

TOKENS = {
    "todo",
    "fixme",
}

TodoContext = namedtuple("TodoContext", "file line_number full_line filetype")
Todo = namedtuple("Todo", "token text context")

def log_error(message):
    print(message, file=sys.stderr)

def get_files(glob_paths: Iterable[str], recursive: bool=True) -> Iterable[str]:
    for glob_path in glob_paths:
        yield from glob.iglob(glob_path, recursive=recursive)

def get_todo_text(line: str) -> Optional[Tuple[str, str]]:
    # Check for TODO tokens
    lower_line = line.lower()
    for token in TOKENS:
        if token in lower_line:
            break
    else:
        return None

    # Look at what comes before and after
    before, *after = re.split(token, line, flags=re.IGNORECASE)

    # Guard against e.g. "autodoc"
    if before and before[-1] in VARNAME_CHARS:
        return None

    # Re-assemble the string
    text = ", ".join(after)

    # Remove the colon after the TODO
    text = text.lstrip(":")
    return token, text

def scan_line(line: str, context: TodoContext) -> Optional[Todo]:
    token_and_text = get_todo_text(line)
    if token_and_text is not None:
        token, text = token_and_text
        return Todo(token=token, text=text, context=context)

def scan_file(path: str) -> Iterable[Todo]:
    extension = path.split(".")[-1]
    try:
        with open(path) as file:
            for line_no, line in enumerate(file):
                line = line.strip()
                context = TodoContext(path, line_no, line, extension)
                todo = scan_line(line, context)
                if todo is not None:
                    yield todo
    except Exception as exception:
        log_error("{} while scanning {}: {}".format(type(exception).__name__, path, exception))

def scan_files(paths: Iterable[str], output_file: str) -> Iterable[Todo]:
    for path in paths:
        if path == output_file:
            continue
        yield from scan_file(path)


def to_csv(todos: Iterable[Todo], output_file: str):
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "file",
            "line_number",
            "text",
            "token",
            "full_line",
            "filetype"
        ])
        for todo in todos:
            writer.writerow([
                todo.context.file,
                todo.context.line_number,
                todo.text,
                todo.token,
                todo.context.full_line,
                todo.context.filetype,
            ])
