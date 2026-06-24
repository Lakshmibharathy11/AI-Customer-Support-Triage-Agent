# src/ingestion/chunker.py

import re
import uuid
from pathlib import Path
from dataclasses import dataclass, field

import yaml


@dataclass
class ParentChunk:
    parent_id: str
    article_id: str
    title: str
    category: str
    department: str
    tier_visibility: list
    section_title: str
    text: str
    has_table: bool


@dataclass
class ChildChunk:
    child_id: str
    parent_id: str
    text: str


def parse_frontmatter(raw_text: str) -> tuple[dict, str]:
    """
    Splits a markdown file into (frontmatter_dict, body_text).
    Expects frontmatter delimited by --- at top of file.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_text, re.DOTALL)
    if not match:
        raise ValueError("No valid YAML frontmatter found")

    frontmatter_raw, body = match.groups()
    metadata = yaml.safe_load(frontmatter_raw)
    return metadata, body.strip()


def split_into_sections(body: str) -> list[tuple[str, str]]:
    """
    Splits article body into (section_title, section_text) pairs
    based on '## ' headers. Drops the top-level '# Title' line.
    """
    # Remove the top-level H1 title line if present
    body = re.sub(r"^#\s+.*\n+", "", body, count=1)

    # Strip any leading '## ' on the very first section before splitting,
    # so the split regex behaves consistently for section 0 as well.
    body = re.sub(r"^##\s+", "", body.strip())

    # Split on '## ' headers, keeping the header text
    raw_sections = re.split(r"\n##\s+", body)

    sections = []
    for chunk in raw_sections:
        chunk = chunk.strip()
        if not chunk:
            continue

        lines = chunk.split("\n", 1)
        section_title = lines[0].strip()
        section_text = lines[1].strip() if len(lines) > 1 else ""

        if section_text:
            sections.append((section_title, section_text))

    return sections


def contains_table(text: str) -> bool:
    """
    Detects a markdown table by looking for the header separator row
    pattern, e.g. | --- | --- |
    """
    return bool(re.search(r"\|\s*-+\s*\|", text))


def split_into_sentences(text: str) -> list[str]:
    """
    Splits prose into sentences for child chunking.
    Tables are NEVER passed through this function directly —
    callers must keep table blocks intact as a single child.
    """
    # Basic sentence splitter: splits on '. ' but avoids breaking
    # on common abbreviations is out of scope for this KB's content.
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def extract_table_block(text: str) -> tuple[str | None, str]:
    """
    If the section text contains a markdown table, extracts the
    table block as one unit and returns (table_block, remaining_text).
    If no table found, returns (None, original_text).
    """
    lines = text.split("\n")
    table_lines = []
    other_lines = []
    in_table = False

    for line in lines:
        is_table_line = line.strip().startswith("|")
        if is_table_line:
            in_table = True
            table_lines.append(line)
        else:
            if in_table and line.strip() == "":
                in_table = False
            if not is_table_line:
                other_lines.append(line)

    if table_lines:
        table_block = "\n".join(table_lines)
        remaining = "\n".join(other_lines)
        return table_block, remaining

    return None, text


def chunk_article(filepath: Path) -> tuple[list[ParentChunk], list[ChildChunk]]:
    """
    Parses one markdown KB article into parent chunks (per section)
    and child chunks (sentences + intact table blocks).
    """
    raw_text = filepath.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(raw_text)

    sections = split_into_sections(body)

    parents: list[ParentChunk] = []
    children: list[ChildChunk] = []

    for section_title, section_text in sections:
        has_table = contains_table(section_text)
        parent_id = str(uuid.uuid4())

        parent = ParentChunk(
            parent_id=parent_id,
            article_id=metadata.get("article_id", filepath.stem),
            title=metadata.get("title", ""),
            category=metadata.get("category", ""),
            department=metadata.get("department", ""),
            tier_visibility=metadata.get("tier_visibility", []),
            section_title=section_title,
            text=section_text,
            has_table=has_table,
        )
        parents.append(parent)

        if has_table:
            table_block, prose_text = extract_table_block(section_text)

            # The table becomes ONE child chunk — never split apart
            if table_block:
                children.append(ChildChunk(
                    child_id=str(uuid.uuid4()),
                    parent_id=parent_id,
                    text=f"{section_title}: {table_block}",
                ))

            # Remaining prose around the table gets sentence-split normally
            for sentence in split_into_sentences(prose_text):
                children.append(ChildChunk(
                    child_id=str(uuid.uuid4()),
                    parent_id=parent_id,
                    text=sentence,
                ))
        else:
            for sentence in split_into_sentences(section_text):
                children.append(ChildChunk(
                    child_id=str(uuid.uuid4()),
                    parent_id=parent_id,
                    text=sentence,
                ))

    return parents, children


def chunk_knowledge_base(kb_root: Path) -> tuple[list[ParentChunk], list[ChildChunk]]:
    """
    Walks every .md file under kb_root (all topic subfolders)
    and chunks them all into combined parent/child lists.
    """
    all_parents: list[ParentChunk] = []
    all_children: list[ChildChunk] = []

    md_files = sorted(kb_root.rglob("*.md"))

    for filepath in md_files:
        parents, children = chunk_article(filepath)
        all_parents.extend(parents)
        all_children.extend(children)

    return all_parents, all_children