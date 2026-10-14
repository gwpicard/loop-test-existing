"""Judge for piece 3: the --title option of the command-line tool."""

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TABLE = "Sun 696000\nEarth 6371\n"


def run_cli(args, input_text=None):
    return subprocess.run(
        [sys.executable, "-m", "tabulate.cli"] + args,
        input=input_text,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def run_plain(args, input_text=None):
    # the title option does not exist yet on main: the call must still run
    return run_cli(args, input_text)


def test_D1_title_above_table():
    result = run_cli(["--title", "Planets"], TABLE)
    lines = result.stdout.splitlines()
    assert result.returncode == 0, result.stderr
    assert lines[0] == "Planets"
    assert "Sun" in lines[1] or "-----" in lines[1]
    expected_table = run_plain([], TABLE).stdout
    assert "\n".join(lines[1:]) + "\n" == expected_table


def test_D2_title_above_each_file():
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "a.txt")
        b = os.path.join(d, "b.txt")
        for path in (a, b):
            with open(path, "w") as f:
                f.write(TABLE)
        result = run_cli(["--title", "Planets", a, b])
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines.count("Planets") == 2
    table = run_plain([], TABLE).stdout.splitlines()
    assert lines == ["Planets"] + table + ["Planets"] + table


def test_D3_title_goes_to_output_file():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out.txt")
        result = run_cli(["--title", "Planets", "--output", out], TABLE)
        assert result.returncode == 0, result.stderr
        assert result.stdout == ""
        with open(out) as f:
            content = f.read()
    assert content == "Planets\n" + run_plain([], TABLE).stdout


def test_D4_title_is_plain_text_in_html():
    result = run_cli(["--title", "Planets", "-f", "html"], TABLE)
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "Planets"
    assert lines[1].startswith("<table")


def test_D5_no_title_output_unchanged():
    result = run_plain([], TABLE)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith("-----")
    assert "Planets" not in result.stdout


def test_D6_help_lists_title():
    result = run_cli(["--help"])
    assert "--title TITLE" in result.stdout
