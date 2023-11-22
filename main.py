import dearpygui.dearpygui as dpg
import numpy as np
import scipy as sci
import time
import collections
import threading

from core import Core


def research():
    sampling_frequency = dpg.get_value("sampling_frequency")
    reference_sequence_length = dpg.get_value("reference_sequence_length")
    baud_rate = dpg.get_value("baud_rate")
    carrier_frequency = dpg.get_value("carrier_frequency")
    time_delay = dpg.get_value("time_delay")
    ampl0 = dpg.get_value("ampl0")
    ampl1 = dpg.get_value("ampl1")
    enable_noise = dpg.get_value("enable_noise")

    print('sampling_frequency:', sampling_frequency)
    print('reference_sequence_length:', reference_sequence_length)
    print('baud_rate:', baud_rate)
    print('carrier_frequency:', carrier_frequency)
    print('time_delay:', time_delay)
    print('ampl0:', ampl0)
    print('ampl1:', ampl1)
    print('enable_noise:', enable_noise)

    core = Core(sampling_frequency, reference_sequence_length, baud_rate, carrier_frequency, time_delay, 0,
                enable_noise, ampl0, ampl1)

    n = 100
    data_x = []
    data_y = []
    for snr in np.linspace(-20, 10, 50):
        print('snr:', snr)
        core.setSnr(snr)
        counter = 0
        for i in range(n):
            if core.process():
                counter += 1
        data_x.append(snr)
        y = counter / n
        data_y.append(y)
        dpg.set_value('research_series', [np.array(data_x), np.array(data_y)])
        dpg.fit_axis_data('research_x_axis')
        dpg.fit_axis_data('research_y_axis')


def research_start():
    thread = threading.Thread(target=research)
    thread.start()
    dpg.set_value('tab_bar', 'research_tab')


def process():
    sampling_frequency = dpg.get_value("sampling_frequency")
    reference_sequence_length = dpg.get_value("reference_sequence_length")
    baud_rate = dpg.get_value("baud_rate")
    carrier_frequency = dpg.get_value("carrier_frequency")
    time_delay = dpg.get_value("time_delay")
    snr = dpg.get_value("snr")
    ampl0 = dpg.get_value("ampl0")
    ampl1 = dpg.get_value("ampl1")
    enable_noise = dpg.get_value("enable_noise")

    core = Core(sampling_frequency, reference_sequence_length, baud_rate, carrier_frequency, time_delay, snr,
                enable_noise, ampl0, ampl1)
    core.process()

    # Draw drag lines
    dpg.set_value('convolution_dline1', core.min_delay)
    dpg.set_value('convolution_dline2', core.max_delay)

    # Update charts
    dpg.set_value("reference_series", [core.reference_modulation_xis, core.reference_modulation_yis])
    dpg.fit_axis_data("reference_x_axis")
    dpg.fit_axis_data("reference_y_axis")

    dpg.set_value("target_series_1", [core.target_signal_xis, core.target_modulation_yis])
    dpg.set_value("target_series_2", [core.reference_modulation_xis, core.reference_modulation_yis])
    dpg.fit_axis_data("target_x_axis")
    dpg.fit_axis_data("target_y_axis")

    dpg.set_value("convolution_series", [core.correlation_xis, core.correlation_yis])
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
                dpg.add_input_float(width=-1, default_value=0.5, tag='ampl0')
                dpg.add_spacer()
                dpg.add_text('Amplitude 1 [dB]:')
                dpg.add_input_float(width=-1, default_value=1.0, tag='ampl1')
                dpg.add_spacer()
                dpg.add_text('Carrier Frequency Offset [kHz]:')
                dpg.add_input_float(width=-1, default_value=0.05, tag='carrier_frequency_offset')

            dpg.add_button(label="Generate Signal", width=-1, callback=process)
            dpg.add_button(label="Start Research", width=-1, callback=research_start)

        with dpg.tab_bar(tag='tab_bar'):
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

                        with dpg.plot(label="Convolution", anti_aliased=True) as plot:
                            dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="convolution_x_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="convolution_y_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="foo", tag="foobar", )
                            dpg.add_line_series([], [], parent="convolution_y_axis", tag="convolution_series")
                            dpg.add_drag_line(label="min", color=[255, 0, 0, 255], tag='convolution_dline1')
                            dpg.add_drag_line(label="max", color=[255, 0, 0, 255], tag='convolution_dline2')

            with dpg.tab(label="Research", tag="research_tab"):
                with dpg.child_window(tag="research_window", border=False):
                    with dpg.subplots(rows=1, columns=1, no_title=True, width=-1, height=-1):
                        with dpg.plot(label="Target Signal", anti_aliased=True):
                            dpg.add_plot_axis(dpg.mvXAxis, label="time [ms]", tag="research_x_axis")
                            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="research_y_axis")
                            dpg.add_line_series([], [], parent="research_y_axis", tag="research_series")
                            dpg.add_error_series([], [], [], [], parent="research_y_axis", tag="research_series_error")

dpg.create_viewport(title="Viewport Title", width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(main_window, True)
dpg.start_dearpygui()
dpg.destroy_context()
