"""Search tab for the TUI."""
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Input, Button, Select, Label, Static, DataTable
from textual_timepiece import DatePicker
from textual import on

from arxiv_sdk.categories import Category, CATEGORY_DESCRIPTIONS


class SearchTab(Vertical):
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
                    yield Label("Category:")
                    yield Select(
                        [(desc, code) for code, desc in CATEGORY_DESCRIPTIONS.items()],
                        prompt="Select category",
                        id="category"
                    )
                    yield Label("Start Date:")
                    yield DatePicker(id="start_date")
                    yield Label("End Date:")
                    yield DatePicker(id="end_date")
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
        abstract = self.query_one("#abstract", Input).value
        category = self.query_one("#category", Select).value
        start_date_picker = self.query_one("#start_date", DatePicker)
        end_date_picker = self.query_one("#end_date", DatePicker)
        start_date = start_date_picker.value.isoformat() if start_date_picker.value else None
        end_date = end_date_picker.value.isoformat() if end_date_picker.value else None
        max_results = int(self.query_one("#max_results", Input).value or 10)

        # Build query
        from arxiv_sdk.query import QueryBuilder
        qb = QueryBuilder()
        if title:
            qb.title(title)
        if author:
            qb.author(author)
        if abstract:
            qb.abstract(abstract)
        if category:
            qb.category(category)
        if start_date and end_date:
            qb.date_range(start_date, end_date)

        # Perform search
        try:
            results = await self.app.client.search(qb, max_results=max_results)
            self.display_results(results.entries)
        except Exception as e:
            self.app.notify(f"Search failed: {e}", severity="error")

    def display_results(self, papers):
        """Display results in table."""
        self.papers = papers
        table = self.query_one("#results_table", DataTable)
        table.clear()
        table.columns.clear()
        table.add_columns("Title", "Authors", "Date", "Category")
        for paper in papers:
            authors = ", ".join(a.name for a in paper.authors[:2])
            if len(paper.authors) > 2:
                authors += " et al."
            table.add_row(
                paper.title[:50] + "..." if len(paper.title) > 50 else paper.title,
                authors,
                paper.published.strftime("%Y-%m-%d") if paper.published else "N/A",
                paper.primary_category or "N/A",
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