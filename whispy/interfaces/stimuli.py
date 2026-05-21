from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from whispy.utils import read_config

import pyfar as pf
import sounddevice as sd
import os

# Directory containing this file.
# Required for loading the default configs
FILEPATH = os.path.dirname(os.path.abspath(__file__))


class StimuliHandler(ABC):
    """Abstract base class for all StimuliHandler."""
    @abstractmethod
    def play(self, stimulus: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self, stimulus: Optional[str] = None) -> None:
        raise NotImplementedError


class SounddeviceHandler(StimuliHandler):

    def __init__(self, stimuli=None, base_dir=None, loop=True):
        """Initialize the sounddevice backend and load configured stimuli.

        Parameters
        ----------
        stimuli : str or None, optional
            Path to the stimuli configuration file. If ``None``, the default
            ``configs/stimuli_sounddevice.yml`` from this package is used.
        base_dir : str or None, optional
            Base directory containing the audio files referenced in the stimuli
            configuration. If ``None``, the default ``stimuli`` directory
            of this package is used.
        loop : bool, optional
            If ``True``, playback loops continuously.

        Raises
        ------
        ValueError
            If loaded stimuli do not share the same sampling rate.
        """

        # load config file
        if stimuli is None:
            stimuli = os.path.join(
                FILEPATH, '..', '..', 'configs', 'stimuli.yml')

        self.stimuli = read_config(stimuli)

        if 'SounddeviceHandler' not in self.stimuli:
            raise ValueError("Stimuli are not defined for SounddeviceHandler")

        self.stimuli = self.stimuli["SounddeviceHandler"]

        # parse base directory containing audio stimuli
        if base_dir is None:
            base_dir = os.path.join(FILEPATH, '..', '..', 'stimuli')

        # load and check audio files
        self.sampling_rate = None

        for s_id in self.stimuli.keys():

            signal = pf.io.read_audio(os.path.join(
                base_dir, self.stimuli[s_id]["file"]))

            if self.sampling_rate is None:
                self.sampling_rate = signal.sampling_rate
            elif signal.sampling_rate != self.sampling_rate:
                raise ValueError(
                    "All stimuli must have the same sampling rate")

            self.stimuli[s_id]["signal"] = signal

        # sounddevice settings
        sd.default.samplerate = self.sampling_rate
        self.loop = loop

    def play(self, stimulus: str) -> None:
        """
        Play stimulus.

        Parameters
        ----------
        stimulus : str
            The name of the stimulus as defined in the stimuli configuration
        """
        sd.stop()
        sd.play(self.stimuli[stimulus]['signal'].time.T, loop=self.loop)

    def stop(self, stimulus: str | None = None) -> None:
        """
        Stop playback.

        Parameters
        ----------
        stimulus : str
            The name of the stimulus as defined in the stimuli configuration
        """
        # NOTE: `stimulus` is not required here to stop the playback. But
        #       it might be required by other handlers that must share the same
        #       call signature.
        sd.stop()
