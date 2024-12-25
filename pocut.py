from loguru import logger

from pocut import parse_args
from pocut.app import PocutApp

if __name__ == "__main__":
    args = parse_args()

    logger.debug("Starting PocutApp...")
    app = PocutApp(debug=args.debug)
    app.run()
