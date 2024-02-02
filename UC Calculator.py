from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CallbackContext, CommandHandler

WIFE_SALARY, MY_SALARY = range(2)

async def start_command(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Make Calculation", callback_data='make_calculation')],
        [InlineKeyboardButton("Cancel", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Hello, I'm here to help you with your Universal Credit calculation. Please use the provided buttons to start the calculation or cancel.",
        reply_markup=reply_markup
    )
    return WIFE_SALARY

async def handle_make_calculation(update: Update, context: CallbackContext):
    await update.callback_query.answer()  # Answer the callback query
    await update.callback_query.edit_message_text("Enter the salary of your wife:")
    return WIFE_SALARY

async def handle_cancel(update: Update, context: CallbackContext):
    await update.callback_query.answer()  # Answer the callback query
    await update.callback_query.edit_message_text("Calculation cancelled.")
    return ConversationHandler.END

async def get_wife_salary(update: Update, context: CallbackContext):
    try:
        context.user_data['wife_salary'] = float(update.message.text)
        await update.message.reply_text("Enter your salary:")
        return MY_SALARY
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a valid salary.")
        return WIFE_SALARY

async def get_my_salary(update: Update, context: CallbackContext):
    try:
        context.user_data['my_salary'] = float(update.message.text)
        result = calculate_universal_credit_function(context.user_data['wife_salary'], context.user_data['my_salary'], 1396.70)
        reply_text = f"Total payment for the month: {result:.2f}"

        # Add the "Make Calculation" button after displaying the result
        keyboard = [
            [InlineKeyboardButton("Make Calculation", callback_data='make_calculation')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(reply_text, reply_markup=reply_markup)
        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a valid salary.")
        return MY_SALARY

def calculate_universal_credit_function(wife_salary, my_salary, total_uc_payment) -> float:
    first_take_home_pay = 379.00
    total_take_home_pay = wife_salary + my_salary
    total_payment_for_month = total_uc_payment - ((total_take_home_pay - first_take_home_pay) * 0.55)
    return total_payment_for_month

TOKEN: Final = "6436610184:AAGxBNdiwzrM_dpz5ztFHquGfKRo6UMGG8g"

if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Add handlers for the "Make Calculation" and "Cancel" buttons
    app.add_handler(CallbackQueryHandler(handle_make_calculation, pattern='^make_calculation$'))
    app.add_handler(CallbackQueryHandler(handle_cancel, pattern='^cancel$'))

    # Create a ConversationHandler with two states: WIFE_SALARY and MY_SALARY
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            WIFE_SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wife_salary)],
            MY_SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_my_salary)],
        },
        fallbacks=[],
    )

    # Add the ConversationHandler to the application
    app.add_handler(conversation_handler)

    # Run the bot
    app.run_polling()
