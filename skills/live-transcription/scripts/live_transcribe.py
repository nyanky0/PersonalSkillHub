"""Live meeting transcriber (Windows side). Records mic in 30s chunks, transcribes
each chunk with faster-whisper (Indonesian), appends timestamped text to transcript file.
Run: python live_transcribe.py  — stop with Ctrl+C (or kill from WSL).
Adjust DEVICE after running test_mic.py; DEVICE=None uses system default."""
import queue, sys, datetime
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SR = 16000
CHUNK = 30          # seconds per chunk
MODEL = "small"     # tiny/base/small; small = best balance for Indonesian on CPU
DEVICE = None       # set to tested device index (int) — see test_mic.py
OUT = r"C:\Users\muham\Desktop\IBT\transcript-live.txt"  # adjust per session

q = queue.Queue()
print("Loading whisper model (first run downloads ~500MB)...", flush=True)
model = WhisperModel(MODEL, device="cpu", compute_type="int8")
print("Model ready. Recording... Ctrl+C to stop.", flush=True)

def cb(indata, frames, t, status):
    if status: print(status, file=sys.stderr)
    q.put(indata.copy())

def stamp():
    return datetime.datetime.now().strftime("[%H:%M:%S]")

buf = np.empty((0, 1), dtype="float32")
with open(OUT, "a", encoding="utf-8") as f:
    f.write(f"\n===== SESSION {datetime.datetime.now():%Y-%m-%d %H:%M} =====\n")
    f.flush()
    with sd.InputStream(samplerate=SR, channels=1, dtype="float32", blocksize=0, callback=cb, device=DEVICE):
        try:
            while True:
                buf = np.concatenate([buf, q.get()])
                if len(buf) >= SR * CHUNK:
                    chunk, buf = buf[:SR * CHUNK], buf[SR * CHUNK:]
                    segs, _ = model.transcribe(chunk.squeeze(), language="id", vad_filter=True, beam_size=1)
                    text = " ".join(s.text.strip() for s in segs).strip()
                    if text:
                        line = f"{stamp()} {text}"
                        print(line, flush=True)
                        f.write(line + "\n")
                        f.flush()
        except KeyboardInterrupt:
            pass
print("Stopped.", flush=True)
