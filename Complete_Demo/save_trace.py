#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.9.2

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
from gnuradio import uhd
from helpers import bcolors

class trace_to_file(gr.top_block):
    def __init__(self, filename: str, center_freq: int, verbose = False, sdr = 'hackrf'):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 10e6
        self.freq = freq = center_freq

        ##################################################
        # Blocks
        ##################################################
        if sdr == 'hackrf':
            self.osmosdr_source_0 = osmosdr.source(
                args="numchan=" + str(1) + " " + "hackrf=0"
            )
            self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
            self.osmosdr_source_0.set_sample_rate(samp_rate)
            self.osmosdr_source_0.set_center_freq(freq, 0)
            self.osmosdr_source_0.set_freq_corr(0, 0)
            self.osmosdr_source_0.set_dc_offset_mode(0, 0)
            self.osmosdr_source_0.set_iq_balance_mode(0, 0)
            self.osmosdr_source_0.set_gain_mode(False, 0)
            self.osmosdr_source_0.set_gain(10, 0)
            self.osmosdr_source_0.set_if_gain(20, 0)
            self.osmosdr_source_0.set_bb_gain(20, 0)
            self.osmosdr_source_0.set_antenna("", 0)
            self.osmosdr_source_0.set_bandwidth(0, 0)
        elif sdr == 'usrp':
            self.osmosdr_source_0 = uhd.usrp_source(
            ",".join(("addr=148.60.6.48", "")),
            uhd.stream_args(
                    cpu_format="fc32",
                    args="",
                    channels=list(range(0, 1)),
                ),
            )
            self.osmosdr_source_0.set_samp_rate(samp_rate)
            self.osmosdr_source_0.set_center_freq(freq, 0)
            self.osmosdr_source_0.set_antenna("RX2", 0)
            self.osmosdr_source_0.set_gain(0, 0)

        
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*1, filename, False)
        self.blocks_file_sink_0.set_unbuffered(False)

        self.blocks_correctiq_0 = blocks.correctiq()
        
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.blocks_correctiq_0, 0))
        self.connect((self.blocks_correctiq_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_file_sink_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)


