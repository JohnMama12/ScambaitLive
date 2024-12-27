# ScambaitLive
an AI based automatic scambait tool
based on original code from gemini cookbook: https://github.com/google-gemini/cookbook/blob/main/gemini-2/live_api_starter.py
In order for this to work, install the following packages:
``pip install genai colorama``
Then you must a get free API key at https://aistudio.google.com and add a new enviorment variable named "GOOGLE_API_KEY" and set it to your API key.
You must have Voicemeeter installed (Voice meeter bananna is enough) and route the software where you make your calls, or if you're using textnow or your Web Browser.
Make sure to go into rec.py and set both devices to the voicemeeter output of input and outputs:
```
self.device1_index = self.get_device_index("VoiceMeeter Aux Output") 
self.device2_index = self.get_device_index("VoiceMeeter Output")
```

If done correctly the call should be recorded and transcribed when the rate limit is reach or Q is pressed to stop, and the AI will try to catch on where it was before next time it is run.
The recorded audio is botched but is good enough to transcribe, you can try to adjust the buffer size.
