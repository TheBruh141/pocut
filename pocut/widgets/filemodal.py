import os
from textual.events import Key
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Input, DirectoryTree, Static, Button
from pathlib import Path


class FileSelectorModal(ModalScreen[str]):
    """
    A modal screen for selecting a file with a navigable file tree using keyboard keys.
    """

    LAST_SELECTED_FILE_PATH = "last_selected_file.txt"

    def __init__(self, initial_path: str = ".", supported_extensions=None):
        super().__init__()
        self.initial_path = Path(initial_path).resolve()
        self.supported_extensions = supported_extensions or {".mp3", ".wav"}
        self.selected_file = None
        self.last_selected_path = self.load_last_selected_path()

    def compose(self):
        """
        Compose the layout for the file selector modal.
        """
        with Vertical(id="file_selector_modal"):
            yield Label("Select a Sound File", classes="modal-title")
            yield DirectoryTree(path=str(self.initial_path), id="file_tree")
            yield Input(
                value=self.last_selected_path or "",
                id="selected_file_input",
                placeholder="Selected file path",
            )
            yield Static("", id="file_feedback_message")
            with Horizontal(classes="modal-footer"):
                # How to Use Section
                yield Static(
                    "Shortcuts:\n"
                    "↑/↓: Navigate\n"
                    "→: Expand folder\n"
                    "←: Collapse folder\n"
                    "Enter: Confirm\n"
                    "Esc: Cancel",
                    id="file_selector_help",
                )
                yield Button("Confirm", id="confirm_button", variant="primary")

    def load_last_selected_path(self):
        """
        Load the last selected file path from a file, if it exists.
        """
        if os.path.exists(self.LAST_SELECTED_FILE_PATH):
            with open(self.LAST_SELECTED_FILE_PATH, "r") as file:
                return file.read().strip()
        return None

    def save_last_selected_path(self, path):
        """
        Save the last selected file path to a file.
        """
        with open(self.LAST_SELECTED_FILE_PATH, "w") as file:
            file.write(path)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Args:
            event: The button pressed event.
        """
        if event.button.id == "confirm_button":
            if self.selected_file:
                self.save_last_selected_path(self.selected_file)
                self.dismiss(result=self.selected_file)
            else:
                feedback = self.query_one("#file_feedback_message", Static)
                feedback.update(
                    f"❌ No valid file selected. Please select one of the following types: {self.supported_extensions}"
                )

    async def on_directory_tree_file_selected(
            self, event: DirectoryTree.FileSelected
    ) -> None:
        """
        Handle file selection in the directory tree.

        Args:
            event: The `FileSelected` event from the directory tree.
        """
        file_path = event.path
        feedback = self.query_one("#file_feedback_message", Static)

        if file_path.suffix in self.supported_extensions:
            feedback.update("✅ File is valid!")
            self.query_one("#selected_file_input", Input).value = str(file_path)
            self.selected_file = str(file_path)
        else:
            feedback.update(f"❌ Unsupported file type: {file_path.suffix}")
            self.selected_file = None

    async def on_directory_tree_directory_selected(
            self, event: DirectoryTree.DirectorySelected
    ) -> None:
        """
        Handle directory selection in the directory tree.

        Args:
            event: The `DirectorySelected` event from the directory tree.
        """
        feedback = self.query_one("#file_feedback_message", Static)
        feedback.update("❌ Selected item is not a file.")
        self.selected_file = None

    async def on_key(self, event: Key):
        """
        Handle keyboard events for navigation and confirmation.

        Args:
            event: Key press event.
        """
        if event.key == "enter":  # Confirm selection
            if self.selected_file:
                self.save_last_selected_path(self.selected_file)
                self.dismiss(result=self.selected_file)
            else:
                feedback = self.query_one("#file_feedback_message", Static)
                feedback.update(
                    f"❌ No valid file selected. Please select one of the following types: {self.supported_extensions}"
                )
        elif event.key == "escape":  # Cancel selection
            self.dismiss()
