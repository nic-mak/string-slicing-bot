import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

from questions import QuestionGenerator


class StringSlicingBot:
    FILENAME_TOKEN = 'token.txt'

    STATE_QUESTION, STATE_ANSWER = range(2)

    def __init__(self):
        # Setup logging config
        self.set_logging_config()

        # Setup question generator
        self.question_generator = QuestionGenerator()
        self.current_question = {}  # Stores current answer to be sent when user replies

        # Setup telegram component
        self.token = self.get_token(self.FILENAME_TOKEN)
        application = ApplicationBuilder().token(self.token).build()
        self.initialise_handlers(application)
        application.run_polling()

    @staticmethod
    def get_token(filename):
        file = open(filename)
        token = file.readline()
        file.close()
        return token

    @staticmethod
    def set_logging_config():
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.effective_chat.username

        text = f"Hi {username}! Welcome to the String Slicing Bot. Please enter /question to start."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        logging.info(
            f"User {update.effective_chat.username}, id: {update.effective_chat.id} has started the bot")

        return self.STATE_QUESTION

    async def command_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Generates question
        question_string, answer_string = self.question_generator.get_question()

        # Stores current question and answer string for user
        user_id = update.effective_chat.id
        self.current_question[user_id] = (question_string, answer_string)

        # Send question to user
        text = f"Question:\n{question_string}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        logging.info(
            f"User {update.effective_chat.username}, id: {update.effective_chat.id} received question {question_string}"
        )

        return self.STATE_ANSWER

    async def command_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id, user_message = update.effective_chat.id, update.effective_message.text
        question_string, answer_string = self.current_question[user_id]

        text = f"Question: {question_string}" \
               f"\nYour Answer: {user_message}" \
               f"\nExpected Answer: {answer_string}" \
               f"\n\nPress /question for another question, or /cancel to exit."

        keyboard = [[KeyboardButton('/question')], [KeyboardButton('/cancel')]]
        keyboard_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard_markup)
        logging.info(
            f"User {update.effective_chat.username}, id: {update.effective_chat.id} answered question {question_string}"
            f" with answer: {user_message}. Expected answer: {answer_string}"
        )

        return self.STATE_QUESTION

    async def command_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Clean up dictionary
        user_id = update.effective_chat.id
        del self.current_question[user_id]

        text = "Thank you for using String Slicing Bot, have a nice day!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        logging.info(
            f"User {update.effective_chat.username}, id: {update.effective_chat.id} has called /cancel")

        return ConversationHandler.END

    def initialise_handlers(self, application) -> None:
        """
        Defines handlers and adds to application
        :param application: ApplicationBuilder() object
        :return: None
        """
        handlers = [
            CommandHandler('start', self.command_start),
            ConversationHandler(
                entry_points=[CommandHandler('question', self.command_question)],
                states={
                    self.STATE_QUESTION: [CommandHandler('question', self.command_question)],
                    self.STATE_ANSWER: [MessageHandler(filters.TEXT, self.command_answer)]
                },
                fallbacks=[CommandHandler("cancel", self.command_cancel)],
                allow_reentry=True
            )
        ]

        for handler in handlers:
            application.add_handler(handler)


if __name__ == '__main__':
    string_slicing_bot = StringSlicingBot()
