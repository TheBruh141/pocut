from pocut import parse_args
from pocut.app import PocutApp

import sys
import warnings


def check_version() -> bool:
    """
    Checking Python version:

    Notes for development:
        This function is here because I don't want to create a potential cyclical import from
        pocut.utils, if you can find a better way to position this for better clarity. Go ahead, I will be merged.

    :return: bool

    """

    expect_major = 3
    expect_minor = 13
    expect_rev = 1
    if sys.version_info[:3] != (expect_major, expect_minor, expect_rev):
        print(
            "INFO: Script developed and tested with Python "
            + str(expect_major)
            + "."
            + str(expect_minor)
            + "."
            + str(expect_rev)
        )
        current_version = (
            str(sys.version_info[0])
            + "."
            + str(sys.version_info[1])
            + "."
            + str(sys.version_info[2])
        )
        if sys.version_info[:2] != (expect_major, expect_minor):
            warnings.warn(
                "Current Python version was unexpected: Python " + current_version
            )
            return False
        else:
            print("      Current version is different: Python " + current_version)

            return True


if __name__ == "__main__":
    compatible_version = check_version()
    args = parse_args()
    if compatible_version == False and not args.untested:
        raise SystemExit("Unexpected Python version")
    # print(compatible_version, args.untested)
    app = PocutApp(debug=args.debug, dump_dom=args.dump_dom)
    app.run()
