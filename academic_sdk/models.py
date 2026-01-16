"""Shared models for academic SDKs."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Link(BaseModel):
    """A link associated with a paper."""
    href: str
    title: Optional[str] = None
    rel: Optional[str] = None


class Author(BaseModel):
    """An author of a paper."""
    name: str
    affiliations: Optional[List[str]] = None


class Paper(BaseModel):
    """Base model for a scholarly paper."""
    id: str
    title: str
    summary: Optional[str] = None  # Abstract
    authors: List[Author] = Field(default_factory=list)
    published: Optional[datetime] = None
    updated: Optional[datetime] = None
    doi: Optional[str] = None
    links: List[Link] = Field(default_factory=list)
    
    # Optional fields for extensibility
    primary_category: Optional[str] = None  # arXiv
    categories: Optional[List[str]] = None  # arXiv
    venue: Optional[str] = None  # Semantic Scholar
    year: Optional[int] = None  # Semantic Scholar
    citation_count: Optional[int] = None  # Semantic Scholar
    influential_citation_count: Optional[int] = None  # Semantic Scholar
    open_access_pdf: Optional[Dict[str, Any]] = None  # Semantic Scholar
    references: Optional[List[Dict[str, Any]]] = None  # Semantic Scholar
    citations: Optional[List[Dict[str, Any]]] = None  # Semantic Scholar
    tldr: Optional[Dict[str, Any]] = None  # Semantic Scholar TL;DR