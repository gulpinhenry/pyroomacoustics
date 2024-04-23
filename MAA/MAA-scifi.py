"""
This example creates a free-field simulation of direction of arrival estimation.
"""

import argparse
import os
from pathlib import Path
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

import pyroomacoustics as pra

azimuth_true = -np.pi / 6

plus_minus = np.pi/60
ear = 0.01
camera = [1.5, 2, 3]

def convertStereotoMono(stereoAudio):
    #make monoAudio ndarray
    monoAudio = np.zeros(len(stereoAudio))
    #convert stereo to mono
    for i in range(len(stereoAudio)):
        monoAudio[i] = (stereoAudio[i][0] + stereoAudio[i][1]) // 2
    return monoAudio

fs, audio_clock = wavfile.read("audio/clock.wav")
# audio_clock = convertStereotoMono(audio_clock)
fs, audio_bark = wavfile.read("audio/barkPCM.wav")
audio_bark = convertStereotoMono(audio_bark)
filename="./MAA/output.wav"




if __name__ == "__main__":
    scaling = 1
    distance = 0.75
    floor = np.array([[5.25, -5.5, -5.5, -1.75, -1.75, -5.75, -5.75, 5.25],[0, 0, 3.5, 3.5, 7.25, 7.25, 10.75, 10.75]])
    room = pra.Room.from_corners(floor, fs=fs, materials=pra.Material(energy_absorption=0.2, scattering=0.1))
    room.extrude(3.75)
    
    print([camera[0] + distance * scaling * np.sin(azimuth_true + plus_minus) , camera[1], camera[2] + distance * scaling * np.cos(azimuth_true + plus_minus)],
          [camera[0] + distance * scaling * np.sin(azimuth_true - plus_minus) , camera[1], camera[2] + distance * scaling * np.cos(azimuth_true - plus_minus)])
    
    # Note: y and z seemed to be swapped in pyroomacoustics
    room.add_source([camera[0] + distance * scaling * np.sin(azimuth_true + plus_minus) , camera[1], camera[2] + distance * scaling * np.cos(azimuth_true + plus_minus)], signal=audio_clock, delay=0.5)
    room.add_source([camera[0] + distance * scaling * np.sin(azimuth_true - plus_minus) , camera[1], camera[2] + distance * scaling * np.cos(azimuth_true - plus_minus)], signal=audio_bark, delay=0.5)
    # room.add_source([camera[0] + 2 * scaling * np.sin(azimuth_true + plus_minus) , camera[1] + 2 * scaling * np.cos(azimuth_true + plus_minus), camera[2]], signal=audio_clock, delay=0.5)
    # room.add_source([camera[0] + 2 * scaling * np.sin(azimuth_true - plus_minus) , camera[1] + 2 * scaling * np.cos(azimuth_true - plus_minus), camera[2]], signal=audio_bark, delay=0.5)
    
    
    room.add_microphone([camera[0] + ear, camera[1], camera[2]])
    room.add_microphone([camera[0] - ear, camera[1], camera[2]])
    # room.set_ray_tracing()
    # run the simulation
    room.simulate()
    print(room.mic_array)
    room.mic_array.to_wav(
        filename,
        norm=True,
        bitdepth=np.int16,
    )
    # room.image_source_model()
    # room.ray_tracing()
    s = time.perf_counter()
    room.compute_rir()
    print("Computation time:", time.perf_counter() - s)

    room.plot_rir()

    room.plot(img_order=1)
    
    plt.show()
