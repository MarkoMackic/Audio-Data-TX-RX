from itertools import zip_longest
import pyaudio
import wave
import numpy as np
from time import sleep
from sys import platform

rate =  128000 # define the sampling rate of file.
# you could obitain this from wave module but it's
# hardoded into all of three files.
 
fet = 50 # frequency error tolerance

class DecodeException(Exception):
    '''Raise this when decode fails'''
    pass

if platform in ('linux', 'linux2'):

    from ctypes import *

    def py_error_handler(filename, line, function, err, fmt):
        '''Supress ALSA errors'''
        pass

    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)


def grouper(iterable, n, fillvalue=None):
    '''Return iterables sliced by every n members'''

    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def decode(file_name):
    '''Decode wav file back to text   '''
    buf = [] # store data to decode in here
    chunk = 2048 # file will be read by 2048 frames each loop
    output = "" # final string to return
    waitpause = 0  # some state machine

    wf = wave.open(file_name, 'rb')  # open up a wave file
    swidth = wf.getsampwidth() #get sample width

   

    window = np.blackman(chunk) # use a Blackman window
    

    # open stream / to play while decoding
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels = wf.getnchannels(),
                    rate = rate,
                    output = True)


    data = wf.readframes(chunk)
    while len(data) == chunk*swidth:
        stream.write(data) # write chunk of data to stream

        # unpack the data and times by the hamming window
        indata = np.array(wave.struct.unpack("%dh"%(len(data)/swidth),\
                                             data))*window
        fftData=abs(np.fft.rfft(indata))**2 # Take the fft and square each value
        which = fftData[1:].argmax() + 1   # find the maximum
        if which != len(fftData)-1: # use quadratic interpolation around the max
            y0,y1,y2 = np.log(fftData[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            thefreq = (which+x1)*rate/chunk
        else:
            thefreq = which*rate/chunk


        if(abs(thefreq-19000) < fet):
            if waitpause == 0:
                print("Recieved 0")
                buf.append('0')
                waitpause = 1
        elif(abs(thefreq-19500) < fet):
            if waitpause == 0:
                print("Recieved 1")
                buf.append('1')
                waitpause = 1

        elif(abs(thefreq-20000) < fet):
            waitpause = 0
         
        data = wf.readframes(chunk) #read another chunk

    if data:
        stream.write(data) #write to stream if somehting left
    if len(buf) > 0:
        for i in grouper(buf, 7, '0'):
            print(i)
            output += chr(int(''.join(i), 2))
        if len(buf) % 7 != 0:
            print("Mistake during receiving or decoding!")

    return output

    stream.close()
    p.terminate()

if __name__ == "__main__":
    while True:
        file_name = input("File to decode >>")
        print(decode(file_name))