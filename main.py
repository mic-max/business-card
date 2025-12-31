import base64
import math
import drawsvg as dw

W = 88.9
H = 50.8
R = 3

# Dovetail parameters
PIN_DEPTH = 5.0
NUM_PINS = 4
SMALL_H = 2.3
LARGE_H = SMALL_H + 2 * (PIN_DEPTH * math.tan(math.radians(9.5)))
SPACING = (H - SMALL_H) / (NUM_PINS - 1)
FONT_SIZE = 10.0
TEXT_Y = 12.6

# Laser Styles
cut_style = {
    "fill": "none",
    "stroke": "black",
    "stroke_width": "0.001in"
}

pin_style = {
    "fill": "grey",
    "stroke": "grey",
    "stroke_width": "0.003in"
}

# Main
d = dw.Drawing(W, H, origin=(0, 0))
clip = dw.ClipPath()
clip.append(dw.Rectangle(0, 0, W, H, rx=R, ry=R))
g = dw.Group(clip_path=clip)

def embed_png(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def dovetail_pin(x, y, dx):
    p = dw.Path(**pin_style)
    p.M(x, y - SMALL_H / 2)
    p.L(x + dx * PIN_DEPTH, y - LARGE_H / 2)
    p.L(x + dx * PIN_DEPTH, y + LARGE_H / 2)
    p.L(x, y + SMALL_H / 2)
    p.Z()
    return p

HALF_BLIND_THICKNESS = PIN_DEPTH / 3
for x in [0, W - HALF_BLIND_THICKNESS]:
    g.append(dw.Rectangle(
        x, 0,
        HALF_BLIND_THICKNESS, H,
        fill='grey'
    ))
for i in range(NUM_PINS):
    y = (SMALL_H / 2) + (i * SPACING)
    g.append(dovetail_pin(W - HALF_BLIND_THICKNESS, y, -1))
    g.append(dovetail_pin(HALF_BLIND_THICKNESS, y, 1))


text = dw.Text(
    "Maxwell Made",
    FONT_SIZE,
    W - 10,
    TEXT_Y,
    text_anchor="end",
    font_family="Times New Roman",
    fill="black",
    style="font-feature-settings: 'smcp';"
)
d.append(text)

text = dw.Text(
    ".ca",
    5,
    W - 10,
    18.5,
    text_anchor="end",
    font_family="Times New Roman",
    fill="black",
)
d.append(text)

# Multiline text (lower-right)
lines = [
    "Michael Maxwell",
    "Furniture Maker",
    "Ottawa, ON",
    "613 324 3802",
]

for i, line in enumerate(reversed(lines)):
    y = H - 4 - i * 5
    d.append(dw.Text(
        line,
        4,
        W - 10,
        y,
        text_anchor="end",
        font_family="Times New Roman",
        fill="black",
        style="font-feature-settings: 'smcp';"
    ))
g.append(dw.Rectangle(
    0, 0,
    W, H,
    rx=R, ry=R,
    **cut_style
))

png_data = embed_png("logo.png")
img = dw.Image(11, 18, 30, 30, png_data)
d.append(img)

d.append(g)
d.save_svg("out.svg")
