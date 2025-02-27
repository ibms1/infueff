import streamlit as st
from PIL import Image
import numpy as np
import tempfile
import cv2
import os

def apply_effects(image, effect):
    if effect == "قزم":
        return image.resize((int(image.width), int(image.height / 2)))
    elif effect == "عملاق":
        return image.resize((int(image.width), int(image.height * 2)))
    elif effect == "ملون وخلفية رمادية":
        # تحويل الصورة إلى رمادية
        gray_image = np.array(image.convert("L"))
        # نسخ الصورة الرمادية إلى القنوات الثلاث
        result = np.stack((gray_image,) * 3, axis=-1)
        return Image.fromarray(result)
    elif effect == "خلفية نارية":
        fire_image = np.array(image)
        fire_overlay = np.full(fire_image.shape, [255, 0, 0], dtype=np.uint8)  # لون ناري
        blended = cv2.addWeighted(fire_image, 0.7, fire_overlay, 0.3, 0)
        return Image.fromarray(blended)
    elif effect == "خلفية جليدية":
        ice_image = np.array(image)
        ice_overlay = np.full(ice_image.shape, [173, 216, 230], dtype=np.uint8)  # لون جليدي
        blended = cv2.addWeighted(ice_image, 0.7, ice_overlay, 0.3, 0)
        return Image.fromarray(blended)
    return image

st.title("تطبيق مؤثرات الفيديو")

uploaded_file = st.file_uploader("اختر ملف فيديو", type=["mp4", "mov"])

if uploaded_file is not None:
    # حفظ الملف المرفوع مؤقتًا
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    # فتح الفيديو باستخدام المسار المؤقت
    video_capture = cv2.VideoCapture(tfile.name)
    
    if not video_capture.isOpened():
        st.error("فشل في فتح الفيديو.")
    else:
        effect = st.selectbox("اختر المؤثر", ["قزم", "عملاق", "ملون وخلفية رمادية", "خلفية نارية", "خلفية جليدية"])
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        
        if st.button("تطبيق المؤثر"):
            with st.spinner("يتم معالجة الفيديو..."):
                frames = []
                while True:
                    ret, frame = video_capture.read()
                    if not ret:
                        break
                    
                    # تحويل الإطار إلى صيغة RGB
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    
                    # تطبيق المؤثر
                    processed_image = apply_effects(image, effect)
                    
                    # إضافة الإطار المعالج إلى القائمة
                    frames.append(np.array(processed_image))
                
                # إغلاق الفيديو الأصلي
                video_capture.release()
                
                if frames:
                    # حفظ الفيديو الناتج
                    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                    
                    # الحصول على أبعاد الإطار المعالج
                    height, width = frames[0].shape[:2]
                    
                    # إنشاء كاتب الفيديو
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output_file.name, fourcc, fps if fps > 0 else 20.0, (width, height))
                    
                    # كتابة الإطارات
                    for frame in frames:
                        # التأكد من أن الإطار بصيغة BGR قبل الكتابة
                        out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    
                    # إغلاق كاتب الفيديو
                    out.release()
                    
                    # عرض الفيديو الناتج
                    st.video(output_file.name)
                else:
                    st.error("لم يتم التقاط أي إطارات من الفيديو.")
    
    # حذف الملف المؤقت
    os.unlink(tfile.name)