from tproj.cli import get_tproj_argparser
from argparse import Namespace
import pytest

parser = get_tproj_argparser()

cli_args = [
    (["create", "-n", "hello", "-f"],
     Namespace(subcmd="create", name="hello", force=True)),
    (["create", "-n", "helloe"],
     Namespace(subcmd="create", name="helloe", force=False)),
    (["create"], Namespace(subcmd="create", name=None, force=False)),
    (["apply", "hello"], Namespace(subcmd="apply", name="hello", out_dir=".")),
    (["apply", "hello", "-O", "other"],
     Namespace(subcmd="apply", name="hello", out_dir="other")),
    (["ls"], Namespace(subcmd="ls")),
]


@pytest.mark.parametrize("argv, excepts", cli_args)
def test_cli_args(argv: list, excepts: Namespace):
    args = parser.parse_args(argv)
    assert args == excepts
