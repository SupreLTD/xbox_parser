import schedule
import time

import game_parser

import xparser

schedule.every().day.at('03:00').do(xparser.parse)
schedule.every().day.at('05:00').do(game_parser.slow_parse)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)
