import pyaudio
from numpy import linspace,sin,pi,int16
from time import sleep
import numpy as np

RATE = 128000 # hardcoded sampling rate
amplitude = 30000 

pa = pyaudio.PyAudio()
stream = pa.open(
            output=True,
            channels=1,
            rate=RATE, 
            format=pyaudio.paInt16 #use 16 bit audio
            )

def note(freq, length, amp=1, rate=44100):
    '''Generate a note given frequency, 
    amplitude, duration and sampling rate
    '''
     t = linspace(0,length,length*rate) # generate x axis
     data = sin(2*pi*freq*t)*amp # generate y axis
     return data.astype(int16) # return data

tone0 = note(19000, (1/19000) * (19000/20), amplitude, rate=RATE) # tone for 0
tone1 = note(19500, (1/19500) * (19500/20), amplitude, rate=RATE) # tone for 1
tonep = note(20000, (1/20000) * (20000/20), amplitude, rate=RATE) # tone for pause

def send_message(msg):
    ''' Decode message to bit stream and send according tones.   '''
    global stream
    for char in msg:
        binrepr = format(ord(char),'b')
        if len(binrepr) < 7:
            binrepr="0"+binrepr
        for bit in binrepr:
            if bit == '1':
                stream.write(tone1)
            else:
                stream.write(tone0)

            stream.write(tonep)

if __name__ == "__main__":
    while True:
        send_message(input("Enter message to transmitt >>"))
