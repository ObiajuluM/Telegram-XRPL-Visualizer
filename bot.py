import random
import time
import telebot
from xrpl.clients import JsonRpcClient
from misc import (
    get_token_info,
    telegram_key,
    welcome_msg,
    enter_acc,
    enter_nft,
    enter_pay,
    enter_token,
    dashboard,
    enter_escrow,
    enter_check,
    enter_nfofer,
    enter_tko,
    get_account_info,get_check_info,
    get_nft_info, pay_txn_info, get_nft_offer_info, get_xrp_escrow_info, get_offer_info
)

bot = telebot.TeleBot(telegram_key, parse_mode="HTML")
client = JsonRpcClient("https://xrplcluster.com")


@bot.message_handler(commands=["start"])
def send_welcome(message: telebot.types.Message):
    bot.reply_to(message, welcome_msg, reply_markup=dashboard)
    bot.send_message(681072070, f"New user: t.me/{message.from_user.username}", disable_notification=False)

@bot.message_handler(func=lambda message: True)
def do_work(message: telebot.types.Message):
    if message.text == "🏧 Payment Transaction":
        pay_txn = bot.reply_to(message, enter_pay)
        bot.register_next_step_handler(pay_txn, do_pay_txn)
    elif message.text == "💳 Account":
        addr = bot.reply_to(message, enter_acc)
        bot.register_next_step_handler(addr, do_acc)
    elif message.text == "🪙 Token":
        token = bot.reply_to(message, enter_token)
        bot.register_next_step_handler(token, do_token)
    elif message.text == "🖼️ NFT":
        nft = bot.reply_to(message, enter_nft)
        bot.register_next_step_handler(nft, do_nft)
    elif message.text == "💹 Token Offer":
        nft = bot.reply_to(message, enter_tko)
        bot.register_next_step_handler(nft, do_nft)
    elif message.text == "🔒 Escrow":
        nft = bot.reply_to(message, enter_escrow)
        bot.register_next_step_handler(nft, do_nft)
    elif message.text == "🧾 Check":
        nft = bot.reply_to(message, enter_check)
        bot.register_next_step_handler(nft, do_nft)
    elif message.text == "🖼️ NFT Offer":
        nft = bot.reply_to(message, enter_nfofer)
        bot.register_next_step_handler(nft, do_nft)
    else:
        bot.send_message(message.chat.id, "I do not undestand the command 🤷")


@bot.message_handler(func=lambda message: True)
def do_acc(message: telebot.types.Message):
    try:
        address = message.text
        bot.send_message(message.chat.id, "Here is a mini game while i do some work in the background.....")
        bot.send_dice(message.chat.id, emoji=random.choice(["🎯", "🎲", "🏀", "⚽", "🎳", "🎰"]))
        time.sleep(3)
        bot.reply_to(message, get_account_info(client, address))
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "oops something went wrong 🤖😭")


@bot.message_handler(func=lambda message: True)
def do_pay_txn(message: telebot.types.Message):
    try:
        txid = message.text
        bot.send_message(message.chat.id, "Here is a mini game while i do some work in the background.....")
        bot.send_dice(message.chat.id, emoji=random.choice(["🎯", "🎲", "🏀", "⚽", "🎳", "🎰"]))
        time.sleep(3)
        bot.reply_to(message, pay_txn_info(client, txid))
    except Exception as e:
        bot.send_message(message.chat.id, "oops something went wrong 🤖😭")


@bot.message_handler(func=lambda message: True)
def do_nft(message: telebot.types.Message):
    try:
        nftid = message.text
        bot.send_message(message.chat.id, "Here is a mini game while i do some work in the background.....")
        bot.send_dice(message.chat.id, emoji=random.choice(["🎯", "🎲", "🏀", "⚽", "🎳", "🎰"]))
        time.sleep(3)
        bot.reply_to(message, get_nft_info(nftid))
    except Exception as e:
        bot.send_message(message.chat.id, "oops something went wrong 🤖😭")

@bot.message_handler(func=lambda message: True)
def do_token(message: telebot.types.Message):
    try:
        token = message.text[0:3]
        issuer = message.text[4::]
        bot.send_message(message.chat.id, "Here is a mini game while i do some work in the background.....")
        bot.send_dice(message.chat.id, emoji=random.choice(["🎯", "🎲", "🏀", "⚽", "🎳", "🎰"]))
        # time.sleep(3)
        bot.reply_to(message, get_token_info(client, issuer, token))
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "oops something went wrong 🤖😭")

@bot.message_handler(func=lambda message: True)
def do_tko(message: telebot.types.Message):
    try:
        tko = message.text
        bot.send_message(message.chat.id, "Here is a mini game while i do some work in the background.....")
        bot.send_dice(message.chat.id, emoji=random.choice(["🎯", "🎲", "🏀", "⚽", "🎳", "🎰"]))
        time.sleep(3)
        bot.reply_to(message, get_offer_info(client, offer_id=tko))
    except Exception as e:
        bot.send_message(message.chat.id, "oops something went wrong 🤖😭")

@bot.message_handler(func=lambda message: True)
def do_escrow(message: telebot.types.Message):
    try:
        escrow = message.text
        bot.send_message(message.chat.id, "Here is a mini game while i do some work in the background.....")
        bot.send_dice(message.chat.id, emoji=random.choice(["🎯", "🎲", "🏀", "⚽", "🎳", "🎰"]))
        time.sleep(3)
        bot.reply_to(message, get_xrp_escrow_info(client, escrow))
    except Exception as e:
        bot.send_message(message.chat.id, "oops something went wrong 🤖😭")

@bot.message_handler(func=lambda message: True)
def do_check(message: telebot.types.Message):
    try:
        check = message.text
        bot.send_message(message.chat.id, "Here is a mini game while i do some work in the background.....")
        bot.send_dice(message.chat.id, emoji=random.choice(["🎯", "🎲", "🏀", "⚽", "🎳", "🎰"]))
        time.sleep(3)
        bot.reply_to(message, get_check_info(client, check))
    except Exception as e:
        bot.send_message(message.chat.id, "oops something went wrong 🤖😭")

@bot.message_handler(func=lambda message: True)
def do_nfofer(message: telebot.types.Message):
    try:
        nfofer = message.text
        bot.send_message(message.chat.id, "Here is a mini game while i do some work in the background.....")
        bot.send_dice(message.chat.id, emoji=random.choice(["🎯", "🎲", "🏀", "⚽", "🎳", "🎰"]))
        time.sleep(3)
        bot.reply_to(message, get_nft_offer_info(nfofer))
    except Exception as e:
        bot.send_message(message.chat.id, "oops something went wrong 🤖😭")


bot.infinity_polling()

