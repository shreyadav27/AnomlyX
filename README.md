# AnomlyX

AnomlyX is a frontend prototype for industrial metal defect diagnosis. It helps an inspector manually select a defect type and severity level, then generates visual signs, likely root causes, engineering remedies, prevention checks, and a printable inspection report.

The project is currently built as a static web app using HTML, CSS, and JavaScript. It is intended as a manual diagnostic workflow first, with a future path toward image upload and machine-learning based prediction.

## Features

- Manual defect diagnosis by defect type and severity.
- Severity levels for `Low`, `Medium`, and `High`.
- Defect reference image thumbnails for severity comparison.
- Root cause, remedy, and prevention checklist output.
- Defect library with search and quick-load actions.
- Printable diagnostic report page.
- Browser-based save action using `localStorage`.
- Placeholder screen for a future AI image diagnosis workflow.

## Supported Defect List

The current manual knowledge base includes:

| Defect | Process Area | Description |
| --- | --- | --- |
| Porosity | Casting / Welding | Gas pockets or cavities trapped inside or on the surface of metal. |
| Crack | Structural | Linear fracture caused by stress, cooling rate, fatigue, or poor fusion. |
| Slag Inclusion | Welding | Non-metallic trapped material inside a weld bead or casting. |
| Misrun | Casting | Incomplete casting caused by molten metal failing to fill the mold cavity. |
| Corrosion | Service / Surface | Chemical or electrochemical degradation such as rust, pitting, or section loss. |
| Shrinkage | Casting | Void or depression caused by metal contraction during solidification. |

Each defect has three severity entries: low, medium, and high. Every severity entry includes visual signs, root cause notes, recommended remedies, and prevention checklist items.

## Project Structure

```text
AnomlyX/
├── index.html          # Main application markup
├── styles.css          # Application styling and responsive layout
├── script.js           # Defect data, UI rendering, navigation, reports
├── assets/defects/     # Normalized defect reference images
├── frontend.md         # UI prompt/design notes
├── plan.md             # Development roadmap notes
└── README.md
```

## How to Run

Because this is a static prototype, no build step is required.

1. Open `index.html` directly in a browser.
2. Or serve the folder locally:

```bash
python3 -m http.server 8000
```

Then visit:

```text
http://localhost:8000
```

## Basic Usage

1. Go to the `Diagnose` page.
2. Select a defect type.
3. Choose `Low`, `Medium`, or `High` severity.
4. Add optional inspector, batch, material, location, and notes.
5. Click `Generate Diagnosis` or `Update Result`.
6. Use `Print Report` to open the report page and print/export from the browser.
7. Use the `Defect Library` to browse supported defects and load one into the diagnosis workflow.

## Known Defects and Limitations

- The extra `manual-porosity-enhanced.png` asset is not currently used by the app workflow.
- The AI upload page is only a placeholder. No model, backend API, or image prediction flow is connected yet.
- The app uses static frontend data. Defects, remedies, and image paths are hard-coded in `script.js`.
- Saved results only store the latest report in browser `localStorage`; there is no report history database.
- Print/export currently relies on the browser print dialog instead of a dedicated PDF export library.
- The diagnostic guidance is educational/prototype content and should be validated by qualified manufacturing or quality-control experts before real production use.

## Future Improvements

- Move defect data into a JSON file or backend service.
- Keep new image assets named with the same pattern: `assets/defects/<severity>-<defect>.png`.
- Add more defect categories such as blowhole, undercut, lack of fusion, pitting corrosion, cold shut, and surface roughness.
- Add report history, exportable PDFs, and persistent inspection records.
- Add image upload and ML inference using a trained computer-vision model.
- Add dataset folders for training images grouped by defect and severity.
- Validate root causes and remedies against welding/casting inspection standards.

## Tech Stack

- HTML5
- CSS3
- Vanilla JavaScript
- Google Fonts and Material Symbols

## Status

AnomlyX is in the manual prototype phase. The current focus is validating the diagnostic workflow, defect knowledge base, and report layout before adding a machine-learning backend.
