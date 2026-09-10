.PHONY: pdf clean

pdf:
	@if command -v latexmk >/dev/null 2>&1; then \
		latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex; \
	else \
		pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex; \
		bibtex manuscript; \
		pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex; \
		pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex; \
	fi

clean:
	@if command -v latexmk >/dev/null 2>&1; then \
		latexmk -C manuscript.tex; \
	else \
		rm -f manuscript.aux manuscript.bbl manuscript.blg manuscript.log \
		      manuscript.out manuscript.toc manuscript.fdb_latexmk \
		      manuscript.fls manuscript.synctex.gz; \
	fi
