import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعداد النموذج (التعرف التلقائي على اللغة)
model = whisper.load_model("base")
print("جاري تحليل الفيديو واستخراج النصوص...")
result = model.transcribe("video.mp4", word_timestamps=True)

video = VideoFileClip("video.mp4")
clips = []

def fix_text(text):
    # إصلاح النصوص العربية (التشكيل والاتجاه) وترك الإنجليزية كما هي
    reshaped = reshape(text)
    return get_display(reshaped)

# 2. إعدادات التصميم
FONT_SIZE = 26 # حجم الخط صغير كما طلبت
BOTTOM_MARGIN = 0.88 # لإنزال النص للأسفل (88% من ارتفاع الشاشة)

for segment in result['segments']:
    start_t = segment['start']
    duration = segment['end'] - segment['start']
    text_content = segment['text'].strip()

    # إنشاء قصاصة النص
    txt_clip = TextClip(
        fix_text(text_content), 
        fontsize=FONT_SIZE, 
        color='white', 
        font='Arial', # الخط الافتراضي في سيرفرات Ubuntu
        method='caption',
        size=(video.w * 0.8, None) # النص لا يتجاوز 80% من عرض الشاشة
    )
    
    # تحديد الوقت والموقع (في المنتصف وبالأسفل)
    txt_clip = txt_clip.set_start(start_t).set_duration(duration).set_pos(('center', video.h * BOTTOM_MARGIN))
    
    clips.append(txt_clip)

# 3. دمج النصوص مع الفيديو الأصلي وتصديره
print("جاري دمج النصوص وإنتاج الفيديو النهائي...")
final_video = CompositeVideoClip([video] + clips)
final_video.write_videofile("output.mp4", codec="libx264", audio_codec="aac", fps=video.fps)
print("تمت العملية بنجاح!")
