import multiprocessing
from access_pattern import AccessPatternGenerator, FileAccessData
from decay_function import DecayFunctionCalculator


class WeightCalculator(multiprocessing.Process):
    def run(self) -> None:
        pattern_generator = AccessPatternGenerator()
        timestamps = pattern_generator.generate_access_pattern()

        file_data = FileAccessData()
        file_data.add_requests(timestamps)

        grouped_timestamps = file_data.group_timestamps()

        decay_function = DecayFunctionCalculator()
        f = decay_function.compute_decay_factor(grouped_timestamps, 100, 120)
        print("\n")
        print("actual w = ", 100, ", adjusted w = ", f)
