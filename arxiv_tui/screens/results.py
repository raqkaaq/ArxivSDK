"""Results screen for displaying search results."""
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Button, Static
from textual import on

from arxiv_sdk.models import ArxivPaper


class ResultsScreen(Screen):
    """Screen for displaying search results in a table."""

    def __init__(self):
        super().__init__()
        self.results = None

    def on_mount(self) -> None:
        """Load results on mount."""
        self.load_results()

    def load_results(self) -> None:
        """Load and display search results."""
        if not hasattr(self.app, 'query') or not hasattr(self.app, 'max_results'):
            self.notify("No search query set", severity="error")
            return

        # Perform search
        import asyncio
        asyncio.create_task(self._do_search())

    async def _do_search(self):
        """Async search."""
        try:
            results = await self.app.client.search(self.app.query, max_results=self.app.max_results)
            self.results = results.entries
            self.display_results()
        except Exception as e:
            self.notify(f"Search failed: {e}", severity="error")

    def display_results(self) -> None:
        """Display results in table."""
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("Title", "Authors", "Date", "Category")
        for paper in self.results:
            authors = ", ".join(a.name for a in paper.authors[:2])  # First 2 authors
            if len(paper.authors) > 2:
                authors += " et al."
            table.add_row(
                paper.title[:50] + "..." if len(paper.title) > 50 else paper.title,
                authors,
                paper.published.strftime("%Y-%m-%d") if paper.published else "N/A",
                paper.primary_category or "N/A",
                key=paper.id  # Use ID as key
            )

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Search Results", classes="title")
            yield DataTable(id="results_table")
            yield Button("Back to Search", id="back")

    @on(DataTable.RowSelected)
    def row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        paper_id = event.row_key
        paper = next((p for p in self.results if p.id == paper_id), None)
        if paper:
            from .details import DetailsScreen
            self.app.push_screen(DetailsScreen(paper))

    @on(Button.Pressed, "#back")
    def back(self) -> None:
        """Go back to search."""
        self.app.pop_screen()