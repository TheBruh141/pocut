from rich.markdown import Markdown
from textual import events, on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Label, Button

from pocut.pages.widgets.common import SmallButton
from pocut.utils import task as t


# TODO: tasks don't update.
class TodoTask(Container, can_focus=True):
    # Note for the wizards that have decided to edit this.
    # we can't have a property named self.task because
    # textual already has a property named task.

    class ShouldCheckDatabase(Message, bubble=True):
        pass

    def __init__(self, task: t.Task, **kwargs):
        super().__init__(**kwargs)
        self.info = task

    def make_all_disabled(self) -> None:
        for widget in self.walk_children():
            widget.disabled = True

    def compose(self) -> ComposeResult:
        with Horizontal(id="task-cluster", classes="task-card"):
            with Vertical(id="task-card"):
                # Task Title
                yield Label(self.info.title, id="title", classes="title")

                # Task Text
                yield Label(self.info.text, id="text", classes="text")

                # Priority and Status
                with Horizontal(classes="task-metadata"):
                    yield Label(f"Priority: {self.info.priority}", classes="priority")
                    status = (
                        "Completed"
                        if self.info.completed
                        else "Ongoing" if self.info.ongoing else "Tracking"
                    )
                    yield SmallButton("Status:", id="status-button")
                    yield Label(f" {status}", classes=f"status-{status.lower()}")

                # Due Date
                if self.info.due_date:
                    yield Label(
                        f"Due: {self.info.due_date.strftime('%Y-%m-%d')}",
                        classes="due-date",
                    )

            #  implement later
            #         # Collapsible Details Section
            #         with Collapsible(title="Details", classes="details"):
            #             with ScrollableContainer():
            #                 yield MarkdownWidget(
            #                     Markdown(
            #                         f"""\
            # ### Task Details
            # - **ID:** {self.info.id or "N/A"}
            # - **Category ID:** {self.info.category_id or "N/A"}
            # - **Attempts:** {self.info.attempts}
            # - **Time Spent:** {self.info.time_spent} minutes
            # - **Recurring:** {"Yes" if self.info.is_daily or self.info.is_weekly or self.info.is_monthly or self.info.is_yearly else "No"}
            #     - **Daily:** {self.info.is_daily}
            #     - **Weekly:** {self.info.is_weekly}
            #     - **Monthly:** {self.info.is_monthly}
            #     - **Yearly:** {self.info.is_yearly}
            # - **Days of Week:** {", ".join(self.info.days_of_week) if self.info.days_of_week else "None"}
            # - **Created At:** {self.info.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            # - **Updated At:** {self.info.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
            #                         """
            #                     ).__str__()
            #                 )
            with Vertical(id="task-status"):
                # yield SmallButton("edit", classes="edit-button", disabled=True)
                yield SmallButton(
                    "\[x]" if self.info.completed == True else "[ ]",
                    id="complete-button",
                    # variant="success" if self.info.completed else "accent",
                    classes="completed" if self.info.completed else "not-completed",
                    disabled=False,
                    tooltip=Markdown(
                        f"**Press me** to make the task {"complete" if self.info.completed else "incomplete" }.\n"
                        "> Note, you need to press enter to access me "
                    ),
                )
                yield SmallButton(
                    label="Delete",
                    id="delete-button",
                    disabled=False,
                    variant="error",
                )

            # yield Digits(self.info.priority.__str__())

    @on(Button.Pressed, "#complete-button")
    def handle_complete_button_press(self, event: Button.Pressed):

        event.button.label = "[ ]" if self.info.completed else "\[x]"
        self.notify("ASDASDA")
        self.post_message(t.TaskData.Complete(self.info))
        pass

    @on(Button.Pressed, "#delete-button")
    def handle_delete_button_press(self, event: Button.Pressed):
        self.post_message(t.TaskData.Delete(self.info))
        self.notify(f"deleted {self.info.title}", severity="information")
        self.remove()
        pass

    @on(Button.Pressed, "#status-button")
    def handle_status_button_press(self, event: Button.Pressed):
        self.notify(f"prev {self.info.ongoing}")
        self.info.ongoing = not self.info.ongoing
        self.post_message(t.TaskData.Update(self.info))
        self.notify(
            f"{"Tracking" if self.info.ongoing else "Stopped Tracking"} {self.info.title}",
            severity="information",
        )
        self.refresh(recompose=True)
        self.notify(f"{self.info.ongoing=}", severity="warning")
