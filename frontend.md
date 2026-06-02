AnomlyX Frontend UI Prompts

Use these prompts in Stitch to generate the UI pages for AnomlyX. The visual direction should feel like a professional industrial diagnostics tool: clean, modern, technical, trustworthy, and easy to scan. Avoid a marketing landing-page feel. The app should look useful from the first screen.

Global UI Style

Create a responsive web application called AnomlyX for industrial metal defect diagnostics. Use a clean engineering-dashboard style with a light background, dark text, subtle borders, and strong visual hierarchy. Use colors carefully: neutral white/gray base, deep charcoal text, steel blue accents, warning amber for medium severity, red for high severity, and green for safe/low status. The interface should feel professional for factory quality control, welding inspection, and engineering students.

Use a top navigation bar with the AnomlyX name on the left and simple navigation links: Dashboard, Diagnose, Defect Library, Reports. Use compact cards only for repeated content or tool panels. Use icons for actions like upload, print, download, search, and warning status. Make the layout fully responsive for desktop and mobile. Buttons should be clear and practical. Avoid decorative hero sections, gradients, and unnecessary animations.

Page 1: Dashboard / Home

Prompt:
Design the main dashboard page for AnomlyX, an industrial metal defect diagnostics platform. The first screen should immediately show the actual diagnostic tool, not a marketing hero. At the top, include a clean navigation bar with the AnomlyX logo/name, links for Dashboard, Diagnose, Defect Library, and Reports, plus a small status badge that says Manual Prototype.

The main dashboard should have a two-column desktop layout. On the left, place a primary panel titled Quick Diagnosis with controls for selecting Defect Type and Severity Level. Include dropdown fields for defects such as Porosity, Crack, Slag Inclusion, Blowhole, Undercut, Lack of Fusion, and Surface Rust. Include a segmented control for severity: Low, Medium, High. Add a primary button labeled View Diagnosis with a search or scan icon.

On the right, show a large Reference Preview panel with a metal defect image placeholder, a small severity badge, and short metadata such as Material: Steel, Inspection Mode: Manual, Confidence: Not AI Generated. Below the main area, add three compact summary cards: Defect Categories, Severity Levels, and Reports Generated. Add a recent activity table showing sample rows like Porosity - Medium, Crack - High, Slag Inclusion - Low.

The style should be clean, industrial, and practical. Use subtle shadows, 8px border radius, thin dividers, and strong spacing. The page should work well on mobile by stacking panels vertically.

Page 2: Manual Diagnosis Page

Prompt:
Design a Manual Diagnosis page for AnomlyX where users can manually inspect metal defects before machine learning is added. This page should be the core working screen of the prototype.

Use a split layout. On the left, create an Input Panel with form controls. Include a dropdown for Defect Type, a segmented control for Severity Level with Low, Medium, and High, and a small reference image selector showing three thumbnails for severity examples. Include fields for optional notes: Inspection Location, Batch ID, Inspector Name, and Date. Add a primary button labeled Generate Diagnosis and a secondary button labeled Reset.

On the right, create a Diagnosis Result panel. It should show the selected defect name, severity badge, defect reference image, root cause section, engineering remedy section, and prevention tips section. Each section should have a clear heading and readable text layout. Root Cause should use an alert/info icon. Remedy should use a tool/wrench icon. Prevention Tips should use a checklist icon.

At the bottom of the result panel, include action buttons: Print Report, Export PDF, and Save Result. The Print and Export buttons should use icons. Make the design feel like software used by engineers or factory quality-control teams. Keep the page dense but readable. No marketing copy. Prioritize usability and clarity.

Page 3: Defect Library Page

Prompt:
Design a Defect Library page for AnomlyX. This page should help users browse different industrial metal defects and understand their severity levels visually.

At the top, include a compact page header with the title Defect Library, a short subtitle Browse known metal defects, root causes, and remedies, and a search input with a filter icon. Add filter chips or dropdowns for Defect Type, Severity, and Process Type such as Welding, Casting, Machining, and Corrosion.

Create a responsive grid of defect cards. Each card should show a real-looking metal defect image placeholder, defect name, short description, three mini severity indicators labeled Low, Medium, High, and a button labeled View Details. Example cards: Porosity, Crack, Slag Inclusion, Blowhole, Undercut, Lack of Fusion, Surface Rust, Pitting Corrosion.

Each card should look practical and compact, not decorative. Use consistent image ratios, small severity badges, and clean spacing. On mobile, cards should stack in one column. On desktop, use a 3-column grid. Include a side filter panel on desktop if it fits, but collapse filters on mobile.

Page 4: Defect Detail Page

Prompt:
Design a Defect Detail page for AnomlyX for one selected defect, for example Porosity. The page should explain the defect clearly and show Low, Medium, and High severity examples.

At the top, show a breadcrumb like Defect Library > Porosity and a page title Porosity. Include a severity overview strip with three selectable tabs: Low, Medium, High. Below it, create a large comparison section with three columns, one for each severity level. Each column should include a defect image, severity badge, visual signs, root causes, and recommended remedies.

Include a technical information section below the comparison area. It should show common causes, affected processes, inspection notes, and prevention checklist. Use tables or structured rows where helpful. Add a button labeled Use in Diagnosis that takes the user back to the Manual Diagnosis page with this defect selected.

The visual style should be serious and engineering-focused. Make the severity comparison easy to scan. Use green for low, amber for medium, and red for high. Avoid long paragraph blocks; use compact readable sections.

Page 5: Report / Printable Result Page

Prompt:
Design a printable diagnostic report page for AnomlyX. The page should look like a professional factory inspection report that can be printed or exported as PDF.

Use a clean document-style layout with a header containing AnomlyX, Report ID, Date, Inspector Name, and Batch ID. Below the header, show the diagnosis summary in a structured table: Defect Type, Severity Level, Material, Inspection Mode, and Status.

Include a large image area showing the selected defect reference image. Next to or below it, show Root Cause Analysis, Recommended Remedy, and Prevention Checklist. Use clear section dividers and compact text. Add a severity badge near the top so the risk level is immediately visible.

At the top-right of the screen version, include action buttons for Print, Download PDF, and Back to Diagnosis. For print layout, hide navigation and buttons. The page should be highly readable in black and white but still use subtle color badges on screen.

Page 6: Future AI Upload Page

Prompt:
Design a future AI Upload Diagnosis page for AnomlyX. This page will be used later when the machine-learning model is added. It should still match the current app style.

Create a main upload workspace. At the top, show the title AI Image Diagnosis and a small badge that says Future ML Feature. In the center, create a drag-and-drop upload area with an upload icon, text that says Upload metal defect image, and accepted formats JPG, PNG, WEBP. Include a preview area that shows the uploaded image.

On the right side, create a Prediction Result panel. Show placeholder states for Defect Type, Severity, Confidence Score, and Suggested Remedy. Include a progress state for Analyzing Image and an empty state before upload. Add a button labeled Run Analysis and another labeled Use Manual Diagnosis.

Below the upload area, include image quality guidelines using compact checklist rows: good lighting, close crop of metal surface, avoid blurry image, remove unnecessary background. The design should clearly communicate that AI is coming later while still feeling part of the product.

Page 7: Settings / Data Management page
Prompt:
Design a Settings and Data Management page for AnomlyX. This page should help the project owner manage defect data in the frontend prototype.

Create a practical admin-style layout. Include sections for Defect Categories, Severity Definitions, Root Causes, Remedies, and Image References. Use a table showing defect records with columns: Defect Name, Severity Levels Completed, Images Added, Remedies Added, Last Updated, and Actions.

Add action buttons for Add Defect, Edit, Duplicate, and Delete. Include small status indicators showing whether each defect has Low, Medium, and High data completed. Add a side panel or modal design for editing one defect, with fields for defect name, severity, root cause, remedy, prevention tip, and image path.

The style should be simple and functional, like a lightweight internal tool. Keep spacing compact. Use clear labels and avoid unnecessary decoration. Make it responsive so the table becomes stacked cards on mobile.

Recommended Page Order for Building

1. Manual Diagnosis Page
2. Defect Library Page
3. Defect Detail Page
4. Report / Printable Result Page
5. Dashboard / Home
6. Future AI Upload Page
7. Settings / Data Management Page

Start with the Manual Diagnosis page because it proves the main product logic first. The other pages can grow around it.
