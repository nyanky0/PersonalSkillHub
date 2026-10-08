"""Mic probe: enumerate devices and measure signal level per candidate input.
Speak for 5s per device while it runs. Pick a device with peak > 0.01.
WASAPI entries may fail at 16kHz (PaErrorCode -9997) — use the MME entry instead."""
import sounddevice as sd
import numpy as np

print(sd.query_devices())
sr = 16000
# candidate default first, then physical mics
for dev in [None, 1, 2]:
    try:
        with sd.InputStream(samplerate=sr, channels=1, dtype="float32", device=dev) as s:
            data, _ = s.read(sr * 5)
        peak = np.abs(data).max()
        rms = np.sqrt((data ** 2).mean())
        print(f"device {dev}: peak={peak:.5f} rms={rms:.6f}", "OK" if peak > 0.01 else "SILENT")
    except Exception as e:
        print(f"device {dev}: {e}")
