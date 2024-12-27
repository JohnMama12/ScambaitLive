import google.generativeai as genai
import pathlib

def transcribe_audio(audio_path, model_name='models/gemini-1.5-flash'):
  """
  Transcribes audio and provides a summary.

  Args:
    audio_path: Path to the audio file.
    model_name: Name of the Gemini model to use.

  Returns:
    Summary of the key information in the audio.
  """

  model = genai.GenerativeModel(model_name)

  prompt = """You're an AI that will provide a detailed transcription from a given audio. 

  Provide a detailed transcription of the conversation
  Take into account the roles of each speaker and give them names by assumption
  for example if one speaker says hello? i need help, assume they are "YOU"
  and any other speaker is "Tech support"
  The summary should be short, and not every single line of detail it should be a couple lines at best"""

  response = model.generate_content([
      prompt,
      {
          "mime_type": "audio/mp3",
          "data": pathlib.Path(audio_path).read_bytes()
      }
  ])

  return response.text

#if __name__ == "__main__":
  # Example usage
  #audio_file = 'output.mp3' 
  #summary = transcribe_audio(audio_file)
  #print(summary)