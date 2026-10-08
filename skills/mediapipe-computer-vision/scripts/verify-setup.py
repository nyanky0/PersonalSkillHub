#!/usr/bin/env python3
"""
Verification script for MediaPipe + OpenCV setup.
Run this to confirm environment is ready before building CV apps.
"""

import sys
import subprocess


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr


def check_python():
    print("Python version:", sys.version.split()[0])
    return sys.version_info >= (3, 8)


def check_import(module, attr=None):
    try:
        m = __import__(module, fromlist=[attr] if attr else [])
        if attr:
            getattr(m, attr)
        version = getattr(m, '__version__', 'unknown')
        print(f"  {module}: {version}")
        return True
    except Exception as e:
        print(f"  {module}: MISSING ({e})")
        return False


def check_opencv():
    ok, out, _ = run("python3 -c \"import cv2; print(cv2.__version__)\"")
    if ok:
        print(f"  opencv: {out.strip()}")
    else:
        print("  opencv: MISSING")
    return ok


def check_mediapipe():
    ok, out, _ = run("python3 -c \"import mediapipe; print(mediapipe.__version__)\"")
    if ok:
        print(f"  mediapipe: {out.strip()}")
        # Check Tasks API
        ok2, out2, _ = run("python3 -c \"from mediapipe.tasks.python.vision import HandLandmarker; print('Tasks API OK')\"")
        if ok2:
            print("  Tasks API: OK")
        else:
            print("  Tasks API: FAILED (wrong version?)")
        return ok and ok2
    else:
        print("  mediapipe: MISSING")
    return False


def check_numpy():
    ok, out, _ = run("python3 -c \"import numpy; print(numpy.__version__)\"")
    if ok:
        print(f"  numpy: {out.strip()}")
    else:
        print("  numpy: MISSING")
    return ok


def check_model():
    import os
    path = "hand_landmarker.task"
    if os.path.exists(path):
        size = os.path.getsize(path) / (1024 * 1024)
        print(f"  Model file: {path} ({size:.1f} MB)")
        return True
    else:
        print(f"  Model file: NOT FOUND ({path})")
        print("    Download: wget https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task")
        return False


def check_webcam():
    ok, out, err = run("python3 -c \"import cv2; cap=cv2.VideoCapture(0); ok, f=cap.read(); print('OK' if ok else 'NO CAM'); cap.release()\" 2>&1")
    if "OK" in out:
        print("  Webcam: DETECTED")
        return True
    else:
        print("  Webcam: NOT DETECTED (expected in WSL)")
        return False


def check_display():
    import os
    display = os.environ.get("DISPLAY", "")
    wayland = os.environ.get("WAYLAND_DISPLAY", "")
    if display or wayland:
        print(f"  Display: DISPLAY={display} WAYLAND_DISPLAY={wayland}")
        # Quick test
        ok, out, err = run("python3 -c \"import cv2; import numpy as np; img=np.zeros((100,100,3),np.uint8); cv2.imshow('test',img); cv2.waitKey(1); cv2.destroyAllWindows(); print('OK')\" 2>&1")
        if "OK" in out:
            print("  GUI: WORKING")
            return True
        else:
            print("  GUI: X SERVER NOT RUNNING (install VcXsrv on Windows host)")
            return False
    else:
        print("  Display: NO DISPLAY ENV (set DISPLAY=:0 with VcXsrv)")
        return False


def main():
    print("=" * 50)
    print("MediaPipe + OpenCV Environment Check")
    print("=" * 50)

    checks = [
        ("Python >= 3.8", check_python),
        ("OpenCV", check_opencv),
        ("MediaPipe (Tasks API)", check_mediapipe),
        ("NumPy", check_numpy),
        ("Model file", check_model),
        ("Webcam", check_webcam),
        ("Display/GUI", check_display),
    ]

    results = []
    for name, fn in checks:
        print(f"\n[{name}]")
        results.append(fn())

    print("\n" + "=" * 50)
    if all(results):
        print("✓ ALL CHECKS PASSED — ready for CV development")
        return 0
    else:
        print("✗ SOME CHECKS FAILED — fix before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())