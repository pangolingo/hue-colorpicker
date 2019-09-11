import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=chunk
)
frames = []
stream.read(CHUNK)

import scipy.io.wavfile as wavfile
import numpy as np
import pylab as pl
rate, data = wavfile.read('FILE.wav')
t = np.arange(len(data[:,0]))*1.0/rate
pl.plot(t, data[:,0])
pl.show()

frames.append(data)
stream.stop_stream()
stream.close()
p.terminate()
