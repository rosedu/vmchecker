# too many dependencies, marking targets as .PHONY
# to be revised in the future

.PHONY: build
build: thesis.pdf clean-tmp

.PHONY: thesis.pdf
thesis.pdf:
	pdflatex -interaction=scrollmode --src-specials thesis.tex
	bibtex thesis
	makeindex thesis.nlo -s nomencl.ist -o thesis.nls
	pdflatex -interaction=scrollmode --src-specials thesis
	makeindex thesis.idx
	@echo; echo; echo
	@echo "****************************************************"
	@echo "***** Ignore errors above. Check errors below. *****"
	@echo
	pdflatex -interaction=scrollmode --src-specials thesis

.PHONY: clean-tmp
clean-tmp:
	rm *.log *.lot *.lof *.blg *.bbl *.out *.toc *.aux || exit 0
	find . -name *.aux | xargs rm
	rm thesis.idx thesis.ilg thesis.ind || exit 0
	rm thesis.nlo thesis.nls || exit 0

.PHONY: clean
clean: clean-tmp
	rm thesis.pdf || exit 0
