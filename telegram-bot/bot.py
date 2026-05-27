import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from keyboards import (
    back_to_main_keyboard,
    cancel_keyboard,
    category_back_keyboard,
    guests_keyboard,
    main_menu_keyboard,
    menu_categories_keyboard,
)
from menu_data import MENU

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states
ASK_NAME, ASK_DATE, ASK_GUESTS, ASK_PHONE = range(4)

RESTAURANT_INFO = (
    "🏛 <b>Ресторан «Империя»</b>\n"
    "<i>Ресторан высокой кухни</i>\n\n"
    "📍 <b>Адрес:</b>\n"
    "42 Невский Променад, Нью-Йорк, NY 10036\n\n"
    "🕐 <b>Часы работы:</b>\n"
    "Пн–Чт: 17:00 – 23:00\n"
    "Пт–Сб: 17:00 – 00:00\n"
    "Вс:      16:00 – 22:00\n\n"
    "📞 <b>Телефон:</b> +1 (212) 555-0194\n"
    "✉️ <b>Email:</b> reservations@imperiya-restaurant.com\n\n"
    "🎻 Живой ансамбль балалайки каждую Пт и Сб с 20:00"
)


# ── Core navigation ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name
    text = (
        f"👋 Добро пожаловать, <b>{name}</b>!\n\n"
        "🏛 <b>Ресторан «Империя»</b> рад приветствовать вас!\n\n"
        "Мы предлагаем изысканную русскую кухню, приготовленную "
        "с любовью и поданную с теплом истинного гостеприимства.\n\n"
        "✦  ─────────────────────  ✦\n\n"
        "Выберите действие:"
    )
    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


async def cb_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏛 <b>Ресторан «Империя»</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📋 <b>Меню «Империи»</b>\n\nВыберите категорию:",
        parse_mode="HTML",
        reply_markup=menu_categories_keyboard(),
    )


async def cb_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    key = query.data.removeprefix("cat_")
    cat = MENU.get(key)
    if not cat:
        await query.answer("Категория не найдена.", show_alert=True)
        return

    await query.answer()

    lines = [f"{cat['emoji']} <b>{cat['label']}</b>\n"]
    for item in cat["items"]:
        lines.append(f"▪️ <b>{item['name']}</b> — {item['price']}")
        lines.append(f"   <i>{item['desc']}</i>\n")

    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=category_back_keyboard(),
    )


async def cb_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        RESTAURANT_INFO,
        parse_mode="HTML",
        reply_markup=back_to_main_keyboard(),
    )


# ── Reservation conversation ──────────────────────────────────────────────────

async def cb_reserve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "📅 <b>Бронирование стола</b> — шаг 1 из 4\n\n"
        "Пожалуйста, введите ваше <b>имя и фамилию</b>:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    return ASK_NAME


async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(
        "📅 <b>Бронирование стола</b> — шаг 2 из 4\n\n"
        "Укажите желаемую <b>дату и время</b> посещения:\n"
        "<i>(например: 15.07.2025, 19:00)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    return ASK_DATE


async def received_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["date"] = update.message.text.strip()
    await update.message.reply_text(
        "📅 <b>Бронирование стола</b> — шаг 3 из 4\n\n"
        "Сколько <b>гостей</b> будет?",
        parse_mode="HTML",
        reply_markup=guests_keyboard(),
    )
    return ASK_GUESTS


async def received_guests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["guests"] = query.data.removeprefix("guests_")
    await query.edit_message_text(
        "📅 <b>Бронирование стола</b> — шаг 4 из 4\n\n"
        "Введите ваш <b>номер телефона</b> для подтверждения:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    return ASK_PHONE


async def received_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["phone"] = update.message.text.strip()
    data = context.user_data

    confirmation = (
        f"✅ Заявка принята!\n\n"
        f"🏛 Ресторан «Империя»\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📅 Дата и время: {data['date']}\n"
        f"👥 Гостей: {data['guests']}\n"
        f"📞 Телефон: {data['phone']}\n\n"
        f"Мы свяжемся с вами для подтверждения в течение 2 часов.\n\n"
        f"Ждём вас! 🥂"
    )
    await update.message.reply_text(
        confirmation,
        reply_markup=main_menu_keyboard(),
    )

    # Forward to admin if configured
    admin_id = os.getenv("ADMIN_CHAT_ID", "").strip()
    if admin_id:
        admin_msg = (
            f"🔔 Новое бронирование — «Империя»\n\n"
            f"👤 Имя: {data['name']}\n"
            f"📅 Дата/время: {data['date']}\n"
            f"👥 Гостей: {data['guests']}\n"
            f"📞 Телефон: {data['phone']}"
        )
        try:
            await context.bot.send_message(
                chat_id=int(admin_id),
                text=admin_msg,
            )
        except Exception as exc:
            logger.warning("Could not notify admin: %s", exc)

    return ConversationHandler.END


async def cancel_reservation_cb(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "❌ Бронирование отменено.\n\nВыберите действие:",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


async def cancel_reservation_cmd(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Бронирование отменено.",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


# ── App assembly ──────────────────────────────────────────────────────────────

def build_app() -> Application:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")

    app = Application.builder().token(token).build()

    reservation_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_reserve, pattern="^reserve$")],
        states={
            ASK_NAME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, received_name)],
            ASK_DATE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, received_date)],
            ASK_GUESTS: [CallbackQueryHandler(received_guests, pattern=r"^guests_")],
            ASK_PHONE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, received_phone)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_reservation_cb, pattern="^cancel_reservation$"),
            CommandHandler("cancel", cancel_reservation_cmd),
        ],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(reservation_conv)
    app.add_handler(CallbackQueryHandler(cb_main,     pattern="^main$"))
    app.add_handler(CallbackQueryHandler(cb_menu,     pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(cb_category, pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(cb_info,     pattern="^info$"))

    return app


def main() -> None:
    app = build_app()
    logger.info("Бот «Империя» запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
