"""Main Textual app for Arxiv TUI."""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual.binding import Binding

from .screens.search import SearchTab
from .screens.semantic_scholar_search import SemanticScholarSearchTab
from .screens.downloads import DownloadsTab
from .screens.view_paper import PaperDetailsScreen


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
        color: $primary;
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
        margin-bottom: 0;
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

    ScrollableContainer {
        scrollbar-size: 0 0;
    }

    ListView {
        scrollbar-size: 0 0;
    }

    #downloads_panel {
        overflow: hidden;
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
        from arxiv_sdk.async_client import AsyncArxivClient
        self.client = AsyncArxivClient()
        from semantic_scholar_sdk.client import SemanticScholarClient
        self.ss_client = SemanticScholarClient()

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Header()
        with TabbedContent():
            with TabPane("ArXiv Search", id="arxiv_search"):
                yield SearchTab()
            with TabPane("Semantic Scholar Search", id="ss_search"):
                yield SemanticScholarSearchTab()
            with TabPane("Downloaded", id="downloads"):
                yield DownloadsTab()
        yield Footer()

    def action_quit(self) -> None:
        """Quit the app."""
        if hasattr(self.client, 'close'):
            import asyncio
            asyncio.create_task(self.client.close())
        self.exit()