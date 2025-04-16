#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Manual Simulated Tempest Example
# GNU Radio version: 3.10.8.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import analog
from gnuradio import blocks
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import filter
from gnuradio import gr
from gnuradio.image_source import *
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore



class manual_simulated_tempest_example(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Manual Simulated Tempest Example", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Manual Simulated Tempest Example")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "manual_simulated_tempest_example")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.refresh_rate = refresh_rate = 60
        self.Vsize = Vsize = 624
        self.Hsize = Hsize = 1024
        self.usrp_rate = usrp_rate = int(30e6)
        self.px_rate = px_rate = Hsize*Vsize*refresh_rate
        self.inter = inter = 10
        self.samp_rate = samp_rate = px_rate*inter
        self.rectangular_pulse = rectangular_pulse = [0.7/255]*inter
        self.noise = noise = 1e-3
        self.lines_offset = lines_offset = (int(Vsize/2))
        self.inverted = inverted = 1
        self.interpolatedHsize = interpolatedHsize = int(Hsize/float(px_rate)*usrp_rate)
        self.horizontal_offset = horizontal_offset = 0
        self.harmonic = harmonic = 1
        self.freq = freq = 0
        self.epsilon_channel = epsilon_channel = 0
        self.decim = decim = inter
        self.Vvisible = Vvisible = 600
        self.Vdisplay = Vdisplay = 768
        self.Hvisible = Hvisible = 800
        self.Hdisplay = Hdisplay = 1024

        ##################################################
        # Blocks
        ##################################################

        self._noise_range = Range(0, 2e-2, 1e-4, 1e-3, 200)
        self._noise_win = RangeWidget(self._noise_range, self.set_noise, "Noise Power", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._noise_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._harmonic_range = Range(1, 10, 1, 1, 200)
        self._harmonic_win = RangeWidget(self._harmonic_range, self.set_harmonic, "Harmonic", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._harmonic_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_range = Range(-1, 1, 1e-5, 0, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, "Frequency Error (normalized)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._freq_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._epsilon_channel_range = Range(-0.1, 0.1, 10e-6, 0, 200)
        self._epsilon_channel_win = RangeWidget(self._epsilon_channel_range, self.set_epsilon_channel, "Sampling error", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._epsilon_channel_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.tempest_image_source_0 = image_source('Imagen_800_600.png', 800, 600, 1024, 624, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=usrp_rate,
                decimation=samp_rate,
                taps=[],
                fractional_bw=0)
        self._lines_offset_range = Range(0, Vsize, 1, (int(Vsize/2)), 200)
        self._lines_offset_win = RangeWidget(self._lines_offset_range, self.set_lines_offset, "Vertical offset", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._lines_offset_win, 3, 1, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._inverted_options = [0, 1]
        # Create the labels list
        self._inverted_labels = ['Yes', 'No']
        # Create the combo box
        # Create the radio buttons
        self._inverted_group_box = Qt.QGroupBox("Inverted colors?" + ": ")
        self._inverted_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._inverted_button_group = variable_chooser_button_group()
        self._inverted_group_box.setLayout(self._inverted_box)
        for i, _label in enumerate(self._inverted_labels):
            radio_button = Qt.QRadioButton(_label)
            self._inverted_box.addWidget(radio_button)
            self._inverted_button_group.addButton(radio_button, i)
        self._inverted_callback = lambda i: Qt.QMetaObject.invokeMethod(self._inverted_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._inverted_options.index(i)))
        self._inverted_callback(self.inverted)
        self._inverted_button_group.buttonClicked[int].connect(
            lambda i: self.set_inverted(self._inverted_options[i]))
        self.top_grid_layout.addWidget(self._inverted_group_box, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_fcc(inter, rectangular_pulse)
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)
        self._horizontal_offset_range = Range(0, interpolatedHsize, 1, 0, 200)
        self._horizontal_offset_win = RangeWidget(self._horizontal_offset_range, self.set_horizontal_offset, "Horizontal offset", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._horizontal_offset_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=noise,
            frequency_offset=freq,
            epsilon=(epsilon_channel+1),
            taps=[1],
            noise_seed=0,
            block_tags=False)
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*1, 'data_single.bin', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, (px_rate*harmonic), 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_throttle_0_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self.blocks_throttle_0_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.tempest_image_source_0, 0), (self.interp_fir_filter_xxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "manual_simulated_tempest_example")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_refresh_rate(self):
        return self.refresh_rate

    def set_refresh_rate(self, refresh_rate):
        self.refresh_rate = refresh_rate
        self.set_px_rate(self.Hsize*self.Vsize*self.refresh_rate)

    def get_Vsize(self):
        return self.Vsize

    def set_Vsize(self, Vsize):
        self.Vsize = Vsize
        self.set_lines_offset((int(self.Vsize/2)))
        self.set_px_rate(self.Hsize*self.Vsize*self.refresh_rate)

    def get_Hsize(self):
        return self.Hsize

    def set_Hsize(self, Hsize):
        self.Hsize = Hsize
        self.set_interpolatedHsize(int(self.Hsize/float(self.px_rate)*self.usrp_rate))
        self.set_px_rate(self.Hsize*self.Vsize*self.refresh_rate)

    def get_usrp_rate(self):
        return self.usrp_rate

    def set_usrp_rate(self, usrp_rate):
        self.usrp_rate = usrp_rate
        self.set_interpolatedHsize(int(self.Hsize/float(self.px_rate)*self.usrp_rate))

    def get_px_rate(self):
        return self.px_rate

    def set_px_rate(self, px_rate):
        self.px_rate = px_rate
        self.set_interpolatedHsize(int(self.Hsize/float(self.px_rate)*self.usrp_rate))
        self.set_samp_rate(self.px_rate*self.inter)
        self.analog_sig_source_x_0.set_frequency((self.px_rate*self.harmonic))

    def get_inter(self):
        return self.inter

    def set_inter(self, inter):
        self.inter = inter
        self.set_decim(self.inter)
        self.set_rectangular_pulse([0.7/255]*self.inter)
        self.set_samp_rate(self.px_rate*self.inter)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.blocks_throttle_0_0.set_sample_rate(self.samp_rate)

    def get_rectangular_pulse(self):
        return self.rectangular_pulse

    def set_rectangular_pulse(self, rectangular_pulse):
        self.rectangular_pulse = rectangular_pulse
        self.interp_fir_filter_xxx_0.set_taps(self.rectangular_pulse)

    def get_noise(self):
        return self.noise

    def set_noise(self, noise):
        self.noise = noise
        self.channels_channel_model_0.set_noise_voltage(self.noise)

    def get_lines_offset(self):
        return self.lines_offset

    def set_lines_offset(self, lines_offset):
        self.lines_offset = lines_offset

    def get_inverted(self):
        return self.inverted

    def set_inverted(self, inverted):
        self.inverted = inverted
        self._inverted_callback(self.inverted)

    def get_interpolatedHsize(self):
        return self.interpolatedHsize

    def set_interpolatedHsize(self, interpolatedHsize):
        self.interpolatedHsize = interpolatedHsize

    def get_horizontal_offset(self):
        return self.horizontal_offset

    def set_horizontal_offset(self, horizontal_offset):
        self.horizontal_offset = horizontal_offset

    def get_harmonic(self):
        return self.harmonic

    def set_harmonic(self, harmonic):
        self.harmonic = harmonic
        self.analog_sig_source_x_0.set_frequency((self.px_rate*self.harmonic))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.channels_channel_model_0.set_frequency_offset(self.freq)

    def get_epsilon_channel(self):
        return self.epsilon_channel

    def set_epsilon_channel(self, epsilon_channel):
        self.epsilon_channel = epsilon_channel
        self.channels_channel_model_0.set_timing_offset((self.epsilon_channel+1))

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim

    def get_Vvisible(self):
        return self.Vvisible

    def set_Vvisible(self, Vvisible):
        self.Vvisible = Vvisible

    def get_Vdisplay(self):
        return self.Vdisplay

    def set_Vdisplay(self, Vdisplay):
        self.Vdisplay = Vdisplay

    def get_Hvisible(self):
        return self.Hvisible

    def set_Hvisible(self, Hvisible):
        self.Hvisible = Hvisible

    def get_Hdisplay(self):
        return self.Hdisplay

    def set_Hdisplay(self, Hdisplay):
        self.Hdisplay = Hdisplay




def main(top_block_cls=manual_simulated_tempest_example, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
