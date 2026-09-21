"""Create an isolated typography revision; preserve the revision-three source."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figures', required=True, type=Path)
    parser.add_argument('--paper', required=True, type=Path)
    args = parser.parse_args()
    figures = args.figures.resolve()
    target = args.paper.resolve()
    figure_hashes = {}
    manifest = json.loads((figures/'manifest.json').read_text(encoding='utf-8'))
    if len(manifest['results']) != 5 or any(v['status'] != 'PASS' for v in manifest['results'].values()):
        raise RuntimeError('Expected five PASS figure results')
    for path in figures.iterdir():
        if path.is_file():
            figure_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    target.mkdir(parents=True, exist_ok=False)
    source = ROOT / 'paper/revision3'
    fingerprints = {}
    for path in source.rglob('*'):
        if path.is_file() and path.suffix in ('.tex', '.json') and 'build' not in path.parts:
            fingerprints[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
            dest = target / path.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            text = path.read_text(encoding='utf-8')
            if path.suffix == '.tex':
                text = text.replace(r'\small', r'\zihao{-4}')
                text = re.sub(r'\x5ctextbf\{([^{}]*)\}', r' \1', text)
                if path.name != 'main.tex':
                    def figure(match):
                        name, caption, label = match.group(1, 2, 3)
                        explanation = (figures / (name + '.caption.txt')).read_text(encoding='utf-8')
                        explanation = explanation.replace('%', r'\%')
                        (target/'captions').mkdir(exist_ok=True)
                        (target/'captions'/f'{name}.tex').write_text(explanation+'\n', encoding='utf-8')
                        figpath = '../../' + figures.relative_to(ROOT).as_posix() + '/' + name + '.pdf'
                        return (r'\begin{figure}[H]\centering' + '\n' +
                                r'\includegraphics[width=165mm]{' + figpath + '}\n' +
                                r'\caption{' + caption + r'}\label{' + label + '}\n' +
                                r'\par\smallskip\begin{minipage}{\linewidth}\zihao{-4}\songti' + '\n' +
                                r'\input{captions/' + name + '}\n' +
                                r'\end{minipage}\end{figure}')
                    pattern = (r'\\begin\{figure\}\[H\]\\centering\s*'
                               r'\\includegraphics\[width=[^\]]+\]\{[^}]+/([^/}]+)\.pdf\}\s*'
                               r'\\caption\{([^}]+)\}\\label\{([^}]+)\}\\end\{figure\}')
                    text = re.sub(pattern, figure, text)
            dest.write_text(text, encoding='utf-8')
    mainfile = target/'main.tex'
    text = mainfile.read_text(encoding='utf-8')
    text = re.sub(r'% Historical[^\n]*\n% This[^\n]*\n', '', text)
    text = text.replace(r'\setmonofont{Consolas}', r'\setmonofont{Times New Roman}'+'\n'+
                        r'\setCJKmainfont{SimSun}[BoldFont=SimSun,ItalicFont=SimSun]'+'\n'+
                        r'\urlstyle{same}')
    text = re.sub(r'\\linespread\{[^}]+\}[^\n]*', r'\\linespread{1}', text)
    text = text.replace(r'\captionsetup{font=small',
                        r'\DeclareCaptionFont{xiaosi}{\zihao{-4}\songti}'+'\n'+r'\captionsetup{font=xiaosi')
    text = text.replace(r'\setlength{\tabcolsep}{9pt}', r'\setlength{\tabcolsep}{4pt}')
    text = text.replace(r'\fontsize{14pt}{18pt}\heiti', r'\zihao{4}\heiti')
    text = text.replace(r'\fontsize{12pt}{18pt}\heiti', r'\zihao{-4}\songti')
    # The research cover is redundant; the official format begins at the abstract.
    text = re.sub(r'\\begin\{titlepage\}.*?\\end\{titlepage\}\n', '', text, flags=re.S)
    text = text.replace(r'\zihao{4}\heiti 摘', r'\zihao{-4}\songti 摘')
    text = text.replace(r'\begin{document}', r'\begin{document}'+'\n'+r'\zihao{-4}\songti')
    text = text.replace(r'\appendix', r'\clearpage'+'\n'+r'\appendix')
    mainfile.write_text(text, encoding='utf-8')
    (target/'baseline.json').write_text(json.dumps({
        'source': 'paper/revision3', 'sha256': fingerprints,
        'scope': 'Five figures, separate explanations and document typography; mathematical content retained.',
        'official_format': 'provenance/official2025/format.pdf',
        'official_format_sha256': hashlib.sha256((ROOT/'provenance/official2025/format.pdf').read_bytes()).hexdigest(),
        'figure_directory': str(figures.relative_to(ROOT)),
        'figure_files_sha256': figure_hashes,
        'redraw_source_sha256': hashlib.sha256((ROOT/'scripts/redraw_npu_figures.py').read_bytes()).hexdigest()
        }, ensure_ascii=False, indent=2), encoding='utf-8')
    bindings = json.loads((target/'bindings.json').read_text(encoding='utf-8'))
    bindings.update(pdf_sha256=None, verification=None, figure_directory=str(figures.relative_to(ROOT)),
                    full_paper_quality_status='NOT_YET_COMPILED_OR_REVIEWED')
    (target/'bindings.json').write_text(json.dumps(bindings, ensure_ascii=False, indent=2), encoding='utf-8')
    (target/'build').mkdir()
    print(target)


if __name__ == '__main__':
    main()
