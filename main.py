import dearpygui.dearpygui as dpg
import numpy as np

from binary_signal import getBinarySignal


# Params
# sampling_frequency = 2150
# reference_sequence_length = 50
# bandwidth = 96
# carrier_frequency = 96

# Calculated params
# target_sequence_length = 2 * reference_sequence_length  # bits
# target_signal_duration = target_sequence_length / bandwidth  # seconds
# # TODO: delete this as far as possible
# samples_per_bit = sampling_frequency // bandwidth
# # reference_signal_length = reference_sequence_length * samples_per_bit
# target_signal_length = target_sequence_length * samples_per_bit

# ALGORITHM ############################################################################################################


# Generate target signal
# target_signal_xis = np.arange(0, target_signal_duration, 1 / sampling_frequency)  # x-samples
# target_signal_yis = [target_sequence[int(np.floor(y * bandwidth))] for y in target_signal_xis]  # y-samples
# print("target_samples:", len(target_signal_xis))

# TODO: delete this
# Generate target signal 2
# target_signal_xis = np.array([i / sampling_frequency for i in range(target_signal_length)])
# target_signal_yis = getBinarySignal(target_sequence, target_sequence_length, samples_per_bit)
# print("target_samples_2: ", len(target_signal_xis))

# Generate ASK
# ampl0 = 0.1
# ampl1 = 1.0
# carrier_signal = np.sin(2 * np.pi * carrier_frequency * target_signal_xis)
# new_binary = [(ampl0 if b == 0 else ampl1) for b in target_signal_yis]
# ask_signal = carrier_signal * new_binary


def process():
    reference_sequence_length = dpg.get_value("reference_sequence_length")
    target_sequence_length = 2 * reference_sequence_length

    # Generate target sequence
    target_sequence = np.random.randint(2, size=target_sequence_length)

    # sampling_frequency = dpg.get_value("input_sampling_frequency")
    # reference_bits = dpg.get_value("input_reference_bits")
    # bandwidth = dpg.get_value("input_bandwidth")
    # snr = dpg.get_value("input_snr")
    # core.init(sampling_frequency, reference_bits, bandwidth, snr)
    #
    # # Update target chart
    # dpg.set_value("target_series", [core.target_samples, core.target_ask_signal])
    # dpg.fit_axis_data("target_x_axis")
    # dpg.fit_axis_data("target_y_axis")
    #
    # # Update reference chart
    # dpg.set_value("reference_series", [core.reference_samples, core.reference_ask_signal])
    # dpg.fit_axis_data("reference_x_axis")
    # dpg.fit_axis_data("reference_y_axis")
    #
    # # Update convolution chart
    # y = core.ask_correlation
    # dpg.set_value("convolution_series", [np.arange(len(core.ask_correlation)), y])
    # dpg.fit_axis_data("convolution_x_axis")
    # # dpg.fit_axis_data("convolution_y_axis")
    # dpg.set_axis_limits("convolution_y_axis", ymin=0, ymax=np.max(y))
    pass


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
                dpg.add_input_int(width=-1, default_value=0, tag='time_delay')
                dpg.add_spacer()
                dpg.add_text('SNR [dB]:')
                dpg.add_input_int(width=-1, default_value=10, tag='snr')
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

            dpg.add_button(label="Generate Signal", width=-1)

        with dpg.tab_bar():
            with dpg.tab(label="Main", tag="main_tab"):
                with dpg.child_window(tag="plot_window", border=False) as plot_child_window:
                    with dpg.subplots(rows=3, columns=1, no_title=True, width=-1, height=-1):
                        with dpg.plot(label="Target Signal", anti_aliased=True):
                            dpg.add_plot_axis(dpg.mvXAxis, label="time [ms]", tag="target_x_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="target_y_axis")
                            dpg.add_line_series([], [], parent="target_y_axis", tag="target_series")

                        with dpg.plot(label="Reference Signal", anti_aliased=True):
                            dpg.add_plot_axis(dpg.mvXAxis, label="time [ms]", tag="reference_x_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="reference_y_axis")
                            dpg.add_line_series([], [], parent="reference_y_axis", tag="reference_series")

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
