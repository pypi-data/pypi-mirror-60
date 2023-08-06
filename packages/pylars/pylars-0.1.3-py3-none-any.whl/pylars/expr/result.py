from typing import Set


class Result:
    compatible: bool
    errors: Set[str]

    def __init__(self, compatible: bool, errors: Set[str]):
        self.compatible = compatible
        self.errors = errors


def success():
    return Result(True, set())


def failure(error: str):
    return Result(False, set([error]))


def combine(lhs, rhs):
    return Result(lhs.compatible & rhs.compatible,
                  lhs.errors | rhs.errors)
