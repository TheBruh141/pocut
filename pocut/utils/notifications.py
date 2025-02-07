"""
This file handles notifications sent by pocut.
Please note that we are tyring to be cross compatible all the time.
"""

import os


def notify(title, message) -> None:
    """
    Send a notification (cross-platform).
    :param title:
    :param message:
    :return: None
    """
    if os.name == "nt":
        notify_windows(title, message)
        return
    else:
        notify_linux(title, message)
        return


def notify_windows(title, message) -> None:
    """
    Send a notification (windows).
    :param title:
    :param message:
    :return:
    """
    os.system(
        f'''osascript -e 'display notification "{message}" with title "{title}"'''
    )


def notify_linux(title, message) -> None:
    """
    Send a notification (linux).
    :param title:
    :param message:
    :return:
    """
    os.system("notify-send {} {}".format(title, message))


if __name__ == "__main__":

    print(f"system is => {"Windows" if os.name == 'nt' else "Linux"}")
    notify("Pocut", "test")
    print("sent notification")
