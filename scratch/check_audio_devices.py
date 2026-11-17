import sys

try:
    import sounddevice as sd
    print("sounddevice is installed.")
    devices = sd.query_devices()
    print("Devices found:")
    print(devices)
    default_input = sd.default.device[0]
    print(f"Default input device index: {default_input}")
    if default_input is not None and default_input >= 0:
        print("Default input device details:", devices[default_input])
    else:
        print("No default input device configured.")
except Exception as e:
    print(f"sounddevice check failed: {e}")

try:
    import pyaudio
    print("pyaudio is installed.")
    p = pyaudio.PyAudio()
    info = p.get_default_input_device_info()
    print("PyAudio default input:", info)
except Exception as e:
    print(f"pyaudio check failed: {e}")

