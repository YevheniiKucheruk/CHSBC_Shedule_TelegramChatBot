from bot.handlers import bot,init_db, initialize_scheduler

def main():
    init_db()

    initialize_scheduler()

    bot.polling()

if __name__ == '__main__':
    main()