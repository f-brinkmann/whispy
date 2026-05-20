# %%
import whispy
from pprint import pprint

config = whispy.utils.read_config("configs/mushra_like_2d.yml")

type(config["window_size"])

# %%
import whispy

whispy.methods.MushraLike2D()

# %%
import pyfar as pf

signal = pf.signals.pulsed_noise(22050, 0, 90, 1, seed=42)
signal = pf.dsp.normalize(signal) * .5

for n, f in enumerate([200, 400, 600]):
    stimulus = pf.dsp.filter.bell(signal, f, 6, 1)
    pf.io.write_audio(stimulus, f'stimulus_{n+1}.wav')

