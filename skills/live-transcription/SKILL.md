---
name: live-transcription
description: "Live meeting transcription: mic + Whisper (WSL→Windows)."
version: 1.0.0
author: Hermes
---

# Live Meeting Transcription

Transcribe live meetings/interviews from microphone to a growing text file, then summarize on demand. Built for WSL hosts where audio input does not exist — recording runs on the Windows side via cmd.exe interop.

## When to Use

- User is in a live meeting (blueprint sessions, customer interviews, calls) and wants live transcription or an on-demand summary.
- User asks "bisa engga ngerangkum dari audio live / mic langsung".

## Architecture (WSL host)

```
WSL (orchestration, summarizing)
  └─ cmd.exe → python live_transcribe.py (Windows side)
       ├─ sounddevice InputStream @16kHz mono float32
       ├─ 30s chunks → faster-whisper small int8 (CPU), language="id"
       └─ append "[HH:MM:SS] text" → Desktop transcript file (readable from /mnt/c)
```

Install once (Windows python):
```
cmd.exe /c "python -m pip install --user faster-whisper sounddevice"
```

## Workflow

1. Enumerate + test microphones BEFORE starting a long session — see Pitfalls. Pick the device with real signal (peak > 0.01 over 5s of speech).
2. Copy `scripts/live_transcribe.py` to a Windows path (e.g. Desktop), launch in background:
   ```
   cmd.exe /c "cd /d C:\Users\<user>\Desktop\<dir> && python live_transcribe.py"
   ```
   with terminal(background=true). First run downloads the Whisper model (~500MB) — wait for "Model ready" in poll output.
3. Verify: wait 60–75s, `tail` the transcript file. First chunk should appear. If session header exists but no lines after ~2 chunks, mic is wrong — kill, re-test devices.
4. Summarize on demand: read the transcript file (path printed at script top), summarize into meeting notes (existing docx skill handles the formatted output).
5. Stop: process(action='kill') on the background session.

## Pitfalls

- **Default mic device is often a silent virtual device** (e.g. SteelSeries Sonar). `sd.query_devices()` lists many; default may capture nothing. ALWAYS run `scripts/test_mic.py`-style level probe (peak/RMS over 5s) per candidate device and pick a physical mic (Realtek Microphone Array, etc.).
- **WASAPI devices may reject 16kHz** (`PaErrorCode -9997`). Use the MME variant of the device (lower index).
- **WSL has no audio input** — never attempt pactl/arecord on the WSL side; run capture on Windows.
- **Windows audio devices can change** when headsets/SteelSeries connect — device index is not stable across boots. Re-probe each session.
- **Latency is ~60s** (30s buffer + 30s CPU transcribe). Whisper `small` is the accuracy/speed balance on laptop CPU; `medium` lags badly, `tiny` garbles Indonesian technical terms.
- **Popup-free is mandatory** for this user — background Windows processes must never steal focus. Plain console python via cmd.exe interop is safe.
- Meeting-room acoustics: mic far from the customer's voice degrades accuracy badly. Recommend a laptop placed centrally if quality matters.
- cmd.exe interop: must run from /mnt/c (cd first) or paths resolve wrong. Batch work through one long-lived background process rather than repeated exec.
- **cmd.exe inline Python quoting breaks**: `cmd.exe /c "python -c \"import X; print('ok')\""` from WSL mangles nested quotes → `SyntaxError: unterminated string literal`. To check deps or run short Python on Windows side: write a temp .py to a /mnt/c path, then `cmd.exe /c "cd /d C:\\... && python file.py"`. Do not fight quote layers.
- **Default mic can be good**: in this session device None (system default) had peak=0.06039 (OK), while devices 1 and 2 were SILENT. Don't assume default is bad — always probe, but probe None first.

## Support files

- `scripts/live_transcribe.py` — the transcriber (copy to Windows path, run via cmd.exe background).
- `scripts/test_mic.py` — mic enumeration + 5s signal-level probe; run before every session.
- `references/meeting-notes-format.md` — .docx meeting-notes structure for summarizing transcripts.

## Summarizing live transcripts

Raw chunks are noisy (mis-heard technical terms, dropped words). When summarizing:
- Group by topic, not by timestamp.
- Flag ambiguous/unclear phrases as "perlu konfirmasi" instead of guessing.
- Reuse the structured meeting-notes format (header meta, sessions, decision boxes, open questions, action items table).
