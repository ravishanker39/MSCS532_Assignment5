"""Correctness, partition boundaries, pivot selection and stack regressions."""

import itertools
import random
import unittest

from quicksort import _partition, deterministic_quicksort, randomized_quicksort


class QuicksortTests(unittest.TestCase):
    def check_both(self, original):
        for sorter in (deterministic_quicksort, randomized_quicksort):
            with self.subTest(sorter=sorter.__name__, size=len(original)):
                values = original.copy()
                if sorter is randomized_quicksort:
                    result = sorter(values, random.Random(41))
                else:
                    result = sorter(values)
                self.assertIsNone(result)
                self.assertEqual(values, sorted(original))

    def test_empty_and_singleton(self):
        for values in ([], [42]):
            self.check_both(values)

    def test_exhaustive_small_lists(self):
        for size in range(7):
            for keys in itertools.product((-1, 0, 1), repeat=size):
                self.check_both(list(keys))

    def test_ordered_above_typical_recursion_limit(self):
        # The last pivot produces extreme splits here. A recursive call on
        # the large side each time would exhaust a typical Python call stack.
        self.check_both(list(range(1500)))
        self.check_both(list(range(1500, 0, -1)))

    def test_all_equal_and_skewed_duplicates(self):
        self.check_both([7] * 5000)
        self.check_both([7] * 2000 + [-10, 20, 7, 9, 20])

    def test_comparable_nonnumeric_keys(self):
        self.check_both(["beta", "", "alpha", "beta", "z"])

    def test_random_permutations(self):
        for seed in range(20):
            values = list(range(200))
            random.Random(seed).shuffle(values)
            self.check_both(values)

    def test_partition_leaves_neighbors_intact(self):
        for pivot_index in range(1, 7):
            values = [99, 4, 1, 4, 0, 8, 4, -99]
            original = values.copy()
            pivot = original[pivot_index]
            first, last = _partition(values, 1, 6, pivot_index)
            # Check the untouched outer slots first, then verify that the six
            # inner keys survived and fall into the smaller, equal and larger groups.
            self.assertEqual((values[0], values[-1]), (99, -99))
            self.assertCountEqual(values[1:7], original[1:7])
            self.assertTrue(all(x < pivot for x in values[1:first]))
            self.assertEqual(values[first:last + 1], [pivot] * original[1:7].count(pivot))
            self.assertTrue(all(x > pivot for x in values[last + 1:7]))

    def test_reproducible_draws_within_each_subarray(self):
        class TracedRandom(random.Random):
            def __init__(self, seed):
                super().__init__(seed)
                self.draws = []

            def randrange(self, start, stop):
                choice = super().randrange(start, stop)
                self.draws.append((start, stop, choice))
                return choice

        traces = []
        # Sorted output alone cannot show which pivots were chosen. Compare
        # the recorded draws from two identical seeds and one different seed.
        for seed in (19, 19, 20):
            rng = TracedRandom(seed)
            values = list(range(64))
            randomized_quicksort(values, rng)
            self.assertEqual(values, list(range(64)))
            self.assertTrue(all(0 <= a <= i < b <= 64 for a, b, i in rng.draws))
            self.assertTrue(any(b - a < 64 for a, b, i in rng.draws))
            traces.append(rng.draws)
        self.assertEqual(traces[0], traces[1])
        self.assertNotEqual(traces[0], traces[2])


if __name__ == "__main__":
    unittest.main()
