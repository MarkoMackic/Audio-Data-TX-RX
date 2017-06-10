So this project is started beacuse I wanted to modulate some data into
audio and back, I had to experiment a lot to get accurate decoding results
at speed of 2 bytes per second :D But non the less this was one of the more
interesting projects I worked on. So you might have to tweak them if you want
to try,or you might not. Leave me in issues how this worked for you if you try it
I'd appreciate your feedback. : )

I tweaked the settings of sampling rate, amplification, and frequencies of 
the tones, and these do the job on my laptop.

The protocol is very simple and time undefined 

SENDER: 
    Text -> Bit stream
    For n = 0 to Length(Bit stream)
        Send note of bit at n-th position
        Send pause note

RECEIVER:
	Record signal coming from microphone to sound file

	Decode file:
		
		Since the sender sends pause note,
		we need some kind of state machine to hold
		it.Call it pause_wait.It should be boolean and
		first initialized to 0.

		We need a buffer for holding undecoded data, and 
		output variable for returning output.

		We should go through signal and analyze frequencies, 
		if we get tones for 1 or 0 we check if pause_wait is 
		0 , if it is, append according data to buffer, if it's
		not, then pass.
		If we get pause tone we reset our pause_wait to 0.

		At the end we have buffer with ASCII encoded info about
		our chars. It should be vertified by statement
			if length(buf) % 7 != 0 or lenth(buf) = 0 
		then buffer is invalid. After that's confirmed we 
		can extract 7 by 7 bits of data and append according 
		char to the output. Return the output at the end of function

	
