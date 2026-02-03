import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. تحميل النموذج مع تفعيل Word-level Timestamps
model = whisper.load_model("base")
print("جاري تحليل الكلمات بدقة عالية...")
result = model.transcribe("video.mp4", word_timestamps=True)

video = VideoFileClip("video.mp4")
final_clips = [video]

def fix_text(text):
    # معالجة النصوص العربية
    return get_display(reshape(text))

# --- إعدادات التصميم الاحترافي ---
FONT_SIZE = 34
TEXT_COLOR = 'black'        # النص أسود ليبرز فوق الأصفر
HIGHLIGHT_COLOR = 'yellow'  # المربع الأصفر
Y_POS = video.h * 0.70      # رفع النص (70% من الارتفاع) ليكون بعيداً عن الحافة

# 2. توليد المربعات والنصوص لكل كلمة
for segment in result['segments']:
    if 'words' in segment:
        for word in segment['words']:
            text_str = word['word'].strip()
            start_t = word['start']
            end_t = word['end']
            duration = end_t - start_t
            
            if duration <= 0: continue

            # إنشاء نص الكلمة
            txt = TextClip(
                fix_text(text_str),
                fontsize=FONT_SIZE,
                color=TEXT_COLOR,
                font='Arial-Bold',
                method='label'
            ).set_start(start_t).set_duration(duration)

            # إنشاء الخلفية الصفراء (Highlight) بحجم الكلمة
            bg = ColorClip(
                size=(txt.w + 15, txt.h + 10),
                color=(255, 255, 0) # أصفر فاقع
            ).set_opacity(0.9).set_start(start_t).set_duration(duration)

            # وضع الكلمة والمربع في المنتصف تماماً
            bg = bg.set_pos(('center', Y_POS))
            txt = txt.set_pos(('center', Y_POS + 5)) # إزاحة بسيطة لتوسيط النص داخل المربع

            final_clips.append(bg)
            final_clips.append(txt)

# 3. دمج الطبقات وتصدير الفيديو
print("جاري دمج الكلمات المتحركة...")
final_video = CompositeVideoClip(final_clips)
final_video.write_videofile("output.mp4", codec="libx264", audio_codec="aac", fps=video.fps)
