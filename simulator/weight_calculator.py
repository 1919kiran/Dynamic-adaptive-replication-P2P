import multiprocessing
from access_pattern import AccessPatternGenerator
from decay_function import compute_decay_factor


class WeightCalculator(multiprocessing.Process):
    def run(self) -> None:
        pattern_generator = AccessPatternGenerator()
        # pattern = pattern_generator.generate_access_pattern()
        # print(pattern)
        f = compute_decay_factor(10, 0.05, 10)
        print(f)
