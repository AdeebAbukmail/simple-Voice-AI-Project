import os
import time
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from gtts import gTTS
import ollama
import serial

# إعداد الاتصال بالأردوينو 
try:
    # ملاحظة لزميلك: غير 'COM3' للمنفذ الصحيح الذي يستخدمه الأردوينو في لابتوبك
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)
    print("🤖 [الإلكترونيات]: تم ربط الروبوت بالأردوينو بنجاح.")
except:
    print("⚠️ تحذير: لم يتم العثور على أردوينو. سيعمل الروبوت صوتياً فقط.")
    arduino = None

def trigger_movement():
    """إرسال إشارة رقمية فورية للأردوينو لتفعيل حركة التحية"""
    if arduino:
        arduino.write(b'H')  
        print("🤖 [حركة]: تم إرسال إشارة الترحيب الرقمية للتحية.")

def speak(text):
    """تحويل رد الروبوت إلى صوت مسموع وسلس متوافق مع نظام التشغيل"""
    tts = gTTS(text=text, lang='ar', slow=False)
    tts.save("reply.mp3")
    # تشغيل ملف الصوت مباشرة عبر مشغل النظام المخفي لضمان التوافق مع بايثون الحديثة
    os.system("start /min reply.mp3")
    # انتظار ديناميكي حتى ينتهي الروبوت من نطق الكلام بالكامل قبل الانتقال للخطوة التالية
    time.sleep(len(text) * 0.28) 

def record_audio_and_listen():
    """تسجيل الصوت من المايكروفون لفترة 8 ثوانٍ"""
    fs = 16000  # معدل العينات القياسي
    duration = 3  # فترة الاستماع 8 ثوانٍ كاملة بناءً على طلبك
    
    print(f"\n👂 [أديب AI]: مستعد وأستمع إليك الآن (تحدث لمدة {duration} ثوانٍ)...")
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # انتظار انتهاء الـ 8 ثوانٍ من التسجيل
    
    wav.write('temp_input.wav', fs, myrecording)
    
    recognizer = sr.Recognizer()
    with sr.AudioFile('temp_input.wav') as source:
        audio = recognizer.record(source)
    
    try:
        if os.path.exists('temp_input.wav'):
            os.remove('temp_input.wav') 
        text = recognizer.recognize_google(audio, language='ar-EG')
        print(f"🗣️ المستخدم قال: {text}")
        return text
    except:
        return ""

def ask_ai(user_question):
    # النص المحدث للنطق الصحيح والسلس تماماً كما أردت في التعديل الأخير
    introduction_text = "مرحباً! أنا أديب ذكاء اصطناعي. تم إنشائي بواسطة أديب أبو كميل، ضمن مخيم أسترو الهندسي، وتحت إشراف مجموعة من المهندسين مثل أحمد المغني وعمار صيام ومهندسين آخرين."
    
    # الرد الفوري المبرمج مسبقاً بالنص المحدث إذا سأله المستخدم عن هويته
    if any(word in user_question for word in ["من أنت", "من انت", "شو اسمك", "من تكون"]):
        return introduction_text

    print("🧠 جاري التفكير عبر النموذج المحلي...")
    try:
        response = ollama.chat(model='gemma2:2b', messages=[
            {'role': 'system', 'content': 'أنت الروبوت أديب ذكاء اصطناعي في مخيم هندسي. يجب أن تجيب باختصار شديد وبجملة واحدة واضحة ومفهومة باللغة العربية الفصحى فقط، ودون استخدام أي رموز تعبيرية أو إيموجي.'},
            {'role': 'user', 'content': user_question}
        ])
        return response['message']['content']
    except:
        return "عذراً يا صديقي، واجهت مشكلة في التوصيل بعقلي المحلي داخل برنامج Ollama."

# --- مرحلة انطلاق الروبوت والتعريف الافتتاحي الفوري عند الـ Run ---
startup_text = "مرحباً! أنا أديب ذكاء اصطناعي. تم إنشائي بواسطة أديب أبو كميل، ضمن مخيم أسترو الهندسي، وتحت إشراف مجموعة من المهندسين مثل أحمد المغني وعمار صيام ومهندسين آخرين."
print(f"\n🚀 [أديب AI]: {startup_text}")
speak(startup_text)  # الروبوت ينطق العبارة فورًا بصوت طبيعي وسلس بمجرد تشغيله (يبدأ بكلمة مرحباً!)

# الحلقة المستمرة لعمل الروبوت صوتياً بعد إلقاء مقدمته المتميزة
print("🤖 الروبوت جاهز الآن لبدء المحادثة التفاعلية المستمرة...")
while True:
    user_input = record_audio_and_listen()
    if user_input:
        # تفعيل الحركة فوراً عند سماع أي تحية من المستخدم
        if any(word in user_input for word in ["أهلاً", "اهلا", "مرحبا", "سلام", "مرحب"]):
            trigger_movement()
            
        ai_reply = ask_ai(user_input)
        print(f"🤖 أديب AI: {ai_reply}")
        speak(ai_reply)
        
    time.sleep(0.5)
