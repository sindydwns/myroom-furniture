from openai import OpenAI

client = OpenAI()

def to_text(file_path):
    audio_file= open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcription.text
