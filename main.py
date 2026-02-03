import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. تحميل النموذج بدقة Medium
model = whisper.load_model("medium") 
result = model.transcribe("video.mp4", word_timestamps=True)

video = VideoFileClip("video.mp4")
final_clips = [video]

def fix_text(text):
    return get_display(reshape(text))

# --- إعدادات المونتاج المعدلة ---
FONT_SIZE = 32             # تصغير حجم الخط كما طلبت
MAX_WIDTH = video.w * 0.8  # ضمان عدم خروج النص عن الإطار
Y_POS = video.h * 0.75     # موقع النص (مرتفع قليلاً عن الحافة)

# 2. معالجة الكلمات وتنسيقها
all_words = []
for segment in result['segments']:
    all_words.extend(segment.get('words', []))

# تقسيم الكلمات لمجموعات (3 كلمات لكل ظهور)
for i in range(0, len(all_words), 3):
    chunk = all_words[i:i+3]
    chunk_start = chunk[0]['start']
    chunk_end = chunk[-1]['end']
    chunk_text = " ".join([w['word'].strip() for w in chunk])
    
    # النص الأساسي (يظهر باللون الأبيض كخلفية ثابتة للجملة)
    main_txt = TextClip(
        fix_text(chunk_text),
        fontsize=FONT_SIZE,
        color='white',
        font='Arial-Bold',
        method='caption',
        size=(MAX_WIDTH, None)
    ).set_start(chunk_start).set_duration(chunk_end - chunk_start).set_pos(('center', Y_POS))
    
    final_clips.append(main_txt)

    # 3. المربع الأصفر (خلف الكلمة المتحركة)
    total_chars = len(chunk_text)
    # حساب بداية النص أفقياً لضمان دقة مكان المربع
    start_x = (video.w - main_txt.w) / 2 
    current_x = start_x

    for word in chunk:
        w_str = word['word'].strip()
        w_start = word['start']
        w_end = word['end']
        
        # عرض المربع يتناسب مع طول الكلمة
        word_w = (len(w_str) / total_chars) * main_txt.w
        
        # المربع الأصفر خلف الكلمة (Highlight)
        highlight = ColorClip(
            size=(int(word_w + 10), int(main_txt.h + 5)), # الحجم يغطي الكلمة بالكامل
            color=(255, 255, 0)
        ).set_start(w_start).set_duration(w_end - w_start).set_opacity(0.6) # شفافية بسيطة ليظهر النص
        
        # وضع المربع "خلف" النص (عن طريق إضافته للقائمة قبل نص الكلمة الأسود)
        highlight = highlight.set_pos((current_x - 5, Y_POS))
        
        # نص الكلمة باللون الأسود ليظهر فوق الأصفر
        word_txt = TextClip(
            fix_text(w_str),
            fontsize=FONT_SIZE,
            color='black',
            font='Arial-Bold'
        ).set_start(w_start).set_duration(w_end - w_start).set_pos((current_x, Y_POS))
        
        final_clips.append(highlight)
        final_clips.append(word_txt)
        
        # تحريك الإحداثيات للكلمة التالية
        current_x += word_w + (main_txt.w / total_chars)

# 4. التصدير بجودة عالية وحجم متوازن
final_video = CompositeVideoClip(final_clips)
final_video.write_videofile(
    "output.mp4", 
    codec="libx264", 
    audio_codec="aac", 
    fps=video.fps,
    bitrate="5000k", 
    preset="medium"
)
