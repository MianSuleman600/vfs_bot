import argparse
from vfs_bot.factory import VFSBotFactory
from utils.logger import setup_logging

logger = setup_logging()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--country', required=True, help='Country code, e.g. NO, PK')
    args = parser.parse_args()

    bot = VFSBotFactory.get_bot(args.country)

    logger.info(f"Bot started for {args.country}. Polling for updates...")
    bot.run()  # <-- this handles the Telegram app internally

if __name__ == '__main__':
    main()
