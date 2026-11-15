"""In-place Quicksort for lists whose elements have a consistent total order."""

import argparse
from random import Random
from typing import TypeVar

T = TypeVar("T")


def _partition(values: list[T], low: int, high: int, pivot_index: int) -> tuple[int, int]:
    """Return the inclusive bounds of the group equal to the chosen pivot."""
    pivot = values[pivot_index]
    # Set the pivot aside at high so neither scan moves it. In the report's
    # example, [4, 1, 3, 2, 5, 3], the last 3 is already in that slot.
    values[pivot_index], values[high] = values[high], values[pivot_index]

    # first_equal marks the next slot for a key smaller than the pivot.
    first_equal = low
    for index in range(low, high):
        if values[index] < pivot:
            # In the example, 1 swaps with 4. Later, 2 swaps with that same
            # 4 in its new slot. The list is now [1, 2, 3, 4, 5, 3].
            values[first_equal], values[index] = values[index], values[first_equal]
            first_equal += 1

    # Start the second scan where the smaller keys end. Every remaining
    # key is at least the pivot, so if pivot < key is false, the keys tie.
    last_equal = first_equal
    for index in range(first_equal, high):
        if not pivot < values[index]:
            # The other 3 is already at index 2. It swaps with itself,
            # but last_equal still advances to 3 to record that tie.
            values[last_equal], values[index] = values[index], values[last_equal]
            last_equal += 1
    # Place the saved pivot just after the ties. Here it swaps with 4 at
    # index 3, leaving [1, 2, 3, 3, 5, 4].
    values[last_equal], values[high] = values[high], values[last_equal]
    # Both bounds are inclusive. Returning (2, 3) lets the caller skip both 3s.
    return first_equal, last_equal


def _sort(values: list[T], low: int, high: int, rng: Random | None) -> None:
    """Recurse on the smaller strict side and handle the larger side in this frame."""
    # An empty or one-key range needs no partition. This also stops the loop
    # when a partition of identical keys consumes the entire active range.
    while low < high:
        # The fixed rule uses the last slot. For a random pivot, high + 1
        # lets randrange choose that slot too, since its stop is exclusive.
        pivot_index = high if rng is None else rng.randrange(low, high + 1)
        first_equal, last_equal = _partition(values, low, high, pivot_index)
        # Compare the lengths on either side of the ties. The recursive
        # call takes at most half the range. The loop handles the rest.
        if first_equal - low < high - last_equal:
            if low + 1 < first_equal:
                _sort(values, low, first_equal - 1, rng)
            # The left side is sorted. Continue the loop on the right side.
            low = last_equal + 1
        else:
            # The example has two keys on each side, so this branch runs.
            # On the right, pivot 4 turns [5, 4] into [4, 5].
            if last_equal + 1 < high:
                _sort(values, last_equal + 1, high, rng)
            # Resume on the left. In [1, 2], 1 is already below pivot 2,
            # so this final partition leaves the list [1, 2, 3, 3, 4, 5].
            high = first_equal - 1


def deterministic_quicksort(values: list[T]) -> None:
    """Sort in place using the last key as pivot. Return None. Ties may reorder."""
    _sort(values, 0, len(values) - 1, None)


def randomized_quicksort(values: list[T], rng: Random | None = None) -> None:
    """Sort in place using uniform pivot indices. Pass a seeded generator to replay."""
    # Pass one generator through the whole sort so successive partitions
    # advance the same sequence of pivot draws.
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
