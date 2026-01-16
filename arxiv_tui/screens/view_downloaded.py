"""View downloaded paper screen."""
from textual.containers import Vertical, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Static, Label
from textual import on

import webbrowser
import os


class ViewDownloadedScreen(Screen):
    """Screen for viewing downloaded PDF details."""

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

    def __init__(self, pdf_path, data):
        super().__init__()
        self.pdf_path = pdf_path
        self.data = data

    def compose(self):
        filename = os.path.basename(self.pdf_path)
        with Vertical():
            yield Static(f"Downloaded Paper: {filename}", classes="title")
            with ScrollableContainer():
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
            with Vertical():
                yield Button("Open in Browser", id="open_browser")
                yield Button("Back", id="back")

    @on(Button.Pressed, "#open_browser")
    def open_in_browser(self):
        """Open PDF in browser."""
        webbrowser.open(f"file://{self.pdf_path}")
        self.app.notify("Opened in browser", severity="information")

    @on(Button.Pressed, "#back")
    def back(self):
        """Go back."""
        self.app.pop_screen()