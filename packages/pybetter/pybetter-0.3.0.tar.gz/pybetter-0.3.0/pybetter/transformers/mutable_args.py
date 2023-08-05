import typing
from typing import Union

from libcst import (
    FunctionDef,
    RemovalSentinel,
    List,
    Name,
    Dict,
    SimpleStatementLine,
    Assign,
    AssignTarget,
    If,
    ComparisonTarget,
    Comparison,
    Is,
    Newline,
    IndentedBlock,
    BaseStatement,
    EmptyLine,
    Parameters,
)

from pybetter.transformers.base import NoqaAwareTransformer


class ArgEmptyInitTransformer(NoqaAwareTransformer):
    def leave_FunctionDef(
        self, original_node: FunctionDef, updated_node: FunctionDef
    ) -> Union[BaseStatement, RemovalSentinel]:
        modified_defaults: typing.List = []
        mutable_args: typing.Dict[Name, Union[List, Dict]] = {}

        for default_param in original_node.params.params:
            if isinstance(default_param.default, (List, Dict)):
                mutable_args[default_param.name] = default_param.default.deep_clone()
                modified_defaults.append(
                    default_param.with_changes(default=Name("None"))
                )
            else:
                modified_defaults.append(default_param)

        modified_params: Parameters = original_node.params.with_changes(
            params=modified_defaults
        )

        initializations: typing.List[If] = [
            If(
                test=Comparison(
                    left=Name(value=arg.value, lpar=[], rpar=[]),
                    comparisons=[
                        ComparisonTarget(
                            operator=Is(),
                            comparator=Name(value="None", lpar=[], rpar=[]),
                        )
                    ],
                ),
                body=IndentedBlock(
                    body=[
                        SimpleStatementLine(
                            body=[
                                Assign(
                                    targets=[
                                        AssignTarget(target=Name(value=arg.value))
                                    ],
                                    value=init,
                                )
                            ]
                        )
                    ],
                    footer=[EmptyLine(newline=Newline(value=None))],
                ),
            )
            for arg, init in mutable_args.items()
        ]

        modified_body = (*initializations, *original_node.body.body)

        return updated_node.with_changes(
            params=modified_params,
            body=original_node.body.with_changes(body=modified_body),
        )
