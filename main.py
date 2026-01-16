#!/usr/bin/env python3
"""Main entry point for Arxiv TUI."""
import argparse
from arxiv_tui.app import ArxivTUI


def main():
    parser = argparse.ArgumentParser(description="Arxiv TUI - Interactive arXiv Explorer")
    parser.add_argument(
        "--downloads",
        default="./data",
        help="Path to downloads directory (default: ./data)"
    )
    args = parser.parse_args()

    app = ArxivTUI(downloads_path=args.downloads)
    app.run()


if __name__ == "__main__":
    main()