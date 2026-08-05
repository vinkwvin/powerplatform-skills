# .docx mechanics

The gotchas that decide whether the file opens clean everywhere. Tier `PLATFORM` throughout.

## The ones that bite

**Use built-in heading styles.** `HeadingLevel` / `Heading 1`–`Heading 3`. A table of contents
built from custom styles comes out **empty**, and nobody notices until the document is circulated.

**Tables need dual widths.** Set a width on the table *and* on every cell, in absolute units.
Percentage widths break in Google Docs. Column widths should sum to the table width.

**Never a literal `\n`.** Use separate paragraphs. A newline inside a run renders as nothing in
some readers and as a box in others.

**Table shading:** `ShadingType.CLEAR`, never `SOLID` — `SOLID` renders black.

**Lists:** use a numbering definition, never a literal `•` character.

**Images need an explicit type** (`png`, `jpg`) when inserted.

**Page breaks go inside a paragraph**, not between them.

**Don't use a table as a horizontal rule.** Use a paragraph bottom border.

## Validating the package, not just reading it

`python-docx` will happily read a file other readers reject, so "it opened in Python" is not
evidence the file is sound. `validate_manual.py` checks the package itself:

- it is a valid zip, with no corrupt entries
- `[Content_Types].xml`, `_rels/.rels` and `word/document.xml` are present
- every `.xml` and `.rels` part parses
- every `r:id` referenced by `document.xml` exists in `document.xml.rels`

A missing relationship is the classic cause of "Word says the file is corrupt and offers to
repair it" — and it is invisible to a reader that only walks paragraphs.

## On converters disagreeing

If a converter refuses a file, test it against a document known to be good before assuming your
output is broken. In this sandbox, LibreOffice fails to load **both** generated manuals *and* the
shipped reference manual that certainly opens in Word — so the converter is the problem, not the
files.

That is worth checking every time. "Tool X won't open it" and "the file is malformed" are
different claims, and only one of them means you have work to do.
