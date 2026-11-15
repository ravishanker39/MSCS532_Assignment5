"""In-place Quicksort for lists whose elements have a consistent total order."""

import argparse
from random import Random
from typing import TypeVar

T = TypeVar("T")


def _partition(values: list[T], low: int, high: int, pivot_index: int) -> tuple[int, int]:
    """Return the inclusive bounds of the group equal to the chosen pivot."""
    pivot = values[pivot_index]
    values[pivot_index], values[high] = values[high], values[pivot_index]

    # First collect keys strictly smaller than the pivot at the front.
    first_equal = low
    for index in range(low, high):
        if values[index] < pivot:
            values[first_equal], values[index] = values[index], values[first_equal]
            first_equal += 1

    # Remaining keys are at least the pivot; this pass groups the ties.
    last_equal = first_equal
    for index in range(first_equal, high):
        if not pivot < values[index]:
            values[last_equal], values[index] = values[index], values[last_equal]
            last_equal += 1
    values[last_equal], values[high] = values[high], values[last_equal]
    return first_equal, last_equal


def _sort(values: list[T], low: int, high: int, rng: Random | None) -> None:
    """Recurse on the smaller strict side and handle the larger side in this frame."""
    while low < high:
        pivot_index = high if rng is None else rng.randrange(low, high + 1)
        first_equal, last_equal = _partition(values, low, high, pivot_index)
        if first_equal - low < high - last_equal:
            if low + 1 < first_equal:
                _sort(values, low, first_equal - 1, rng)
            low = last_equal + 1
        else:
            if last_equal + 1 < high:
                _sort(values, last_equal + 1, high, rng)
            high = first_equal - 1


def deterministic_quicksort(values: list[T]) -> None:
    """Sort in place using the last key as pivot. Return None. Ties may reorder."""
    _sort(values, 0, len(values) - 1, None)


def randomized_quicksort(values: list[T], rng: Random | None = None) -> None:
    """Sort in place using uniform pivot indices. Pass a seeded generator to replay."""
    generator = Random() if rng is None else rng
    _sort(values, 0, len(values) - 1, generator)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("values", nargs="*", type=int, help="integers to sort")
    parser.add_argument("--pivot", choices=("last", "random"), default="last")
    parser.add_argument("--seed", type=int, help="random pivot seed")
    args = parser.parse_args()
    if args.pivot == "last":
        deterministic_quicksort(args.values)
    else:
        randomized_quicksort(args.values, Random(args.seed))
    print(args.values)


if __name__ == "__main__":
    main()
