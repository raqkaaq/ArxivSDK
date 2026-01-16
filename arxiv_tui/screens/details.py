"""Details screen for viewing paper details."""
from textual.app import ComposeResult
from textual.containers import Vertical, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Static, Label
from textual import on

from arxiv_sdk.models import ArxivPaper


class DetailsScreen(Screen):
    """Screen for viewing detailed paper information."""

    def __init__(self, paper: ArxivPaper):
        super().__init__()
        self.paper = paper

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Paper Details", classes="title")
            with ScrollableContainer():
                yield Label(f"Title: {self.paper.title}")
                authors = ", ".join(a.name for a in self.paper.authors)
                yield Label(f"Authors: {authors}")
                yield Label(f"Published: {self.paper.published.strftime('%Y-%m-%d') if self.paper.published else 'N/A'}")
                yield Label(f"Updated: {self.paper.updated.strftime('%Y-%m-%d') if self.paper.updated else 'N/A'}")
                yield Label(f"Category: {self.paper.primary_category}")
                yield Label(f"DOI: {self.paper.doi or 'N/A'}")
                yield Label("Abstract:")
                yield Static(self.paper.summary, classes="abstract")
            with Vertical():
                yield Button("Download PDF", id="download", variant="primary")
                yield Button("Back to Results", id="back")

    @on(Button.Pressed, "#download")
    async def download_pdf(self) -> None:
        """Download the PDF."""
        try:
            path = await self.app.client.download_pdf(self.paper, self.app.downloads_path)
            self.notify(f"Downloaded to {path}", severity="information")
        except Exception as e:
            self.notify(f"Download failed: {e}", severity="error")

    @on(Button.Pressed, "#back")
    def back(self) -> None:
        """Go back to results."""
        self.app.pop_screen()