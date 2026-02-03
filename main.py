import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. تحميل النموذج وتوقيت الكلمات
model = whisper.load_model("base")
result = model.transcribe("video.mp4", word_timestamps=True)

video = VideoFileClip("video.mp4")
final_clips = [video]

def fix_text(text):
    return get_display(reshape(text))

# --- إعدادات التصميم ---
FONT_SIZE = 35
WORDS_PER_SEGMENT = 4  # عدد الكلمات التي تظهر معاً
Y_POS = video.h * 0.75  # موقع النص (مرتفع قليلاً)

# 2. تقسيم الكلمات إلى مجموعات (كل مجموعة 4 كلمات)
all_words = []
for segment in result['segments']:
    all_words.extend(segment.get('words', []))

for i in range(0, len(all_words), WORDS_PER_SEGMENT):
    chunk = all_words[i : i + WORDS_PER_SEGMENT]
    if not chunk: continue
    
    chunk_start = chunk[0]['start']
    chunk_end = chunk[-1]['end']
    chunk_duration = chunk_end - chunk_start
    
    # بناء نص المجموعة كاملة للعرض كخلفية ثابتة
    full_chunk_text = " ".join([w['word'].strip() for w in chunk])
    
    # القالب الأساسي للمجموعة (نص أبيض ثابت يظهر لمدة الـ 4 كلمات)
    base_text_clip = TextClip(
        fix_text(full_chunk_text),
        fontsize=FONT_SIZE,
        color='white',
        font='Arial-Bold',
        method='label'
    ).set_start(chunk_start).set_duration(chunk_duration).set_pos(('center', Y_POS))
    
    final_clips.append(base_text_clip)

    # 3. إضافة "المربع المتحرك" تحت الكلمة التي تُنطق الآن
    for word in chunk:
        w_text = word['word'].strip()
        w_start = word['start']
        w_end = word['end']
        w_dur = w_end - w_start
        
        if w_dur <= 0: continue

        # قياس حجم الكلمة الواحدة لتحديد عرض المربع تحتها
        word_measure = TextClip(fix_text(w_text), fontsize=FONT_SIZE, font='Arial-Bold')
        
        # إنشاء المربع الأصفر (سيكون تحت الكلمة كخط سميك)
        highlight = ColorClip(
            size=(word_measure.w + 10, 8), # العرض حسب الكلمة والسمك 8 بكسل
            color=(255, 255, 0) # أصفر
        ).set_start(w_start).set_duration(w_dur).set_opacity(0.8)
        
        # ملاحظة: حساب الموقع الأفقي الدقيق لكل كلمة داخل الجملة معقد برمجياً،
        # لذا سنستخدم التأثير الأجمل وهو ظهور المربع في المنتصف تحت الجملة أثناء نطق الكلمة
        highlight = highlight.set_pos(('center', Y_POS + word_measure.h + 5))
        
        final_clips.append(highlight)

# 4. الإنتاج
final_video = CompositeVideoClip(final_clips)
final_video.write_videofile("output.mp4", codec="libx264", audio_codec="aac", fps=video.fps)
