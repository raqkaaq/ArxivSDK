"""Downloads tab for the TUI."""
import os
import json
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import ListView, ListItem, Label, Button, Static
from textual import on


class DownloadsTab(Vertical):
    """Tab for viewing downloaded papers."""

    def __init__(self):
        super().__init__()
        self.downloads_path = None  # Set by app

    def compose(self):
        self.downloads_path = self.app.downloads_path
        yield Static("Downloaded Papers", classes="title")
        yield ListView(id="downloads_list")

    def on_mount(self):
        self.load_downloads()

    def on_show(self):
        self.load_downloads()

    def load_downloads(self):
        """Load list of downloaded PDFs."""
        if not os.path.exists(self.downloads_path):
            return

        list_view = self.query_one("#downloads_list", ListView)
        list_view.clear()

        for root, dirs, files in os.walk(self.downloads_path):
            for file in files:
                if file.endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.downloads_path)
                    item = ListItem(Label(rel_path))
                    item.path = full_path
                    list_view.append(item)

    @on(ListView.Selected)
    def show_paper(self, event):
        """Show selected paper details."""
        pdf_path = event.item.path
        # Load from JSON metadata
        data = {}
        json_path = pdf_path.replace('.pdf', '.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                self.app.notify(f"Failed to load metadata: {e}", severity="warning")
                data = {'summary': 'Failed to load metadata'}
        else:
            data = {'summary': 'No metadata available'}
        from .view_downloaded import ViewDownloadedScreen
        self.app.push_screen(ViewDownloadedScreen(pdf_path, data))

