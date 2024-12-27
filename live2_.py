# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
## Setup

To install the dependencies for this script, run:

``` 
pip install google-genai opencv-python pyaudio pillow mss
```

Before running this script, ensure the `GOOGLE_API_KEY` environment
variable is set to the api-key you obtained from Google AI Studio.

Important: **Use headphones**. This script uses the system default audio
input and output, which often won't include echo cancellation. So to prevent
the model from interrupting itself it is important that you use headphones. 

## Run

To run the script:

```
python live_api_starter.py
```

The script takes a video-mode flag `--mode`, this can be "camera", "screen", or "none".
The default is "camera". To share your screen run:

```
python live_api_starter.py --mode screen
```
"""

import asyncio
import base64
import io
import os
import sys
import traceback
import datetime
from colorama import Fore, Back, Style
import cv2
import pyaudio
import PIL.Image
import mss
import ast
import argparse
import rec
import os
from google import genai
import transcribe
if sys.version_info < (3, 11, 0):
    import taskgroup, exceptiongroup

    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "models/gemini-2.0-flash-exp"

DEFAULT_MODE = "none"

client = genai.Client(http_options={"api_version": "v1alpha"})
def set_preset():
    # Initialize a dictionary to store the details
    details = {}

    # Get character name
    contact_details = input("""Please give a name to the character. If you don't have one, type "no" and the AI will generate a name for you: """)
    if contact_details.strip().upper() == "NO":
        print("AI will pick a name.")
        details['name'] = "Make a fake first and last name avoid using names like john doe, john smith,etc."  # Replace with an actual name generation logic if needed
    else:
        details['name'] = contact_details

    # Get location
    location = input("""Where does your character live? (country and state) Type "no" to use a random location picked by the AI: """)
    if location.strip().upper() == "NO":
        print("AI will pick a location.")
        details['location'] = "Pick a random location in US or Canada state/town,etc"  # Replace with actual location generation
    else:
        details['location'] = location

    # Get postal code
    postal_code = input("""Please give a postal code. Type "no" and the AI will generate a postal code for you: """)
    if postal_code.strip().upper() == "NO":
        print("AI will pick a postal code.")
        details['postal_code'] = "Make a postal code based on the given location."  # Replace with actual postal code generation
    else:
        details['postal_code'] = postal_code

    # Get phone number (mandatory)
    phone_number = input("Please give a callback number (this cannot be left blank): ").strip()
    while not phone_number:
        print("Phone number cannot be blank. Please provide one.")
        phone_number = input("Please give a callback number: ").strip()
    details['phone_number'] = phone_number

    # Get email address
    email = input("""Please give an email address. Type "no" and the AI will generate an email address for you: """)
    if email.strip().upper() == "NO":
        print("AI will pick an email address.")
        details['email'] = "Please make a random email adresss it must be creative and not obiously fake like using @email.com"  # Replace with actual email generation logic
    else:
        details['email'] = email

    # Print the details and return them
    print("Thank you! Here are the details you entered/generated:")
    for key, value in details.items():
        print(f"{key.capitalize()}: {value}")

    return details
if not os.path.isfile("config.txt"):
    # Call the function to test
    character_details = set_preset()
    f = open("config.txt",'x')
    f.write(str(character_details))
    f.close()
    #sprint(character_details)
if os.path.isfile("config.txt"):

    print(Fore.GREEN+"Loaded config.txt")
else:
    print(Fore.RED+"Something went wrong with loading config file")
config = open("config.txt",'r')
character_details = config.read()
character_details =  ast.literal_eval(character_details)
#print(character_details)

option_picker = input(Fore.WHITE+f"{Fore.GREEN}Welcome to Scam-O-Baiter!{Fore.WHITE}\nChoose the scam:{Fore.YELLOW}\n1. Microsoft\n{Fore.BLUE}2. Airline flight\n{Fore.CYAN}3. Prize winnings\n{Fore.GREEN}4.Unauthorized paypal payment\n{Fore.MAGENTA}5.Norton support\n{Fore.WHITE}6. Custom option w/ contact details\n{Style.BRIGHT}Choose a option: ")
ai_prompt = ""
if option_picker == "1":
    ai_prompt = f'''Act as a technologically illiterate person, portraying the character as a typical Black person with a relatable, lively, and expressive personality. You will not repeat any introduction messages if you have gotten context of a previous conversation. ***Remember do not repeat "Oh hello, thank you for getting my call" Only do that IF YOU DO NOT HAVE CONTEXT OF A PREVIOUS CONVERSATION*** The character is currently on the phone with 'Microsoft' tech support because their computer  got a popup while they were (insert reason here, such as browsing or using facebook). The popup told them to call the number, and they are genuinely confused and concerned about what’s happening.

The character should struggle to understand and follow the tech support representative’s instructions, with moments of hesitation, confusion, and lively reactions. Use conversational expressions, humor, and culturally relatable phrases, like 'Now, hold on, you said what now?' or 'Wait, baby, this thing ain't working!' to emphasize their personality. Include frequent pauses and verbal expressions like 'Oh, Lord,' 'Hold on, lemme see,' or 'This thing got me stressed!'

Stay in character and do not repeat what the tech support representative says word-for-word. Avoid flipping the roles or taking over as tech support yourself, And avoid using the word "pc" and instead use "Computer" Only or "laptop" if applicable. Use "Laptop" only if the tech support has ask what type of computer it is or you can choose to say it's a "desktop" too. Also, do not use or describe visual representations of sounds such as grunt, shuffling,laugh, or sneezes. Instead, focus on dynamic and authentic dialogue that highlights the character's lack of technical understanding, expressive reactions, and personality quirks to make the interaction lively and realistic. When asked to spell out numbers, say the numbers comma seperated, i.e when asked to say your phone number, or a code,etc take that in mind for the future. When they introduce themselves or say hello respond in a overly cheerfull voice like if you been waiting ages to talk with someone "Oh Hello, thanks for getting my call! I was browsing and going to like facebook but then i got this concerning popup saying my PC was infected with some virus it said to call your guy's number. I hope you can help me" DO NOT introduce yourself if you are given previous context of a conversation simply follow the flow based on the previous conversation Your character's name is {character_details.get("name")} you live in {character_details.get("location")}, Your phone number is {character_details.get("phone_number")} your zip code is {character_details.get("postal_code")} , and your email is {character_details.get("email")}'''
elif option_picker == "2":
    ai_prompt = f'NOTE: If you got further context in the conversation please continue the conversationYou are to roll play as a male character who wants to book a flight NOT support/help desk. You are simply pretending to be a customer., you must pick a random destination, 1 passenger (you), and a random time frame from at least {datetime.datetime.now()}. Your characters name is {character_details.get("name")} you live in {character_details.get("location")}, Your phone number is {character_details.get("phone_number")} your zip code is {character_details.get("postal_code")} , and your email is {character_details.get("email")}'
elif option_picker == "3":
    ai_prompt = f'''You are to roll play as a male character whos isNOT the user YOU a customer who is calling about a supposed prize winnings you're to get. Say you got the number from the email you got. You're exited by the high amount of winnings you're supposed to get and is wondering on the steps to claim the money. Whenever they say Hello respond a variation of "Oh hi, Um i got this email that says i won a prize? it said to call this number to claim it" Your character's name is {character_details.get("name")} you live in {character_details.get("location")}, Your phone number is {character_details.get("phone_number")} your zip code is {character_details.get("postal_code")} , and your email is {character_details.get("email")}'''
elif option_picker == "4":
    ai_prompt = f'''You are to roll play as a  male customer NOT support who got a email that a unauthorized payment was done on your paypal account from a specific retailer i.e walmart, wallgreens, target,etc. Your character's name is {character_details.get("name")} you live in {character_details.get("location")}, Your phone number is {character_details.get("phone_number")} your zip code is {character_details.get("postal_code")} , and your email is {character_details.get("email")}'''
elif option_picker == "5":
    ai_prompt = f'''You're going to roll-play as a male character who isn't well versed in computers. (You got the computer used from your grandson who fixed it for you)
    You are calling norton support because you got a popup when you where on the internet and then it said you pc was 
    infected with a virus and you needed to renew your norton antivirus subscription and you needed to call this number to renew your subscription (pretend the number is norton and you believe the person you are in conversation with is norton support, do not doubt any authenticity.). When ever doing a task from the support agent add a delay to make it seem something is loading hmm, umm,etc. Do not instantly say it fished, it loaded,etc. Your character's name is {character_details.get("name")} you live in {character_details.get("location")}, Your phone number is {character_details.get("phone_number")} your zip code is {character_details.get("postal_code")} , and your email is {character_details.get("email")}'''
elif option_picker == "6":
    print(Style.BRIGHT)
    ai_prompt = input("Type a pre-prompt:")
    print(Style.NORMAL)
    ai_prompt = ai_prompt + f""" Your character's name is {character_details.get("name")} you live in {character_details.get("location")}, Your phone number is {character_details.get("phone_number")} your zip code is {character_details.get("postal_code")} , and your email is {character_details.get("email")}"""

if os.path.isfile("output.mp3"):
    summary = transcribe.transcribe_audio("output.mp3")

    ai_prompt = ai_prompt + "Here is the relevant previous conversation you just had, remember to stay in character and remember your previous conversation! AT ALL COSTS SDO NOT repeat your introduction message. HERE is the context: " + summary

print(f"{Fore.GREEN}PROMPT: {Fore.WHITE}{ai_prompt}")

CONFIG = {
    "generation_config": {
        "response_modalities": ["AUDIO"],
        "speech_config": "Charon"
    },
    "system_instruction": ai_prompt
}



pya = pyaudio.PyAudio()
recorder = rec.AudioRecorder()
rec.start_recording()

class AudioLoop:
    def __init__(self, video_mode=DEFAULT_MODE):
        self.video_mode = video_mode
        
        self.audio_in_queue = None
        self.out_queue = None

        
        self.session = None

        self.send_text_task = None
        self.receive_audio_task = None
        self.play_audio_task = None

    async def send_text(self):
        while True:
            
            text = await asyncio.to_thread(
                input,
                "message > ",
            )
            if text.lower() == "q":
                self.audio_stream.close()
                rec.stop_recording.py
                os.system("py live2_.py")
                break
            await self.session.send(text or ".", end_of_turn=True)
            


    def _get_frame(self, cap):
        # Read the frameq
        ret, frame = cap.read()
        # Check if the frame was read successfully
        if not ret:
            return None
        # Fix: Convert BGR to RGB color space
        # OpenCV captures in BGR but PIL expects RGB format
        # This prevents the blue tint in the video feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)  # Now using RGB frame
        img.thumbnail([1024, 1024])

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        # This takes about a second, and will block the whole program
        # causing the audio pipeline to overflow if you don't to_thread it.
        cap = await asyncio.to_thread(
            cv2.VideoCapture, 0
        )  # 0 represents the default camera

        while True:
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break

            await asyncio.sleep(1.0)

            await self.out_queue.put(frame)

        # Release the VideoCapture object
        cap.release()

    def _get_screen(self):
        sct = mss.mss()
        monitor = sct.monitors[0]

        i = sct.grab(monitor)

        mime_type = "image/jpeg"
        image_bytes = mss.tools.to_png(i.rgb, i.size)
        img = PIL.Image.open(io.BytesIO(image_bytes))

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_screen(self):

        while True:
            frame = await asyncio.to_thread(self._get_screen)
            if frame is None:
                break

            await asyncio.sleep(1.0)

            await self.out_queue.put(frame)

    async def send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send(msg)

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def receive_audio(self):
        "Background task to reads from the websocket and write pcm chunks to the output queue"
        while True:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(text, end="")

            # If you interrupt the model, it sends a turn_complete.
            # For interruptions to work, we need to stop playback.
            # So empty out the audio queue because it may have loaded
            # much more audio than has played yet.
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                if self.video_mode == "camera":
                    tg.create_task(self.get_frames())
                elif self.video_mode == "screen":
                    tg.create_task(self.get_screen())
                
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            pass
        except ExceptionGroup as EG:
            self.audio_stream.close()
            rec.stop_recording()
            traceback.print_exception(EG)
            os.sys("py live2_.py")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        default=DEFAULT_MODE,
        help="pixels to stream from",
        choices=["camera", "screen", "none"],
    )
    args = parser.parse_args()
    main = AudioLoop(video_mode=args.mode)
    asyncio.run(main.run())