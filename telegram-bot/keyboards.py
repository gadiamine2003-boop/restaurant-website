from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from menu_data import MENU


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Меню", callback_data="menu")],
        [InlineKeyboardButton("📅 Забронировать стол", callback_data="reserve")],
        [InlineKeyboardButton("ℹ️ О ресторане", callback_data="info")],
    ])


def menu_categories_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"{cat['emoji']} {cat['label']}", callback_data=f"cat_{key}")]
        for key, cat in MENU.items()
    ]
    rows.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main")])
    return InlineKeyboardMarkup(rows)


def category_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ К категориям", callback_data="menu")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main")],
    ])


def guests_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1", callback_data="guests_1"),
            InlineKeyboardButton("2", callback_data="guests_2"),
            InlineKeyboardButton("3", callback_data="guests_3"),
            InlineKeyboardButton("4", callback_data="guests_4"),
        ],
        [
            InlineKeyboardButton("5", callback_data="guests_5"),
            InlineKeyboardButton("6", callback_data="guests_6"),
            InlineKeyboardButton("7", callback_data="guests_7"),
            InlineKeyboardButton("8+", callback_data="guests_8+"),
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_reservation")],
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_reservation")],
    ])


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main")],
    ])
