import dearpygui.dearpygui as dpg
import numpy as np

dpg.create_context()

def generateSignal():
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


with dpg.window() as main_window:
    with dpg.group(horizontal=True):
        with dpg.child_window(width=300) as setting_child_window:
            dpg.add_text("Sampling Frequency [Hz]:")
            dpg.add_input_int(width=-1, default_value=48000, callback=generateSignal, tag="input_sampling_frequency")
            dpg.add_spacer()
            dpg.add_text("Reference Bits [bits]:")
            dpg.add_input_int(width=-1, default_value=8192, callback=generateSignal, tag="input_reference_bits")
            dpg.add_spacer()
            dpg.add_text("Bandwidth [bits/sec]:")
            dpg.add_input_int(width=-1, default_value=9600, callback=generateSignal, tag="input_bandwidth")
            dpg.add_spacer()
            dpg.add_text("SNR [dB]:")
            dpg.add_input_int(width=-1, default_value=10, callback=generateSignal, tag="input_snr")
            dpg.add_spacer()
            dpg.add_button(label="Generate Signal", width=-1, callback=generateSignal)
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

dpg.create_viewport(title="Viewport Title", width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(main_window, True)
dpg.start_dearpygui()
dpg.destroy_context()
