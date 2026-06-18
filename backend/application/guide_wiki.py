"""
Parser de la wiki de guías (Markdown -> estructura JSON) para el Centro de
aprendizaje. El contenido vive en el front intranet (static/guide/<tipo>/) y se
lee server-side, evitando que el navegador lo pida directamente.

Las funciones son puras (no tocan DB ni red); reciben el texto del Markdown y la
URL base pública para resolver imágenes relativas.
"""
import re

_SHOT_RE = re.compile(r'^\**\[SCREENSHOT[^\]]*\]\**\s*$', re.I)
_IMG_RE  = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)')
_STOP_RE = re.compile(r'^(#{2,6}\s|[-*]\s|\d+\.\s|\||!\[|---|\**\[SCREENSHOT)', re.I)


def _esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _inline(t):
    t = _esc(t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?:[^)]+)\)',
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def _shot_box(caption):
    desc = re.sub(r'^SCREENSHOT\s*\d*\s*:?\s*', '', caption or '', flags=re.I).strip()
    inner = _inline(desc) if desc else 'Espacio para screenshot / imagen'
    return (
        '<div class="guia-md-shot">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">'
        '<rect x="3" y="3" width="18" height="18" rx="2"/>'
        '<circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>'
        f'<span>{inner}</span></div>'
    )


def _cells(row):
    row = re.sub(r'^\s*\|', '', row)
    row = re.sub(r'\|\s*$', '', row)
    return [c.strip() for c in row.split('|')]


def _table(rows):
    head = _cells(rows[0])
    body = [_cells(r) for r in rows[2:]]
    html = ('<div class="guia-md-tablewrap"><table class="guia-md-table"><thead><tr>'
            + ''.join(f'<th>{_inline(c)}</th>' for c in head)
            + '</tr></thead><tbody>')
    for r in body:
        html += '<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in r) + '</tr>'
    return html + '</tbody></table></div>'


def _blocks(md, image_base):
    lines = md.replace('\r', '').split('\n')
    n = len(lines)
    html = ''
    i = 0
    while i < n:
        line = lines[i]
        if line.strip() == '' or re.match(r'^---+\s*$', line):
            i += 1
            continue
        m = re.match(r'^####\s+(.*)', line)
        if m:
            html += f'<h5 class="guia-md-h4">{_inline(m.group(1))}</h5>'
            i += 1
            continue
        m = re.match(r'^###\s+(.*)', line)
        if m:
            html += f'<h4 class="guia-md-h3">{_inline(m.group(1))}</h4>'
            i += 1
            continue
        if _SHOT_RE.match(line):
            html += _shot_box(re.sub(r'[\*\[\]]', '', line).strip())
            i += 1
            continue
        m = _IMG_RE.match(line)
        if m:
            src = m.group(2)
            if not re.match(r'^https?:', src, re.I):
                rel = re.sub(r'^\./?', '', src)
                rel = re.sub(r'^imagenes/', '', rel)  # estructura aplanada en /shared_uploads/guides/<tipo>/
                src = f"{image_base}/{rel}"
            alt = _esc(m.group(1))
            cap = f'<figcaption>{alt}</figcaption>' if m.group(1) else ''
            html += (f'<figure class="guia-md-fig"><img src="{src}" alt="{alt}" '
                     f'loading="lazy">{cap}</figure>')
            i += 1
            continue
        if (re.match(r'^\s*\|.*\|\s*$', line) and i + 1 < n
                and re.match(r'^\s*\|?[\s:|-]+$', lines[i + 1])):
            tbl = []
            while i < n and '|' in lines[i] and lines[i].strip() != '':
                tbl.append(lines[i])
                i += 1
            html += _table(tbl)
            continue
        if re.match(r'^\s*\d+\.\s+', line):
            items = []
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(re.sub(r'^\s*\d+\.\s+', '', lines[i]))
                i += 1
            html += '<ol class="guia-md-list">' + ''.join(
                f'<li>{_inline(t)}</li>' for t in items) + '</ol>'
            continue
        if re.match(r'^\s*[-*]\s+', line):
            items = []
            while i < n and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(re.sub(r'^\s*[-*]\s+', '', lines[i]))
                i += 1
            html += '<ul class="guia-md-list">' + ''.join(
                f'<li>{_inline(t)}</li>' for t in items) + '</ul>'
            continue
        para = []
        while i < n and not (lines[i].strip() == '' or _STOP_RE.match(lines[i])):
            para.append(lines[i])
            i += 1
        if para:
            html += f'<p>{_inline(" ".join(para))}</p>'
        else:
            i += 1
    return html


def parse_guide(md, image_base):
    """Markdown -> {title, intro, reading_min, sections:[{title, html}]}."""
    lines = (md or '').replace('\r', '').split('\n')
    n = len(lines)
    title = ''
    i = 0
    while i < n:
        m = re.match(r'^#\s+(.*)', lines[i])
        if m:
            title = re.sub(r'^.*:\s*', '', m.group(1)).strip()
            i += 1
            break
        i += 1
    intro = []
    while i < n and not re.match(r'^##\s+', lines[i]):
        intro.append(lines[i])
        i += 1
    sections = []
    cur = None
    while i < n:
        m = re.match(r'^##\s+(.*)', lines[i])
        if m:
            if cur:
                sections.append(cur)
            cur = {'title': re.sub(r'^\d+\.\s*', '', m.group(1)).strip(), 'body': []}
        elif cur is not None:
            cur['body'].append(lines[i])
        i += 1
    if cur:
        sections.append(cur)

    intro_text = '\n'.join(intro).strip()
    words = len((intro_text + ' '
                 + ' '.join(' '.join(s['body']) for s in sections)).split())
    reading_min = max(2, round(words / 200))
    return {
        'title': title,
        'intro': intro_text,
        'reading_min': reading_min,
        'sections': [
            {'title': s['title'], 'html': _blocks('\n'.join(s['body']), image_base)}
            for s in sections
        ],
    }
