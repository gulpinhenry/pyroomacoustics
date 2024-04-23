"""
This example creates a free-field simulation of direction of arrival estimation.
"""

import argparse
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

import pyroomacoustics as pra

def convertStereotoMono(stereoAudio):
    #make monoAudio ndarray
    monoAudio = np.zeros(len(stereoAudio))
    #convert stereo to mono
    for i in range(len(stereoAudio)):
        monoAudio[i] = (stereoAudio[i][0] + stereoAudio[i][1]) // 2
    return monoAudio

fs, audio_dingdong = wavfile.read("audio/dingdongPCM.wav")
audio_dingdong = convertStereotoMono(audio_dingdong)
fs, audio_bark = wavfile.read("audio/barkPCM.wav")
audio_bark = convertStereotoMono(audio_bark)
filename="my_room_simulation/output.wav"
print(audio_bark, audio_dingdong)




if __name__ == "__main__":

    # we use a white noise signal for the source
    fs = 16000
    # create anechoic room
    room = pra.AnechoicRoom(fs=fs)

    # place the source at a 90 degree angle and 5 meters distance from origin
    azimuth_true = np.pi / 6
    # plus or minus three degrees
    plus_minus = np.pi/60
    # room.add_source([5 * np.cos(azimuth_true + plus_minus) , 5 * np.sin(azimuth_true + plus_minus), 0], signal=audio_dingdong, delay=1.3)
    room.add_source([5 * np.cos(azimuth_true - plus_minus) , 5 * np.sin(azimuth_true - plus_minus), 0], signal=audio_bark, delay=1.3)

    room.add_microphone([0,0,0])
    room.set_ray_tracing()
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

    # what is this
    room.plot_rir()

    room.plot(img_order=1)
    
    plt.show()
