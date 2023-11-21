import dearpygui.dearpygui as dpg
import numpy as np
import scipy as sci


def applyNoise(signal, snr):
    # Calculate the power of the signal
    signal_power = np.square(signal).mean()
    # Calculate the noise power based on the desired SNR and signal power
    noise_power = signal_power / (10 ** (snr / 10))
    # Generate the noise with the calculated power
    noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
    return signal + noise


def ask(signal_xis, signal_yis, carrier_frequency, ampl0, ampl1):
    new_binary = [(ampl0 if b == 0 else ampl1) for b in signal_yis]
    return np.sin(2 * np.pi * carrier_frequency * signal_xis) * new_binary


def process():
    sampling_frequency = dpg.get_value("sampling_frequency") * 1000
    reference_sequence_length = dpg.get_value("reference_sequence_length")
    baud_rate = dpg.get_value("baud_rate")
    carrier_frequency = dpg.get_value("carrier_frequency") * 1000
    time_delay = dpg.get_value("time_delay")
    snr = dpg.get_value("snr")
    target_sequence_length = 2 * reference_sequence_length  # bits
    target_signal_duration = target_sequence_length / baud_rate  # seconds
    samples_per_bit = sampling_frequency // baud_rate

    # Generate target sequence
    target_sequence = np.random.randint(2, size=target_sequence_length)

    # Generate target signal
    target_signal_xis = np.arange(0, target_signal_duration, 1 / sampling_frequency)  # x-samples
    target_signal_yis = [target_sequence[int(np.floor(y * baud_rate))] for y in target_signal_xis]  # y-samples

    # ASK
    ampl0 = dpg.get_value("ampl0")
    ampl1 = dpg.get_value("ampl1")
    target_modulation_yis = ask(target_signal_xis, target_signal_yis, carrier_frequency, ampl0, ampl1)
    offset = int(np.rint((time_delay / 1000) * sampling_frequency))
    reference_modulation_xis = target_signal_xis[offset:offset + samples_per_bit * reference_sequence_length]
    reference_modulation_yis = target_modulation_yis[offset:offset + samples_per_bit * reference_sequence_length]

    # Apply noise
    if dpg.get_value("enable_noise"):
        target_modulation_yis = applyNoise(target_modulation_yis, snr)
        reference_modulation_yis = applyNoise(reference_modulation_yis, 10)

    # Calculate correlation
    correlation_yis = sci.signal.correlate(target_modulation_yis, reference_modulation_yis)
    correlation_xis = np.arange(len(correlation_yis))

    # Update charts
    dpg.set_value("reference_series", [reference_modulation_xis, reference_modulation_yis])
    dpg.fit_axis_data("reference_x_axis")
    dpg.fit_axis_data("reference_y_axis")

    dpg.set_value("target_series_1", [target_signal_xis, target_modulation_yis])
    dpg.set_value("target_series_2", [reference_modulation_xis, reference_modulation_yis])
    dpg.fit_axis_data("target_x_axis")
    dpg.fit_axis_data("target_y_axis")

    dpg.set_value("convolution_series", [correlation_xis, correlation_yis])
    dpg.fit_axis_data("convolution_x_axis")
    dpg.fit_axis_data("convolution_y_axis")


# Window
dpg.create_context()
with dpg.window() as main_window:
    with dpg.group(horizontal=True):
        with dpg.child_window(width=300) as setting_child_window:
            with dpg.collapsing_header(label="Main parameters", default_open=True):
                dpg.add_text('Sampling Frequency [kHz]:')
                dpg.add_input_int(width=-1, default_value=10, tag='sampling_frequency')
                dpg.add_spacer()
                dpg.add_text('Reference Sequence Length [bits]:')
                dpg.add_input_int(width=-1, default_value=128, tag='reference_sequence_length')
                dpg.add_spacer()
                dpg.add_text('Baud Rate [bits/sec]:')
                dpg.add_input_int(width=-1, default_value=500, tag='baud_rate')
                dpg.add_spacer()
                dpg.add_text('Carrier Frequency [kHz]:')
                dpg.add_input_float(width=-1, default_value=0.5, tag='carrier_frequency')
                dpg.add_spacer()
                dpg.add_text('Time Delay [ms]:')
                dpg.add_input_int(width=-1, default_value=100, tag='time_delay')
                dpg.add_spacer()
                dpg.add_text('SNR [dB]:')
                dpg.add_input_int(width=-1, default_value=10, tag='snr')
                dpg.add_checkbox(label="Enable Noise", tag="enable_noise", default_value=True)
                dpg.add_spacer()

            with dpg.collapsing_header(label="Modulation parameters"):
                dpg.add_text('Modulation mode:')
                dpg.add_radio_button(items=['ASK', 'FSK', 'CPFSK', 'BPSK'], default_value='ASK', tag='modulation_mode')
                dpg.add_spacer()
                dpg.add_text('Amplitude 0 [dB]:')
                dpg.add_input_float(width=-1, default_value=0.1, tag='ampl0')
                dpg.add_spacer()
                dpg.add_text('Amplitude 1 [dB]:')
                dpg.add_input_float(width=-1, default_value=1.0, tag='ampl1')
                dpg.add_spacer()
                dpg.add_text('Carrier Frequency Offset [kHz]:')
                dpg.add_input_float(width=-1, default_value=0.05, tag='carrier_frequency_offset')

            dpg.add_button(label="Generate Signal", width=-1, callback=process)

        with dpg.tab_bar():
            with dpg.tab(label="Main", tag="main_tab"):
                with dpg.child_window(tag="plot_window", border=False) as plot_child_window:
                    with dpg.subplots(rows=3, columns=1, no_title=True, width=-1, height=-1):
                        with dpg.plot(label="Reference Signal", anti_aliased=True):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="time [ms]", tag="reference_x_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="reference_y_axis")
                            dpg.add_line_series([], [], parent="reference_y_axis", tag="reference_series",
                                                label='reference')

                        with dpg.plot(label="Target/Reference Signal", anti_aliased=True):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="time [ms]", tag="target_x_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="target_y_axis")
                            dpg.add_line_series([], [], parent="target_y_axis", tag="target_series_1", label='target')
                            dpg.add_line_series([], [], parent="target_y_axis", tag="target_series_2",
                                                label='reference')

                        with dpg.plot(label="Convolution", anti_aliased=True):
                            dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="convolution_x_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="convolution_y_axis")
                            dpg.add_line_series([], [], parent="convolution_y_axis", tag="convolution_series")

            with dpg.tab(label="Research", tag="research_tab"):
                with dpg.child_window(tag="research_window", border=False):
                    with dpg.subplots(rows=1, columns=1, no_title=True, width=-1, height=-1):
                        with dpg.plot(label="Target Signal", anti_aliased=True):
                            dpg.add_plot_axis(dpg.mvXAxis, label="time [ms]", tag="research_x_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="research_y_axis")
                            dpg.add_line_series([], [], parent="target_y_axis", tag="research_series")

dpg.create_viewport(title="Viewport Title", width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(main_window, True)
dpg.start_dearpygui()
dpg.destroy_context()
