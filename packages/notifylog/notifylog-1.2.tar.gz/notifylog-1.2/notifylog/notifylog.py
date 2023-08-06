from datetime import datetime

import colorama
import dbus
from bs4 import BeautifulSoup
from colorama import Fore, Style
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


def clean_text(raw_text):
    soup = BeautifulSoup(raw_text, 'html.parser')
    for unwanted in soup(["script", "style", "meta"]):
        unwanted.extract()
    return soup.get_text()


def process_notification(session_bus, signal_message):
    """
    Process message and print payload to stdout.

        session_bus: SessionBus (current login message bus)
        message: SignalMessage (which can be sent or received over a D-Bus)

        Message arguments depend on a member. For the 'org.freedesktop.Notifications.Notify' there are:
            String app_name
            UInt32 replaces_id
            String app_icon
            String summary
            String body
            Array of [String] actions
            Dict of {String, Variant} hints
            Int32 timeout
    """
    if not signal_message.get_member() == "Notify":
        return

    message = signal_message.get_args_list()
    app_title = message[0]
    message_title = message[3]
    message_body = message[4]
    current_time = datetime.now().strftime('%H:%M')
    print(f'---[ {Fore.YELLOW}{app_title}{Style.RESET_ALL} at {current_time} ]---')
    print(f'{message_title}')
    print(f'{clean_text(message_body)}', end='\n\n')


def run():
    colorama.init()

    DBusGMainLoop(set_as_default=True)
    mainloop = GLib.MainLoop()

    bus = dbus.SessionBus()
    bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications'")
    bus.add_message_filter(process_notification)

    print(f'notify-log started...', end='\n\n')
    try:
        try:
            mainloop.run()
        except KeyboardInterrupt:
            raise
    except (KeyboardInterrupt, SystemExit):
        print('\nBuy!')


if __name__ == '__main__':
    run()
