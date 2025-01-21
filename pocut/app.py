import asyncio
import json
import time

from textual import on, events
from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane, Tabs, Button

from pocut import AppState
from pocut.config import DEFAULT_CONFIG_PATH, parse_args
from pocut.pages import PomodoroTab, SettingsTab
from pocut.pages.todo_screen import TodoTab
from pocut.pages.widgets.todo_tab import TodoTask


class PocutApp(App):
    """
    Main application class for the Pomodoro timer.

    Attributes:
        CSS_PATH (str): Path to the application's CSS file.
        BINDINGS (list): Key bindings for the application.
        state (AppState): The shared application state.
    """

    CSS_PATH = "pocut.tcss"
    # BINDINGS = [
    #     ("a", "previous_tab", "Switch to the previous tab"),
    #     ("d", "next_tab", "Switch to the next tab"),
    # ]
    _tabs: TabbedContent

    def __init__(self, debug: bool, dump_dom):
        """
        Initialize the application.

        Args:
            debug (bool): Whether debug mode is enabled.
            dump_dom (str | bool): Whether dom is dumped.
        """
        super().__init__()
        self.pomodoro_tab: PomodoroTab
        self.state = AppState(DEFAULT_CONFIG_PATH, debug_mode=debug)
        self.dump_dom_path = dump_dom
        self.dump_dom_task = None

    async def on_mount(self):
        """
        Called when the app's DOM has been created and is ready for interaction.
        """
        if self.dump_dom_path:
            # Schedule the periodic task to start after the app is fully initialized
            self.call_after_refresh(self.start_dumping_dom)

    def start_dumping_dom(self):
        """
        Start the periodic DOM dumping task.
        """
        self.dump_dom_task = asyncio.create_task(self._schedule_dump_dom())

    async def _schedule_dump_dom(self):
        """
        Periodically dump the DOM every second.
        """
        while True:
            try:
                start_time = time.time()
                self.dump_dom(self.dump_dom_path)  # Ensure this is awaited
                elapsed = time.time() - start_time
                self.notify("DOM dump took {:.2f} seconds.".format(elapsed))
                # Adjust sleep to maintain consistent intervals
                await asyncio.sleep(max(1 - elapsed, 0))
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.notify(f"Error in periodic DOM dumping: {e}", severity="error")

    async def on_shutdown(self):
        """
        Clean up tasks when the app is shutting down.
        """
        if self.dump_dom_task:
            self.dump_dom_task.cancel()
            try:
                await self.dump_dom_task
            except asyncio.CancelledError:
                pass

    def compose(self) -> ComposeResult:
        """
        Compose the app layout.

        Returns:
            ComposeResult: The app layout.
        """
        with TabbedContent(id="the-parent") as tc:
            self._tabs = tc
            with TabPane("Pomodoro", id="pomodoro"):
                self.pomodoro_tab = PomodoroTab(
                    self.state.config_path, self.state.debug_mode
                )
                yield self.pomodoro_tab
            with TabPane("Todos", id="todo_tab"):
                yield TodoTab(self.state)

            with TabPane("Settings", id="settings"):
                yield SettingsTab(self.state)

    def action_set_durations(self, work: int, break_: int) -> None:
        """
        Set the durations for work and break phases.

        Args:
            work (int): Work phase duration in seconds.
            break_ (int): Break phase duration in seconds.
        """
        self.state.work_duration = work
        self.state.break_duration = break_

    def dump_dom(self, dump_dom_file: str):
        """
        Dump the DOM to a file as JSON, showing the hierarchy and all available data.

        Args:
            dump_dom_file (str): The path to the file where the DOM will be dumped.
        """

        def serialize_value(value):
            """
            Serialize a value to make it JSON-serializable.

            Args:
                value: The value to serialize.

            Returns:
                A JSON-serializable representation of the value.
            """
            if isinstance(value, str):
                return value
            elif isinstance(value, (int, float, bool, type(None))):
                return value
            elif hasattr(
                value, "__str__"
            ):  # If the object can be converted to a string
                return str(value)
            else:
                return f"<Unserializable: {type(value).__name__}>"

        def serialize_element(element):
            """
            Serialize a DOM element into a dictionary with all its attributes and children.

            Args:
                element: The DOM element to serialize.

            Returns:
                dict: A dictionary representing the element and its children.
            """
            return {
                "type": str(type(element)),  # Element type
                "id": getattr(element, "id", None),  # Element ID (if it exists)
                "classes": list(getattr(element, "classes", [])),  # Element classes
                "attributes": {
                    key: serialize_value(value)
                    for key, value in getattr(element, "attributes", {}).items()
                },
                "content": serialize_value(
                    getattr(element, "renderable", None)
                ),  # Element content
                "children": [
                    serialize_element(child)
                    for child in getattr(element, "children", [])
                ],  # Recursive children
            }

        try:
            # Serialize the entire DOM hierarchy starting from the root element
            dom_hierarchy = [
                serialize_element(element)
                for element in self.walk_children(with_self=True)
            ]

            # Write the DOM hierarchy to a file as JSON
            with open(dump_dom_file, "w") as file:
                json.dump(
                    {"last_updated": time.time(), "dom": dom_hierarchy}, file, indent=2
                )

            self.notify(
                f"DOM successfully dumped to {dump_dom_file}.", severity="information"
            )
        except Exception as e:
            exit(f"\n\n\n ACTUAL ERROR \nFailed to dump DOM: {e}\n\n\n")

    @on(TodoTask.ShouldCheckDatabase)
    def handle_database_update(self):
        # self.notify("TOP LEVEL")
        self.pomodoro_tab.update_tracker()
