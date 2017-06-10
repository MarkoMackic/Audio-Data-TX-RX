from decoder import *
from recorder import *


if __name__ == '__main__':
	input("Press enter to decode info from microphone ")
	record_to_file('sample.wav')
	print(decode('sample.wav'))