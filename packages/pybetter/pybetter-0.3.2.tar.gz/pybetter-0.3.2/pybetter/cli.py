import difflib
from typing import List, FrozenSet, Tuple

import libcst as cst
import click
from pyemojify import emojify

from pybetter.improvements import (
    FixNotInConditionOrder,
    BaseImprovement,
    FixMutableDefaultArgs,
    FixParenthesesInReturn,
    FixMissingAllAttribute,
    FixEqualsNone,
    FixBooleanEqualityChecks,
    FixTrivialFmtStringCreation,
)
from pybetter.utils import resolve_paths

ALL_IMPROVEMENTS: List[BaseImprovement] = [
    FixNotInConditionOrder(),
    FixMutableDefaultArgs(),
    FixParenthesesInReturn(),
    FixMissingAllAttribute(),
    FixEqualsNone(),
    FixBooleanEqualityChecks(),
    FixTrivialFmtStringCreation(),
]


def parse_improvement_codes(code_list: str) -> FrozenSet[str]:
    all_codes = frozenset([improvement.CODE for improvement in ALL_IMPROVEMENTS])
    codes = frozenset([code.strip() for code in code_list.split(",")]) - {""}

    if not codes:
        return frozenset()

    wrong_codes = codes.difference(all_codes)
    if wrong_codes:
        print(
            emojify(
                f":no_entry_sign: Unknown improvements selected: {','.join(wrong_codes)}"
            )
        )
        return frozenset()

    return codes


def process_file(
    source: str, improvements: List[BaseImprovement]
) -> Tuple[str, List[BaseImprovement]]:
    tree: cst.Module = cst.parse_module(source)
    modified_tree: cst.Module = tree
    improvements_applied = []

    for case in improvements:
        intermediate_tree = modified_tree
        modified_tree = case.improve(intermediate_tree)

        if not modified_tree.deep_equals(intermediate_tree):
            improvements_applied.append(case)

    return modified_tree.code, improvements_applied


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--noop",
    is_flag=True,
    default=False,
    help="Do not make any changes to the source files.",
)
@click.option(
    "--diff",
    "show_diff",
    is_flag=True,
    default=False,
    help="Show diff-like output of the changes made.",
)
@click.option(
    "--select",
    "selected",
    type=str,
    metavar="CODES",
    help="Apply only improvements with the provided codes.",
)
@click.option(
    "--exclude",
    "excluded",
    type=str,
    metavar="CODES",
    help="Exclude improvements with the provided codes.",
)
@click.argument("paths", type=click.Path(), nargs=-1)
def main(paths, noop: bool, show_diff: bool, selected: str, excluded: str):
    if not paths:
        print(emojify("Nothing to do. :sleeping:"))
        return

    selected_improvements = ALL_IMPROVEMENTS

    if selected and excluded:
        print(
            emojify(
                ":no_entry_sign: '--select' and '--exclude' options are mutually exclusive!"
            )
        )
        return

    if selected:
        selected_codes = parse_improvement_codes(selected)

        selected_improvements = [
            improvement
            for improvement in ALL_IMPROVEMENTS
            if improvement.CODE in selected_codes
        ]
    elif excluded:
        excluded_codes = parse_improvement_codes(excluded)

        selected_improvements = [
            improvement
            for improvement in ALL_IMPROVEMENTS
            if improvement.CODE not in excluded_codes
        ]

    if not selected_improvements:
        print(emojify(f":sleeping: No improvements to apply."))
        return

    python_files = filter(lambda fn: fn.endswith(".py"), resolve_paths(*paths))

    for path_to_source in python_files:
        with open(path_to_source, "r+") as source_file:
            original_source: str = source_file.read()
            processed_source, applied = process_file(
                original_source, selected_improvements
            )

            if original_source == processed_source:
                continue

            print(f"--> Fixing '{source_file.name}'...")
            for case in applied:
                print(f"  [+] ({case.CODE}) {case.DESCRIPTION}")

            if show_diff:
                print()
                print(
                    "".join(
                        difflib.unified_diff(
                            original_source.splitlines(keepends=True),
                            processed_source.splitlines(keepends=True),
                            fromfile=source_file.name,
                            tofile=source_file.name,
                        )
                    )
                )

            if noop:
                continue

            source_file.seek(0)
            source_file.truncate()
            source_file.write(processed_source)

            print()

    print(emojify(":sparkles: All done! :sparkles:"))
