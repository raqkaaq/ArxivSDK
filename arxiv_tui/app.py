"""Main Textual app for Arxiv TUI."""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual.binding import Binding

from .screens.search import SearchTab
from .screens.downloads import DownloadsTab
from .screens.view_paper import ViewPaperScreen


class ArxivTUI(App):
    """Main TUI application for arXiv exploration."""

    CSS = """
    Screen {
        background: $surface;
        padding: 1;
    }

    .title {
        text-align: center;
        margin: 1;
    }

    .abstract {
        height: 10;
        border: solid $primary;
    }

    #search_panel {
        width: 30%;
        padding: 1;
        margin-right: 1;
    }

    #results_panel {
        width: 70%;
        padding: 1;
    }

    Vertical {
        margin-bottom: 1;
    }

    Horizontal {
        margin-bottom: 1;
    }

    Button {
        margin: 0 1 1 0;
    }

    Input {
        margin-bottom: 1;
    }

    Label {
        margin-bottom: 1;
    }

    Select {
        margin-bottom: 1;
    }

    DataTable {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, downloads_path: str = "./data"):
        super().__init__()
        self.downloads_path = downloads_path
        self.client = None  # Will be set based on async availability

    def on_mount(self) -> None:
        """Set up on app start."""
        try:
            from arxiv_sdk.async_client import AsyncArxivClient
            self.client = AsyncArxivClient()
        except ImportError:
            from arxiv_sdk.client import ArxivClient
            self.client = ArxivClient()

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Header()
        with TabbedContent():
            with TabPane("Search", id="search"):
                yield SearchTab()
            with TabPane("Downloaded", id="downloads"):
                yield DownloadsTab()
        yield Footer()

    def action_quit(self) -> None:
        """Quit the app."""
        if hasattr(self.client, 'close'):
            import asyncio
            asyncio.create_task(self.client.close())
        self.exit()