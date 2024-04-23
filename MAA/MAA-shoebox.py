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

try:
    from stl import mesh
except ImportError as err:
    print(
        "The numpy-stl package is required for this example. "
        "Install it with `pip install numpy-stl`"
    )
    raise err

default_stl_path = Path(__file__).parent / "3dpea.stl"
azimuth_true = -np.pi / 6

plus_minus = np.pi/60
# camera = [0, 1, 0]
camera = [0, 0.0001, 0] # fixed at zero for now
ear = 0.01

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
    parser = argparse.ArgumentParser(description="Basic room from STL file example")
    parser.add_argument(
        "--file", type=str, default=default_stl_path, help="Path to STL file"
    )
    args = parser.parse_args()


    material = pra.Material(energy_absorption=0.2, scattering=0.1)
    the_mesh = mesh.Mesh.from_file(args.file)
    ntriang, nvec, npts = the_mesh.vectors.shape
    scaling = 1
    print(ntriang, nvec, npts)

    walls = []
    for w in range(ntriang):
        walls.append(
            pra.wall_factory(
                the_mesh.vectors[w].T * scaling,
                material.energy_absorption["coeffs"],
                material.scattering["coeffs"],
            )
        )
    # print([walls[i].corners for i in range(len(walls))])
    room = (
        pra.Room(
            walls,
            fs=16000,
            max_order=3,
            ray_tracing=True,
            air_absorption=True,
        )
    )

    room.plot(img_order=1)


    # Note: y and z seemed to be swapped in pyroomacoustics
    room.add_source([camera[0] + 2 * scaling * np.sin(azimuth_true + plus_minus) , camera[1], camera[2] + 2 * scaling * np.cos(azimuth_true + plus_minus)], signal=audio_clock, delay=0.5)
    room.add_source([camera[0] + 2 * scaling * np.sin(azimuth_true - plus_minus) , camera[1], camera[2] + 2 * scaling * np.cos(azimuth_true - plus_minus)], signal=audio_bark, delay=0.5)
    # room.add_source([camera[0] + 2 * scaling * np.sin(azimuth_true + plus_minus) , camera[1] + 2 * scaling * np.cos(azimuth_true + plus_minus), camera[2]], signal=audio_clock, delay=0.5)
    # room.add_source([camera[0] + 2 * scaling * np.sin(azimuth_true - plus_minus) , camera[1] + 2 * scaling * np.cos(azimuth_true - plus_minus), camera[2]], signal=audio_bark, delay=0.5)
    

    camera = [0, 0, 1]
    
    room.add_microphone([0 + ear, 0, 1])
    room.add_microphone([0 - ear, 0, 1])
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
