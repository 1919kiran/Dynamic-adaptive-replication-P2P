def compute_decay_factor(initial_freq, decay_rate, time_delta):
    return initial_freq * abs(1 - decay_rate) ** time_delta


