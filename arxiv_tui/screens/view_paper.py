"""View paper screen."""
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Static, Label, Header
from textual import on

import webbrowser


class PaperDetailsScreen(Screen):
    """Screen for viewing paper details (searched or downloaded)."""

    CSS = """
    Vertical {
        layout: vertical;
        height: 85%;
        overflow: hidden;
    }

    .content {
        overflow: hidden;
    }

    Horizontal {
        dock: bottom;
        height: auto;
        padding: 1;
    }
    """

    def __init__(self, paper=None, data=None, filename=None, pdf_path=None):
        super().__init__()
        self.paper = paper
        self.data = data
        self.filename = filename
        self.pdf_path = pdf_path

    def compose(self):
        yield Header()
        with Vertical():
            title_text = "Paper Details" if self.paper else f"Downloaded Paper: {self.filename}"
            yield Static(title_text, classes="title")
            with Vertical(classes="content"):
                if self.paper:
                    yield Label(f"Title: {self.paper.title}")
                    authors = ", ".join(a.name for a in self.paper.authors)
                    yield Label(f"Authors: {authors}")
                    yield Label(f"Published: {self.paper.published.strftime('%Y-%m-%d') if self.paper.published else 'N/A'}")
                    yield Label(f"Updated: {self.paper.updated.strftime('%Y-%m-%d') if self.paper.updated else 'N/A'}")
                    yield Label(f"Category: {self.paper.primary_category}")
                    yield Label(f"DOI: {self.paper.doi or 'N/A'}")
                    yield Label("Abstract:")
                    yield Static(self.paper.summary, classes="abstract")
                elif self.data:
                    yield Label(f"Title: {self.data.get('title', 'N/A')}")
                    authors = self.data.get('authors', [])
                    if authors:
                        author_names = ", ".join(a.get('name', '') for a in authors)
                        yield Label(f"Authors: {author_names}")
                    else:
                        yield Label("Authors: N/A")
                    published = self.data.get('published')
                    if published:
                        yield Label(f"Published: {published.strftime('%Y-%m-%d') if hasattr(published, 'strftime') else str(published)}")
                    else:
                        yield Label("Published: N/A")
                    updated = self.data.get('updated')
                    if updated:
                        yield Label(f"Updated: {updated.strftime('%Y-%m-%d') if hasattr(updated, 'strftime') else str(updated)}")
                    else:
                        yield Label("Updated: N/A")
                    yield Label(f"Category: {self.data.get('primary_category', 'N/A')}")
                    yield Label(f"DOI: {self.data.get('doi') or 'N/A'}")
                    yield Label("Abstract:")
                    yield Static(self.data.get('summary', 'No abstract available'), classes="abstract")
        with Horizontal():
            if self.paper:
                yield Button("Download PDF", id="download", variant="primary")
            yield Button("Open in Browser", id="open_browser")
            yield Button("Back", id="back")

    @on(Button.Pressed, "#download")
    async def download_pdf(self):
        """Download the PDF."""
        if self.paper:
            try:
                path = await self.app.client.download_pdf(self.paper, self.app.downloads_path)
                self.app.notify(f"Downloaded to {path}", severity="information")
            except Exception as e:
                self.app.notify(f"Download failed: {e}", severity="error")

    @on(Button.Pressed, "#open_browser")
    def open_in_browser(self):
        """Open PDF in browser."""
        if self.pdf_path:
            # Downloaded paper
            import os
            webbrowser.open(f"file://{os.path.abspath(self.pdf_path)}")
            self.app.notify("Opened in browser", severity="information")
        elif self.paper and self.paper.pdf_url:
            # Searched paper
            webbrowser.open(self.paper.pdf_url)
            self.app.notify("Opened in browser", severity="information")
        else:
            self.app.notify("No PDF URL available", severity="error")

    @on(Button.Pressed, "#back")
    def back(self):
        """Go back."""
        self.app.pop_screen()