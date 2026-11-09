# Beam Bending, Deflection & Column Buckling Analyzer

An interactive tool with two pages. The **beam page** analyses beams under different supports and loads: it plots shear force, bending moment, deflection and stress, checks the result against a yield limit, and includes a **3D bending and fracture simulation** with real-world scenarios, a moving-vehicle bridge crossing, a diving-board animation and a live Mohr's circle. The **column buckling page** simulates the sudden buckling and fracture of a slender column, with real-life examples.

Built as a **Mechanics of Solids (ME2110)** course project by **Avi Gupta**, M.Tech (MSME), 1st year. The theory follows the course material taught by **Prof. Prakhar Gupta**.

> **Development note:** The concept, requirements and feature specification were defined by Avi Gupta from the ME2110 course material. The code was generated with Claude (Anthropic) from his prompts. The solver was checked against closed-form beam formulas (see [Validation](#validation)).

---

## Technologies

| Layer | Technology | Role |
|---|---|---|
| Page and styling | HTML5, CSS3, Tailwind CSS | Interface and dark theme |
| Logic | JavaScript (ES6) | Beam solver, buckling model, interaction, animation physics |
| Charts | Chart.js | Shear, moment, deflection and P_cr charts |
| 2D drawing | HTML5 Canvas | Beam schematic, 2D simulation, Mohr's circle, buckling animation |
| 3D drawing | three.js (WebGL) | 3D beam, loads, truck and diver |

The whole project is one self-contained file, `beam-analyzer.html`.

## Features

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

## Column buckling page

A second page, reached with the **Column buckling** button at the top (or the `#buckling` link), simulates the buckling of a slender column. It uses only the concepts from the ME2110 notes:

- **End conditions:** fixed–free (P<sub>cr</sub> = π²EI/4L², with higher modes P<sub>n</sub> = [(2n+1)π/2]²EI/L²), pin–pin (π²EI/L²) and fixed–fixed (4π²EI/L²).
- **Section and material:** rectangular (weaker axis, bh³/12) or circular (πd⁴/64) section, with E and yield strength. P<sub>cr</sub> ∝ EI and P<sub>cr</sub> ∝ 1/L² are shown in a table and a chart.
- **Slenderness check:** the column is treated as slender when L/D > 10. A short column crushes before it buckles.
- **Animation:** the load is raised towards P<sub>cr</sub>. At P<sub>cr</sub> the column bends suddenly into the buckled shape y = y<sup>L</sup>(1 − cos(√(P/EI) x)) (fixed–free), and the sideways deflection grows until the bending stress σ = P/A + Mc/I (with M = EI y″) reaches the yield strength. The column then **fractures** at the section of largest stress and the pieces fall.
- **Real-life examples:** flagpole or lamp post, piston rod, plastic ruler, truss strut, building column, wooden scaffold pole and an antenna mast.

The sideways deflection is not fixed by the linear theory in the notes, so the animation exaggerates it and lets it grow until yield. The fracture motion is an illustration.

## Quick start

```
Open beam-analyzer.html in any modern browser. An internet connection is needed to load the Tailwind, Chart.js and three.js libraries.
```

## How to use it

1. Pick a **real-world simulator** or set the boundary condition, section and material yourself.
2. Add loads from the **load library** or the table. Or drag them directly on the schematic.
3. Read the analysis: banner, cards, V, M and v diagrams, support reactions.
4. Click the **stress chart** at a height y to see the Mohr's circle.
5. In the simulation panel, move the **load multiplier** slider to bend the beam, or press **Ramp load to failure**.
6. Try **Animate crossing** on the bridge scenario and **Dive** on the diving board.
7. Press **Column buckling** at the top, pick a real-life example, choose the end condition, and press **Run buckling test**. Watch the column stay straight until P = P_cr, buckle suddenly, and fracture.

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

M/EI is integrated twice numerically (trapezoid rule on about 600 points, plus extra points around each load), and the integration constants are fixed by the boundary conditions:

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

**8. Simulation (beam page).** The system is linear, so stored results are scaled by the load multiplier $m$ (deflection × $m$, stress × $m$). Fracture occurs at $m = \text{FoS}$, at the section of maximum $|M|$. Deflections are drawn exaggerated so they are visible, and the page shows the factor.

**9. Column buckling (buckling page).** A slender column under an axial compressive load P is analysed with the same moment–curvature relation, $M = EI\,y''$. For a fixed–free column of length $L$ with end deflection $y^L$, the moment at $x$ is $M = P(y^L - y)$, which gives

$$EI\,y'' + P\,y = P\,y^L$$

The solution with $y(0) = 0$ and $y'(0) = 0$ is

$$y(x) = y^L\left(1 - \cos\sqrt{\tfrac{P}{EI}}\,x\right)$$

and the condition $y(L) = y^L$ requires $\cos\left(\sqrt{P/EI}\,L\right) = 0$, so

$$P_n = \left[\frac{(2n+1)\pi}{2}\right]^2 \frac{EI}{L^2}, \qquad P_{cr} = P_0 = \frac{\pi^2 EI}{4L^2}$$

Higher modes occur only if the lower ones are restrained, and between two modes no buckled profile exists. The same method gives $P_{cr} = \pi^2 EI/L^2$ for pin–pin and $4\pi^2 EI/L^2$ for fixed–fixed columns, so the three cases are in the ratio 1 : 4 : 16. In all cases $P_{cr} \propto EI$ and $P_{cr} \propto 1/L^2$, with $I = \pi d^4/64$ (circle) or $bh^3/12$ about the weaker axis (rectangle). A column is treated as slender when $L/D > 10$. Fracture in the animation occurs when the combined axial and bending stress reaches yield,

$$\sigma = \frac{P}{A} + \frac{M\,c}{I} \ge \sigma_{yield}, \qquad M = EI\,y''$$

The linear theory leaves the size of the sideways deflection undetermined, so the animation lets it grow until the stress reaches yield and exaggerates it for display.

## Validation

The beam solver in the page was run in Node.js and checked against closed-form results (L = 6 m, E = 200 GPa, 100 × 200 mm section):

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

Column buckling checks (steel, E = 200 GPa, 20 × 20 mm, L = 1 m, fixed–free): the program gives P_cr = 6579.7 N and the closed form π²EI/4L² gives 6579.7 N. For the same column the pin–pin load is 4 times the fixed–free load and the fixed–fixed load is 4 times the pin–pin load (1 : 4 : 16). All seven real-life examples were checked to be slender (L/D > 10) with an Euler stress below yield, so they buckle rather than crush.

The solver values above were checked numerically. The 3D view, vehicle crossing, diver, drag-and-drop and Mohr's circle are visual features that are worth checking by hand against the formulas in the Theory section.

## Project structure

```
.
├── beam-analyzer.html    # full web version: beam page + column buckling page (HTML + Tailwind + JavaScript + Chart.js + three.js)
└── README.md
└── LICENSE
```

## Limitations

- Euler–Bernoulli theory only: small deflections, plane sections, no shear deformation (less accurate for short, deep beams)
- The failure check uses bending stress only. The Mohr's circle shows the uniaxial bending state at any height; a full von Mises or Tresca check is not done
- Transverse shear stress (τ = VQ/Ib) is not included
- Linear elastic material with no plasticity. Ductile metals would form a plastic hinge rather than snapping at yield
- Symmetric sections only, loaded through the centroid (no unsymmetrical bending)
- The beam analysis has no axial loads; column buckling is handled separately on the buckling page
- The cantilever is always fixed at the left end
- Buckling page: a perfectly straight, centrally loaded, elastic column. There are no initial imperfections or load eccentricity, no inelastic (short-column) buckling formula, and no fixed–pinned end condition
- Buckling page: the linear theory does not fix the buckled amplitude, so the growth to fracture and the fracture motion are illustrations
- The moving-vehicle analysis is static (quasi-static): the vehicle's weight is applied at each position with no dynamic amplification, and only one vehicle type (a 3-axle truck) is built in
- The fracture and dive animations are illustrations, not fracture-mechanics or biomechanics models. Deflection in the animations is exaggerated
- The scenario presets use estimated sizes for teaching, not design values

## Possible extensions

1. Transverse shear stress, then a combined-stress (von Mises or Tresca) check along the beam
2. Fixed–pinned columns and buckling about both axes
3. Deflection verification by energy methods (Lectures 29–30)
4. Unsymmetrical sections and shear centre (Lectures 25–26)
5. Vehicle choices and dynamic amplification factors for bridge loading

## Acknowledgements

- **Prof. Prakhar Gupta**, course instructor
- **Ajeet Kumar**, [*Solid Mechanics: APL104*](https://web.iitd.ac.in/~ajeetk/APL104.html), IIT Delhi: the lecture notes and videos used as the course reference
- Reference book: *Solid Mechanics for Undergraduates* by Ajeet Kumar ([web edition](https://web.iitd.ac.in/~ajeetk/smb/book.html)) and *Strength of Materials* by S. P. Timoshenko
- Code generated with [Claude](https://claude.ai) (Anthropic) from the author's prompts
- Built with [Chart.js](https://www.chartjs.org/), [three.js](https://threejs.org/) and [Tailwind CSS](https://tailwindcss.com/)

## Author

**Avi Gupta**, M.Tech (MSME), 1st year
