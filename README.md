# Beam Bending & Deflection Analyzer

An interactive tool for analysing beams under different supports and loads. It plots shear force, bending moment, deflection and stress, checks the result against a yield limit, and includes a **3D bending and fracture simulation** with real-world scenarios, a moving-vehicle bridge crossing, a diving-board animation and a live Mohr's circle.

Built as a **Mechanics of Solids (ME2110)** course project by **Avi Gupta**, M.Tech (MSME), 1st year. The theory follows the course material taught by **Prof. Prakhar Gupta**, whose notes source is Ajeet Kumar's IIT Delhi APL104 web page (see [Acknowledgements](#acknowledgements)).

> **Development note:** The concept, requirements and feature specification were defined by Avi Gupta from the ME2110 course material. The code was generated with Claude (Anthropic) from his prompts. The solver was checked against closed-form beam formulas (see [Validation](#validation)).

---

## Two versions

| | Web version (full) | Python version |
|---|---|---|
| File | `beam-analyzer.html` | `beam_analyzer.py` |
| Stack | HTML5, CSS3, Tailwind CSS, JavaScript, Chart.js, three.js, Canvas | Python 3, NumPy, pandas, Streamlit, Plotly |
| Run | Open the file in a browser | `streamlit run beam_analyzer.py` |
| Simulation | 3D (and 2D) real-time animation | 2D animation, frames computed in Python |
| Scenarios, load library, moving vehicle, diver, drag-and-drop, Mohr's circle | Yes | **Not included** |

Both use the same solver method, so each can be used to cross-check the other. The Python version has the core analysis and the 2D breaking simulation only.

## Features (web version)

### Analysis
- **Boundary conditions:** simply supported, cantilever, fixed–fixed
- **Geometry and material:** length, rectangular (b × h) or circular (d) section, Young's modulus E, yield strength; presets for Steel, Aluminum and Wood
- **Loads (any number, editable):** point loads, uniformly distributed loads (UDL), concentrated moments
- **Results:** shear force V(x), bending moment M(x), deflection v(x), bending stress distribution σ = −My/I
- **Maximum values:** Mmax, Vmax, δmax and σmax with their locations
- **Failure check:** factor of safety against yield, with SAFE, CAUTION and FAILURE status
- **Hover inspection:** read V, M, v and σ at any position x, with a linked crosshair across all charts
- **Support reactions** for every case, including the statically indeterminate fixed–fixed beam
- **Mohr's circle:** click a height y on the stress chart to see the circle for the bending stress state at that point (uniaxial σx = −My/I, no transverse shear), with principal stresses σ1 and σ2 and maximum shear τmax.
- **Formulas in the chart titles:** every diagram is titled with the relation it is plotted from, for example EI·v″ = M(x).

### Real-world simulators and loads
- **Scenario presets:**
  - highway bridge girder with a truck
  - diving board with a swimmer
  - bookshelf under books
  - overhead crane girder
  - plain concrete balcony without rebar
  - aircraft wing spar
  - timber floor joist
  - roof beam under snow
  - pipe-rack beam with fixed ends
- **None option:** an "empty beam" choice and a **Clear all** button remove every load.
- **Real-world load library:** person, car (two axles), loaded truck (three axles), machine or motor, crane hoist, crowd, snow, stored goods, upward wind or lift, a moment, and the **self-weight** of the current beam (computed from its section and material).

### 3D simulation
- The beam is drawn in 3D and bends in proportion to a **load multiplier** you control. It is coloured by local stress (cyan low, red at yield).
- Drag to orbit and scroll to zoom. A button switches between 3D and 2D.
- When stress reaches the yield limit the beam shakes, cracks and **fractures** at the point of maximum moment, with a flash and sparks. The pieces fall (hinged pieces swing about the supports, free pieces fall and bounce) and the loads on the beam fall with them and disappear after landing.
- **Ramp load to failure** raises the load automatically. **Reset** rebuilds the beam.
- **Animate crossing:** a 3-axle truck drives across the bridge from x = 0 to beyond L. The charts update as it moves, the beam bends under it in 3D, and the dashed yellow lines trace the **maximum and minimum shear and moment envelopes** over the whole crossing (including the other loads on the beam). If the stress reaches the yield limit during the crossing, the beam fractures and the truck falls with it.
- **Dive:** a diver walks to the end of the board, bounces it twice, launches with a flip into water with a splash, and the board springs back and oscillates. The board is coloured by the stress in each section as it bounces.

### Interaction
- **Drag and drop on the schematic:** drag point loads and moments along the beam, drag either end of a UDL, or drag the middle of a UDL to move the whole load. The charts update live.

## Quick start

**Web version**
```
Open beam-analyzer.html in any modern browser (internet needed for the Tailwind, Chart.js and three.js CDNs).
```

**Python version**
```bash
pip install streamlit plotly numpy pandas
streamlit run beam_analyzer.py
```
The app opens in your browser at `http://localhost:8501`.

## How to use it

1. Pick a **real-world simulator** or set the boundary condition, section and material yourself.
2. Add loads from the **load library** or the table. Or drag them directly on the schematic.
3. Read the analysis: banner, cards, V, M and v diagrams, support reactions.
4. Click the **stress chart** at a height y to see the Mohr's circle.
5. In the simulation panel, move the **load multiplier** slider to bend the beam, or press **Ramp load to failure**.
6. Try **Animate crossing** on the bridge scenario and **Dive** on the diving board.

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

**5. Mohr's circle (bending stress state).** At height $y$ the stress state is uniaxial: $\sigma_x = -My/I$, $\sigma_y = 0$, $\tau_{xy} = 0$. The circle has centre $\sigma_x/2$ and radius

$$\tau_{max} = \left|\frac{\sigma_x}{2}\right|, \qquad \sigma_{1,2} = \frac{\sigma_x}{2} \pm \tau_{max}$$

The transverse shear stress $\tau = VQ/(Ib)$ is deliberately not included, because it has not been covered in the ME2110 course yet.

**6. Failure check.**

$$\text{FoS} = \frac{\sigma_{yield}}{\sigma_{max}}$$

SAFE for FoS ≥ 2, CAUTION for 1 ≤ FoS < 2, FAILURE for FoS < 1. This check uses the maximum bending stress at the outer fibre, where the state is uniaxial.

**7. Moving loads and envelopes.** For each vehicle position (91 steps across the span plus run-off), the beam is solved with the vehicle's axles that are on the beam added to the existing loads. The envelope at each $x$ is the maximum and minimum of $M$ and $V$ over all positions.

**8. Simulation.** The system is linear, so stored results are scaled by the load multiplier $m$ (deflection × $m$, stress × $m$). Fracture occurs at $m = \text{FoS}$, at the section of maximum $|M|$. Deflections are drawn exaggerated so they are visible, and the page shows the factor.

## Course topics covered

Course: ME2110 (Mechanics of Solids). Topics are mapped to the titles on [Ajeet Kumar's APL104 lecture index](https://web.iitd.ac.in/~ajeetk/APL104.html), the notes source. Lecture numbers may differ from your course:

| Project feature | Lecture(s) |
|---|---|
| Young's modulus, linear elasticity | 15–16: Stress–strain relations |
| Support reactions from equilibrium | 5–6: Stress equilibrium equations |
| Principal stresses and Mohr's circle | 7–10: Stress transformation |
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

The solver values above were checked numerically. The 3D view, vehicle crossing, diver, drag-and-drop and Mohr's circle are visual features that are worth checking by hand against the formulas in the Theory section.

## Project structure

```
.
├── beam-analyzer.html    # full web version (HTML + Tailwind + JavaScript + Chart.js + three.js)
├── beam_analyzer.py      # Python version (Streamlit + Plotly + NumPy), core analysis and 2D simulation
└── README.md
```

## Limitations

- Euler–Bernoulli theory only: small deflections, plane sections, no shear deformation (less accurate for short, deep beams)
- The failure check uses bending stress only. The Mohr's circle shows the uniaxial bending state at any height; a full von Mises or Tresca check is not done
- Transverse shear stress (τ = VQ/Ib) is not included
- Linear elastic material with no plasticity. Ductile metals would form a plastic hinge rather than snapping at yield
- Symmetric sections only, loaded through the centroid (no unsymmetrical bending)
- No axial loads or buckling check
- The cantilever is always fixed at the left end
- The moving-vehicle analysis is static (quasi-static): the vehicle's weight is applied at each position with no dynamic amplification, and only one vehicle type (a 3-axle truck) is built in
- The fracture and dive animations are illustrations, not fracture-mechanics or biomechanics models. Deflection in the animations is exaggerated
- The scenario presets use estimated sizes for teaching, not design values

## Possible extensions

1. Transverse shear stress, then a combined-stress (von Mises or Tresca) check along the beam
2. Euler buckling check (Lecture 28)
3. Deflection verification by energy methods (Lectures 29–30)
4. Unsymmetrical sections and shear centre (Lectures 25–26)
5. Vehicle choices and dynamic amplification factors for bridge loading
6. Bringing the scenarios, 3D view and Mohr's circle to the Python version

## Acknowledgements

- **Prof. Prakhar Gupta**, course instructor
- **Ajeet Kumar**, [*Solid Mechanics: APL104*](https://web.iitd.ac.in/~ajeetk/APL104.html), IIT Delhi: the lecture notes and videos used as the course reference
- Reference book: *Solid Mechanics for Undergraduates* by Ajeet Kumar ([web edition](https://web.iitd.ac.in/~ajeetk/smb/book.html)) and *Strength of Materials* by S. P. Timoshenko
- Code generated with [Claude](https://claude.ai) (Anthropic) from the author's prompts
- Built with [Chart.js](https://www.chartjs.org/), [three.js](https://threejs.org/), [Tailwind CSS](https://tailwindcss.com/), [Streamlit](https://streamlit.io/), [Plotly](https://plotly.com/python/) and [NumPy](https://numpy.org/)

## Author

**Avi Gupta**, M.Tech (MSME), 1st year

## License

Add a license of your choice before publishing (for example MIT) and place it in a `LICENSE` file.
