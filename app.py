import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบลงทะเบียนรหัสนักเรียน - สมาคมคุรุสัมพันธ์ฯ", layout="wide")

# ส่วนหัวของโปรแกรม
st.title("🕌 ระบบฐานข้อมูลประจำปี 2570")
st.subheader("สมาคมคุรุสัมพันธ์อิสลามแห่งประเทศไทย ในพระบรมราชูปถัมภ์")
st.write("---")

# ฟังก์ชันสำหรับโหลดข้อมูลจากไฟล์ Excel
@st.cache_data
def load_excel_data():
    try:
        file_name = "data_2570.xlsx"
        df_school = pd.read_excel(file_name, sheet_name="ชื่อโรงเรียนและสถานที่ติดต่อ", skiprows=1)
        return df_school
    except Exception as e:
        # คืนค่าข้อมูลจำลองหากไม่พบไฟล์หรือหาแผ่นงานไม่เจอ
        return pd.DataFrame({
            '*ชื่อโรงเรียน': ['โรงเรียนคุรุสัมพันธ์วิทยา', 'โรงเรียนดารุลอุลูม', 'โรงเรียนมัสยิดเยาวชน'],
            '*หน่วยสอบที่': [1, 2, 3],
            '*เขตการศึกษาที่': [5, 5, 12],
            'จังหวัด': ['กรุงเทพมหานคร', 'นนทบุรี', 'กระบี่']
        })

df_source = load_excel_data()

if 'student_db' not in st.session_state:
    st.session_state.student_db = []

st.header("📝 ฟอร์มลงทะเบียนนักเรียนใหม่ (ปีการศึกษา 2569)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏫 ข้อมูลสังกัด/โรงเรียน")
    school_options = df_source['*ชื่อโรงเรียน'].dropna().unique() if '*ชื่อโรงเรียน' in df_source.columns else ["ไม่พบข้อมูลโรงเรียนในไฟล์ Excel"]
    selected_school = st.selectbox("เลือกโรงเรียน *", options=school_options)
    
    # ดึงข้อมูลหน่วยสอบ เขต จังหวัด อัตโนมัติ
    if selected_school in df_source['*ชื่อโรงเรียน'].values:
        school_info = df_source[df_source['*ชื่อโรงเรียน'] == selected_school].iloc[0]
        exam_unit = str(school_info.get('*หน่วยสอบที่', ''))
        edu_zone = str(school_info.get('*เขตการศึกษาที่', ''))
        province = str(school_info.get('จังหวัด', ''))
    else:
        exam_unit, edu_zone, province = "", "", ""
    
    exam_unit_input = st.text_input("หน่วยสอบที่", value=exam_unit)
    edu_zone_input = st.text_input("เขตการศึกษาที่", value=edu_zone)
    province_input = st.text_input("จังหวัด", value=province)

with col2:
    st.markdown("### 👤 ข้อมูลส่วนตัวนักเรียน")
    student_id = st.text_input("เลขประจำตัวประชาชน / รหัสประจำตัวนักเรียน *", max_chars=13)
    prefix = st.selectbox("คำนำหน้า *", ["เด็กชาย", "เด็กหญิง", "นาย", "นางสาว"])
    first_name = st.text_input("ชื่อ *")
    last_name = st.text_input("นามสกุล *")
    grade = st.selectbox("ระดับชั้นเรียนฟัรดูอีน *", ["ชั้น 1", "ชั้น 2", "ชั้น 3", "ชั้น 4", "ชั้น 5"])
    gender = "ชาย" if prefix in ["เด็กชาย", "นาย"] else "หญิง"

if st.button("💾 บันทึกข้อมูลและออกรหัสนักเรียน", type="primary"):
    if not student_id or not first_name or not last_name:
        st.error("❌ กรุณากรอกข้อมูลส่วนตัวนักเรียนให้ครบถ้วน")
    else:
        running_num = len(st.session_state.student_db) + 1
        standard_student_code = f"2569-{edu_zone_input.zfill(2)}-{exam_unit_input.zfill(3)}-{running_num:04d}"
        
        new_student = {
            "รหัสนักเรียนสมาคมฯ": standard_student_code,
            "เลขประจำตัว": student_id,
            "ชื่อ-นามสกุล": f"{prefix} {first_name} {last_name}",
            "เพศ": gender,
            "ชั้นเรียน": grade,
            "โรงเรียน": selected_school,
            "หน่วยสอบ": exam_unit_input,
            "เขตการศึกษา": edu_zone_input,
            "จังหวัด": province_input,
            "วันที่ลงทะเบียน": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.student_db.append(new_student)
        st.success(f"🎉 ลงทะเบียนสำเร็จ! รหัสนักเรียนคือ: **{standard_student_code}**")

st.write("---")
st.header("📋 รายชื่อนักเรียนฟัรดูอีนที่ลงทะเบียนแล้ว")

if st.session_state.student_db:
    df_result = pd.DataFrame(st.session_state.student_db)
    st.dataframe(df_result, use_container_width=True)
    csv = df_result.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลนักเรียน (.CSV)",
        data=csv,
        file_name='รายชื่อนักเรียนฟัรดูอีน_สมาคมคุรุสัมพันธ์.csv',
        mime='text/csv',
    )
else:
    st.info("💡 ยังไม่มีข้อมูลนักเรียนที่ลงทะเบียนในระบบ")