% Mircea Bardac, 2008-2009
% dev@mircea.bardac.net
% thesis.cs.pub.ro.cls - class for thesis

% Copyright notice: you must keep the original author(s)/copyright information in the files
% Released: 2009-06-23 - v 0.1 (preview and public testing phase)

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{thesis.cs.pub.ro}[2008/07/14]

\let\ExecuteOptions@ltx\ExecuteOptions
\def\ExecuteOptions#1{%
 \ExecuteOptions@ltx{a4paper,10pt,oneside,onecolumn,final}%
}%
\LoadClassWithOptions{report}
\let\ExecuteOptions\ExecuteOptions@ltx

% uncomment the lines bellow for Romanian Language support
% Use UTF8 file encoding when writing .tex files in Romanian
% Romanian Language support
\usepackage{ucs}
\usepackage[utf8x]{inputenc}
%\usepackage[english,romanian]{babel}
\usepackage[english]{babel}

\usepackage{makeidx}

\usepackage[top=3.5cm, bottom=3.5cm, left=3.5cm, right=3cm]{geometry}
\setlength{\headheight}{1.20cm}
\setlength{\headsep}{0.50cm}

\usepackage{parskip}

% package for variable line spacing (1, 1.5, 2)
% usage: write \onehalfspacing before the part which should be
% with 1.5 line spacing
% for example, in "thesis.tex" before "\input{src/main}" will make
% all the chapters with 1.5 line spacing
\usepackage{setspace}

% hyper-references
% http://www.tug.org/applications/hyperref/manual.html
\usepackage{hyperref}
\hypersetup{%
	colorlinks=true,
	linkcolor=blue,
	anchorcolor=black,
	citecolor=black,
	filecolor=blue,
	menucolor=black,
	urlcolor=blue,
	bookmarks=true,
	bookmarksnumbered=true
}
\urlstyle{sf}

% Treat _ as a normal character
\usepackage{underscore}

% Support for including graphics
\usepackage{graphicx}
\DeclareGraphicsExtensions{.pdf,.png,.jpg}

% Code listings support
\usepackage{listings}

\lstset{
	numbers=left, numberstyle=\footnotesize,
	frame=lines, captionpos=b,
	breaklines=true,
	basicstyle=\ttfamily
}

% notations and abbreviations
% http://www-h.eng.cam.ac.uk/help/tpl/textprocessing/nomencl.pdf
% Sample usage (anywhere in the doc): \abbrev{ABC}{Alpha Beta Gama}
\usepackage{nomencl}

\let\abbrev\nomenclature
\renewcommand{\nomname}{Notations and Abbreviations}

\renewcommand{\nomlabel}[1]{#1 --}
\setlength{\nomitemsep}{-\parsep}

% to be used in the main .tex file
\newcommand{\printabbrev}{
	\printnomenclature
	\newpage
}

\makenomenclature


% restart numbering footnotes on every page
\usepackage{perpage}
\MakePerPage{footnote}

% custom variables for altering front page content

% for some reason I can't use \VAR@author as described in
% http://www.gocad.org/meeting/Nancy2008/papers/gocad.sty
\newcommand{\VARauthor} {}
\newcommand{\VARdate} {}
\newcommand{\VARadviser} {}
\newcommand{\VARtitleen} {}
\newcommand{\VARtitlero} {}
\newcommand{\VARtitlefooteren} {}
\newcommand{\VARtitlefooterro} {}

\renewcommand{\author}[1]{ \renewcommand{\VARauthor}{#1} }
\renewcommand{\date}[1]{ \renewcommand{\VARdate}{#1} }
\newcommand{\adviser}[1]{ \renewcommand{\VARadviser}{#1} }
\newcommand{\titleen}[1]{ \renewcommand{\VARtitleen}{#1} }
\newcommand{\titlero}[1]{ \renewcommand{\VARtitlero}{#1} }
\newcommand{\titlefooteren}[1]{ \renewcommand{\VARtitlefooteren}{#1} }
\newcommand{\titlefooterro}[1]{ \renewcommand{\VARtitlefooterro}{#1} }


% fancyhdr package
% headers with chapter title and page number
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{} % delete default settings
\fancyhead[L,RO]{\bfseries \thepage} % page number
\fancyhead[L]{\bfseries\leftmark}    % section name

% line in header
\renewcommand{\headrulewidth}{0.5pt}
% more space for the line in header
\addtolength{\headheight}{0.5pt}

% no line in footer
\renewcommand{\footrulewidth}{0pt}

% longtable package
\usepackage{longtable}

% Fix verbatim environment: smaller text size
\let\oldverbatim=\verbatim
\renewenvironment{verbatim}{
  \begin{small}
  \begin{oldverbatim}
  \vspace*{1em}
}%
{%
  \vspace*{1em}
  \end{oldverbatim}
  \end{small}
}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% iiscthes.sty - IISC Thesis Style
% http://etd.ncsi.iisc.ernet.in/instructions/templates.htm

% Page formatting and numbering

\newenvironment{frontmatter}{\pagenumbering{roman}}{\newpage \pagenumbering{arabic}}

\renewenvironment{abstract}{\null\vfil\prefacesection{Abstract}}{\par\vfill\null}

\def\prefacesection#1{%
	\chapter*{#1}
	\addcontentsline{toc}{chapter}{#1}}

% Added by Y.N. Srikant
\def\keywords{\prefacesection{Keywords}}
\def\notations{\prefacesection{Notation and Abbreviations}}
\def\vita{\prefacesection{Vita}}
\def\publications{\prefacesection{Publications based on this Thesis}}

%% end iiscthes.sty
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\def\notitlesection#1{%
    \addcontentsline{toc}{chapter}{#1}}

\newenvironment{acknowledgements} {
    \notitlesection{Acknowledgements}
    \thispagestyle{empty} }
{\pagestyle{fancy}}

\newcommand{\includechapter}[1]{\input{src/chapter-#1/index}}
\newcommand{\includesection}[2]{\input{src/chapter-#1/#2}}

% No indent
\setlength{\parindent}{0pt}

\usepackage[T1]{fontenc}

% Default fonts
% (more info: http://www.tug.dk/FontCatalogue/)

% TT font: Courier
\usepackage{courier}

% SF font: Helvetica (default document font)
\usepackage[scaled]{helvet}
\renewcommand*\familydefault{\sfdefault}

% command for specifying TODOs
\newcommand{\todo}[1]{
	\colorbox{yellow}{
		\begin{minipage}{15cm}
			\textbf{TODO:}\\
			#1
		\end{minipage}
	}
}

% command for formatting inline functions
% Usage (default language = C)
%   \func{function_name}
%   \func[language]{function_name}
%      'language' must be supported by package 'listings'
\newcommand{\func}[2][C]{\lstset{language=#1}\lstinline|#2|\lstset{language=C}}

% command for formatting file names
\newcommand{\file}[1]{\textbf{\texttt{#1}}}

% command for formatting inline commands
\newcommand{\cmd}[1]{\textbf{\texttt{#1}}}

% commands for creating labeled hyper-linked references
\newcommand{\labelindexref}[2]{\hyperref[#2]{#1~\ref*{#2}}}
\newcommand{\labelref}[2]{\hyperref[#2]{#1}}

% command for inserting labeled figures
% Usage: \fig{file}{label}{caption}
%   TODO: references should point to the top of the image
\newcommand{\fig}[4][]{
\begin{figure}[htb]
	\begin{center}
		\includegraphics[#1]{#2}
		\caption{#4 \label{#3}}
    \end{center}
\end{figure}
}
% suport for multiple columns
%\usepackage{multicol}

% suport for subfloats
%\usepackage{subfig}

% booktabs (professional tables)
%\usepackage{booktabs}

% multirow (useful for creating multirow cells)
%\usepackage{multirow}

% mathematical formulas
%\usepackage{amsmath}
