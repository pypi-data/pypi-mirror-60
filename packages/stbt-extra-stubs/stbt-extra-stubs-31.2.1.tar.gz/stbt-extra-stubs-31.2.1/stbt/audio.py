# coding: utf-8

"""Stb-tester APIs for audio capture, analysis, and verification.

Copyright © 2018-2019 Stb-tester.com Ltd.

This file contains API stubs for local installation, to allow IDE linting &
autocompletion. The real implementation of these APIs is not open-source and it
requires the Stb-tester Node hardware.
"""

__all__ = ["AudioChunk",
           "audio_chunks",
           "get_rms_volume",
           "play_audio_file",
           "VolumeChangeDirection",
           "VolumeChangeTimeout",
           "wait_for_volume_change"]

from .premium import (  # pylint:disable=relative-beyond-top-level
    AudioChunk,
    audio_chunks,
    get_rms_volume,
    play_audio_file,
    VolumeChangeDirection,
    VolumeChangeTimeout,
    wait_for_volume_change)
