import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. تحميل أقوى نموذج (medium أو base) لدقة استخراج الكلمات
model = whisper.load_model("medium") 
result = model.transcribe("video.mp4", word_timestamps=True)

video = VideoFileClip("video.mp4")
final_clips = [video]

def fix_text(text):
    return get_display(reshape(text))

# --- إعدادات المحترفين ---
FONT_SIZE = 45 
MAX_WIDTH = video.w * 0.8  # النص لن يخرج عن 80% من عرض الشاشة
Y_POS = video.h * 0.75     # موقع النص

# 2. معالجة النصوص وضمان عدم الخروج عن الإطار
for segment in result['segments']:
    words = segment.get('words', [])
    if not words: continue

    # تقسيم الجملة إلى مجموعات صغيرة (3 كلمات) لضمان عدم خروجها عن الشاشة
    for i in range(0, len(words), 3):
        chunk = words[i:i+3]
        chunk_text = " ".join([w['word'].strip() for w in chunk])
        chunk_start = chunk[0]['start']
        chunk_end = chunk[-1]['end']
        
        # النص الأساسي (أبيض)
        base_txt = TextClip(
            fix_text(chunk_text),
            fontsize=FONT_SIZE,
            color='white',
            font='Arial-Bold',
            method='caption', # استخدام caption يمنع خروج النص عن الإطار
            size=(MAX_WIDTH, None)
        ).set_start(chunk_start).set_duration(chunk_end - chunk_start).set_pos(('center', Y_POS))
        
        final_clips.append(base_txt)

        # 3. المربع الأصفر "الذكي" الذي يتحرك تحت كل كلمة
        for word in chunk:
            w_start = word['start']
            w_end = word['end']
            
            # إنشاء خط سفلي تحت الكلمة
            # ملاحظة: لتحقيق الحركة بدقة 100% تحت كل كلمة نحتاج لقصاصة ملونة تظهر في وقت الكلمة
            highlight = ColorClip(
                size=(int(base_txt.w / len(chunk)), 6), # العرض تقريبي حسب طول الجملة
                color=(255, 255, 0)
            ).set_start(w_start).set_duration(w_end - w_start).set_opacity(0.8)
            
            # تحديد موقع الخط الأصفر تحت الكلمة (يتحرك أفقياً)
            idx = chunk.index(word)
            offset = (idx - (len(chunk)-1)/2) * (base_txt.w / len(chunk))
            
            highlight = highlight.set_pos((video.w/2 + offset - (highlight.w/2), Y_POS + base_txt.h - 5))
            final_clips.append(highlight)

# 4. التصدير بأعلى جودة (High Bitrate)
print("جاري الإنتاج بدقة HD...")
final_video = CompositeVideoClip(final_clips)
final_video.write_videofile(
    "output.mp4", 
    codec="libx264", 
    audio_codec="aac", 
    fps=video.fps,
    bitrate="8000k", # رفع الدقة لـ 8 ميجا لضمان الجودة
    preset="slow"    # تحسين المعالجة
)
