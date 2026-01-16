"""View paper screen."""
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Static, Label, Header
from textual import on

import webbrowser


class ViewPaperScreen(Screen):
    """Screen for viewing paper details."""

    CSS = """
    Vertical {
        layout: vertical;
        height: 100%;
    }

    ScrollableContainer {
        height: 100%;
    }

    Horizontal {
        dock: bottom;
        height: auto;
        padding: 1;
    }
    """

    def __init__(self, paper):
        super().__init__()
        self.paper = paper

    def compose(self):
        yield Header()
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
        with Horizontal():
            yield Button("Download PDF", id="download", variant="primary")
            yield Button("Open in Browser", id="open_browser")
            yield Button("Back", id="back")

        yield Static("Arxiv SDK v0.2.0", classes="footer")

    @on(Button.Pressed, "#download")
    async def download_pdf(self):
        """Download the PDF."""
        try:
            path = await self.app.client.download_pdf(self.paper, self.app.downloads_path)
            self.app.notify(f"Downloaded to {path}", severity="information")
        except Exception as e:
            self.app.notify(f"Download failed: {e}", severity="error")

    @on(Button.Pressed, "#open_browser")
    def open_in_browser(self):
        """Open PDF in browser."""
        if self.paper.pdf_url:
            webbrowser.open(self.paper.pdf_url)
            self.app.notify("Opened in browser", severity="information")
        else:
            self.app.notify("No PDF URL available", severity="error")

    @on(Button.Pressed, "#back")
    def back(self):
        """Go back."""
        self.app.pop_screen()