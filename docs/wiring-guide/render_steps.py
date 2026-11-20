"""Render one image per assembly step of the CyberShot Cam wiring guide.

Run: Blender -b -P render_steps.py -- <outdir> [step ...]
Coordinates match the three.js page: (x, y_up, z) -> Blender (x, -z, y).
"""
import bpy, sys, math, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "out"
ONLY = [int(a) for a in argv[1:]]
os.makedirs(OUT, exist_ok=True)

def V(x, y, z):  # page coords -> blender
    return Vector((x, -z, y))

# monochrome blueprint palette: power = white, signal = light grey, GND = dark grey; only solder joints carry colour
RED, BLK, SIG, YEL = (1.0, 1.0, 1.0), (0.07, 0.07, 0.07), (0.38, 0.38, 0.38), (0.38, 0.38, 0.38)
ACCENT = (1.0, 0.32, 0.12)

comps = {
    "board": ((0, 0, 0), (6.4, 0.25, 2.8), (0.10, 0.15, 0.20)),
    "lcd": ((-5.6, 0, -6.2), (3.6, 0.2, 5.0), (0.07, 0.25, 0.55)),
    "joy": ((5.6, 0, -5.8), (2.6, 0.2, 3.4), (0.08, 0.08, 0.08)),
    "btn": ((6.2, 0, 5.2), (0, 0, 0), None),
    "led": ((2.4, 0, 6.4), (0, 0, 0), None),
    "batt": ((-9.2, 0, 7.2), (7.6, 0.9, 2.2), (0.04, 0.04, 0.04)),
    "tp": ((-3.2, 0, 7.2), (2.6, 0.15, 1.7), (0.08, 0.25, 0.75)),
    "sw": ((0.2, 0, 9.6), (1.2, 0.8, 0.7), (0.05, 0.05, 0.05)),
    "mt": ((-3.2, 0, 10.6), (3.6, 0.15, 1.7), (0.08, 0.25, 0.75)),
}

P = {}
def add_pin(pid, comp, dx, dz, label, y=None):
    c = comps[comp]
    P[pid] = dict(x=c[0][0] + dx, z=c[0][2] + dz, y=(y if y is not None else (c[1][1] or 0.2) + 0.05), label=label, comp=comp)

HDR_R = ["43","44","1","2","42","41","40","39","38","37","36","35","0","45","48","47","21","20","19","GND"]
HDR_L = ["3V3","RST","4","5","6","7","15","16","17","18","8","3","46","9","10","11","12","13","14","5V"]
for i, n in enumerate(HDR_R):
    add_pin("b" + n, "board", 2.95 - i * 0.31, -1.15, n)
for i, n in enumerate(HDR_L):
    add_pin("b" + n, "board", 2.95 - i * 0.31, 1.15, n)
for i, n in enumerate(["VCC", "GND", "CS", "RESET", "A0", "SDA", "SCK", "LED"]):
    add_pin("l" + n, "lcd", -1.575 + i * 0.45, 2.3, n)
for i, n in enumerate(["GND", "+5V", "VRx", "VRy", "SW"]):
    add_pin("j" + n, "joy", -0.9 + i * 0.45, -1.5, n)
add_pin("btn1", "btn", -0.35, 0.75, "T1", 0.15); add_pin("btn2", "btn", 0.35, 0.75, "T2", 0.15)
add_pin("rA", "led", -1.4, -0.9, "100Ω", 0.12); add_pin("rB", "led", -0.4, -0.3, "100Ω", 0.12)
add_pin("ledA", "led", 0.15, 0.0, "+ long", 0.12); add_pin("ledK", "led", 0.45, 0.0, "- short", 0.12)
add_pin("battP", "batt", 3.9, -0.45, "red", 0.5); add_pin("battN", "batt", 3.9, 0.45, "black", 0.5)
add_pin("tpBp", "tp", -1.1, -0.45, "B+"); add_pin("tpBn", "tp", -1.1, 0.45, "B-")
add_pin("tpOp", "tp", 1.1, -0.45, "OUT+"); add_pin("tpOn", "tp", 1.1, 0.45, "OUT-")
add_pin("sw1", "sw", -0.3, -0.45, "SW", 0.2); add_pin("sw2", "sw", 0.3, -0.45, "SW", 0.2)
add_pin("mtIp", "mt", -1.6, -0.45, "VIN+"); add_pin("mtIn", "mt", -1.6, 0.45, "VIN-")
add_pin("mtOp", "mt", 1.6, -0.45, "VOUT+"); add_pin("mtOn", "mt", 1.6, 0.45, "VOUT-")
add_pin("bus3", "board", 4.7, -0.5, "3V3 BUS", 0.15); P["bus3"]["comp"] = "bus"
add_pin("busG", "board", -4.7, -0.5, "GND BUS", 0.15); P["busG"]["comp"] = "bus"

W = [
    ("b3V3", "bus3", RED, 1, ["bus3"]), ("bGND", "busG", BLK, 1, ["busG"]),
    ("lVCC", "bus3", RED, 1, []), ("lGND", "busG", BLK, 1, []), ("lCS", "b43", SIG, 1, []),
    ("lRESET", "b21", SIG, 1, []), ("lA0", "b14", SIG, 1, []), ("lSDA", "b45", SIG, 1, []),
    ("lSCK", "b47", SIG, 1, []), ("lLED", "lVCC", RED, 1, ["lLED", "lVCC"]),
    ("j+5V", "bus3", RED, 2, ["bus3"]), ("jGND", "busG", BLK, 2, ["busG"]), ("jVRx", "b1", SIG, 2, []),
    ("jVRy", "b2", SIG, 2, []), ("jSW", "b42", SIG, 2, []),
    ("btn1", "b41", SIG, 3, ["btn1"]), ("btn2", "busG", BLK, 3, ["btn2", "busG"]),
    ("b48", "rA", SIG, 4, ["rA"]), ("rB", "ledA", YEL, 4, ["rB", "ledA"]), ("ledK", "busG", BLK, 4, ["ledK", "busG"]),
    ("battP", "tpBp", RED, 5, ["tpBp"]), ("battN", "tpBn", BLK, 5, ["tpBn"]),
    ("tpOp", "sw1", RED, 6, ["tpOp", "sw1"]), ("sw2", "mtIp", RED, 6, ["sw2", "mtIp"]), ("tpOn", "mtIn", BLK, 6, ["tpOn", "mtIn"]),
    ("mtOp", "b5V", RED, 8, ["mtOp"]), ("mtOn", "busG", BLK, 8, ["mtOn", "busG"]),
]
STEP_FOCUS = {0: ["board"], 1: ["lcd", "board"], 2: ["joy", "board"], 3: ["btn", "board"], 4: ["led", "board"],
              5: ["batt", "tp"], 6: ["tp", "sw", "mt"], 7: ["mt"], 8: ["mt", "board"]}
STEP_TITLE = {0: "STEP 0  Board only", 1: "STEP 1  LCD", 2: "STEP 2  Joystick", 3: "STEP 3  Shutter button",
              4: "STEP 4  Flash LED", 5: "STEP 5  Battery -> TP4056", 6: "STEP 6  Switch + MT3608",
              7: "STEP 7  Set MT3608 to 5.0V", 8: "STEP 8  MT3608 -> Board"}

# ---------------- scene setup ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1400, 900
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.002, 0.002, 0.002, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
scene.view_settings.look = "AgX - Punchy" if "AgX - Punchy" in [l.name for l in []] else scene.view_settings.look
# bloom via compositor
try:
    tree = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
    tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = tree.nodes.new("CompositorNodeRLayers"); gl = tree.nodes.new("CompositorNodeGlare"); out = tree.nodes.new("NodeGroupOutput")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Threshold"].default_value = 0.85
    gl.inputs["Strength"].default_value = 0.9
    gl.inputs["Size"].default_value = 0.6
    tree.links.new(rl.outputs["Image"], gl.inputs["Image"]); tree.links.new(gl.outputs["Image"], out.inputs[0])
    scene.compositing_node_group = tree
    scene.render.use_compositing = True
except Exception as e:
    print("COMPOSITOR_FAIL", e)

def material(name, rgb, rough=0.5, metal=0.0, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    b.inputs["Alpha"].default_value = alpha
    return m

GHOST = material("ghost", (0.03, 0.03, 0.03), 0.6, alpha=0.05)
HOLO_FILL = {}
def holo_fill(rgb):
    k = tuple(round(c, 3) for c in rgb)
    if k not in HOLO_FILL:
        lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        HOLO_FILL[k] = material("fill%d" % len(HOLO_FILL), (0.03 + lum * 0.2,) * 3, 0.35, alpha=0.5)
    return HOLO_FILL[k]
EDGE = material("edge", (0.92, 0.92, 0.92), 0.5, emit=4.0)
EDGE_DIM = material("edge_dim", (0.5, 0.5, 0.5), 0.5, emit=0.12)
PAD = material("pad", (0.8, 0.8, 0.8), 0.3, 0.5, emit=0.8)
JOINT = material("joint", ACCENT, 0.3, 0.0, emit=1.0)
JOINT_DIM = material("joint_dim", ACCENT, 0.4, alpha=0.25)

def add_box(name, center, size, mat):
    bpy.ops.mesh.primitive_cube_add(location=center)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(mat); return o

def add_cyl(name, center, r, depth, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=center, rotation=rot, vertices=32)
    o = bpy.context.object; o.name = name; o.data.materials.append(mat); return o

def add_sphere(name, center, r, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=center, segments=24, ring_count=16)
    o = bpy.context.object; o.name = name; o.scale = scale; o.data.materials.append(mat)
    bpy.ops.object.shade_smooth(); return o

# ground
bpy.ops.mesh.primitive_plane_add(size=60, location=(-1.5, -2, 0))
g = bpy.context.object; g.location.z = -0.02; g.data.materials.append(material("mat", (0.004, 0.004, 0.004), 0.9))
bpy.ops.mesh.primitive_grid_add(x_subdivisions=61, y_subdivisions=61, size=60, location=(-1.5, -2, 0))
gr = bpy.context.object; wm = gr.modifiers.new("w", "WIREFRAME"); wm.thickness = 0.015
gr.data.materials.append(material("grid", (0.5, 0.5, 0.5), 0.5, emit=0.06))

comp_objs = {k: [] for k in comps}
edge_objs = {k: [] for k in comps}
def body(comp, o, orig_mat):
    rgb = tuple(orig_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value)[:3]
    f = holo_fill(rgb); o.data.materials[0] = f; o["orig"] = f.name; comp_objs[comp].append(o)
    tw = o.copy(); tw.data = o.data.copy(); scene.collection.objects.link(tw)
    tw.data.materials[0] = EDGE
    m = tw.modifiers.new("wf", "WIREFRAME"); m.thickness = 0.03; m.use_replace = True
    edge_objs[comp].append(tw)

for cid, (pos, size, col) in comps.items():
    x, y, z = pos
    if cid in ("board", "lcd", "joy", "batt", "tp", "mt", "sw"):
        m = material(cid, col, 0.55)
        body(cid, add_box(cid, V(x, size[1] / 2, z), (size[0], size[2], size[1]), m), m)
    if cid == "board":
        for nm, c, s, rgb, met in [("module", (1.6, 0.42, 0), (2.2, 1.7, 0.35), (0.72, 0.74, 0.77), 0.8),
                                   ("camera", (-0.7, 0.5, 0), (0.9, 0.9, 0.5), (0.03, 0.03, 0.03), 0.0),
                                   ("sdslot", (-1.9, 0.32, 0.1), (1.0, 1.2, 0.15), (0.55, 0.56, 0.58), 0.8),
                                   ("usb", (-3.1, 0.4, 0), (0.8, 0.6, 0.3), (0.6, 0.62, 0.64), 0.9)]:
            m = material(nm, rgb, 0.35, met); body(cid, add_box(nm, V(x + c[0], c[1], z + c[2]), s, m), m)
        m = material("lens", (0.02, 0.02, 0.05), 0.05, 0.3); body(cid, add_cyl("lens", V(x - 0.7, 0.85, z), 0.25, 0.2, m), m)
    if cid == "lcd":
        m = material("screen", (0.01, 0.01, 0.015), 0.08)
        body(cid, add_box("screen", V(x, 0.23, z - 0.3), (3.0, 3.6, 0.06), m), m)
    if cid == "joy":
        m = material("joybase", (0.2, 0.2, 0.2), 0.6); body(cid, add_box("joybase", V(x, 0.65, z + 0.3), (1.6, 1.6, 0.9), m), m)
        m = material("stick", (0.1, 0.1, 0.1), 0.4); body(cid, add_cyl("stick", V(x, 1.5, z + 0.3), 0.12, 0.8, m), m)
        m = material("cap", (0.05, 0.05, 0.05), 0.5); body(cid, add_sphere("cap", V(x, 1.95, z + 0.3), 0.55, m, (1, 1, 0.6)), m)
    if cid == "btn":
        m = material("btnbody", (0.05, 0.05, 0.05), 0.4); body(cid, add_cyl("btnbody", V(x, 0.4, z), 0.6, 0.8, m), m)
        m = material("btncap", (0.85, 0.12, 0.10), 0.3); body(cid, add_cyl("btncap", V(x, 0.95, z), 0.47, 0.35, m), m)
    if cid == "led":
        m = material("resistor", (0.85, 0.77, 0.6), 0.5)
        r = add_cyl("resistor", V(x - 0.9, 0.12, z - 0.6), 0.13, 0.9, m, rot=(0, math.pi / 2, 0.55)); body(cid, r, m)
        m = material("ledbody", (1.0, 0.1, 0.08), 0.1); m.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.6
        body(cid, add_cyl("ledbody", V(x + 0.3, 0.45, z - 0.25), 0.25, 0.5, m), m)
        body(cid, add_sphere("leddome", V(x + 0.3, 0.7, z - 0.25), 0.25, m), m)
    if cid == "batt":
        m = material("cell", (0.12, 0.42, 0.85), 0.35, 0.2); body(cid, add_cyl("cell", V(x, 0.95, z), 0.9, 6.5, m, rot=(0, math.pi / 2, 0)), m)
    if cid == "mt":
        m = material("pot", (0.15, 0.4, 0.9), 0.4); body(cid, add_box("pot", V(x, 0.4, z - 0.3), (0.6, 0.6, 0.5), m), m)
    if cid == "tp":
        m = material("usbc", (0.6, 0.62, 0.64), 0.3, 0.9); body(cid, add_box("usbc", V(x, 0.3, z - 0.85), (0.7, 0.5, 0.3), m), m)
    if cid == "sw":
        m = material("rocker", (0.85, 0.12, 0.10), 0.4); body(cid, add_box("rocker", V(x, 0.9, z), (0.9, 0.5, 0.25), m), m)

pad_objs = {}
for pid, p in P.items():
    if p["comp"] == "bus":
        continue
    pad_objs[pid] = add_cyl("pad_" + pid, V(p["x"], p["y"] - 0.02, p["z"]), 0.11, 0.06, PAD)

def wire_curve(name, a, b, rgb):
    pa, pb = Vector((a["x"], a["y"], a["z"])), Vector((b["x"], b["y"], b["z"]))
    d = (pa - pb).length; h = min(2.6, 0.5 + d * 0.14); top = max(pa.y, pb.y) + h
    m1 = pa.lerp(pb, 0.25); m1.y = top
    m2 = pa.lerp(pb, 0.75); m2.y = top
    pts = [pa, Vector((pa.x, pa.y + 0.35, pa.z)), m1, m2, Vector((pb.x, pb.y + 0.35, pb.z)), pb]
    cd = bpy.data.curves.new(name, "CURVE"); cd.dimensions = "3D"; cd.bevel_depth = 0.07; cd.bevel_resolution = 4
    sp = cd.splines.new("NURBS"); sp.points.add(len(pts) - 1)
    for i, q in enumerate(pts):
        bv = V(q.x, q.y, q.z); sp.points[i].co = (bv.x, bv.y, bv.z, 1)
    sp.use_endpoint_u = True; sp.order_u = 4
    o = bpy.data.objects.new(name, cd); scene.collection.objects.link(o)
    m = material(name, rgb, 0.4, emit=2.2 if rgb == RED else 0.8); cd.materials.append(m); o["orig"] = m.name
    return o

wire_objs = [(w, wire_curve(f"wire{i}", P[w[0]], P[w[1]], w[2])) for i, w in enumerate(W)]
joint_ids = sorted({j for w in W for j in w[4]})
joint_objs = {j: add_sphere("joint_" + j, V(P[j]["x"], P[j]["y"] + 0.08, P[j]["z"]), 0.2, JOINT) for j in joint_ids}

# labels
FONT = None
for fp in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
    if os.path.exists(fp):
        try:
            FONT = bpy.data.fonts.load(fp); break
        except Exception:
            pass
LABEL_MAT = material("labeltext", (0.95, 0.95, 0.95), 0.5, emit=3.0)
LABEL_PIN = material("labelpin", (0.9, 0.9, 0.9), 0.5, emit=2.6)

bpy.ops.object.camera_add(); cam = bpy.context.object; scene.camera = cam
cam.data.lens = 40
target = bpy.data.objects.new("target", None); scene.collection.objects.link(target)
tc = cam.constraints.new("TRACK_TO"); tc.target = target; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"

bpy.ops.object.light_add(type="AREA", location=(2, -6, 18)); key = bpy.context.object
key.data.energy = 900; key.data.size = 14; key.data.color = (1.0, 1.0, 1.0)
bpy.ops.object.light_add(type="SUN", location=(0, 0, 10), rotation=(0.6, 0.2, 0.8)); bpy.context.object.data.energy = 1.2

def make_text(body_txt, loc, size, mat, name):
    cd = bpy.data.curves.new(name, "FONT"); cd.body = body_txt; cd.size = size; cd.align_x = "CENTER"; cd.align_y = "CENTER"
    if FONT: cd.font = FONT
    cd.extrude = 0.01
    o = bpy.data.objects.new(name, cd); scene.collection.objects.link(o)
    cd.materials.append(mat); o.location = loc
    c = o.constraints.new("TRACK_TO"); c.target = cam; c.track_axis = "TRACK_Z"; c.up_axis = "UP_Y"
    return o

temp_objs = []
def clear_temp():
    for o in temp_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    temp_objs.clear()

def set_mat(o, mat):
    if o.type == "CURVE":
        o.data.materials[0] = mat
    else:
        o.data.materials[0] = mat

PIN_TXT = {"board": lambda l: ("GPIO " + l) if l.isdigit() else l}

def render_step(step):
    clear_temp()
    active = [w for w in W if w[3] == step]
    focus = set(STEP_FOCUS.get(step, []))
    for w in active:
        focus.add(P[w[0]]["comp"]); focus.add(P[w[1]]["comp"])
    for cid, objs in comp_objs.items():
        for o in objs:
            set_mat(o, bpy.data.materials[o["orig"]] if cid in focus else GHOST)
    for cid, objs in edge_objs.items():
        for o in objs:
            o.data.materials[0] = EDGE if cid in focus else EDGE_DIM
    for w, o in wire_objs:
        o.hide_render = w[3] != step
    act_joints = {j for w in active for j in w[4]}
    for j, o in joint_objs.items():
        o.hide_render = j not in act_joints
    for pid, o in pad_objs.items():
        o.hide_render = P[pid]["comp"] not in focus
    # labels for pins used in this step
    used = []
    for w in active:
        for pid in (w[0], w[1]):
            if pid not in used:
                used.append(pid)
    for k, pid in enumerate(used):
        p = P[pid]
        txt = PIN_TXT.get(p["comp"], lambda l: l)(p["label"])
        off = (-0.75 if p["z"] < P.get("b5V")["z"] else 0.75) if p["comp"] == "board" else -0.6
        same = [q for q in used if P[q]["comp"] == p["comp"] and abs(P[q]["z"] - p["z"]) < 0.01] or [pid]
        idx = same.index(pid)
        lift = 0.7 + (0.75 if (idx % 2) else 0.0)
        temp_objs.append(make_text(txt, V(p["x"], p["y"] + lift, p["z"] + off), 0.3, LABEL_PIN, "lbl_" + pid))
        # thin leader line from pad up to the label
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=lift - 0.2, location=V(p["x"], p["y"] + (lift - 0.2) / 2, p["z"] + off * 0.0), vertices=8)
        ld = bpy.context.object; ld.data.materials.append(LABEL_PIN); temp_objs.append(ld)
    # camera framing over focused things
    pts = [Vector((P[pid]["x"], P[pid]["z"])) for pid in used] or []
    for cid in focus:
        if cid not in comps:
            continue
        (x, _, z), size, _ = comps[cid]
        hx, hz = max(size[0], 1.4) / 2, max(size[2], 1.4) / 2
        pts += [Vector((x - hx, z - hz)), Vector((x + hx, z + hz))]
    xs, zs = [q.x for q in pts], [q.y for q in pts]
    cx, cz = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2
    span = max(max(xs) - min(xs), (max(zs) - min(zs)) * 1.5, 4.0)
    dist = span * 1.15 + 3
    target.location = V(cx, 0.3, cz)
    cam.location = V(cx - dist * 0.12, dist * 0.82, cz + dist * 0.62)
    scene.render.filepath = os.path.join(OUT, f"step{step}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", step, flush=True)

for s in (ONLY or list(range(9))):
    render_step(s)
