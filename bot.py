# TOKEN = "7314638802:AAEGABdxn_p7CiqogkP0T8xcDKZL2pxWzbM"  # 🔹 Tokenni almashtiring
# TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"  # 🔹 Tokenni almashtiring
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# render servar uchun yozildi
import os
from flask import Flask
#----------------------------

import json
import time
import csv
import pandas as pd


TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"
MOVIE_CHANNEL = "@test_uchun_kanall_video_arxiv"
ADMIN_ID = 8936611
SETTINGS_FILE = "settings.json"
USERS_FILE = "users.json"
DATA_FILE = "ratings.json"
REVIEWS_FILE = "reviews.json"

bot = telebot.TeleBot(TOKEN)

# render servar uchun yozildi
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

#----------------------------

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"channels": []}


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file) #----------------------------public dan private kanal uchun
        #json.dump(settings, file, indent=4)


def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            data = json.load(file)
            if isinstance(data, dict):  # Agar dict bo‘lsa, to‘g‘ri yuklandi
                return data
            else:
                return {}  # Agar list yoki boshqa formatda bo‘lsa, bo‘sh dict qaytaramiz
    except FileNotFoundError:
        return {}  # Agar fayl topilmasa, bo‘sh dict qaytarish
    except json.JSONDecodeError:
        return {}  # Agar fayl buzilgan bo‘lsa, bo‘sh dict qaytarish

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)  # Faylni chiroyli formatda saqlash




def load_reviews():
    try:
        with open(REVIEWS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_reviews(reviews):
    with open(REVIEWS_FILE, "w") as file:
        json.dump(reviews, file)



users = load_users()
settings = load_settings()
reviews = load_reviews()


# -------------------------users reyting buyrugi------------------------------------------

def add_review(movie_id, user_id, rating=None, comment=None):
    if movie_id not in reviews:
        reviews[movie_id] = {}
    if user_id not in reviews[movie_id]:
        reviews[movie_id][user_id] = {"rating": None, "comment": None}
    if rating:
        reviews[movie_id][user_id]["rating"] = rating
    if comment:
        reviews[movie_id][user_id]["comment"] = comment
    save_reviews(reviews)












# ---------------------------- start -----------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)  # ID ni string formatga o‘tkazamiz
    users_data = load_users()  # Foydalanuvchilar bazasini yuklash

    # Foydalanuvchini bazaga saqlash
    if user_id not in users_data:
        users_data[user_id] = {
            "id": user_id,
            "first_name": message.chat.first_name,
            "last_name": message.chat.last_name if message.chat.last_name else "",
            "username": message.chat.username if message.chat.username else ""
        }
        save_users(users_data)

    # ✅ Obunani tekshirish (public va private kanallar uchun)
    if not check_subscription(user_id):
        send_subscription_message(user_id)
        return  # Agar foydalanuvchi obuna bo‘lmagan bo‘lsa, uni to‘xtatamiz

    bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi Kino Ko‘dini kiriting:")





#-----------------------------------------

def send_subscription_message(user_id):
    channels = settings.get("channels", [])  # JSON fayldan kanallar ro‘yxatini yuklash
    if not channels:
        bot.send_message(user_id, "⚠️ Hozircha obuna bo‘lish uchun kanallar mavjud emas!")
        return

    markup = InlineKeyboardMarkup()

    for channel in channels:
        if channel.startswith("@"):  # Public kanal
            markup.add(InlineKeyboardButton("🔗 Public Kanalga o'tish", url=f"https://t.me/{channel[1:]}"))
        else:  # Private kanal
            markup.add(InlineKeyboardButton("🔐 Private Kanalga o'tish", url="https://t.me/+OhAcUEHKo_AxM2My"))

    markup.add(InlineKeyboardButton("✅ Tasdiqlash",
                                    callback_data="check_subs"))  # **confirm_join o‘rniga check_subs ishlatiladi!**
    bot.send_message(user_id, "🔹 Iltimos, quyidagi kanallarga obuna bo‘ling va 'Tasdiqlash' tugmasini bosing:",
                     reply_markup=markup)




#-----------------------------------------

def check_subscription(user_id):
    channels = settings.get("channels", [])  # JSON dan kanallarni yuklaymiz

    for channel in channels:
        try:
            member = bot.get_chat_member(channel, user_id)  # Public kanal uchun ishlaydi
            if member.status not in ["member", "administrator", "creator"]:
                return False  # Foydalanuvchi kanalga azo emas
        except Exception as e:
            print(f"❌ Obunani tekshirishda xatolik: {e}")
            return False  # Xatolik bo‘lsa ham, foydalanuvchini obuna bo‘lmagan deb qabul qilamiz

    return True  # Agar foydalanuvchi barcha kanallarga obuna bo‘lsa, True qaytariladi




#-----------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def callback_check_subs(call):
    user_id = call.message.chat.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id  # Tugmalarni o‘zgartirish uchun message_id kerak

    if check_subscription(user_id):
        # Xabarni tugmalarni olib tashlab yangilash
        bot.edit_message_text("✅ Siz barcha kanallarga a’zo bo‘ldingiz! Endi kino ko‘dini kiriting:", chat_id,
                              message_id)
    else:
        send_subscription_message(user_id)  # Agar obuna bo'lmagan bo'lsa, qaytadan tasdiqlashni so‘raymiz

    bot.answer_callback_query(call.id)  # Callbackni javoblash



# ---------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "confirm_join")
def confirm_join(call):
    user_id = call.message.chat.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    bot.edit_message_text("✅ Siz kanalga qo‘shilgan deb qabul qilindi! Endi kino ko‘dini kiriting.", chat_id, message_id)
    bot.answer_callback_query(call.id)







# ---------------------------------------------- kino jonatish --------------
@bot.message_handler(func=lambda message: message.text.isdigit())  # Faqat son qabul qiladi
def send_movie(message):
    user_id = message.chat.id
    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        for channel in settings.get("channels", []):
            markup.add(InlineKeyboardButton(f"🔗 Kanalga o'tish", url=f"https://t.me/{channel[1:]}"))
        markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
        bot.send_message(user_id, "❌ Avval quyidagi kanallarga obuna bo‘ling va tasdiqlang!", reply_markup=markup)
        return

    message_id = int(message.text.strip())
    try:
        markup = InlineKeyboardMarkup()

        markup.row(
            InlineKeyboardButton("1⭐", callback_data=f"rate_{message_id}_1"),
            InlineKeyboardButton("2⭐", callback_data=f"rate_{message_id}_2"),
            InlineKeyboardButton("3⭐", callback_data=f"rate_{message_id}_3"),
            InlineKeyboardButton("4⭐", callback_data=f"rate_{message_id}_4"),
            InlineKeyboardButton("5⭐", callback_data=f"rate_{message_id}_5")
        )
        markup.add(InlineKeyboardButton("💬 Fikr qoldirish", callback_data=f"review_{message_id}"))
        markup.add(InlineKeyboardButton("📤 Do‘stlarga ulashish", switch_inline_query=str(message_id)))

        # 🔹 protect_content=True qo'shildi
        bot.copy_message(user_id, MOVIE_CHANNEL, message_id, reply_markup=markup, protect_content=True)

    except Exception:
        bot.send_message(user_id, "❌ Bunday Ko'd topilmadi yoki video mavjud emas!")


#----------------------ID video jonatish--------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data.startswith("rate_"))
def rate_movie(call):
    _, movie_id, rating = call.data.split("_")
    add_review(movie_id, call.message.chat.id, rating=int(rating))
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Fikr qoldirish", callback_data=f"review_{movie_id}"))
    markup.add(InlineKeyboardButton("📤 Do‘stlarga ulashish", switch_inline_query=str(movie_id)))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, "Bahoyingiz qabul qilindi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("review_"))
def ask_review(call):
    movie_id = call.data.split("_")[1]
    msg = bot.send_message(call.message.chat.id, "Fikringizni yozing:")
    bot.register_next_step_handler(msg, save_review, movie_id)


# ✅ Fikrni saqlash

#def save_review(message, movie_id):
#    user_id = message.chat.id
#    review_text = message.text
#
#    add_review(movie_id, user_id, comment=review_text)  # Fikrni saqlaymiz
#
#    bot.send_message(user_id, "✅ Fikringiz saqlandi!")
#
    # Adminni xabardor qilish
#    markup = InlineKeyboardMarkup()
#    markup.add(InlineKeyboardButton("✏️ Javob qaytarish", callback_data=f"reply_{user_id}_{movie_id}"))
#
#    bot.send_message(ADMIN_ID, f"📩 Yangi fikr:\n🎬 Kino ID: {movie_id}\n👤 User ID: {user_id}\n💬 {review_text}",
#                     reply_markup=markup)

def save_review(message, movie_id):
    user_id = message.chat.id
    first_name = message.chat.first_name
    last_name = message.chat.last_name if message.chat.last_name else "N/A"
    username = message.chat.username if message.chat.username else "N/A"
    review_text = message.text

    add_review(movie_id, user_id, comment=review_text)  # Fikrni saqlaymiz

    bot.send_message(user_id, "✅ Fikringiz saqlandi!")

    # Adminni xabardor qilish
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✏️ Javob qaytarish", callback_data=f"reply_{user_id}_{movie_id}"))

    bot.send_message(ADMIN_ID, f"📩 Yangi fikr:\n"
                               f"🎬 Kino ID: {movie_id}\n"
                               f"👤 User ID: {user_id}\n"
                               f"🆔 Username: @{username}\n"
                               f"👤 Ism: {first_name}\n"
                               f"👥 Familiya: {last_name}\n"
                               f"💬 Fikr: {review_text}",
                     reply_markup=markup)













# ---------------------------------------------- admin panel ---------------------------------------

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Reklama", callback_data="reklama"))
        markup.add(InlineKeyboardButton("➕ Kanal qo‘shish", callback_data="add_channel"),
                   InlineKeyboardButton("❌ Kanalni o‘chirish", callback_data="remove_channel"))
        markup.add(InlineKeyboardButton("📋 Kanallar ro‘yxati", callback_data="list_channels"))
        markup.add(InlineKeyboardButton("🔄 Botni qayta ishga tushirish", callback_data="restart"))

        bot.send_message(ADMIN_ID, "⚙️ *Admin Panel* – Kerakli funksiyani tanlang:",
                         parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")


# ---------------------------------------------- admin panel qoshimchasi ---------------------------------------













#----------------------users panel--------------------------------------------

@bot.message_handler(commands=['users'])
def users_panel(message):
    if message.chat.id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⭐ + 💬 Reyting va Fikrlar", callback_data="show_reviews"))
        markup.add(InlineKeyboardButton("👥 Obunachilar soni", callback_data="show_subscribers"))
        markup.add(InlineKeyboardButton("📊 Statistika", callback_data="show_statistics"))
        markup.add(InlineKeyboardButton("🔍 Eng ko‘p baholangan filmlar", callback_data="top_rated_movies"))
        markup.add(InlineKeyboardButton("📈 Foydalanuvchi faolligi", callback_data="user_activity"))
        markup.add(InlineKeyboardButton("📥 Foydalanuvchilarni yuklab olish", callback_data="download_users"))
        markup.add(InlineKeyboardButton("📩 Foydalanuvchi xabarlarini ko‘rish", callback_data="show_messages"))
        #markup.add(InlineKeyboardButton("📢 Xabarlarni kanal/guruhga forward qilishni yoqish", callback_data="enable_forwarding"))

        bot.send_message(ADMIN_ID, "📊 Users Panel", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")


#----------------------------- ⭐ + 💬 Reyting va Fikrlar -------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == "show_reviews")
def show_users_reviews(call):
    if call.message.chat.id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📄 TXT", callback_data="show_reviews_txt"))
        markup.add(InlineKeyboardButton("📑 CSV", callback_data="show_reviews_csv"))
        markup.add(InlineKeyboardButton("📊 Excel", callback_data="show_reviews_xlsx"))

        bot.send_message(ADMIN_ID, "📂 Qaysi formatda yuklab olmoqchisiz?", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")



# 📄 TXT
@bot.callback_query_handler(func=lambda call: call.data == "show_reviews_txt")
def show_users_reviews_txt(call):
    if call.message.chat.id == ADMIN_ID:
        reviews_data = load_reviews()

        with open("reviews.txt", "w", encoding="utf-8") as file:
            for movie_id, users in reviews_data.items():
                file.write(f"🎬 Kino ID: {movie_id}\n")
                for user_id, data in users.items():
                    file.write(f"👤 User {user_id}: {data.get('rating', 'N/A')}⭐ - {data.get('comment', 'N/A')}\n")
                file.write("\n" + "-"*30 + "\n")  # Har bir kino orasiga chiziq qo‘shish

        with open("reviews.txt", "rb") as file:
            bot.send_document(ADMIN_ID, file, caption="📂 Kino reyting va fikrlar (TXT format)")
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")


# 📑 CSV
@bot.callback_query_handler(func=lambda call: call.data == "show_reviews_csv")
def show_users_reviews_csv(call):
    if call.message.chat.id == ADMIN_ID:
        reviews_data = load_reviews()

        with open("reviews.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Kino ID", "Foydalanuvchi ID", "Reyting", "Fikr"])

            for movie_id, users in reviews_data.items():
                for user_id, data in users.items():
                    writer.writerow([
                        movie_id, user_id,
                        data.get("rating", "N/A"),
                        data.get("comment", "N/A")
                    ])

        with open("reviews.csv", "rb") as file:
            bot.send_document(ADMIN_ID, file, caption="📂 Kino reyting va fikrlar (CSV format)")
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")




# 📊 Excel
@bot.callback_query_handler(func=lambda call: call.data == "show_reviews_xlsx")
def show_users_reviews_xlsx(call):
    if call.message.chat.id == ADMIN_ID:
        reviews_data = load_reviews()
        data = []

        for movie_id, users in reviews_data.items():
            for user_id, data_entry in users.items():
                data.append([
                    movie_id, user_id,
                    data_entry.get("rating", "N/A"),
                    data_entry.get("comment", "N/A")
                ])

        df = pd.DataFrame(data, columns=["Kino ID", "Foydalanuvchi ID", "Reyting", "Fikr"])
        df.to_excel("reviews.xlsx", index=False)  # Excel faylga yozish

        with open("reviews.xlsx", "rb") as file:
            bot.send_document(ADMIN_ID, file, caption="📂 Kino reyting va fikrlar (Excel format)")
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")

















#------------------------------------- reklama -----------------------------------------------------

@bot.message_handler(commands=['reklama'])
def reklama(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "📢 Reklama xabarini yuboring (matn, rasm yoki video).")
        bot.register_next_step_handler(message, send_advertisement)
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")


def send_advertisement(message):
    users = load_users()
    for user_id in users:
        try:
            if message.text:
                bot.send_message(user_id, message.text)
            elif message.photo:
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                bot.send_video(user_id, message.video.file_id, caption=message.caption)
        except Exception:
            pass
    bot.send_message(ADMIN_ID, "✅ Reklama barcha foydalanuvchilarga yuborildi!")


# -------------------------- Kanal qo'shish ----------------------------------------------------------------------------

# Kanal qo'shish
@bot.message_handler(commands=['add_channel'])
def add_channel(message):
    if message.chat.id == ADMIN_ID:
        try:
            channel_name = message.text.split()[1]  # Kanal nomi
            channels = settings.get("channels", [])
            if channel_name not in channels:
                channels.append(channel_name)
                settings["channels"] = channels
                save_settings(settings)
                bot.send_message(ADMIN_ID, f"Kanal {channel_name} muvaffaqiyatli qo'shildi.")
            else:
                bot.send_message(ADMIN_ID, f"{channel_name} kanali allaqachon mavjud.")
        except IndexError:
            bot.send_message(ADMIN_ID, "Kanal nomini kiriting: /add_channel @kanal_nomi")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")




#@bot.message_handler(commands=['add_channel'])
#def add_channel(message):
#    if message.chat.id == ADMIN_ID:
#        try:
#            channel_username = message.text.split()[1]  # Kanal nomini olish
#            chat_info = bot.get_chat(channel_username)  # Telegramdan chat ma’lumotini olish
#            channel_id = chat_info.id  # Kanalning chat_id si
#
#            settings = load_settings()
#            channels = settings.get("channels", [])
#
#            if str(channel_id) not in channels:
#                channels.append(str(channel_id))  # ID ni string qilib saqlaymiz
#                settings["channels"] = channels
#                save_settings(settings)
#                bot.send_message(ADMIN_ID, f"✅ Kanal qo‘shildi: {channel_username} ({channel_id})")
#            else:
#                bot.send_message(ADMIN_ID, f"⚠️ {channel_username} allaqachon qo‘shilgan.")
#        except IndexError:
#            bot.send_message(ADMIN_ID, "❌ Xatolik! Kanal qo‘shish uchun: `/add_channel @kanal_nomi`")
#        except Exception as e:
#            bot.send_message(ADMIN_ID, f"❌ Kanalni qo‘shib bo‘lmadi: {e}")
#    else:
#        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")





# -------------------------- Kanalni o'chirish -------------------------------------------------------------------------
# Kanalni o'chirish
@bot.message_handler(commands=['remove_channel'])
def remove_channel(message):
    if message.chat.id == ADMIN_ID:
        try:
            channel_name = message.text.split()[1]  # Kanal nomi
            channels = settings.get("channels", [])
            if channel_name in channels:
                channels.remove(channel_name)
                settings["channels"] = channels
                save_settings(settings)
                bot.send_message(ADMIN_ID, f"Kanal {channel_name} muvaffaqiyatli o'chirildi.")
            else:
                bot.send_message(ADMIN_ID, f"{channel_name} kanali topilmadi.")
        except IndexError:
            bot.send_message(ADMIN_ID, "Kanal nomini kiriting: /remove_channel @kanal_nomi")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

# -------------------------- Mavjud kanallarni ko'rsatish --------------------------------------------------------------

# Mavjud kanallarni ko'rsatish
#@bot.message_handler(commands=['list_channels'])
#def list_channels(message):
#    if message.chat.id == ADMIN_ID:
#        channels = settings.get("channels", [])
#        if channels:
#            bot.send_message(ADMIN_ID, "Mavjud kanallar:\n" + "\n".join(channels))
#        else:
#            bot.send_message(ADMIN_ID, "Hozircha hech qanday kanal mavjud emas.")
#    else:
#        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")


@bot.message_handler(commands=['list_channels'])
def list_channels(message):
    if message.chat.id == ADMIN_ID:
        settings = load_settings()
        channels = settings.get("channels", [])

        if channels:
            bot.send_message(ADMIN_ID, "📌 Qo‘shilgan kanallar:\n" + "\n".join(channels))
        else:
            bot.send_message(ADMIN_ID, "🚫 Hali hech qanday kanal qo‘shilmagan.")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")



#def check_subscription(user_id):
#    channels = settings.get("channels", [])  # JSON fayldan kanallarni yuklash

#    for channel in channels:
#        try:
#            if channel.startswith("@"):  # Public kanal uchun tekshirish
#                member = bot.get_chat_member(channel, user_id)
#                if member.status not in ["member", "administrator", "creator"]:
#                    return False
#            else:  # Private kanallar uchun qo‘lda tasdiqlash talab qilinadi
#                return "manual_check"
#        except Exception as e:
#            print(f"❌ Kanalda tekshirishda xatolik: {e}")
#            return "manual_check"  # Xato bo‘lsa, foydalanuvchi qo‘lda tasdiqlashi kerak

#    return True



#----------------------users panel--------------------------------------------

#----------------------------- ⭐ + 💬 Reyting va Fikrlar -------------------------------------------









#------------------------------- 👥 Botdagi obunachilar soni -------------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == "show_subscribers")
def show_subscribers(call):
    if call.message.chat.id == ADMIN_ID:
        users_data = load_users()  # Foydalanuvchilarni yuklash
        subscribers_count = len(users_data)  # Lug‘at ichidagi elementlar soni
        bot.send_message(ADMIN_ID, f"👥 Botdagi obunachilar soni: {subscribers_count} ta")
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")


#------------------------------- 📊 Umumiy statistika -------------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == "show_statistics")
def show_statistics(call):
    if call.message.chat.id == ADMIN_ID:
        users_data = load_users()  # Foydalanuvchilarni yuklash
        reviews_data = load_reviews()  # Fikrlarni yuklash

        total_reviews = sum(len(user_reviews) for user_reviews in reviews_data.values())  # Fikrlar sonini hisoblash
        subscribers_count = len(users_data)  # Obunachilar sonini hisoblash

        bot.send_message(ADMIN_ID, f"📊 Umumiy statistika:\n👥 Obunachilar: {subscribers_count}\n💬 Fikrlar soni: {total_reviews}")
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")



#------------------------------- 🔝 Eng ko‘p baholangan 5 ta film -------------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == "top_rated_movies")
def top_rated_movies(call):
    if call.message.chat.id == ADMIN_ID:
        sorted_movies = sorted(reviews.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        msg = "🔝 Eng ko‘p baholangan 5 ta film:\n"
        for movie_id, users in sorted_movies:
            msg += f"🎬 ID: {movie_id} - {len(users)} ta baho\n"
        bot.send_message(ADMIN_ID, msg)
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")


#------------------------------- 📈 Foydalanuvchi faolligi -------------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == "user_activity")
def user_activity(call):
    if call.message.chat.id == ADMIN_ID:
        activity_msg = "📈 Foydalanuvchi faolligi:\n"
        for user_id in users:
            reviews_count = sum(1 for movie in reviews.values() if user_id in movie)
            activity_msg += f"👤 User {user_id}: {reviews_count} ta baho yoki fikr\n"
        bot.send_message(ADMIN_ID, activity_msg)
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")



#------------------------------- foydalanuvchilarni yuklash -------------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == "download_users")
def download_users(call):
    if call.message.chat.id == ADMIN_ID:
        users = load_users()  # JSON fayldan foydalanuvchilarni yuklash #---------------------------------------------------

        with open("users.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Ism", "Familiya", "Username"])

            for user_id, user_data in users.items():
                writer.writerow([
                    user_id,
                    user_data.get("first_name", ""),
                    user_data.get("last_name", ""),
                    user_data.get("username", "")
                ])

        with open("users.csv", "rb") as file:
            bot.send_document(ADMIN_ID, file, caption="📂 Foydalanuvchilar CSV fayli")
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")









#---------------------------- Foydalanuvchilarning yozgan xabarlarini saqlash ----------------------

# Xabarlarni kanal/guruhga forward qilishni yoqish
forwarding_enabled = False  # Standart holatda o‘chirilgan


@bot.callback_query_handler(func=lambda call: call.data in ["show_messages", "enable_forwarding"])
def admin_message_actions(call):
    global forwarding_enabled

    if call.data == "show_messages":  # Foydalanuvchi xabarlarini ko‘rsatish (bot ichida)
        send_stored_messages(call.message)

    elif call.data == "enable_forwarding":  # Xabarlarni avtomatik kanal/guruhga forward qilishni yoqish
        forwarding_enabled = not forwarding_enabled
        status = "✅ Yoqildi" if forwarding_enabled else "❌ O‘chirildi"
        bot.send_message(ADMIN_ID, f"📢 Foydalanuvchi xabarlarini kanal/guruhga forward qilish: {status}")

    bot.answer_callback_query(call.id)

#--------------------------------------------


stored_messages = []  # Foydalanuvchilarning yuborgan xabarlarini saqlash

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'voice'])
def store_user_messages(message):
    user_id = message.chat.id

    # ❌ Agar foydalanuvchi `/start` yoki kino kodini (raqam) kiritsa, saqlanmaydi
    if message.text and (message.text.startswith("/") or message.text.isdigit()):
        return

    first_name = message.chat.first_name if message.chat.first_name else "N/A"
    last_name = message.chat.last_name if message.chat.last_name else "N/A"
    username = f"@{message.chat.username}" if message.chat.username else "N/A"

    user_info = f"👤 *{first_name} {last_name}* ({username}) - `{user_id}`"

    # Forward qilingan xabarni tekshiramiz
    if message.forward_from:
        forward_user_id = message.forward_from.id
        forward_first_name = message.forward_from.first_name
        forward_last_name = message.forward_from.last_name if message.forward_from.last_name else "N/A"
        forward_username = f"@{message.forward_from.username}" if message.forward_from.username else "N/A"
        forward_info = (f"↪️ *Forward qilingan foydalanuvchi:*\n"
                        f"👤 *{forward_first_name} {forward_last_name}*\n"
                        f"🆔 *ID:* `{forward_user_id}`\n"
                        f"🔗 *Username:* {forward_username}")
    elif message.forward_sender_name:
        forward_info = f"↪️ *Forward qilingan:* {message.forward_sender_name} (ID mavjud emas)"
    else:
        forward_info = "↪️ Forward qilinmagan"

    msg_data = {"user_info": user_info, "forward_info": forward_info, "type": None, "content": None}

    if message.text:
        msg_data["type"] = "text"
        msg_data["content"] = message.text
    elif message.photo:
        msg_data["type"] = "photo"
        msg_data["content"] = message.photo[-1].file_id
    elif message.video:
        msg_data["type"] = "video"
        msg_data["content"] = message.video.file_id
    elif message.document:
        msg_data["type"] = "document"
        msg_data["content"] = message.document.file_id
    elif message.voice:  # ✅ Ovozli xabarlarni qo‘shish
        msg_data["type"] = "voice"
        msg_data["content"] = message.voice.file_id

    if msg_data["type"] and msg_data["content"]:
        stored_messages.append(msg_data)
    else:
        bot.send_message(ADMIN_ID, "❌ Xatolik: Xabar noto‘g‘ri formatda keldi!")




@bot.message_handler(commands=['messages'])
def send_stored_messages(message):
    if message.chat.id == ADMIN_ID:
        if not stored_messages:
            bot.send_message(ADMIN_ID, "📭 Hech qanday yangi xabar yo‘q!")
        else:
            for msg in stored_messages:
                forward_text = msg.get("forward_info", "↪️ Forward qilinmagan")

                full_caption = f"{msg['user_info']}\n{forward_text}\n"

                if msg["type"] == "text":
                    bot.send_message(ADMIN_ID, full_caption + f"\n💬 {msg['content']}", parse_mode="Markdown")
                elif msg["type"] == "photo":
                    bot.send_photo(ADMIN_ID, msg["content"], caption=full_caption, parse_mode="Markdown")
                elif msg["type"] == "video":
                    bot.send_video(ADMIN_ID, msg["content"], caption=full_caption, parse_mode="Markdown")
                elif msg["type"] == "document":
                    bot.send_document(ADMIN_ID, msg["content"], caption=full_caption, parse_mode="Markdown")
                elif msg["type"] == "voice":  # ✅ Ovozli xabarlar ham yuboriladi
                    bot.send_voice(ADMIN_ID, msg["content"], caption=full_caption, parse_mode="Markdown")

            stored_messages.clear()  # Yuborilgan xabarlarni tozalash
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")


#-------------------------- Admin javob qaytarishi uchun ---------------------------------------

# ruchnoy variant - "/reply user_id movie_id javob_matni"
#@bot.message_handler(commands=['reply'])
#def reply_review(message):
#    args = message.text.split(maxsplit=3)  # /reply user_id movie_id javob_matni
#    if len(args) < 4:
#        bot.send_message(ADMIN_ID, "❌ Noto‘g‘ri format! To‘g‘ri foydalanish: `/reply user_id movie_id javob_matni`")
#        return

#    _, user_id, movie_id, reply_text = args  # Argumentlarni ajratamiz
#    user_id = int(user_id)  # ID ni son formatiga o‘tkazamiz




# Admin tugmani bossa, javob yozishi uchun oynani ochish
@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def ask_admin_reply(call):
    _, user_id, movie_id = call.data.split("_")

    msg = bot.send_message(ADMIN_ID, f"✍️ User {user_id} uchun kino {movie_id} bo‘yicha javob yozing:")

    bot.register_next_step_handler(msg, send_admin_reply, user_id, movie_id)


    # ruchnoy variant - "/reply user_id movie_id javob_matni"
    # Foydalanuvchiga javob yuborish
    #bot.send_message(user_id, f"📩 Sizning fikringizga javob:\n🎬 Kino Ko‘di: {movie_id}\n"
    #                          f"👮‍♂️ Admin: {reply_text}")

    #bot.send_message(ADMIN_ID, "✅ Javob foydalanuvchiga yuborildi!")




def send_admin_reply(message, user_id, movie_id):
    reply_text = message.text  # Adminning yozgan javobi

    bot.send_message(user_id, f"📩 Sizning fikringizga javob:\n🎬 Kino Ko‘di: {movie_id}\n"
                              f"👮‍♂️ Admin: {reply_text}")

    bot.send_message(ADMIN_ID, "✅ Javob foydalanuvchiga yuborildi!")



@bot.message_handler(func=lambda message: message.reply_to_message and "📩 Sizning fikringizga javob" in message.reply_to_message.text)
def notify_admin(message):
    bot.send_message(ADMIN_ID, f"🔔 {message.chat.id} ({message.chat.username}) adminning javobiga munosabat bildirdi:\n"
                               f"💬 {message.text}")




# ---------------------------------------------- admin panel qoshimchasi ---------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    if call.message.chat.id == ADMIN_ID:
        if call.data == "reklama":
            reklama(call.message)
        elif call.data == "add_channel":
            bot.send_message(ADMIN_ID, "➕ Kanal qo‘shish uchun: /add_channel @kanal_nomi")
        elif call.data == "remove_channel":
            bot.send_message(ADMIN_ID, "❌ Kanal o‘chirish uchun: /remove_channel @kanal_nomi")
        elif call.data == "list_channels":
            list_channels(call.message)
        elif call.data == "restart":
            bot.send_message(ADMIN_ID, "♻️ Bot qayta ishga tushirilmoqda... (hozircha qo‘lda qayta ishga tushiring)")
    bot.answer_callback_query(call.id)



# bot.polling(none_stop=True)
# 🔹 Botni doimiy ishlatish
bot.remove_webhook()
bot.infinity_polling()


# render servar uchun yozildi
if __name__ == "__main__":
    # Render tomonidan ajratilgan portni olish
    port = int(os.environ.get("PORT", 5000))  # Agar PORT yo'q bo'lsa, 5000 ni ishlatadi
    app.run(host="0.0.0.0", port=port)  # Flask'ni Render portiga bog‘lash
#----------------------------
