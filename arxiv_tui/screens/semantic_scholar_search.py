"""Search tab for the TUI."""
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Input, Button, Label, Static, DataTable
from textual import on


class SemanticScholarSearchTab(Vertical):
    """Tab for entering search parameters and viewing results."""

    def __init__(self):
        super().__init__()
        self.papers = []

    def compose(self):
        with Horizontal():
            with Vertical(id="search_panel"):
                yield Static("Search Papers", classes="title")
                with ScrollableContainer():
                    yield Label("Title:")
                    yield Input(placeholder="Enter title keywords", id="title")
                    yield Label("Author:")
                    yield Input(placeholder="Enter author name", id="author")
                    yield Label("Abstract:")
                    yield Input(placeholder="Enter abstract keywords", id="abstract")
                    yield Label("Venue:")
                    yield Input(placeholder="Enter venue (e.g., arXiv)", id="venue")
                    yield Label("Max Results:")
                    yield Input(value="10", placeholder="Max results", id="max_results")
                    yield Button("Search", id="search", variant="primary")
            with Vertical(id="results_panel"):
                 yield DataTable(cursor_type="row", show_cursor=True, id="results_table")

    @on(Button.Pressed, "#search")
    async def search(self) -> None:
        """Perform search and display results."""
        title = self.query_one("#title", Input).value
        author = self.query_one("#author", Input).value
        venue = self.query_one("#venue", Input).value
        max_results = int(self.query_one("#max_results", Input).value or 10)

        # Build query string
        query_parts = []
        if title:
            query_parts.append(f"title:{title}")
        if author:
            query_parts.append(f"author:{author}")
        if venue:
            query_parts.append(f"venue:{venue}")
        query = " ".join(query_parts) if query_parts else ""

        # Perform search
        try:
            results = await self.app.ss_client.search(query or "machine learning", limit=max_results)
            self.display_results(results)
        except Exception as e:
            self.app.notify(f"Search failed: {e}", severity="error")

    def display_results(self, papers):
        """Display results in table."""
        self.papers = papers
        table = self.query_one("#results_table", DataTable)
        table.clear()
        table.columns = []
        table.add_columns("Title", "Authors", "Year", "Venue")
        for paper in papers:
            authors = ", ".join(a.name for a in paper.authors[:2])
            if len(paper.authors) > 2:
                authors += " et al."
            table.add_row(
                paper.title[:50] + "..." if len(paper.title) > 50 else paper.title,
                authors,
                str(paper.year) if paper.year else "N/A",
                paper.venue or "N/A",
                key=paper.id
            )

    @on(DataTable.RowSelected)
    def row_selected(self, event):
        """Handle row selection."""
        paper_id = event.row_key
        paper = next((p for p in self.papers if p.id == paper_id), None)
        if paper:
            from .view_paper import PaperDetailsScreen
            self.app.push_screen(PaperDetailsScreen(paper=paper))