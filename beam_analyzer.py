"""Beam Bending & Deflection Analyzer  (Streamlit + Plotly + NumPy)

Install:  pip install streamlit plotly numpy pandas
Run:      streamlit run beam_analyzer.py        (opens in your browser)

Sign convention: point/UDL loads positive DOWN, moments positive CLOCKWISE,
sagging bending moment positive, deflection v positive UP.
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from types import SimpleNamespace as NS

G = 9.81
MAT = {"Steel": (200.0, 250.0), "Aluminum": (69.0, 275.0), "Wood": (11.0, 40.0), "Custom": (100.0, 100.0)}
LT = {"Point load (kN, down +)": "P", "UDL (kN/m, down +)": "W", "Moment (kN·m, clockwise +)": "M"}
LCOL = {"P": "#fb923c", "W": "#38bdf8", "M": "#c084fc"}
CS = [[0, "#22d3ee"], [0.5, "#fbbf24"], [1, "#ef4444"]]   # stress colour scale: low -> yield


# =====================================================================
# 1. SOLVER  (pure NumPy, no UI)
# =====================================================================
def cum(x, y):
    """Running trapezoid integral of y over x."""
    return np.concatenate([[0.0], np.cumsum((y[1:] + y[:-1]) / 2 * np.diff(x))])


def solve(bc, L, I, c, E_gpa, Sy, loads):
    """loads: list of (type, magnitude[kN, kN/m, kN.m], a[m], b[m]).  Returns a namespace of results."""
    EI = E_gpa * 1e9 * I
    ld = [(t, m * 1e3, float(np.clip(min(a, b), 0, L)), float(np.clip(max(a, b), 0, L))) for t, m, a, b in loads]

    def lv(x):                       # shear from the applied loads only
        v = np.zeros_like(x)
        for t, m, a, b in ld:
            if t == "P": v -= m * (x > a)
            elif t == "W": v -= m * np.clip(np.minimum(x, b) - a, 0, None)
        return v

    def lm(x):                       # moment from the applied loads only (sagging +)
        s = np.zeros_like(x)
        for t, m, a, b in ld:
            if t == "P": s -= m * np.clip(x - a, 0, None) * (x > a)
            elif t == "M": s += m * (x > a)
            else:
                k = np.clip(np.minimum(x, b) - a, 0, None)
                s -= m * k * (x - a - k / 2)
        return s

    Ftot = sum(m if t == "P" else m * (b - a) if t == "W" else 0 for t, m, a, b in ld)

    # x grid: uniform + a point just before/after every load position (clean vertical jumps)
    eps = L * 1e-7
    sp = [0, L] + [a for _, _, a, _ in ld] + [b for t, _, _, b in ld if t == "W"]
    extra = [v for s in sp for v in (s - eps, s + eps) if 0 <= v <= L]
    xs = np.unique(np.concatenate([np.linspace(0, L, 1201), extra]))

    Le = np.array([L * (1 + 1e-9)])
    if bc == "ss":                                   # equilibrium
        R0, Mw = -lm(Le)[0] / L, 0.0
        reac = {"R at x = 0": R0, "R at x = L": Ftot - R0}
    elif bc == "cant":
        R0 = Ftot
        Mw = -(lm(Le)[0] + R0 * L)
        reac = {"Wall reaction": R0, "Wall moment": Mw}
    else:                                            # fixed-fixed: compatibility (theta(L)=0, v(L)=0)
        mB = lm(xs)
        I0, I1 = cum(xs, mB)[-1], cum(xs, (L - xs) * mB)[-1]
        A = np.array([[L**2 / 2, L], [L**3 / 6, L**2 / 2]])
        R0, Mw = np.linalg.solve(A, [-I0, -I1])
        reac = None

    V = lv(xs) + R0
    M = lm(xs) + R0 * xs + Mw
    V[0] = V[-1] = 0.0
    if reac is None:
        reac = {"R at x = 0": R0, "M at x = 0": Mw, "R at x = L": Ftot - R0, "M at x = L": M[-1]}

    th = cum(xs, M / EI)                             # EI v'' = M  ->  integrate twice
    vr = cum(xs, th)
    v = vr + (-vr[-1] / L * xs if bc == "ss" else 0)

    kM, kV, kD = (int(np.argmax(np.abs(a))) for a in (M, V, v))
    sig = abs(M[kM]) * c / I / 1e6                   # MPa
    return NS(x=xs, V=V, M=M, v=v, I=I, c=c, EI=EI, Ftot=Ftot, reac=reac, kM=kM, kV=kV, kD=kD,
              Mmax=M[kM], Vmax=V[kV], Dmax=v[kD], sig=sig, fos=Sy / sig if sig > 0 else np.inf)


# =====================================================================
# 2. FIGURES
# =====================================================================
def schematic(bc, L, loads):
    f = go.Figure()
    f.add_shape(type="rect", x0=0, x1=L, y0=-.07, y1=.07, fillcolor="#cbd5e1", line_width=0)
    if bc == "ss":
        f.add_trace(go.Scatter(x=[0, L], y=[-.12, -.12], mode="markers", hoverinfo="skip",
                               marker=dict(symbol="triangle-up", size=18, color="#64748b")))
    else:
        for x0, x1 in ([(-.025 * L, 0)] + ([(L, 1.025 * L)] if bc == "fix" else [])):
            f.add_shape(type="rect", x0=x0, x1=x1, y0=-.5, y1=.5, fillcolor="#475569", line_width=0)
    for t, m, a, b in loads:
        col = LCOL[t]
        if t == "P":
            s = 1 if m >= 0 else -1
            f.add_annotation(x=a, y=s * .09, ax=a, ay=s * 1.0, axref="x", ayref="y", showarrow=True,
                             arrowhead=2, arrowwidth=2.5, arrowcolor=col)
            f.add_annotation(x=a, y=s * 1.25, text=f"{m:g} kN", showarrow=False, font=dict(color=col))
        elif t == "W":
            s = 1 if m >= 0 else -1
            for x in np.linspace(a, b, max(3, int((b - a) / L * 20))):
                f.add_annotation(x=x, y=s * .09, ax=x, ay=s * .6, axref="x", ayref="y", showarrow=True,
                                 arrowhead=2, arrowwidth=1.5, arrowcolor=col)
            f.add_shape(type="line", x0=a, x1=b, y0=s * .6, y1=s * .6, line=dict(color=col, width=2))
            f.add_annotation(x=(a + b) / 2, y=s * .85, text=f"{m:g} kN/m", showarrow=False, font=dict(color=col))
        else:
            f.add_annotation(x=a, y=.55, text=("⟳ " if m >= 0 else "⟲ ") + f"{m:g} kN·m", showarrow=False,
                             font=dict(color=col, size=15))
    f.update_layout(template="plotly_dark", height=230, showlegend=False, margin=dict(l=40, r=20, t=10, b=30),
                    xaxis=dict(range=[-.08 * L, 1.08 * L], title="x (m)"), yaxis=dict(range=[-.8, 1.5], visible=False))
    return f


def diagrams(R):
    f = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=.07,
                      subplot_titles=("Shear force V(x)  [kN]", "Bending moment M(x)  [kN·m]",
                                      "Deflection v(x)  [mm]  (negative = downward)"))
    rows = [(R.V / 1e3, "V", "kN", "#22d3ee", "rgba(34,211,238,.15)", R.kV),
            (R.M / 1e3, "M", "kN·m", "#e879f9", "rgba(232,121,249,.15)", R.kM),
            (R.v * 1e3, "v", "mm", "#a3e635", "rgba(163,230,53,.15)", R.kD)]
    for i, (y, n, u, col, fill, k) in enumerate(rows, 1):
        ht = f"{n} = %{{y:.4f}} {u}<extra></extra>"
        f.add_trace(go.Scatter(x=R.x, y=y, name=n, line=dict(color=col, width=2), fill="tozeroy",
                               fillcolor=fill, hovertemplate=ht), row=i, col=1)
        f.add_trace(go.Scatter(x=[R.x[k]], y=[y[k]], mode="markers", name=f"max |{n}|", hovertemplate=ht,
                               marker=dict(color="#f87171", size=11, symbol="diamond", line=dict(color="#fff", width=1))),
                    row=i, col=1)
    f.update_xaxes(showspikes=True, spikemode="across", spikethickness=1, spikecolor="#e2e8f0")
    f.update_xaxes(title_text="x (m)", row=3, col=1)
    f.update_layout(template="plotly_dark", height=640, hovermode="x unified", showlegend=False,
                    margin=dict(l=50, r=20, t=40, b=40))
    return f


def stress_fig(R, xsec, Sy):
    k = int(np.argmin(np.abs(R.x - xsec)))
    M = R.M[k]
    y = np.linspace(-R.c, R.c, 41)
    sg = -M * y / R.I / 1e6                          # sigma = -M y / I  (tension +)
    f = go.Figure(go.Scatter(x=sg, y=y * 1e3, mode="lines", line=dict(color="#fbbf24", width=3), fill="tozerox",
                             fillcolor="rgba(251,191,36,.18)", name="σ(y)",
                             hovertemplate="σ = %{x:.2f} MPa<br>y = %{y:.1f} mm<extra></extra>"))
    for s in (Sy, -Sy):
        f.add_trace(go.Scatter(x=[s, s], y=[-R.c * 1e3, R.c * 1e3], mode="lines", name="yield",
                               line=dict(color="#f87171", dash="dash"), showlegend=s > 0))
    lim = max(Sy, abs(sg).max()) * 1.15
    f.update_layout(template="plotly_dark", height=380, margin=dict(l=50, r=20, t=30, b=40),
                    title=f"Section at x = {R.x[k]:.3f} m   (M = {M/1e3:.2f} kN·m, |σ|max = {abs(sg).max():.1f} MPa)",
                    xaxis=dict(title="σ (MPa), tension +", range=[-lim, lim], zeroline=True),
                    yaxis=dict(title="y from neutral axis (mm)", zeroline=True))
    return f


# =====================================================================
# 3. BREAKING SIMULATION  (frames are computed here in Python, played by Plotly)
# =====================================================================
def make_piece(px, py, r, L, mode, pv=None):
    p = dict(px=px, py=py, r=r, mode=mode, cx=px.mean(), cy=py.mean(), al=0.0, w=0.0, vx=0.0, vy=0.0, tx=0.0, ty=0.0)
    if mode == "h":                                  # hinged about a support
        ox, oy = px[pv], py[pv]
        p.update(ox=ox, oy=oy, rc=max(np.hypot(p["cx"] - ox, p["cy"] - oy), .05 * L),
                 th0=np.arctan2(p["cy"] - oy, p["cx"] - ox))
        p["w"] = -.8 * np.cos(p["th0"])
    if mode == "f":                                  # free falling body
        p.update(vx=.1 * L, vy=.25 * L, w=-1.4)
    return p


def pose(p):
    if p["mode"] == "s":
        return p["px"], p["py"]
    ox, oy = (p["ox"], p["oy"]) if p["mode"] == "h" else (p["cx"], p["cy"])
    ca, sa = np.cos(p["al"]), np.sin(p["al"])
    dx, dy = p["px"] - ox, p["py"] - oy
    return ox + dx * ca - dy * sa + p["tx"], oy + dx * sa + dy * ca + p["ty"]


def step(p, dt, gy):
    if p["mode"] == "h":                             # swinging rod: alpha'' = -k cos(theta) - damping
        p["w"] += (-.75 * G * np.cos(p["th0"] + p["al"]) / p["rc"] - 1.3 * p["w"]) * dt
        old = p["al"]
        p["al"] += p["w"] * dt
        if pose(p)[1].min() < gy:
            p["al"], p["w"] = old, p["w"] * -.25
    elif p["mode"] == "f":                           # free body: gravity, spin, bounce
        p["vy"] -= G * dt
        p["tx"] += p["vx"] * dt
        p["ty"] += p["vy"] * dt
        p["al"] += p["w"] * dt
        ymin = pose(p)[1].min()
        if ymin < gy:
            p["ty"] += gy - ymin
            p["vy"] = -.3 * p["vy"] if p["vy"] < -1 else 0.0
            p["vx"] *= .85
            p["w"] *= .7


def sim_figure(R, bc, L, Sy, loads, m0):
    fos, c = R.fos, R.c
    k = .12 * L / (abs(R.Dmax) * fos)                # exaggeration: deflection at failure = 12 % of L
    gy = -.42 * L
    xs = np.unique(np.append(np.linspace(0, L, 140), R.x[R.kM]))
    vi, Mi = np.interp(xs, R.x, R.v), np.interp(xs, R.x, R.M)
    rng = np.random.default_rng(1)

    def shape(m, jit=0.0):
        return xs, vi * m * k + jit * L * rng.uniform(-1, 1), np.abs(Mi) * m * c / R.I / 1e6 / Sy

    def beam_d(x, y, r):
        return dict(x=x, y=y, marker=dict(size=8, symbol="square", color=r, colorscale=CS, cmin=0, cmax=1, showscale=False),
                    customdata=np.asarray(r) * Sy)

    def loads_d(m):
        X, Y, S_, C = [], [], [], []
        for t, mag, a, b in loads:
            for x in (np.linspace(a, b, max(3, int((b - a) / L * 16))) if t == "W" else [a]):
                yb = np.interp(x, xs, vi) * m * k
                dn = mag >= 0
                X.append(x); Y.append(yb + (.06 if dn else -.06) * L)
                S_.append("star" if t == "M" else "triangle-down" if dn else "triangle-up"); C.append(LCOL[t])
        return dict(x=X, y=Y, marker=dict(symbol=S_, color=C, size=13))

    EMPTY = dict(x=[], y=[], marker=dict(size=8, symbol="square", color=[], colorscale=CS, cmin=0, cmax=1))
    frames, first = [], []

    def add(data, text=None):
        if not first:
            first.extend(data)          # keep the plain dicts: go.Frame turns them into Scatter objects
        ann = [] if not text else [dict(text=text, x=.5, y=.96, xref="paper", yref="paper", showarrow=False,
                                        font=dict(size=22, color="#f87171"))]
        frames.append(go.Frame(name=str(len(frames)), data=data, traces=[1, 2, 3, 4, 5], layout=dict(annotations=ann)))

    # ---- phase 1: load ramps up, beam bends and glows toward red
    start = min(m0, fos)
    for u in np.linspace(0, 1, 45):
        m = start + (fos - start) * (1 - (1 - u) ** 2)
        rt = m / fos
        add([beam_d(*shape(m, .006 * max(0, rt - .9) / .1)), EMPTY, EMPTY, dict(x=[], y=[]), loads_d(m)])
    for _ in range(8):                               # last tremble before fracture
        add([beam_d(*shape(fos, .008)), EMPTY, EMPTY, dict(x=[], y=[]), loads_d(fos)])

    # ---- phase 2: fracture at the point of maximum moment, pieces fall
    x, y, r = shape(fos)
    xb = R.x[R.kM]
    j = int(np.searchsorted(xs, xb))
    e0, e1 = xb < .02 * L, xb > .98 * L
    sl_l = slice(0, None) if e1 else None if e0 else slice(0, j + 1)
    sl_r = slice(0, None) if e0 else None if e1 else slice(j, None)

    def mk(sl, mode, pv=None):
        if sl is None: return None
        px, py, rr = x[sl], y[sl], r[sl]
        return make_piece(px, py, rr, L, mode, len(px) - 1 if pv == -1 else pv)

    if bc == "ss":     pcs = [mk(sl_l, "h", 0), mk(sl_r, "h", -1)]
    elif bc == "cant": pcs = [mk(sl_r, "f")] if e0 else [mk(sl_l, "s"), mk(sl_r, "f")]
    else:              pcs = [mk(sl_r, "h", -1)] if e0 else [mk(sl_l, "h", 0)] if e1 else [mk(sl_l, "s"), mk(sl_r, "s")]
    pcs = [p for p in pcs if p]

    n = 40
    ang, spd = rng.uniform(0, 2 * np.pi, n), rng.uniform(1.5, 6, n) * (L / 6) ** .5
    spx, spy = np.full(n, xb), np.full(n, np.interp(xb, xs, y))
    svx, svy, life = np.cos(ang) * spd, np.sin(ang) * spd + 2, rng.uniform(.4, 1.1, n)
    dt = 1 / 30
    for i in range(75):
        for p in pcs: step(p, dt, gy)
        svy -= G * .7 * dt; spx = spx + svx * dt; spy = spy + svy * dt; life -= dt
        alive = life > 0
        ds = [EMPTY, EMPTY]
        for slot, p in enumerate(pcs[:2]):
            px, py = pose(p)
            ds[slot] = dict(x=px, y=py, marker=dict(size=8, symbol="square", color=p["r"], colorscale=CS, cmin=0, cmax=1))
        add([EMPTY, ds[0], ds[1],
             dict(x=np.where(alive, spx, np.nan), y=np.where(alive, spy, np.nan),
                  marker=dict(size=6, color="#fbbf24", symbol="circle")), dict(x=[], y=[])],
            text=f"FRACTURE at x = {xb:.2f} m" if i > 2 else None)

    d0 = first
    sup = dict(x=[0, L] if bc == "ss" else [], y=[-.05 * L] * 2 if bc == "ss" else [])
    fig = go.Figure(
        data=[go.Scatter(**sup, mode="markers", hoverinfo="skip", marker=dict(symbol="triangle-up", size=18, color="#64748b")),
              go.Scatter(mode="markers", hovertemplate="x = %{x:.2f} m<br>σ = %{customdata:.1f} MPa<extra></extra>", **d0[0]),
              go.Scatter(mode="markers", hoverinfo="skip", **d0[1]), go.Scatter(mode="markers", hoverinfo="skip", **d0[2]),
              go.Scatter(mode="markers", hoverinfo="skip", **d0[3]), go.Scatter(mode="markers", hoverinfo="skip", **d0[4])],
        frames=frames)
    walls = [(-.03 * L, 0)] + ([(L, 1.03 * L)] if bc == "fix" else []) if bc != "ss" else []
    for x0, x1 in walls:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=-.14 * L, y1=.14 * L, fillcolor="#475569", line_width=0)
    fig.add_shape(type="rect", x0=-.1 * L, x1=1.1 * L, y0=gy - .05 * L, y1=gy, fillcolor="#1e293b", line_width=0)
    play = dict(frame=dict(duration=33, redraw=True), fromcurrent=True, transition=dict(duration=0))
    fig.update_layout(
        template="plotly_dark", height=480, showlegend=False, margin=dict(l=20, r=20, t=10, b=10),
        xaxis=dict(range=[-.08 * L, 1.08 * L], visible=False),
        yaxis=dict(range=[gy - .05 * L, .22 * L], visible=False, scaleanchor="x"),
        updatemenus=[dict(type="buttons", x=.02, y=.02, xanchor="left", yanchor="bottom", direction="left", buttons=[
            dict(label="▶ Play to failure", method="animate", args=[None, play]),
            dict(label="⏸ Pause", method="animate", args=[[None], dict(mode="immediate", frame=dict(duration=0, redraw=False))]),
            dict(label="⟲ Rewind", method="animate", args=[["0"], dict(mode="immediate", frame=dict(duration=0, redraw=True))])])])
    return fig


# =====================================================================
# 4. USER INTERFACE
# =====================================================================
st.set_page_config(page_title="Beam Bending & Deflection Analyzer", layout="wide")
st.title("Beam Bending & Deflection Analyzer")
st.caption("Solid Mechanics · Euler–Bernoulli beam · hover the charts to read V, M and v at any x")

with st.sidebar:
    st.header("Beam")
    bc = {"Simply supported": "ss", "Cantilever": "cant", "Fixed–fixed": "fix"}[
        st.radio("Boundary condition", ["Simply supported", "Cantilever", "Fixed–fixed"])]
    L = st.number_input("Length L (m)", 0.1, 100.0, 6.0, 0.5)
    if st.radio("Cross-section", ["Rectangular", "Circular"], horizontal=True) == "Rectangular":
        b = st.number_input("Width b (mm)", 1.0, 2000.0, 100.0) / 1e3
        h = st.number_input("Height h (mm)", 1.0, 2000.0, 200.0) / 1e3
        I, c = b * h**3 / 12, h / 2
    else:
        d = st.number_input("Diameter d (mm)", 1.0, 2000.0, 150.0) / 1e3
        I, c = np.pi * d**4 / 64, d / 2
    mat = st.selectbox("Material preset", list(MAT))
    E = st.number_input("Young’s modulus E (GPa)", 0.1, 1000.0, MAT[mat][0], key=f"E{mat}")
    Sy = st.number_input("Yield / breaking stress (MPa)", 1.0, 5000.0, MAT[mat][1], key=f"S{mat}")
    st.header("Loads")
    st.caption("Add rows with the + at the bottom. For a point load or moment use only 'Position / start'.")
    df = st.data_editor(
        pd.DataFrame({"Type": list(LT)[:2], "Magnitude": [20.0, 10.0], "Position / start (m)": [2.0, 3.0],
                      "End (m, UDL only)": [None, 6.0]}),
        num_rows="dynamic", use_container_width=True,
        column_config={"Type": st.column_config.SelectboxColumn(options=list(LT), required=True)})

loads = []
for _, row in df.dropna(subset=["Type", "Magnitude", "Position / start (m)"]).iterrows():
    t, a = LT[row["Type"]], float(row["Position / start (m)"])
    e = row["End (m, UDL only)"]
    loads.append((t, float(row["Magnitude"]), a, float(e) if t == "W" and pd.notna(e) else a))

R = solve(bc, L, I, c, E, Sy, loads)

tab1, tab2 = st.tabs(["Analysis", "Bending & breaking simulation"])

with tab1:
    if R.fos < 1:
        st.error(f"FAILURE: σmax = {R.sig:.1f} MPa exceeds the yield strength of {Sy:.0f} MPa (FoS = {R.fos:.2f}).")
    elif R.fos < 2:
        st.warning(f"CAUTION: factor of safety is {R.fos:.2f}, close to the limit.")
    else:
        st.success(f"SAFE: σmax = {R.sig:.1f} MPa, factor of safety = {'∞' if np.isinf(R.fos) else f'{R.fos:.2f}'}.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Max bending moment", f"{abs(R.Mmax)/1e3:.2f} kN·m", f"at x = {R.x[R.kM]:.2f} m", delta_color="off")
    m2.metric("Max shear force", f"{abs(R.Vmax)/1e3:.2f} kN", f"at x = {R.x[R.kV]:.2f} m", delta_color="off")
    m3.metric("Max deflection", f"{abs(R.Dmax)*1e3:.3f} mm", f"at x = {R.x[R.kD]:.2f} m", delta_color="off")
    m4.metric("Max bending stress", f"{R.sig:.1f} MPa", f"yield {Sy:.0f} MPa", delta_color="off")
    st.plotly_chart(schematic(bc, L, loads), use_container_width=True)
    st.plotly_chart(diagrams(R), use_container_width=True)
    left, right = st.columns([3, 2])
    with left:
        xsec = st.slider("Cross-section position x (m)", 0.0, float(L), float(R.x[R.kM]), float(L) / 200, key=f"x{L}")
        st.plotly_chart(stress_fig(R, xsec, Sy), use_container_width=True)
    with right:
        st.subheader("Support reactions")
        for name, val in R.reac.items():
            st.write(f"**{name}:** {val/1e3:.2f} {'kN·m' if name.startswith(('M', 'Wall m')) else 'kN'}")
        st.write(f"I = {I*1e12/1e6:.3e}×10⁶ mm⁴ · EI = {R.EI/1e3:.1f} kN·m²")

with tab2:
    if not np.isfinite(R.fos) or abs(R.Dmax) < 1e-15:
        st.info("Add at least one load so the beam has something to bend under.")
    else:
        st.write(f"The beam breaks when the load reaches **×{R.fos:.2f}** of the loads you set "
                 f"(σmax = {Sy:.0f} MPa at x = {R.x[R.kM]:.2f} m). Deflection is exaggerated so you can see it.")
        m0 = st.slider("Starting load multiplier", 0.0, float(R.fos), min(1.0, float(R.fos)), float(R.fos) / 100)
        st.plotly_chart(sim_figure(R, bc, L, Sy, loads, m0), use_container_width=True)
        st.caption("Press ▶ Play to failure. Colour = local bending stress (cyan low, red at yield). "
                   "Change the starting multiplier to begin from a heavier load.")