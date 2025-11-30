# # External packages
# import tempfile
# from fastapi import UploadFile, File

# # Internal packages
# from app.core.config import model


# async def transcription(file: UploadFile = File(...)):
#     audio_bytes = await file.read()

#     with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
#         temp_file.write(audio_bytes)
#         temp_file.flush()

#         segments, info = model.transcribe(
#             temp_file.name,
#             language='ja',
#             beam_size=10
#         )

#     text = " ".join([s.text for s in segments])
#     return {"text": text}