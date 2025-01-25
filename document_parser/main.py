import logging
from src.parser_cli import run

def main():
    logging.basicConfig(level=logging.INFO)
    run()

if __name__ == "__main__":
    main()
