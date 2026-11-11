#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if ! command -v pdflatex >/dev/null || ! command -v pdfinfo >/dev/null; then
  echo 'BLOCKED: pdflatex and pdfinfo are required' >&2; exit 2
fi
APA7_MODE=0
if grep -Fq '\input{references_apa7.tex}' manuscript.tex; then
  APA7_MODE=1
  test -f references_apa7.tex || { echo 'BLOCKED: missing references_apa7.tex' >&2; exit 2; }
fi
if command -v bibtex >/dev/null; then BIB=bibtex
elif command -v bibtex.original >/dev/null; then BIB=bibtex.original
else echo 'BLOCKED: BibTeX executable required' >&2; exit 2
fi
sha256sum -c --status <<'EOF'
eea7cf77daab1914c6e4ba74ce64de20a8d82a485e3aba7d0eaa77f076f8d2ad  figures/licensed_historical/Michell1973_Figure12_ORIGINAL_CROP.pdf
15bc7e74431360d3a440f33f6f6b1265bd7e05d9b07853b4217a978ad2efb090  figures/licensed_historical/Michell1973_Figure14_ORIGINAL_CROP.pdf
EOF
echo 'PRIVATE_LICENSED_PLATES_HASH_PASS'
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error manuscript.tex > /dev/null
if [[ "$APA7_MODE" -eq 0 ]]; then "$BIB" manuscript > /dev/null; fi
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error manuscript.tex > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error manuscript.tex > /dev/null
pages=$(pdfinfo manuscript.pdf | awk '/^Pages:/{print $2}')
if [[ "$APA7_MODE" -eq 0 && "$pages" != '20' ]]; then echo "BLOCKED: expected 20 pages, got $pages" >&2; exit 2; fi
if (( pages < 20 )); then echo 'BLOCKED: unexpected page loss in A05-R3' >&2; exit 2; fi
if grep -E 'LaTeX Warning: (Citation|Reference)|undefined (citations|references)|Overfull \\hbox|Overfull \\vbox|Missing character:|Float too large' manuscript.log >/dev/null; then
  echo 'BLOCKED: unresolved LaTeX warning; inspect manuscript.log' >&2
  grep -E 'LaTeX Warning: (Citation|Reference)|undefined (citations|references)|Overfull \\hbox|Overfull \\vbox|Missing character:|Float too large' manuscript.log >&2
  exit 2
fi
if [[ "$(grep -c '^\\newlabel{fig:' manuscript.aux || true)" != '10' ]]; then
  echo 'BLOCKED: expected ten figure cross-reference labels' >&2;exit 2
fi
if [[ "$(grep -c '^\\newlabel{tab:' manuscript.aux || true)" != '5' ]]; then
  echo 'BLOCKED: expected five table cross-reference labels' >&2;exit 2
fi
sha256sum manuscript.pdf
printf 'A05_LOCAL_BUILD_PASS pages=%s figures=10 tables=5 mode=%s; review visuals before author-signing\n' "$pages" "$APA7_MODE"
