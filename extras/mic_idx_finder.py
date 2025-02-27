import pyaudio as pa

def main():

    p = pa.PyAudio()

    dev_idx = None
    print('\n[INFO] : AVAILABLE INPUT AUDIO DEVICES:\n')
    input_devices = []
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev.get('maxInputChannels'):
            input_devices.append(i)
            print(i, dev.get('name'))
            
            if dev.get('name') == 'sysdefault':
                dev_idx = i

    if dev_idx:
        print(f"\nDefault microphone detected, device ID is '{dev_idx}'")
    else:
        print("\nNo default microphone detected. Please check your device settings")


if __name__ == '__main__':
    main()
