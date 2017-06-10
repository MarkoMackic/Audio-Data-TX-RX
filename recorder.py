from array import array
from struct import pack
from sys import byteorder
import copy
import pyaudio
import wave

threshold = 600 
rate = 128000
chunk_size = 4096
silent_chunks = 3 * rate / chunk_size  # about 3sec
fmt = pyaudio.paInt16 # 16 bit audio
channs = 1 # mono
trim_append = rate / 4 

def is_silent(data_chunk):
    """Returns 'True' if below the 'silent' threshold"""
    return max(data_chunk) < threshold

def trim(data_all):
    _from = 0
    _to = len(data_all) - 1
    for i, b in enumerate(data_all):
        if abs(b) > threshold:
            _from = max(0, i - trim_append)
            break

    for i, b in enumerate(reversed(data_all)):
        if abs(b) > threshold:
            _to = min(len(data_all) - 1, len(data_all) - 1 - i + trim_append)
            break

    return copy.deepcopy(data_all[int(_from):int(_to + 1)])

def record():
    """Record from the microphone and 
    return the data as an array of signed shorts."""
    global silent_chunks

    p = pyaudio.PyAudio()
    stream = p.open(format=fmt, channels=channs, rate=rate, input=True, output=True, frames_per_buffer=chunk_size)

    sc = 0
    audio_started = False
    data_all = array('h')
   
    while True:
        try:
            # little endian, signed short
            data_chunk = array('h', stream.read(chunk_size))
            if byteorder == 'big':
                data_chunk.byteswap()
            data_all.extend(data_chunk)

            silent = is_silent(data_chunk)

            if audio_started:
                if silent:
                    sc += 1
                    if sc > silent_chunks:
                        print("Stopped recording")
                        break

                else: 
                    sc = 0
            elif not silent:
                print("Started recording")
                audio_started = True              
        except KeyboardInterrupt:
            break
    sample_width = p.get_sample_size(fmt)
    stream.stop_stream()
    stream.close()
    p.terminate()

    data_all = trim(data_all)  # we trim
    return sample_width, data_all

def record_to_file(path):
    """Records from the microphone and outputs the resulting data to file"""
    sample_width, data = record()
    data = pack('<' + ('h' * len(data)), *data)

    wave_file = wave.open(path, 'wb')
    wave_file.setnchannels(channs)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(rate)
    wave_file.writeframes(data)
    wave_file.close()


if __name__ == '__main__':
    print("Wait in silence to begin recording; wait in silence to terminate")
    file_name = input("Enter file name >> ")
    record_to_file(file_name)
    print("Done - result written to %s.wav"%(file_name))
