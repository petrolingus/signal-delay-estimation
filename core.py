import numpy as np
import scipy as sci
import time


def ask(signal_xis, signal_yis, carrier_frequency, ampl0, ampl1, is_research, ask_carr):
    new_binary = [(ampl0 if b == 0 else ampl1) for b in signal_yis]
    if is_research:
        return ask_carr * new_binary
    else:
        return np.sin(2 * np.pi * carrier_frequency * signal_xis) * new_binary


def fsk(signal_xis, signal_yis, carrier_frequency: float, mod_amp: float):
    df = 0.5 * mod_amp * carrier_frequency
    f = np.choose(np.array(signal_yis), [np.repeat(carrier_frequency - df, np.array(signal_yis).size),
                                         np.repeat(carrier_frequency + df, np.array(signal_yis).size)])
    phase = np.cumsum(2 * np.pi * f * np.array(signal_xis))
    return np.sin(phase)


def psk(signal_xis, signal_yis, carrier_frequency):
    phase = 2 * np.pi * carrier_frequency * signal_xis + np.pi * np.array(signal_yis)
    return np.sin(phase)


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
                 enable_noise, modulation_mode, ampl0, ampl1, carrier_frequency_offset):
        self.sampling_frequency = sampling_frequency * 1000  # Hz
        self.reference_sequence_length = reference_sequence_length
        self.baud_rate = baud_rate
        self.carrier_frequency = carrier_frequency * 1000  # Hz
        self.time_delay = time_delay / 1000  # seconds
        self.snr = snr
        self.enable_noise = enable_noise
        if modulation_mode == 'ASK':
            self.modulation_mode = 0
        elif modulation_mode == 'FSK':
            self.modulation_mode = 1
        else:
            self.modulation_mode = 2

        self.carrier_frequency_offset = carrier_frequency_offset
        self.ampl0 = ampl0
        self.ampl1 = ampl1
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
        # Research
        self.is_research = None
        self.ask_carr = None

    def enableResearch(self):
        self.target_signal_xis = np.arange(0, self.target_signal_duration, 1 / self.sampling_frequency)
        self.ask_carr = np.sin(2 * np.pi * self.carrier_frequency * self.target_signal_xis)
        self.is_research = True

    def setSnr(self, snr):
        self.snr = snr

    def process(self):

        # start1 = time.time()

        # Generate target sequence
        target_sequence = np.random.randint(2, size=self.target_sequence_length)

        # Generate target signal
        if not self.is_research:
            self.target_signal_xis = np.arange(0, self.target_signal_duration, 1 / self.sampling_frequency)  # x
        target_signal_yis = [target_sequence[int(np.floor(y * self.baud_rate))] for y in self.target_signal_xis]  # y

        if self.modulation_mode == 0:
            self.target_modulation_yis = ask(self.target_signal_xis, target_signal_yis, self.carrier_frequency,
                                             self.ampl0, self.ampl1, self.is_research, self.ask_carr)
        elif self.modulation_mode == 1:
            self.target_modulation_yis = fsk(self.target_signal_xis, target_signal_yis, self.carrier_frequency, 1)
        else:
            self.target_modulation_yis = psk(self.target_signal_xis, target_signal_yis, self.carrier_frequency)

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
                                                    mode='valid', method='fft')
        self.correlation_xis = [i / self.sampling_frequency for i in np.arange(len(self.correlation_yis))]

        # Find maximum
        max_index = self.correlation_yis.argmax()
        self.min_delay = ((max_index - self.samples_per_bit / 2) / self.sampling_frequency)
        self.max_delay = ((max_index + self.samples_per_bit / 2) / self.sampling_frequency)

        # end1 = time.time()
        # print("Generate target sequence:", (end1 - start1))

        return self.min_delay < self.time_delay < self.max_delay
