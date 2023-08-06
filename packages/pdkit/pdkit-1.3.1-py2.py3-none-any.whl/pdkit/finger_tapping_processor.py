#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 Birkbeck College. All rights reserved.
#
# Licensed under the MIT license. See file LICENSE for details.
#
# Author(s): J.S. Pons

import sys
import logging

import numpy as np
import math


class FingerTappingProcessor:
    """
        This is the main Finger Tapping Processor class. Once the data is loaded it will be accessible at \
        data_frame (pandas.DataFrame), where it looks like: data_frame.x, data_frame.y: components of tapping \
        position. data_frame.x_target, data_frame.y_target their target.

        These values are recommended by the author of the pilot study :cite:`Kassavetis2015_2`. Check reference \
        for more details.

        window = 6 #seconds

        :Example:

        >>> import pdkit
        >>> ftp = pdkit.FingerTappingProcessor()
        >>> ts = pdkit.FingerTappingTimeSeries().load(path_to_data, 'ft_cloudupdrs')
        >>> frequency = ftp.frequency(ts)
    """
    def __init__(self, window=6):
        try:
            self.window = window # secs

            logging.debug("TremorProcessor init")

        except IOError as e:
            ierr = "({}): {}".format(e.errno, e.strerror)
            logging.error("TremorProcessor I/O error %s", ierr)

        except ValueError as verr:
            logging.error("TremorProcessor ValueError ->%s", verr.message)

        except:
            logging.error("Unexpected error on TremorProcessor init: %s", sys.exc_info()[0])

    def frequency(self, data_frame):
        """
            This method returns the number of #taps divided by the test duration

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return frequency: frequency
            :rtype frequency: float

        """
        freq = sum(data_frame.action_type == 1) / data_frame.td[-1]
        duration = math.ceil(data_frame.td[-1])

        return freq, duration

    def moving_frequency(self, data_frame):
        """
            This method returns moving frequency

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return diff_mov_freq: frequency
            :rtype diff_mov_freq: float

        """
        f = []
        for i in range(0, (data_frame.td[-1].astype('int') - self.window)):
            f.append(sum(data_frame.action_type[(data_frame.td >= i) & (data_frame.td < (i + self.window))] == 1) /
                     float(self.window))

        diff_mov_freq = (np.array(f[1:-1]) - np.array(f[0:-2])) / np.array(f[0:-2])

        duration = math.ceil(data_frame.td[-1])

        return diff_mov_freq, duration

    def continuous_frequency(self, data_frame):
        """
            This method returns continuous frequency

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return cont_freq: frequency
            :rtype cont_freq: float

        """
        tap_timestamps = data_frame.td[data_frame.action_type==1]
        cont_freq = 1.0/(np.array(tap_timestamps[1:-1])-np.array(tap_timestamps[0:-2]))
        duration = math.ceil(data_frame.td[-1])

        return cont_freq, duration

    def mean_moving_time(self, data_frame):
        """
            This method calculates the mean time (ms) that the hand was moving from one target to the next

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return mmt: the mean moving time in ms
            :rtype mmt: float

        """
        diff = data_frame.td[1:-1].values-data_frame.td[0:-2].values
        mmt = np.mean(diff[np.arange(1,len(diff),2)]) * 1000.0
        duration = math.ceil(data_frame.td[-1])

        return mmt, duration

    def incoordination_score(self, data_frame):
        """
            This method calculates the variance of the time interval in msec between taps

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return is: incoordination score
            :rtype is: float

        """
        diff = data_frame.td[1:-1].values - data_frame.td[0:-2].values
        inc_s = np.var(diff[np.arange(1, len(diff), 2)], dtype=np.float64) * 1000.0
        duration = math.ceil(data_frame.td[-1])
        return inc_s, duration

    def mean_alnt_target_distance(self, data_frame):
        """
            This method calculates the distance (number of pixels) between alternate tapping

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return matd: the mean alternate target distance in pixels
            :rtype matd: float

        """
        dist = np.sqrt((data_frame.x[1:-1].values-data_frame.x[0:-2].values)**2+
                       (data_frame.y[1:-1].values-data_frame.y[0:-2].values)**2)
        matd = np.mean(dist[np.arange(1,len(dist),2)])
        duration = math.ceil(data_frame.td[-1])
        return matd, duration

    def kinesia_scores(self, data_frame):
        """
            This method calculates the number of key taps

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return ks: key taps
            :rtype ks: float
            :return duration: test duration (seconds)
            :rtype duration: float

        """
        # tap_timestamps = data_frame.td[data_frame.action_type == 1]
        # grouped = tap_timestamps.groupby(pd.TimeGrouper('30u'))
        # return np.mean(grouped.size().values)
        ks = sum(data_frame.action_type == 1)
        duration = math.ceil(data_frame.td[-1])
        return ks, duration

    def akinesia_times(self, data_frame):
        """
            This method calculates akinesia times, mean dwell time on each key in milliseconds

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return at: akinesia times
            :rtype at: float
            :return duration: test duration (seconds)
            :rtype duration: float
        """

        raise_timestamps = data_frame.td[data_frame.action_type == 1]
        down_timestamps = data_frame.td[data_frame.action_type == 0]
        if len(raise_timestamps) == len(down_timestamps):
            at = np.mean(down_timestamps.values - raise_timestamps.values)
        else:
            if len(raise_timestamps) > len(down_timestamps):
                at = np.mean(down_timestamps.values - raise_timestamps.values[:-(len(raise_timestamps)
                                                                                 - len(down_timestamps))])
            else:
                at = np.mean(down_timestamps.values[:-(len(down_timestamps)-len(raise_timestamps))]
                             - raise_timestamps.values)
        duration = math.ceil(data_frame.td[-1])
        return np.abs(at), duration

    def dysmetria_score(self, data_frame):
        """
            This method calculates accuracy of target taps in pixels

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return ds: dysmetria score in pixels
            :rtype ds: float

        """
        tap_data = data_frame[data_frame.action_type == 0]
        ds = np.mean(np.sqrt((tap_data.x - tap_data.x_target) ** 2 + (tap_data.y - tap_data.y_target) ** 2))
        duration = math.ceil(data_frame.td[-1])
        return ds, duration

    def extract_features(self, data_frame, pre=''):
        """
            This method extracts all the features available to the Finger Tapping Processor class.

            :param data_frame: the data frame
            :type data_frame: pandas.DataFrame
            :return: 'frequency', 'moving_frequency','continuous_frequency','mean_moving_time','incoordination_score', \
                    'mean_alnt_target_distance','kinesia_scores', 'akinesia_times','dysmetria_score'
            :rtype: list

        """
        try:
            if 'x_target' in data_frame.columns:
                return {pre+'frequency': self.frequency(data_frame)[0],
                        pre+'mean_moving_time': self.mean_moving_time(data_frame)[0],
                        pre+'incoordination_score': self.incoordination_score(data_frame)[0],
                        pre+'mean_alnt_target_distance': self.mean_alnt_target_distance(data_frame)[0],
                        pre+'kinesia_scores': self.kinesia_scores(data_frame)[0],
                        pre+'akinesia_times': self.akinesia_times(data_frame)[0],
                        pre+'dysmetria_score': self.dysmetria_score(data_frame)[0]}
            else:
                return {pre+'frequency': self.frequency(data_frame)[0],
                        pre+'mean_moving_time': self.mean_moving_time(data_frame)[0],
                        pre+'incoordination_score': self.incoordination_score(data_frame)[0],
                        pre+'mean_alnt_target_distance': self.mean_alnt_target_distance(data_frame)[0],
                        pre+'kinesia_scores': self.kinesia_scores(data_frame)[0],
                        pre+'akinesia_times': self.akinesia_times(data_frame)[0]}                
        except:
            logging.error("Error on FingerTappingProcessor process, extract features: %s", sys.exc_info()[0])
