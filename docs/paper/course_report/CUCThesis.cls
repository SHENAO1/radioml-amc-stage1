\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{CUCThesis}[2026/05/05 Reconstructed CUC course report class]
\LoadClass[UTF8,openany,zihao=-4]{ctexbook}

\RequirePackage[a4paper,margin=2.5cm]{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{setspace}
\RequirePackage{booktabs}
\RequirePackage{caption}
\RequirePackage{float}
\RequirePackage{titlesec}
\RequirePackage{enumitem}
\RequirePackage{xcolor}
\RequirePackage{tabularray}
\RequirePackage[backend=biber,style=gb7714-2015]{biblatex}

\setstretch{1.35}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.25em}
\raggedbottom
\setlength{\headheight}{15pt}
\renewcommand{\topfraction}{0.92}
\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.08}
\renewcommand{\floatpagefraction}{0.85}
\setlength{\textfloatsep}{0.8em plus 0.2em minus 0.2em}
\setlength{\floatsep}{0.8em plus 0.2em minus 0.2em}
\setlength{\intextsep}{0.8em plus 0.2em minus 0.2em}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{中国传媒大学作业报告}
\fancyfoot[C]{\thepage}
\fancypagestyle{plain}{%
  \fancyhf{}%
  \fancyhead[C]{中国传媒大学作业报告}%
  \fancyfoot[C]{\thepage}%
}
\captionsetup{labelsep=quad}
\ctexset{
  chapter = {
    format = \raggedright\zihao{3}\heiti,
    beforeskip = -0.8em,
    afterskip = 1.1em
  },
  section = {
    format = \raggedright\zihao{4}\heiti,
    beforeskip = 1.0em,
    afterskip = 0.7em
  },
  subsection = {
    format = \raggedright\zihao{-4}\heiti,
    beforeskip = 0.8em,
    afterskip = 0.5em
  }
}

\newcommand{\cuc@type}{}
\newcommand{\cuc@header}{}
\newcommand{\cuc@classification}{}
\newcommand{\cuc@security}{}
\newcommand{\cuc@studentid}{}
\newcommand{\cuc@titlecover}{}
\newcommand{\cuc@titlebody}{}
\newcommand{\cuc@author}{}
\newcommand{\cuc@date}{}
\newcommand{\customtitle}[1]{#1}
\newcommand{\setup}[1]{\setkeys{cucsetup}{#1}}
\makeatletter
\define@key{cucsetup}{Type}{\renewcommand{\cuc@type}{#1}}
\define@key{cucsetup}{Header}{\renewcommand{\cuc@header}{#1}}
\define@key{cucsetup}{Classification}{\renewcommand{\cuc@classification}{#1}}
\define@key{cucsetup}{Security}{\renewcommand{\cuc@security}{#1}}
\define@key{cucsetup}{StudentID}{\renewcommand{\cuc@studentid}{#1}}
\define@key{cucsetup}{TitleinCover}{\renewcommand{\cuc@titlecover}{#1}}
\define@key{cucsetup}{TitleinBody}{\renewcommand{\cuc@titlebody}{#1}}
\define@key{cucsetup}{Author}{\renewcommand{\cuc@author}{#1}}
\define@key{cucsetup}{Date}{\renewcommand{\cuc@date}{#1}}
\makeatother

\makeatletter
\newcommand{\coverpage}{
  \begin{titlepage}
    \centering
    \vspace*{2cm}
    {\zihao{2}\bfseries \cuc@header\par}
    \vspace{2.2cm}
    {\zihao{1}\bfseries \cuc@titlecover\par}
    \vspace{2.2cm}
    {\zihao{2}\cuc@type\par}
    \vspace{1.8cm}
    {\zihao{3}
    \renewcommand{\arraystretch}{1.35}
    \begin{tabular}{rl}
      姓名： & \cuc@author\\
      学号： & \cuc@studentid\\
      日期： & \cuc@date
    \end{tabular}\par}
    \vfill
  \end{titlepage}
}
\makeatother

\newenvironment{cnabstract}[1][]{%
  \def\cuc@cnkeywords{#1}%
  {\ctexset{chapter = {format = \centering\zihao{3}\heiti}}\chapter*{摘\quad 要}}
  \thispagestyle{empty}
  \addcontentsline{toc}{chapter}{摘\quad 要}
}{%
  \par\noindent\textbf{关键词：} \cuc@cnkeywords
  \clearpage
}

\newenvironment{enabstract}[1][]{%
  \def\cuc@enkeywords{#1}%
  \chapter*{Abstract}
  \addcontentsline{toc}{chapter}{Abstract}
}{%
  \par\noindent\textbf{Keywords:} \cuc@enkeywords
  \clearpage
}

\newenvironment{reference}{\chapter*{参考文献}\addcontentsline{toc}{chapter}{参考文献}}{}
\newcommand{\frontmatterstyle}{plain}
