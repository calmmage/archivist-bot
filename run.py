import argparse
from archivist_bot.app import main

def parse_args():
    parser = argparse.ArgumentParser(description="Archivist Telegram Bot")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(debug=args.debug)
