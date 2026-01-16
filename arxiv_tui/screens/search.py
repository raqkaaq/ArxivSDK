"""Search tab for the TUI."""
import calendar
from datetime import datetime

from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Input, Button, Select, Label, Static, DataTable

from textual import on

from arxiv_sdk.categories import Category, CATEGORY_DESCRIPTIONS


class SearchTab(Vertical):
    """Tab for entering search parameters and viewing results."""

    def __init__(self):
        super().__init__()
        self.papers = []
        self.sort_reverse = {}

    def compose(self):
        current_year = datetime.now().year
        year_options = [(str(y), str(y)) for y in reversed(range(2000, current_year + 1))]
        month_options = [(calendar.month_name[m], str(m)) for m in range(1, 13)]
        day_options = [(str(d), str(d)) for d in range(1, 32)]

        with Horizontal():
            with Vertical(id="search_panel"):
                yield Static("Search Papers", classes="title")
                with ScrollableContainer(id="search_scroll"):
                    with Horizontal():
                        with Vertical():
                            yield Label("Title:")
                            yield Input(placeholder="Enter title keywords", id="title")
                        with Vertical():
                            yield Label("Author:")
                            yield Input(placeholder="Enter author name", id="author")
                    with Horizontal():
                        with Vertical():
                            yield Label("Abstract:")
                            yield Input(placeholder="Enter abstract keywords", id="abstract")
                        with Vertical():
                            yield Label("Category:")
                            yield Select(
                                [(desc, code.value) for code, desc in CATEGORY_DESCRIPTIONS.items()],
                                prompt="Select category",
                                id="category"
                            )
                    yield Label("Start Date:")
                    with Horizontal(classes="date-row"):
                        yield Select(year_options, prompt="Year", id="start_year", classes="date-select")
                        yield Select(month_options, prompt="Month", id="start_month", classes="date-select month-select")
                        yield Select(day_options, prompt="Day", id="start_day", classes="date-select")
                    yield Label("End Date:")
                    with Horizontal(classes="date-row"):
                        yield Select(year_options, prompt="Year", id="end_year", classes="date-select")
                        yield Select(month_options, prompt="Month", id="end_month", classes="date-select month-select")
                        yield Select(day_options, prompt="Day", id="end_day", classes="date-select")
                    with Horizontal():
                        with Vertical():
                            yield Label("Max Results:")
                            yield Input(value="10", placeholder="Max results", id="max_results")
                        with Vertical():
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
        start_year_val = self.query_one("#start_year", Select).value
        start_year = int(start_year_val) if start_year_val != Select.BLANK else None
        start_month_val = self.query_one("#start_month", Select).value
        start_month = int(start_month_val) if start_month_val != Select.BLANK else None
        start_day_val = self.query_one("#start_day", Select).value
        start_day = int(start_day_val) if start_day_val != Select.BLANK else None
        end_year_val = self.query_one("#end_year", Select).value
        end_year = int(end_year_val) if end_year_val != Select.BLANK else None
        end_month_val = self.query_one("#end_month", Select).value
        end_month = int(end_month_val) if end_month_val != Select.BLANK else None
        end_day_val = self.query_one("#end_day", Select).value
        end_day = int(end_day_val) if end_day_val != Select.BLANK else None
        max_results = int(self.query_one("#max_results", Input).value or 10)

        # Build dates
        start_date = None
        end_date = None
        if start_year:
            start_month = start_month or 1
            start_day = start_day or 1
            try:
                start_date = datetime(int(start_year), int(start_month), int(start_day))
            except ValueError:
                self.app.notify("Invalid start date", severity="error")
                return
        if end_year:
            end_month = end_month or 12
            if end_month == 12:
                end_day = end_day or 31
            else:
                end_day = end_day or calendar.monthrange(int(end_year), int(end_month))[1]
            try:
                end_date = datetime(int(end_year), int(end_month), int(end_day))
            except ValueError:
                self.app.notify("Invalid end date", severity="error")
                return
        if start_date and end_date and start_date > end_date:
            self.app.notify("Start date must be before or equal to end date", severity="error")
            return
        start_date = start_date.isoformat() if start_date else None
        end_date = end_date.isoformat() if end_date else None

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

    @on(DataTable.HeaderSelected, "#results_table")
    def on_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle header click for sorting."""
        table = self.query_one("#results_table", DataTable)
        column = event.column_index
        reverse = self.sort_reverse.get(column, False)
        if column == 0:  # Title
            key = lambda row: row[0].lower()
        elif column == 1:  # Authors
            key = lambda row: row[1].lower()
        elif column == 2:  # Date
            key = lambda row: datetime.strptime(row[2], "%Y-%m-%d") if row[2] != "N/A" else datetime.min
        elif column == 3:  # Category
            key = lambda row: row[3].lower() if row[3] != "N/A" else ""
        else:
            return
        table.sort(key=key, reverse=reverse)
        self.sort_reverse[column] = not reverse

    @on(DataTable.RowSelected)
    def row_selected(self, event):
        """Handle row selection."""
        paper_id = event.row_key
        paper = next((p for p in self.papers if p.id == paper_id), None)
        if paper:
            from .view_paper import PaperDetailsScreen
            self.app.push_screen(PaperDetailsScreen(paper=paper))