from loguru import logger

from pocut import parse_args, configure_logging
from pocut.app import PocutApp

if __name__ == "__main__":
    args = parse_args()
    configure_logging(args.debug, args.log_file, args.max_debug_file_size)

    logger.debug("Starting PocutApp...")
    app = PocutApp(debug=args.debug)
    app.run()
