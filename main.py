import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from googletrans import Translator

# إعداد المترجم والنموذج
translator = Translator()
model = whisper.load_model("base")

# 1. تحليل الفيديو (إنجليزي)
result = model.transcribe("video.mp4", word_timestamps=True)
video = VideoFileClip("video.mp4")
clips = []

def fix_arabic(text):
    # معالجة النصوص العربية لتظهر بشكل صحيح
    reshaped = reshape(text)
    return get_display(reshaped)

# 2. إعدادات التصميم (تصغير الخط والموقع)
FONT_SIZE_EN = 24
FONT_SIZE_AR = 22

for segment in result['segments']:
    start_t = segment['start']
    end_t = segment['end']
    duration = end_t - start_t
    original_text = segment['text'].strip()

    # ترجمة النص للعربية
    try:
        translated = translator.translate(original_text, src='en', dest='ar').text
    except:
        translated = original_text # في حال فشل الاتصال

    # --- النص الإنجليزي (أصغر ومرفوع قليلاً عن العربي) ---
    txt_en = TextClip(original_text, fontsize=FONT_SIZE_EN, color='white', 
                     font='Arial-Bold', method='caption', size=(video.w*0.8, None))
    txt_en = txt_en.set_start(start_t).set_duration(duration).set_pos(('center', video.h*0.80))

    # --- النص العربي (أصغر وفي الأسفل تماماً) ---
    txt_ar = TextClip(fix_arabic(translated), fontsize=FONT_SIZE_AR, color='yellow', 
                     font='Arial', method='caption', size=(video.w*0.8, None))
    txt_ar = txt_ar.set_start(start_t).set_duration(duration).set_pos(('center', video.h*0.88))

    clips.append(txt_en)
    clips.append(txt_ar)

# 3. الإنتاج
final = CompositeVideoClip([video] + clips)
final.write_videofile("output.mp4", codec="libx264", audio_codec="aac", fps=video.fps)
