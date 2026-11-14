# Makes assets/audio/one-world-lounge.mp3:  python3 music_gen.py loop.wav && ffmpeg -i loop.wav -c:a libmp3lame -b:a 112k one-world-lounge.mp3
# One World lounge loop: original synthesis, owned by One World Labs (no third-party samples).
import numpy as np, sys
from scipy.signal import fftconvolve, butter, sosfilt
SR = 44100; BPM = 92; BEAT = 60 / BPM; BARS = 32; BAR = 4 * BEAT
N = int(round(BARS * BAR * SR)); TAIL = int(4 * SR)
rng = np.random.default_rng(7)
L = np.zeros(N + TAIL); R = np.zeros(N + TAIL)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t0, pan=0.0, gain=1.0):
    i = int(round(t0 * SR)); j = min(i + len(sig), len(L)); s = sig[:j - i] * gain
    L[i:j] += s * np.cos((pan + 1) * np.pi / 4); R[i:j] += s * np.sin((pan + 1) * np.pi / 4)
def env(n, a, d, rel, dur):
    t = np.arange(n) / SR; e = np.minimum(t / a, 1.0) * np.exp(-t * d)
    off = t > dur; e[off] *= np.exp(-(t[off] - dur) / rel); return e
def rhodes(m, dur, vel=0.7):
    f = mtof(m); n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    idx = 1.6 * vel * np.exp(-t * 4) + 0.25
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    s += 0.12 * vel * np.sin(2 * np.pi * f * 7.0 * t) * np.exp(-t * 18)   # soft tine
    s *= 1 + 0.12 * np.sin(2 * np.pi * 4.6 * t)                         # tremolo
    return s * env(n, 0.004, 1.1, 0.25, dur) * vel
def pad(m, dur):
    f = mtof(m); n = int((dur + 1.5) * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for det in (-0.12, 0.12):
        ff = f * 2 ** (det / 12)
        for h in range(1, 6): s += np.sin(2 * np.pi * ff * h * t + h) / h ** 1.6
    e = np.minimum(t / 0.9, 1.0); off = t > dur; e[off] *= np.exp(-(t[off] - dur) / 0.8)
    return s * e * 0.08
def bass(m, dur, vel=0.8):
    f = mtof(m); n = int((dur + 0.4) * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return s * env(n, 0.006, 2.2, 0.06, dur) * vel
def vibe(m, dur, vel=0.6):
    f = mtof(m); n = int((dur + 1.6) * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 6)
    s *= 1 + 0.18 * np.sin(2 * np.pi * 5.5 * t)
    return s * env(n, 0.003, 1.6, 0.4, dur) * vel
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(48 + 90 * np.exp(-t * 30)) / SR
    return np.sin(ph) * np.exp(-t * 11) * 0.9
def noise_hit(n_s, dec, lo, hi):
    n = int(n_s * SR); t = np.arange(n) / SR
    sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, rng.standard_normal(n)) * np.exp(-t * dec)
def rim():
    n = int(0.12 * SR); t = np.arange(n) / SR
    return (noise_hit(0.12, 45, 1200, 5000) * 0.6 + np.sin(2 * np.pi * 1750 * t) * np.exp(-t * 60) * 0.35)
def hat(): return noise_hit(0.06, 70, 6000, 14000) * 0.5
def shaker(): return noise_hit(0.09, 35, 4000, 11000) * 0.25

# progression: (bass root, voicing)
PROG = [(41, [53, 57, 60, 64, 67]), (40, [52, 55, 59, 62]), (38, [53, 57, 60, 64]), (43, [53, 59, 64]),
        (36, [52, 55, 59, 62]), (45, [55, 59, 60, 64]), (38, [53, 57, 60, 64]), (43, [53, 57, 60, 62])]
MEL = [[(0.5, 76, .5), (1, 79, .5), (1.5, 81, 1), (3, 79, .5), (3.5, 76, .5)],
       [(0, 74, 1.5), (2, 76, .5), (2.5, 74, .5), (3, 71, 1)],
       [(0.5, 72, .5), (1, 74, .5), (1.5, 76, 1), (3, 77, .5), (3.5, 76, .5)],
       [(0, 74, 2.5), (3, 71, .5), (3.5, 74, .5)],
       [(0.5, 79, .5), (1, 76, .5), (1.5, 79, 1), (3, 81, .5), (3.5, 79, .5)],
       [(0, 76, 1.5), (2, 79, .5), (2.5, 76, .5), (3, 72, 1)],
       [(0.5, 74, .5), (1, 77, .5), (1.5, 81, 1), (3, 79, .5), (3.5, 77, .5)],
       [(0, 74, 3)]]
SW = 0.09  # swing on off-beat eighths (in beats)
def sw(b): return b + (SW if abs(b * 2 - round(b * 2)) < 1e-6 and (round(b * 2) % 2 == 1) else 0)
K, RM = kick(), rim()
for bar in range(BARS):
    t0 = bar * BAR; root, vo = PROG[bar % 8]; sec = bar // 8
    nxt = PROG[(bar + 1) % 8][0]
    for m in vo: add(pad(m, BAR * 0.98), t0, pan=rng.uniform(-.5, .5), gain=1.0)
    comp = [(0, 1.3, .62), (1.5, .45, .48), (2.5, 1.4, .56)] if bar % 2 == 0 else [(0, .9, .6), (1.5, 1.0, .5), (3.5, .45, .45)]
    for b, d, v in comp:
        for k, m in enumerate(vo):
            add(rhodes(m, d * BEAT, v * rng.uniform(.9, 1.05)), t0 + sw(b) * BEAT + k * 0.006, pan=-.35 + .7 * k / max(1, len(vo) - 1), gain=.16)
    for b, m, d, v in [(0, root, .9, .85), (1.5, root, .35, .6), (2, root + 7, .9, .7), (3.5, nxt - 1 if (nxt - root) % 12 else root + 12, .4, .55)]:
        add(bass(m, d * BEAT, v), t0 + sw(b) * BEAT, gain=.42)
    for e8 in range(8):
        b = e8 / 2; v = .55 if e8 % 2 else .3
        add(hat() * v, t0 + sw(b) * BEAT, pan=.3, gain=.55)
    for b in (1, 3): add(RM, t0 + b * BEAT, pan=-.1, gain=.38)
    if sec >= 1:
        for b in ((0, 2.5) if bar % 2 == 0 else (0, 1.75, 2.5)): add(K, t0 + b * BEAT, gain=.55)
    if sec == 2:
        for s16 in range(16):
            b = s16 / 4; add(shaker() * (.8 if s16 % 2 else .45), t0 + sw(b) * BEAT, pan=-.4, gain=.6)
    if sec in (1, 3):
        for b, m, d in MEL[bar % 8]:
            add(vibe(m + (12 if sec == 3 and bar % 8 in (4, 5) else 0) * 0, d * BEAT, .55), t0 + sw(b) * BEAT, pan=.15, gain=.20)
# reverb (shared)
ir_n = int(1.6 * SR); ti = np.arange(ir_n) / SR
irL = rng.standard_normal(ir_n) * np.exp(-ti * 3.2); irR = rng.standard_normal(ir_n) * np.exp(-ti * 3.2)
irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
wl = fftconvolve(L, irL)[:len(L)]; wr = fftconvolve(R, irR)[:len(R)]
L = L + .22 * wl; R = R + .22 * wr
sos = butter(2, 35, btype="high", fs=SR, output="sos")
L, R = sosfilt(sos, L), sosfilt(sos, R)
# seamless loop: fold the tail onto the start
L[:TAIL] += L[N:N + TAIL]; R[:TAIL] += R[N:N + TAIL]
L, R = L[:N], R[:N]
st = np.stack([L, R], 1)
st = np.tanh(st / np.abs(st).max() * 1.4) ; st *= 0.89 / np.abs(st).max()
import wave
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())
print("samples", N, "seconds", N / SR)
