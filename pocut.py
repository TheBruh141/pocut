from pocut import parse_args
from pocut.app import PocutApp

if __name__ == "__main__":
    args = parse_args()

    app = PocutApp(debug=args.debug, dump_dom=args.dump_dom)
    app.run()
