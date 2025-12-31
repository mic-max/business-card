import math
import drawsvg as dw
from dataclasses import dataclass
import xml.etree.ElementTree as ET

@dataclass
class CardConfig:
    width: float = 88.9
    height: float = 50.8
    radius: float = 1.5
    margin: float = 10.0

@dataclass
class DovetailConfig:
    depth: float = 5.0
    count: int = 4
    angle_deg: float = 9.5
    small_height: float = 2.3
    blind_fraction: float = 1 / 3

@dataclass
class TextStyle:
    font: str = 'Times New Roman'
    title_size: float = 10
    domain_size: float = 5
    right_margin: float = 10
    bottom_margin: float = 4
    info_size: float = 4
    line_height: float = 4.5
    title_y: float = 12.6
    domain_y: float = 18.5

@dataclass
class LogoConfig:
    x: float = 10.5
    y: float = 18.4
    scale: float = 0.23

@dataclass
class LaserConfig:
    cut_style = {
        'fill': 'none',
        'stroke': 'black',
        'stroke_width': '0.001in'
    }
    etch_style = {
        'fill': 'grey',
        'stroke': 'none',
    }

def load_paths_data(svg_file, names):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    out = {}

    SVG_NS = {'svg': 'http://www.w3.org/2000/svg'}
    for el in root.findall('.//svg:path', SVG_NS):
        name = el.get('id')
        if name in names:
            out[name] = el.get('d')

    return out

def draw_dovetails(g: dw.Group, card: CardConfig, dovetail: DovetailConfig, laser: LaserConfig):
    def dovetail_pin(x, y, dx, small_h, large_h, depth):
        p = dw.Path(**laser.etch_style)
        p.M(x, y - small_h / 2)
        p.L(x + dx * depth, y - large_h / 2)
        p.L(x + dx * depth, y + large_h / 2)
        p.L(x, y + small_h / 2)
        p.Z()
        return p

    d = dovetail.depth * dovetail.blind_fraction
    g.append(dw.Rectangle(0, 0, d + 0.05, card.height, **laser.etch_style))
    g.append(dw.Rectangle(card.width - d - 0.05, 0, d + 0.05, card.height, **laser.etch_style))

    # Draw the pins
    large_h = dovetail.small_height + 2 * (dovetail.depth * math.tan(math.radians(dovetail.angle_deg)))
    spacing = (card.height - dovetail.small_height) / (dovetail.count - 1)
    for i in range(dovetail.count):
        y = (dovetail.small_height / 2) + (i * spacing)
        g.append(dovetail_pin(card.width - d, y, -1, dovetail.small_height, large_h, dovetail.depth))
        g.append(dovetail_pin(d, y, 1, dovetail.small_height, large_h, dovetail.depth))

def draw_card_outline(card: CardConfig, laser: LaserConfig):
    # Create rounded rectangle clipping group
    clip = dw.ClipPath()
    clip.append(dw.Rectangle(0, 0, card.width, card.height, rx=card.radius, ry=card.radius))
    g = dw.Group(clip_path=clip)
    g.append(dw.Rectangle(0, 0, card.width, card.height, rx=card.radius, ry=card.radius, **laser.cut_style))
    return g

def make_card(
        card=CardConfig(),
        dovetail=DovetailConfig(),
        text=TextStyle(),
        logo=LogoConfig(),
        laser=LaserConfig()
    ):
    d = dw.Drawing(card.width, card.height, origin=(0, 0))
    g = draw_card_outline(card, laser)
    draw_dovetails(g, card, dovetail, laser)

    # Add company name
    x = card.width - text.right_margin
    d.append(dw.Text('Maxwell Made', text.title_size, x, text.title_y, text_anchor='end', font_family=text.font, **laser.etch_style, style='font-feature-settings: \'smcp\';'))
    d.append(dw.Text('.ca', text.domain_size, x, y=text.domain_y, text_anchor='end', font_family=text.font, **laser.etch_style))

    lines = [
        'Michael Maxwell',
        'Furniture Maker',
        'Ottawa, ON',
        '613 324 3802',
    ]

    for i, line in enumerate(reversed(lines)):
        y = card.height - text.bottom_margin - i * text.line_height
        d.append(dw.Text(line, text.info_size, x, y, text_anchor='end', font_family=text.font, **laser.etch_style, style='font-feature-settings: \'smcp\';'))

    group = dw.Group(transform=f'translate({logo.x}, {logo.y}) scale({logo.scale})')
    cut_paths = load_paths_data('logo.svg', {'top', 'left', 'right', 'botleft', 'botright', 'stem'})
    etch_paths = load_paths_data('logo.svg', {'m1', 'm2'})

    group.append(dw.Circle(70.85919, 73.611367, 40-1.6, stroke_width='1mm', stroke=laser.etch_style['fill'], fill='none'))
    for path_data in cut_paths.values():
        p = dw.Path(path_data, **laser.cut_style)
        group.append(p)
    for etch in etch_paths.values():
        p = dw.Path(path_data, **laser.cut_style)
        group.append(dw.Path(etch, **laser.etch_style))

    d.append(group)

    # Compile SVG and write to disk
    d.append(g)
    d.save_svg('out.svg')

# Main
if __name__ == '__main__':
    make_card()
