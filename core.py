import numpy as np
import scipy as sci


def ask(signal_xis, signal_yis, carrier_frequency, ampl0, ampl1):
    new_binary = [(ampl0 if b == 0 else ampl1) for b in signal_yis]
    return np.sin(2 * np.pi * carrier_frequency * signal_xis) * new_binary


def applyNoise(signal, snr):
    # Calculate the power of the signal
    signal_power = np.square(signal).mean()
    # Calculate the noise power based on the desired SNR and signal power
    noise_power = signal_power / (10 ** (snr / 10))
    # Generate the noise with the calculated power
    noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
    return signal + noise


class Core:
    def __init__(self, sampling_frequency, reference_sequence_length, baud_rate, carrier_frequency, time_delay, snr,
                 enable_noise, ampl0, ampl1):
        self.sampling_frequency = sampling_frequency * 1000  # Hz
        self.reference_sequence_length = reference_sequence_length
        self.baud_rate = baud_rate
        self.carrier_frequency = carrier_frequency * 1000  # Hz
        self.time_delay = time_delay / 1000  # seconds
        self.snr = snr
        self.ampl0 = ampl0
        self.ampl1 = ampl1
        self.enable_noise = enable_noise
        # Calculations
        self.target_sequence_length = 2 * reference_sequence_length  # bits
        self.target_signal_duration = self.target_sequence_length / self.baud_rate  # seconds
        self.samples_per_bit = self.sampling_frequency // self.baud_rate
        # Charts
        self.reference_modulation_xis = None
        self.reference_modulation_yis = None
        self.target_signal_xis = None
        self.target_modulation_yis = None
        self.correlation_xis = None
        self.correlation_yis = None
        self.min_delay = None
        self.max_delay = None

    def setSnr(self, snr):
        self.snr = snr

    def process(self):
        # Generate target sequence
        target_sequence = np.random.randint(2, size=self.target_sequence_length)

        # Generate target signal
        self.target_signal_xis = np.arange(0, self.target_signal_duration, 1 / self.sampling_frequency)  # x-samples
        target_signal_yis = [target_sequence[int(np.floor(y * self.baud_rate))] for y in
                             self.target_signal_xis]  # y-samples

        # ASK
        self.target_modulation_yis = ask(self.target_signal_xis, target_signal_yis, self.carrier_frequency, self.ampl0,
                                         self.ampl1)

        # Generate reference signal and offset it
        offset = int(np.rint(self.time_delay * self.sampling_frequency))
        last_index = offset + self.samples_per_bit * self.reference_sequence_length

        if last_index > self.target_signal_xis.size:
            offset = self.target_signal_xis.size - self.samples_per_bit * self.reference_sequence_length  # offset in samples
            print('Too big offset! Use instead:', int((offset / self.sampling_frequency) * 1000))
            # dpg.set_value('time_delay', int((offset / self.sampling_frequency) * 1000))
        self.reference_modulation_xis = self.target_signal_xis[offset:last_index]
        self.reference_modulation_yis = self.target_modulation_yis[offset:last_index]

        # Apply noise
        if self.enable_noise:
            self.target_modulation_yis = applyNoise(self.target_modulation_yis, self.snr)
            self.reference_modulation_yis = applyNoise(self.reference_modulation_yis, 10)

        # Calculate correlation
        self.correlation_yis = sci.signal.correlate(self.target_modulation_yis, self.reference_modulation_yis,
                                                    mode='valid', method='auto')
        self.correlation_xis = [i / self.sampling_frequency for i in np.arange(len(self.correlation_yis))]

        # Find maximum
        self.min_delay = ((self.correlation_yis.argmax() - self.samples_per_bit / 2) / self.sampling_frequency)
        self.max_delay = ((self.correlation_yis.argmax() + self.samples_per_bit / 2) / self.sampling_frequency)

        return self.min_delay < self.time_delay < self.max_delay
