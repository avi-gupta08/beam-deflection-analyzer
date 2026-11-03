# Beam Bending & Deflection Analyzer

An interactive tool for analysing beams under different supports and loads. It plots shear force, bending moment, deflection and bending stress, checks the result against a yield limit, and includes a **live bending and fracture simulation**.

Built as a **Solid Mechanics (APL104)** course project by **Avi Gupta**, M.Tech (MSME), 1st year. The theory follows the course material taught by **Prof. Prakhar Gupta**, whose notes source is Ajeet Kumar's IIT Delhi APL104 web page (see [Acknowledgements](#acknowledgements)).

> **Disclosure:** this project was developed with AI assistance (Claude, by Anthropic). The mechanics were checked against closed-form textbook results (see [Validation](#validation)).

---

## Two versions, one method

| | Web version | Python version |
|---|---|---|
| File | `beam-analyzer.html` | `beam_analyzer.py` |
| Stack | HTML5, CSS3, Tailwind CSS, JavaScript, Chart.js, Canvas | Python 3, NumPy, pandas, Streamlit, Plotly |
| Run | Open the file in a browser | `streamlit run beam_analyzer.py` |
| Simulation | Real-time animation loop | Frames computed in Python, played by Plotly |

Both use the same algorithm, so each can be used to cross-check the other.

## Features

- **Boundary conditions:** simply supported, cantilever, fixed–fixed
- **Geometry and material:** length, rectangular (b × h) or circular (d) section, Young's modulus E, yield strength; presets for Steel, Aluminum and Wood
- **Loads (any number, editable):** point loads, uniformly distributed loads (UDL), concentrated moments
- **Results:** shear force V(x), bending moment M(x), deflection v(x), bending stress distribution σ = −My/I
- **Maximum values:** Mmax, Vmax, δmax and σmax with their locations
- **Failure check:** factor of safety against yield, with SAFE, CAUTION and FAILURE status
- **Hover inspection:** read V, M, v and σ at any position x
- **Support reactions** for every case, including the statically indeterminate fixed–fixed beam
- **Bending and breaking simulation:**
  - the beam bends in proportion to a load multiplier you control
  - it is coloured by local stress (cyan low, red at yield)
  - it shakes, cracks and fractures at the point of maximum moment when stress reaches the yield limit
  - the broken pieces fall under gravity (hinged pieces swing about the supports, free pieces fall and bounce)

## Quick start

**Web version**
```
Open beam-analyzer.html in any modern browser (internet needed for the Tailwind and Chart.js CDNs).
```

**Python version**
```bash
pip install streamlit plotly numpy pandas
streamlit run beam_analyzer.py
```
The app opens in your browser at `http://localhost:8501`.

## Sign convention

- Point loads and UDLs are positive **downward**
- Applied moments are positive **clockwise**
- **Sagging** bending moment is positive
- Deflection v is positive **upward** (a downward sag shows as negative)

## Theory and method

**1. Reactions.** From equilibrium, $\sum F = 0$ and $\sum M = 0$. The fixed–fixed beam is statically indeterminate, so two extra conditions are used (see step 4).

**2. Shear and moment.** Cutting the beam at $x$ and summing the loads to the left:

$$\frac{dM}{dx} = V, \qquad \frac{dV}{dx} = -w$$

**3. Bending stress (flexure formula).**

$$\sigma = -\frac{M\,y}{I}, \qquad \sigma_{max} = \frac{|M|_{max}\,c}{I}$$

with $I = \dfrac{bh^3}{12}$ (rectangle) or $I = \dfrac{\pi d^4}{64}$ (circle).

**4. Deflection (Euler–Bernoulli).**

$$EI\,\frac{d^2v}{dx^2} = M(x)$$

M/EI is integrated twice numerically (trapezoid rule on about 1200 points), and the integration constants are fixed by the boundary conditions:

| Beam | Conditions |
|---|---|
| Simply supported | $v(0) = v(L) = 0$ |
| Cantilever | $v(0) = 0,\ \theta(0) = 0$ |
| Fixed–fixed | $v = \theta = 0$ at both ends, which gives the two redundant reactions |

**5. Failure check.**

$$\text{FoS} = \frac{\sigma_{yield}}{\sigma_{max}}$$

SAFE for FoS ≥ 2, CAUTION for 1 ≤ FoS < 2, FAILURE for FoS < 1. At the extreme fibre the stress state is uniaxial, so the maximum-normal-stress, Tresca and von Mises criteria agree.

**6. Simulation.** The system is linear, so the stored results are scaled by a load multiplier $m$ (deflection × $m$, stress × $m$). Fracture occurs at $m = \text{FoS}$, at the section of maximum $|M|$. Deflections are drawn exaggerated so they are visible, and the app displays the factor.

## Course topics covered

Mapped to the [APL104 lecture index](https://web.iitd.ac.in/~ajeetk/APL104.html):

| Project feature | Lecture(s) |
|---|---|
| Young's modulus, linear elasticity | 15–16: Stress–strain relations |
| Support reactions from equilibrium | 5–6: Stress equilibrium equations |
| Flexure formula, neutral axis, moment of inertia | 23: Pure bending of beams |
| Shear force and bending moment diagrams | 24: Non-uniform bending of beams |
| Deflection by double integration, boundary conditions | 27: Theory of beams, Euler–Bernoulli beams |
| Yield check and factor of safety | 31–32: Theories of failure |

## Validation

The solver was checked against closed-form results (L = 6 m, E = 200 GPa, 100 × 200 mm section):

| Case | Computed | Closed form |
|---|---|---|
| Simply supported, 20 kN at centre: Mmax | 30.00 kN·m | PL/4 = 30 kN·m |
| Simply supported, 20 kN at centre: δmax | 6.75 mm | PL³/48EI = 6.75 mm |
| Simply supported, 10 kN/m over full span: Mmax | 45.00 kN·m | wL²/8 = 45 kN·m |
| Simply supported, 10 kN/m over full span: δmax | 12.656 mm | 5wL⁴/384EI = 12.656 mm |
| Cantilever, 20 kN at tip: Mmax | 120.00 kN·m | PL = 120 kN·m |
| Cantilever, 20 kN at tip: δmax | 108.00 mm | PL³/3EI = 108 mm |
| Fixed–fixed, 20 kN at centre: Mmax | 15.00 kN·m | PL/8 = 15 kN·m |
| Fixed–fixed, 20 kN at centre: δmax | 1.688 mm | PL³/192EI = 1.688 mm |

## Project structure

```
.
├── beam-analyzer.html    # web version (HTML + Tailwind + JavaScript + Chart.js)
├── beam_analyzer.py      # Python version (Streamlit + Plotly + NumPy)
└── README.md
```

## Limitations

- Euler–Bernoulli theory only: small deflections, plane sections, no shear deformation (less accurate for short, deep beams)
- Only bending stress is computed; the transverse shear stress τ = VQ/(Ib) is not
- Linear elastic material with no plasticity. Ductile metals would form a plastic hinge rather than snapping at yield
- Symmetric sections only, loaded through the centroid (no unsymmetrical bending)
- No self-weight, axial loads or buckling check
- The cantilever is always fixed at the left end
- The fracture animation is an illustration, not a fracture-mechanics model

## Possible extensions which i could've included but time was limited

1. Shear stress distribution and a maximum shear stress check
2. Von Mises and Tresca checks once shear stress is included (Lectures 31–32)
3. Euler buckling check (Lecture 28)
4. Deflection verification by energy methods (Lectures 29–30)
5. Unsymmetrical sections and shear centre (Lectures 25–26)

## Acknowledgements

- **Prof. Prakhar Gupta**, course instructor
- **Ajeet Kumar**, [*Solid Mechanics: APL104*](https://web.iitd.ac.in/~ajeetk/APL104.html), IIT Delhi: the lecture notes and videos used as the course reference
- Reference book: *Solid Mechanics for Undergraduates* by Ajeet Kumar ([web edition](https://web.iitd.ac.in/~ajeetk/smb/book.html)) and *Strength of Materials* by S. P. Timoshenko
- Built with [Chart.js](https://www.chartjs.org/), [Tailwind CSS](https://tailwindcss.com/), [Streamlit](https://streamlit.io/), [Plotly](https://plotly.com/python/) and [NumPy](https://numpy.org/)
- Built with cluad4e

## Author

**Avi Gupta**, B.Tech (MSME), 1st year
