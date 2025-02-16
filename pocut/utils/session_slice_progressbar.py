"""
As of now this file is unused.
I really don't have time to implement this...
"""

from rich.text import Text
from textual.widget import Widget
from textual.reactive import reactive

from pocut.utils.task import SessionSlice


class SessionSlicesProgressBar(Widget, can_focus=False):
    """
    A progress bar widget that renders progress based on session slices.

    This widget supports two distinct modes:
      1. Fallback Mode: When no session slices are provided, the progress bar is rendered as a single,
         uniformly colored bar using the 'total' progress value. The filled portion is rendered in green,
         and the unfilled portion in grey.
      2. Session Slices Mode: When a list of SessionSlice objects is provided, the progress bar is divided
         into segments. Each segment corresponds to a session slice (i.e. a time allocation for a specific
         task) and is rendered with a unique color chosen from a predefined palette. The width of each segment
         is proportional to its allocated time relative to the overall total. If the overall total progress exceeds
         the sum of the allocated times, an additional unallocated segment is rendered in orange.

    The widget also supports dynamic state changes. Session slices can be appended at runtime using the
    'append_slice' method, which automatically refreshes the display.

    CSS Configuration:
      The default CSS sets the widget to auto width, a fixed height of 1 character, and horizontal layout.
    """

    DEFAULT_CSS = """
    SessionSlicesProgressBar {
        width: auto;
        height: 1;
        layout: horizontal;
    }
    """

    progress: reactive[float] = reactive(0.0)
    """Current overall progress (in seconds)."""

    total: reactive[float | None] = reactive(None)
    """The total progress value (in seconds) used in fallback mode or as an upper bound when slices are provided."""

    def __init__(
        self, *, total: float | None = None, slices: list[SessionSlice] = None, **kwargs
    ):
        """
        Initialize the SessionSlicesProgressBar widget.

        Args:
            total (float | None): The overall progress total (in seconds) when no session slices are provided.
                                  If provided alongside slices, it serves as the upper bound for overall progress.
            slices (list[SessionSlice], optional): A list of SessionSlice objects, each representing a task's
                                                   allocated time. Defaults to an empty list if not provided.
            **kwargs: Additional keyword arguments to be passed to the base Widget class.
        """
        super().__init__(**kwargs)
        self.total = total
        self.slices: list[SessionSlice] = slices or []

    def append_slice(self, new_slice: SessionSlice) -> None:
        """
        Dynamically append a new session slice and update the progress bar.

        This method adds a new SessionSlice to the existing list and triggers an immediate refresh of the widget,
        allowing for dynamic updates to the rendered progress.

        Args:
            new_slice (SessionSlice): The session slice object to append.
        """
        self.slices.append(new_slice)
        self.refresh()

    @property
    def computed_slices(self) -> list:
        """
        Retrieve computed rendering details for each session slice.

        Returns:
            list: A list of dictionaries, each containing:
                - allocated: The time allocated for the slice.
                - width: The computed width (in characters) for the slice.
                - filled: The number of characters representing the filled progress.
                - empty: The number of characters representing the unfilled progress.
                - color: The color used for the filled portion of the slice.
        """
        return getattr(self, "_computed_slices", [])

    def render(self) -> Text:
        """
        Render the progress bar as a Rich Text object.

        This method computes and renders the progress bar based on the current progress and the mode in which the
        widget is operating.

        Modes:
          - Fallback Mode: If no session slices are provided, it calculates the filled and empty portions
            based on the 'total' attribute. The filled portion is rendered in green; the empty portion in grey.
          - Session Slices Mode: When session slices are available, each slice's width is computed proportionally
            relative to the overall total (either the sum of slice allocations or the provided 'total', whichever is greater).
            For each slice:
              - The filled portion is calculated relative to its allocated time and rendered in a unique color.
              - The unfilled portion is rendered in grey.
            If there is remaining unallocated time (i.e. overall_total exceeds the sum of allocated times),
            that portion is rendered in orange.

        Returns:
            Text: A Rich Text object representing the rendered progress bar.
        """
        width = self.size.width if self.size.width else 40
        text = Text()
        # Reset computed slices for the current render call.
        self._computed_slices = []

        # Fallback mode: no session slices provided.
        if not self.slices:
            if self.total is None or self.total == 0:
                filled_count = 0
                empty_count = width
            else:
                filled_count = int((self.progress / self.total) * width)
                empty_count = width - filled_count
            text.append("━" * filled_count, style="green")
            text.append("━" * empty_count, style="grey37")
            self._computed_slices.append(
                {
                    "allocated": self.total if self.total is not None else 0,
                    "width": width,
                    "filled": filled_count,
                    "empty": empty_count,
                    "color": "green",
                }
            )
            return text

        # Session slices mode.
        # Calculate total allocated time from slices.
        allocated = sum(s.time_allocated for s in self.slices)
        # Determine overall total: use self.total if provided and greater than the allocated time.
        overall_total = (
            self.total
            if self.total is not None and self.total > allocated
            else allocated
        )
        # Clamp overall progress to overall_total.
        overall_progress = min(self.progress, overall_total)

        # Compute each slice's width proportionally relative to overall_total.
        slices_widths = []
        total_allocated_width = 0
        for s in self.slices:
            slice_width = int((s.time_allocated / overall_total) * width)
            slices_widths.append(slice_width)
            total_allocated_width += slice_width
        # Determine remaining width for unallocated progress if any.
        remainder_width = (
            (width - total_allocated_width) if overall_total > allocated else 0
        )

        colors = ["red", "green", "blue", "yellow", "magenta", "cyan"]

        # Distribute overall progress across slices in order.
        remaining_progress = overall_progress
        for i, (s, slice_width) in enumerate(zip(self.slices, slices_widths)):
            slice_alloc = s.time_allocated
            # For this slice, the progress is at most its allocated time.
            slice_progress = min(remaining_progress, slice_alloc)
            fraction = (slice_progress / slice_alloc) if slice_alloc > 0 else 0
            filled_count = int(fraction * slice_width)
            empty_count = slice_width - filled_count
            slice_color = colors[i % len(colors)]
            text.append("━" * filled_count, style=slice_color)
            text.append("━" * empty_count, style="grey37")
            self._computed_slices.append(
                {
                    "allocated": slice_alloc,
                    "width": slice_width,
                    "filled": filled_count,
                    "empty": empty_count,
                    "color": slice_color,
                }
            )
            remaining_progress -= slice_alloc
            if remaining_progress < 0:
                remaining_progress = 0

        # Render unallocated remainder if overall_total exceeds the allocated slices.
        if remainder_width > 0:
            unallocated_progress = max(self.progress - allocated, 0)
            fraction = (
                (unallocated_progress / (overall_total - allocated))
                if (overall_total - allocated) > 0
                else 0
            )
            filled_count = int(fraction * remainder_width)
            empty_count = remainder_width - filled_count
            remainder_color = "orange"  # Color for unallocated progress.
            text.append("━" * filled_count, style=remainder_color)
            text.append("━" * empty_count, style="grey37")
            self._computed_slices.append(
                {
                    "allocated": overall_total - allocated,
                    "width": remainder_width,
                    "filled": filled_count,
                    "empty": empty_count,
                    "color": remainder_color,
                }
            )

        return text
