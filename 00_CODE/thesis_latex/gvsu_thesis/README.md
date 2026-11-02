# Unofficial GVSU Thesis LaTeX Template

This is a simple, unofficial LaTeX template for Grand Valley State University theses.
The formatting rules are built into `gvsu-thesis.sty`, so students mainly need to
replace the placeholder text with their own thesis content.

This template is not an official GVSU document. Always compare your final PDF with
the current Graduate School guidelines and any feedback from your reviewer.

## How To Use

1. Open `main.tex`.
2. Replace the metadata at the top:
   - thesis title
   - student name
   - degree
   - college or school
   - graduation month/year
   - committee names
3. Replace the placeholder text in:
   - `frontmatter/`
   - `chapters/`
   - `appendices/`
4. Compile with XeLaTeX:

```powershell
latexmk -xelatex main.tex
```

On Overleaf, set the compiler to **XeLaTeX**.

## What The Template Formats

- 12 pt document text.
- One-inch margins.
- Title page and approval page counted as pages 1 and 2 with no visible page numbers.
- Dedication page begins with visible page number 3.
- Double-spaced text, including front matter before the table of contents.
- Centered major headings at the top of the page.
- Chapter titles include the word `CHAPTER`.
- Chapter 1 includes the commonly expected thesis subsections.
- Table of contents, list of tables, and list of figures spacing.
- Long list entries are single-spaced internally.
- List of abbreviations has double-spaced entries.
- Appendices start with `APPENDICES`, followed immediately by `Appendix A` on the same page.
- Appendix entries are indented in the table of contents.
- Hyperlink boxes are hidden.

## Fonts

The template is strict about Times New Roman by default. Compile with XeLaTeX or
LuaLaTeX, not pdfLaTeX.

If your TeX system cannot find Times New Roman, privately place these files in
`fonts/`:

- `times.ttf`
- `timesbd.ttf`
- `timesi.ttf`
- `timesbi.ttf`

Do not commit those font files to a public GitHub repository unless you have the
legal right to redistribute them.

## Files

- `main.tex` - main thesis file and metadata.
- `gvsu-thesis.sty` - formatting rules.
- `frontmatter/` - dedication, acknowledgements, abstract, symbols, abbreviations.
- `chapters/` - chapter placeholder files.
- `appendices/` - appendix placeholder files.
- `references.bib` - bibliography placeholder.

## Before Submitting

Open the compiled PDF and visually check:

- title page
- approval page
- page numbering
- table of contents
- lists of tables/figures
- chapter starts
- appendices
- bibliography
