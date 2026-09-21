"""Inspect the delivered PDF and verify redraw data against original processing."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def main():
    source = ROOT/'paper/figure-revision/build/main.pdf'
    report = ROOT/'reports/npu-figure-revision'
    report.mkdir(exist_ok=True)
    renders = report/'pages'
    renders.mkdir(exist_ok=True)
    baseline = json.loads((ROOT/'paper/figure-revision/baseline.json').read_text(encoding='utf-8'))
    figures = ROOT/baseline['figure_directory']
    require(sha(ROOT/'scripts/redraw_npu_figures.py') == baseline['redraw_source_sha256'], 'Redraw source changed')
    for name, digest in baseline['figure_files_sha256'].items():
        require(sha(figures/name) == digest, 'Figure artifact changed: '+name)
    manifest = json.loads((figures/'manifest.json').read_text(encoding='utf-8'))
    require(len(manifest['results']) == 5 and all(v['status'] == 'PASS' for v in manifest['results'].values()),
            'Expected five PASS figure results')
    require(sha(figures/'plotted-data.json') == manifest['plotted_data_sha256'], 'Plotted data changed')
    for name in manifest['results']:
        qa = json.loads((figures/(name+'.qa.json')).read_text(encoding='utf-8'))
        require(qa['status'] == 'PASS', 'Figure QA failed: '+name)
        require(qa['provenance']['source_sha256'] == baseline['redraw_source_sha256'], 'Wrong source version')
        for filename, digest in qa['files'].items():
            require(sha(figures/filename) == digest, 'Export changed: '+filename)
    tex = '\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'paper/figure-revision/sections').glob('*.tex'))
    paths = re.findall(r'\\includegraphics\[[^\]]+\]\{([^}]+)\}', tex)
    actual = {(ROOT/'paper/figure-revision'/p).resolve() for p in paths}
    require(actual == {(figures/(name+'.pdf')).resolve() for name in manifest['results']}, 'TeX figure bindings differ')
    data = json.loads((figures/'plotted-data.json').read_text(encoding='utf-8'))
    for rel, digest in {**manifest['inputs_sha256'], **baseline['sha256']}.items():
        require(sha(ROOT/rel) == digest, 'Input changed: '+rel)
    read = lambda p: json.loads((ROOT/p).read_text(encoding='utf-8'))
    checks = []
    r3 = 'results/runs/npu-paper-r3-analysis-001/'
    r2 = 'results/runs/npu-paper-r2-analysis-001/'
    for key in ('id', 'selected', 'memory'):
        original = read(r3+f'conv_{key}_trajectory.json')
        actual = data['conv_trajectory'][key]
        require(actual['points'] == original['points'], 'Trajectory differs')
        if key != 'memory':
            require(actual['window'] == [p for p in original['points'] if 2180 <= p[0] <= 2350], 'Window differs')
            require((actual['peak'], actual['position']) == (original['peak'], original['position']), 'Peak differs')
    checks.append('conv_full_arrays_window_and_peak_exact')
    require(data['attention_occupancy']['trace'] == read(r3+'attention_p2_occupancy.json')['trace'], 'Trace differs')
    require(data['attention_occupancy']['capacities'] == [4096, 1024], 'Capacity differs')
    checks.append('occupancy_arrays_and_capacities_exact')
    rows = read('results/runs/npu2025-a-005/summary.json')
    analysis = read(r2+'analysis.json')['rows']
    for key in ('initial_time_best', 'final'):
        expected = [100*(1-(a[key]['cycles'] if key != 'final' else r['problem3']['cycles'])/
                        r['problem2']['cycles']) for r,a in zip(rows, analysis)]
        require(data['stage_gain'][key] == expected, 'Reduction differs')
    checks.append('six_case_reduction_formula_exact')
    for stage in (2, 3):
        timeline = read(r2+f'attention_p{stage}_timeline.json')
        detail = read(r3+f'attention_p{stage}_detail.json')
        for pipe in ('MTE2', 'MTE1', 'CUBE', 'VECTOR', 'MTE3', 'FIXP'):
            for spill in (False, True):
                key = pipe + ('_spill' if spill else '_original')
                expected = [[v[2]/1000, (v[3]-v[2])/1000] for v in timeline
                            if v[1] == pipe and v[3] > v[2] and v[4].startswith('SPILL') == spill]
                require(data['attention_compare'][str(stage)][key] == expected, 'Full intervals differ')
                expected = [[v['start'], v['end']-v['start']] for v in detail
                            if v['pipe'] == pipe and v['end'] > v['start']
                            and v['op'].startswith('SPILL') == spill
                            and v['end'] > 8500 and v['start'] < 11500]
                require(data['attention_window'][str(stage)][key] == expected, 'Local intervals differ')
    checks.append('all_pipeline_intervals_units_and_window_exact')
    font_counts, cjk_counts = Counter(), Counter()
    page_info, pictures, out_of_page = [], [], []
    with fitz.open(source) as doc:
        for n, page in enumerate(doc, 1):
            spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b
                     for line in b['lines'] for s in line['spans']]
            for s in spans:
                font_counts[(s['font'], round(s['size'], 3))] += len(s['text'])
                if re.search('[\u3400-\u9fff]', s['text']):
                    cjk_counts[(s['font'], round(s['size'], 3))] += len(s['text'])
                x0, y0, x1, y1 = s['bbox']
                if x0 < 0 or y0 < 0 or x1 > page.rect.width or y1 > page.rect.height:
                    out_of_page.append([n, s['text'], s['bbox']])
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            pic = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            pic.save(renders/f'page-{n:02d}.png')
            pictures.append(pic)
            text = page.get_text()
            page_info.append({'page': n, 'text_chars': len(text), 'text': text,
                              'figures': re.findall(r'图\s*[1-5]\s*[:：]', text)})
        fonts = {font[3]: bool(doc.extract_font(font[0])[3]) for page in doc for font in page.get_fonts()}
        require(all(fonts.values()), 'Unembedded fonts: '+str(fonts))
    for start in range(0, len(pictures), 4):
        sheet = Image.new('RGB', (1400, 2040), 'white')
        for i, pic in enumerate(pictures[start:start+4]):
            thumb = ImageOps.contain(pic, (690, 990))
            x, y = (i%2)*700, (i//2)*1020
            sheet.paste(thumb, (x,y+25))
            ImageDraw.Draw(sheet).text((x+10,y+5), f'Page {start+i+1}', fill='black')
        sheet.save(report/f'contact-{start//4+1}.png')
    result = {'pdf_sha256': sha(source), 'pages': len(pictures), 'data_checks': checks,
              'source_and_inputs_unchanged': True, 'out_of_page': out_of_page,
              'embedded_fonts': fonts,
              'font_sizes': [{'font': f, 'size_pdf_pt': s, 'characters': c} for (f,s),c in font_counts.items()],
              'cjk_font_sizes': [{'font': f, 'size_pdf_pt': s, 'characters': c} for (f,s),c in cjk_counts.items()],
              'page_info': page_info, 'visual_review': 'pending'}
    (report/'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('page_info','font_sizes')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
