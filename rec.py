import pyaudio
import wave
import threading
import time
from pydub import AudioSegment
class AudioRecorder:
    def __init__(self, channels=1, rate=16000, chunk_size=2048, filename="output.wav"):
        self.channels = channels
        self.rate = rate
        self.chunk_size = chunk_size
        self.filename = filename
        self.frames = []
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None

        # Get device indices based on device names
        self.device1_index = self.get_device_index("VoiceMeeter Aux Output")
        self.device2_index = self.get_device_index("VoiceMeeter Output")
        #self.microphone_index = self.get_device_index("Microphone")  # You may want to adjust this to match your mic name

    def get_device_index(self, device_name):
        """Get the index of a device by name."""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_name.lower() in device_info['name'].lower():
                return i
        raise ValueError(f"Device '{device_name}' not found.")

    def start_recording(self):
        """Start recording from the selected devices."""
        if self.is_recording:
            print("Recording is already in progress.")
            return
        
        self.frames = []
        self.is_recording = True

        # Open audio streams for both devices and the microphone
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device1_index  # Device 1
        )
        
        self.stream2 = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device2_index  # Device 2
        )

        #self.stream_microphone = self.audio.open(
           #format=pyaudio.paInt16,
            #channels=self.channels,
            ##input=True,
            #frames_per_buffer=self.chunk_size,
            #input_device_index=self.microphone_index  # Microphone device
        #)

        print("Recording started...")

        # Create a separate thread for each device recording
        threading.Thread(target=self._record_device, args=(self.stream,)).start()
        threading.Thread(target=self._record_device, args=(self.stream2,)).start()
        #threading.Thread(target=self._record_device, args=(self.stream_microphone,)).start()

    def _record_device(self, stream):
        """Record audio from the specified stream and append to frames."""
        while self.is_recording:
            data = stream.read(self.chunk_size)
            self.frames.append(data)

    def stop_recording(self):
        """Stop recording and save the file."""
        if not self.is_recording:
            print("No recording in progress.")
            return
        
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.stream2.stop_stream()
        self.stream2.close()
        #self.stream_microphone.stop_stream()
        #self.stream_microphone.close()

        print("Recording stopped.")
        
        # Save the recording to file
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wavefile = AudioSegment.from_wav("output.wav")
            wavefile.export("output.mp3",bitrate="32k")
        print(f"Recording saved as {self.filename}.")

# Create an instance of the recorder
recorder = AudioRecorder()

def start_recording():
    """Start the audio recording."""
    recorder.start_recording()

def stop_recording():
    """Stop the audio recording."""
    
    recorder.stop_recording()

# Example usage:
# start_recording()
# time.sleep(5)  # Record for 5 seconds
# stop_recording()
