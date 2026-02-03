import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# 1. استخراج النصوص وتوقيتاتها
model = whisper.load_model("base")
result = model.transcribe("video.mp4", word_timestamps=True)

clips = []
video = VideoFileClip("video.mp4")

# 2. إنشاء النصوص المتزامنة
for segment in result['segments']:
    for word in segment['words']:
        # إنشاء نص لكل كلمة يظهر ويختفي مع الصوت
        txt = TextClip(word['word'], fontsize=70, color='yellow', font='Arial-Bold')
        txt = txt.set_start(word['start']).set_duration(word['end'] - word['start']).set_pos('center')
        clips.append(txt)

# 3. دمج النصوص مع الفيديو
result_video = CompositeVideoClip([video] + clips)
result_video.write_videofile("output.mp4", fps=video.fps)
