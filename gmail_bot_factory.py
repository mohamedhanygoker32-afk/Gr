import time
import os
import random
import string
import telebot
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

# ==========================================
# الإعدادات الأساسية (بوت التليجرام بتاعك)
# ==========================================
BOT_TOKEN = "8859772176:AAE_NnifuLt-dWmXISvnHyfBt0-Ciy36CkI"
YOUR_CHAT_ID = "8570149698"

bot = telebot.TeleBot(BOT_TOKEN)

def generate_random_data():
    ua = UserAgent()
    first_names = ["ahmed", "mohamed", "mahmoud", "ali", "khaled", "ibrahim", "youssef", "hassan"]
    last_names = ["smith", "wilson", "brown", "miller", "taylor", "anderson", "thomas"]
    
    f_name = random.choice(first_names)
    l_name = random.choice(last_names)
    rand_num = ''.join(random.choices(string.digits, k=4))
    
    email = f"{f_name}.{l_name}{rand_num}@gmail.com"
    password = f"P@ssw0rd_{rand_num}!"
    return f_name, l_name, email, password, ua.random

def create_gmail_account():
    f_name, l_name, email, password, user_agent = generate_random_data()
    
    print(f"[*] Trying to create: {email}")
    
    with sync_playwright() as p:
        # تشغيل المتصفح بوضع التخفي (Headless False لو عايز تشوف بعينك، True لو شغال على سيرفر)
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        try:
            # الدخول على صفحة إنشاء حساب جوجل
            page.goto("https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp", timeout=60000)
            
            # ملء الاسم الأول والأخير
            page.fill('input[name="firstName"]', f_name)
            page.fill('input[name="lastName"]', l_name)
            page.click('id=collectNameNext')
            page.wait_for_timeout(3000)
            
            # إدخال تاريخ الميلاد والجنس (عشوائي)
            page.select_option('select[id="month"]', str(random.randint(1, 12)))
            page.fill('id=day', str(random.randint(1, 28)))
            page.fill('id=year', str(random.randint(1995, 2004)))
            page.select_option('select[id="gender"]', '1') # ذكر
            page.click('id=birthdaygenderNext')
            page.wait_for_timeout(3000)
            
            # اختيار أو إدخال الإيميل المقترح
            # (في حال ظهرت صفحة اختيار الإيميل أو كتابته يدوياً)
            try:
                page.click('input[value="custom"]', timeout=3000)
                page.wait_for_timeout(1000)
                page.fill('input[name="Username"]', email.split('@')[0])
                page.click('id=next')
            except:
                # لو اختار تلقائي بنعدي
                pass
                
            page.wait_for_timeout(3000)
            
            # إدخال الباسورد
            page.fill('input[name="Passwd"]', password)
            page.fill('input[name="PasswdAgain"]', password)
            page.click('id=createPasswordNext')
            page.wait_for_timeout(5000)
            
            # فحص هل جوجل طلبت رقم تليفون للتحقق؟ (منطقة الخطر)
            if "phone" in page.url or page.locator('input[id="phoneNumberId"]').is_visible():
                browser.close()
                return False, email, password, "Failed: Google requested Phone Verification (CAPTCHA/SMS)"
                
            browser.close()
            return True, email, password, "Success"
            
        except Exception as e:
            browser.close()
            return False, email, password, f"Error: {str(e)}"

# أمر تليجرام لبدء العملية
@bot.message_handler(commands=['start', 'run_factory'])
def start_bot(message):
    if str(message.chat.id) != str(YOUR_CHAT_ID):
        return
        
    bot.reply_to(message, "[*] Gmail Factory Started! Generating accounts... 6767.")
    
    success_count = 0
    fail_count = 0
    
    # محاولة إنشاء 3 حسابات كموجة أولى (عشان نتجنب الحظر السريع)
    for i in range(3):
        success, email, pwd, status = create_gmail_account()
        
        if success:
            success_count += 1
            msg = f"✅ <b>Gmail Created Successfully!</b>\n📧 <code>{email}</code>\n🔑 <code>{pwd}</code>"
            bot.send_message(YOUR_CHAT_ID, msg, parse_mode='HTML')
        else:
            fail_count += 1
            msg = f"❌ <b>Account Failed!</b>\n📧 <code>{email}</code>\n⚠️️ Status: {status}"
            bot.send_message(YOUR_CHAT_ID, msg, parse_mode='HTML')
            
        # استراحة عشوائية بين الحساب عشان جوجل ما تقفشش البوت
        time.sleep(random.randint(10, 20))
        
    summary = f"📊 <b>Factory Run Summary:</b>\n✅ Success: {success_count}\n❌ Failed: {fail_count}"
    bot.send_message(YOUR_CHAT_ID, summary, parse_mode='HTML')

if __name__ == '__main__':
    print("[*] Gmail Bot Factory is online... absolute fox 🦊 orange.")
    bot.infinity_polling()
