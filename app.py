from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
# مفتاح سري لإدارة الجلسات
app.secret_key = 'cybersecurity_drill_secret_key'

# تهيئة قاعدة البيانات لحفظ الإيميلات التي وقعت في الفخ
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agreements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            agreed_status TEXT NOT NULL,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 1. المسار الرئيسي (/) - تم تعديله ليجبر المستخدم على صفحة تسجيل الدخول أولاً
@app.route('/')
def index():
    # إذا لم يكتب المستخدم إيميله بعد، يتم تحويله إجبارياً لصفحة تسجيل الدخول
    if 'phished_user' not in session:
        return redirect(url_for('login'))
    
    # إذا سجل إيميله ووقع في الفخ، تظهر له رسالة التوعية الأمنية
    return render_template('index.html')

# 2. مسار صفحة تسجيل الإيميل الخادعة
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_ip = request.remote_addr
        
        # حفظ الإيميل والـ IP مباشرة بمجرد الضغط على زر "التالي"
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO agreements (email, agreed_status, ip_address)
            VALUES (?, ?, ?)
        ''', (user_email, 'Phished (Caught)', user_ip))
        conn.commit()
        conn.close()
        
        # وضع علامة في المتصفح تفيد بأن المستخدم أكمل التسجيل لكي تفتح له صفحة التنبيه
        session['phished_user'] = user_email
        
        # توجيه المستخدم فوراً إلى صفحة الفخ الرئيسية
        return redirect(url_for('index'))
        
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)