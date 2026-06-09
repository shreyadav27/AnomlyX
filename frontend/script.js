const defectAssetPath = "assets/defects/";
const apiBaseUrl = window.ANOMLYX_API_BASE_URL || "http://127.0.0.1:8002";
const themeStorageKey = "anomlyx-theme";
const historyStorageKey = "anomlyx-history";
const userStorageKey = "anomlyx-current-user";

const loginUsers = [
  { role: "Inspector", name: "Student Inspector", icon: "engineering", label: "Inspection line" },
  { role: "Supervisor", name: "Line Supervisor", icon: "admin_panel_settings", label: "Review access" },
  { role: "Analyst", name: "Quality Analyst", icon: "analytics", label: "Quality lab" },
  { role: "Personal", name: "Personal User", icon: "person", label: "Personal space" }
];

function getDefectImage(fileName) {
  return `${defectAssetPath}${fileName}`;
}

function createReferenceImage(defectName, severity, accentColor) {
  const severityMap = {
    low: { count: 3, label: "LOW", opacity: 0.32 },
    medium: { count: 6, label: "MEDIUM", opacity: 0.48 },
    high: { count: 10, label: "HIGH", opacity: 0.66 }
  };
  const level = severityMap[severity];
  const marks = Array.from({ length: level.count }, (_, index) => {
    const x = 58 + (index * 67) % 560;
    const y = 72 + (index * 41) % 275;
    const width = severity === "high" ? 112 : severity === "medium" ? 82 : 52;
    return `<ellipse cx="${x}" cy="${y}" rx="${width / 2}" ry="${8 + index % 4}" fill="${accentColor}" opacity="${level.opacity}" transform="rotate(${-12 + index * 7} ${x} ${y})"/>`;
  }).join("");

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560">
      <defs>
        <linearGradient id="metal" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stop-color="#e8edf3"/>
          <stop offset="0.45" stop-color="#aeb8c5"/>
          <stop offset="1" stop-color="#f8fafc"/>
        </linearGradient>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch"/>
          <feColorMatrix type="saturate" values="0"/>
          <feComponentTransfer>
            <feFuncA type="table" tableValues="0 0.24"/>
          </feComponentTransfer>
        </filter>
      </defs>
      <rect width="900" height="560" fill="url(#metal)"/>
      <rect width="900" height="560" filter="url(#grain)" opacity="0.5"/>
      <g>${marks}</g>
      <rect x="34" y="34" width="282" height="72" rx="8" fill="#0b1c30" opacity="0.86"/>
      <text x="56" y="68" fill="#ffffff" font-family="Arial, sans-serif" font-size="24" font-weight="700">${defectName}</text>
      <text x="56" y="94" fill="${accentColor}" font-family="Arial, sans-serif" font-size="18" font-weight="700">${level.label} SEVERITY</text>
    </svg>
  `;

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

function createPorosityImage(severity) {
  const severityMap = {
    low: { pores: 12, size: 12, label: "LOW", opacity: 0.58 },
    medium: { pores: 28, size: 18, label: "MEDIUM", opacity: 0.7 },
    high: { pores: 48, size: 26, label: "HIGH", opacity: 0.82 }
  };
  const level = severityMap[severity];
  const pores = Array.from({ length: level.pores }, (_, index) => {
    const x = 70 + (index * 83) % 760;
    const y = 105 + (index * 53) % 360;
    const radius = Math.max(5, level.size - (index % 7) * 2);
    return `
      <circle cx="${x}" cy="${y}" r="${radius}" fill="#151515" opacity="${level.opacity}"/>
      <circle cx="${x - radius / 3}" cy="${y - radius / 3}" r="${Math.max(2, radius / 4)}" fill="#ffffff" opacity="0.18"/>
    `;
  }).join("");

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560">
      <defs>
        <linearGradient id="metal" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stop-color="#cbd5e1"/>
          <stop offset="0.35" stop-color="#eef2f7"/>
          <stop offset="0.7" stop-color="#8f9aaa"/>
          <stop offset="1" stop-color="#f8fafc"/>
        </linearGradient>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.72" numOctaves="4" stitchTiles="stitch"/>
          <feColorMatrix type="saturate" values="0"/>
          <feComponentTransfer>
            <feFuncA type="table" tableValues="0 0.28"/>
          </feComponentTransfer>
        </filter>
      </defs>
      <rect width="900" height="560" fill="url(#metal)"/>
      <rect width="900" height="560" filter="url(#grain)" opacity="0.62"/>
      <g>${pores}</g>
      <rect x="34" y="34" width="294" height="72" rx="8" fill="#0b1c30" opacity="0.88"/>
      <text x="56" y="68" fill="#ffffff" font-family="Arial, sans-serif" font-size="24" font-weight="700">Porosity</text>
      <text x="56" y="94" fill="#fd761a" font-family="Arial, sans-serif" font-size="18" font-weight="700">${level.label} SEVERITY</text>
    </svg>
  `;

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

const defectData = {
  porosity: {
    name: "Porosity",
    category: "Casting / Welding",
    description: "Small gas pockets or cavities trapped inside or on the surface of the metal.",
    images: {
      low: getDefectImage("low-porosity.png"),
      medium: getDefectImage("medium-porosity.png"),
      high: getDefectImage("high-porosity.png")
    },
    severity: {
      low: {
        visual: "Sparse pinholes or isolated round pores. Surface continuity is mostly maintained.",
        root: "Minor moisture, surface contamination, or slight shielding gas disturbance during solidification.",
        remedy: "Clean the surface, verify shielding gas flow, and maintain stable humidity before the next run.",
        prevention: ["Dry workpiece before heating", "Check gas hose leaks", "Clean oil and dust from surface"]
      },
      medium: {
        visual: "Clustered pores in one region with visible surface disruption and local weakness.",
        root: "Inadequate venting, excess moisture in mold, or inconsistent gas coverage during welding.",
        remedy: "Improve venting, increase preheat control, inspect gas flow, and rework affected area if load-bearing.",
        prevention: ["Inspect mold vents", "Preheat substrate", "Maintain gas flow log", "Use clean filler material"]
      },
      high: {
        visual: "Large cavities, honeycomb texture, or widespread pores that reduce structural reliability.",
        root: "Severe gas entrapment, contaminated melt, blocked venting, or incorrect process parameters.",
        remedy: "Reject or cut out the component section, perform alloy/gas audit, and recalibrate the production line.",
        prevention: ["Stop line for root-cause audit", "Test alloy purity", "Clean venting channels", "Verify process temperature"]
      }
    }
  },
  crack: {
    name: "Crack",
    category: "Structural",
    description: "Linear fracture or separation caused by stress, cooling rate, fatigue, or poor fusion.",
    images: {
      low: getDefectImage("low-crack.png"),
      medium: getDefectImage("medium-crack.png"),
      high: getDefectImage("high-crack.png")
    },
    severity: {
      low: {
        visual: "Fine surface hairline crack with short length and no branching.",
        root: "Minor residual stress or small thermal shock during cooling.",
        remedy: "Blend and inspect the area, then monitor with dye penetrant or visual inspection.",
        prevention: ["Control cooling rate", "Avoid sharp corners", "Use post-weld inspection"]
      },
      medium: {
        visual: "Longer visible crack, slight branching, or crack near a stress concentration point.",
        root: "Thermal fatigue, incorrect weld parameters, or high residual stress.",
        remedy: "Stop use of the part, grind out the crack, re-weld if allowed, and perform NDT verification.",
        prevention: ["Apply preheat", "Use correct welding speed", "Reduce residual stress"]
      },
      high: {
        visual: "Deep crack, branching fracture, or crack crossing a load-bearing section.",
        root: "Critical fatigue failure, brittle fracture, or severe process mismatch.",
        remedy: "Reject the component immediately and perform full failure analysis before production continues.",
        prevention: ["Audit material grade", "Review load conditions", "Perform ultrasonic testing", "Revise heat treatment"]
      }
    }
  },
  slag: {
    name: "Slag Inclusion",
    category: "Welding",
    description: "Non-metallic trapped material inside the weld bead or casting.",
    images: {
      low: getDefectImage("low-slag-inclusion.png"),
      medium: getDefectImage("medium-slag-inclusion.png"),
      high: getDefectImage("high-slag-inclusion.png")
    },
    severity: {
      low: {
        visual: "Small isolated dark inclusion with minimal impact on surrounding weld profile.",
        root: "Light slag residue remained between passes.",
        remedy: "Clean the weld area and use controlled pass technique for the next layer.",
        prevention: ["Brush between passes", "Keep electrode angle stable", "Avoid low travel speed"]
      },
      medium: {
        visual: "Multiple elongated inclusions visible along the weld path.",
        root: "Poor inter-pass cleaning, incorrect current, or trapped flux due to bead geometry.",
        remedy: "Remove affected section, clean thoroughly, adjust current, and re-weld with proper technique.",
        prevention: ["Clean every pass", "Adjust amperage", "Maintain correct bead angle"]
      },
      high: {
        visual: "Continuous slag line or heavy inclusion that interrupts weld continuity.",
        root: "Severe process control failure or repeated inadequate cleaning between weld passes.",
        remedy: "Reject weld, gouge out defective area, and repeat welding under supervised parameters.",
        prevention: ["Review welding procedure", "Train operator", "Inspect each pass", "Use correct electrode"]
      }
    }
  },
  misrun: {
    name: "Misrun",
    category: "Casting",
    description: "Incomplete casting where molten metal fails to fill the mold cavity completely.",
    images: {
      low: getDefectImage("low-misrun.png"),
      medium: getDefectImage("medium-misrun.png"),
      high: getDefectImage("high-misrun.png")
    },
    severity: {
      low: {
        visual: "Small unfilled edge, corner, or shallow missing detail.",
        root: "Minor loss of fluidity from slightly low temperature or slow filling.",
        remedy: "Confirm dimensional tolerance and adjust pouring temperature or fill rate.",
        prevention: ["Check metal temperature", "Keep mold dry", "Improve venting"]
      },
      medium: {
        visual: "Noticeable incomplete section that affects fit or local geometry.",
        root: "Insufficient metal flow due to low superheat, narrow gates, or trapped air.",
        remedy: "Scrap if dimensional requirements fail, then increase fill efficiency and venting.",
        prevention: ["Widen gate path", "Increase superheat", "Improve air escape", "Shorten fill time"]
      },
      high: {
        visual: "Major missing portion or incomplete cavity fill.",
        root: "Severe flow failure from incorrect gating, freezing during fill, or inadequate metal volume.",
        remedy: "Reject casting and correct mold design, pour volume, and process timing.",
        prevention: ["Validate mold-fill simulation", "Audit charge weight", "Redesign runners", "Control pour speed"]
      }
    }
  },
  corrosion: {
    name: "Corrosion",
    category: "Service / Surface",
    description: "Chemical or electrochemical metal degradation that creates rust, pitting, or section loss.",
    images: {
      low: getDefectImage("low-corrosion.png"),
      medium: getDefectImage("medium-corrosion.png"),
      high: getDefectImage("high-corrosion.png")
    },
    severity: {
      low: {
        visual: "Light discoloration, early rust film, or small surface spots.",
        root: "Moisture exposure, poor cleaning, or damaged protective coating.",
        remedy: "Clean, dry, and recoat the affected area after confirming no pitting.",
        prevention: ["Keep surface dry", "Repair coating scratches", "Use proper storage"]
      },
      medium: {
        visual: "Visible pitting, scale buildup, or spreading rust patch.",
        root: "Persistent moisture, chemical exposure, or coating failure.",
        remedy: "Remove corrosion, measure thickness, apply inhibitor, and restore coating system.",
        prevention: ["Inspect coating regularly", "Control humidity", "Avoid chloride exposure", "Use corrosion inhibitor"]
      },
      high: {
        visual: "Deep pits, flaking scale, perforation risk, or measurable section loss.",
        root: "Long-term aggressive environment, galvanic attack, or neglected protection.",
        remedy: "Remove from service, assess remaining thickness, repair or replace affected component.",
        prevention: ["Review material grade", "Add cathodic protection", "Improve drainage", "Schedule thickness checks"]
      }
    }
  },
  shrinkage: {
    name: "Shrinkage",
    category: "Casting",
    description: "Void or depression caused when metal contracts during solidification without enough feed metal.",
    images: {
      low: getDefectImage("low-shrinkage.png"),
      medium: getDefectImage("medium-shrinkage.png"),
      high: getDefectImage("high-shrinkage.png")
    },
    severity: {
      low: {
        visual: "Small sink mark or shallow depression on a non-critical surface.",
        root: "Minor feeding imbalance or local hot spot during solidification.",
        remedy: "Check dimensional tolerance and tune riser or cooling control.",
        prevention: ["Balance section thickness", "Use local chills", "Confirm riser feed path"]
      },
      medium: {
        visual: "Visible cavity, sink, or internal void indication near a thicker section.",
        root: "Insufficient riser feeding, poor directional solidification, or isolated hot spot.",
        remedy: "Inspect internally, reject if load-bearing, and revise riser/chill placement.",
        prevention: ["Improve riser size", "Add chills", "Review solidification pattern", "Avoid abrupt thick sections"]
      },
      high: {
        visual: "Large shrinkage cavity, spongy zone, or void network in a critical section.",
        root: "Major feeding failure or casting design that prevents directional solidification.",
        remedy: "Reject the casting and redesign feed system before repeating the run.",
        prevention: ["Run solidification simulation", "Redesign risers", "Modify part geometry", "Control cooling rate"]
      }
    }
  }
};

const state = {
  defectKey: "porosity",
  severity: "medium",
  reportId: "AX-0001",
  uploadedImageUrl: "",
  uploadedImageDataUrl: "",
  prediction: null,
  currentUser: null,
  selectedLoginRole: loginUsers[0].role
};

const elements = {
  loginView: document.getElementById("loginView"),
  loginForm: document.getElementById("loginForm"),
  loginRoleGroup: document.getElementById("loginRoleGroup"),
  loginNameInput: document.getElementById("loginNameInput"),
  authUserName: document.getElementById("authUserName"),
  logoutButton: document.getElementById("logoutButton"),
  defectSelect: document.getElementById("defectSelect"),
  severityGroup: document.getElementById("severityGroup"),
  severityThumbs: document.getElementById("severityThumbs"),
  resultImage: document.getElementById("resultImage"),
  inspectorInput: document.getElementById("inspectorInput"),
  batchInput: document.getElementById("batchInput"),
  materialInput: document.getElementById("materialInput"),
  locationInput: document.getElementById("locationInput"),
  notesInput: document.getElementById("notesInput"),
  imageInput: document.getElementById("imageInput"),
  uploadLabel: document.getElementById("uploadLabel"),
  apiStatus: document.getElementById("apiStatus"),
  resultSourceLabel: document.getElementById("resultSourceLabel"),
  libraryGrid: document.getElementById("libraryGrid"),
  librarySearch: document.getElementById("librarySearch"),
  historyGrid: document.getElementById("historyGrid"),
  historyUserFilter: document.getElementById("historyUserFilter"),
  historyEmpty: document.getElementById("historyEmpty"),
  historyCount: document.getElementById("historyCount"),
  clearHistoryBtn: document.getElementById("clearHistoryBtn"),
  toast: document.getElementById("toast"),
  guideButton: document.getElementById("guideButton"),
  guideModal: document.getElementById("guideModal"),
  themeToggle: document.getElementById("themeToggle"),
  themeIcon: document.getElementById("themeIcon"),
  themeLabel: document.getElementById("themeLabel")
};

function titleCase(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[character];
  });
}

function createReportId() {
  return `AX-${Math.floor(1000 + Math.random() * 9000)}`;
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.addEventListener("load", () => resolve(reader.result));
    reader.addEventListener("error", () => reject(reader.error));
    reader.readAsDataURL(file);
  });
}

function normalizeDefectKey(value) {
  const normalized = value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const aliases = {
    porosity: "porosity",
    crack: "crack",
    slag: "slag",
    "slag inclusion": "slag",
    misrun: "misrun",
    corrosion: "corrosion",
    shrinkage: "shrinkage"
  };
  return aliases[normalized] || null;
}

function normalizeSeverity(value) {
  const normalized = value.toLowerCase();
  return ["low", "medium", "high"].includes(normalized) ? normalized : null;
}

function getCurrentFinding() {
  const defect = defectData[state.defectKey];
  return {
    defect,
    finding: defect.severity[state.severity],
    image: state.uploadedImageUrl || state.uploadedImageDataUrl || defect.images[state.severity]
  };
}

function setApiStatus(message, status = "idle") {
  elements.apiStatus.dataset.status = status;
  elements.apiStatus.querySelector("span:last-child").textContent = message;
}

async function checkBackendConnection() {
  setApiStatus("Checking backend connection...", "loading");

  try {
    const response = await fetch(`${apiBaseUrl}/health`, {
      cache: "no-store"
    });
    const payload = await response.json().catch(() => ({}));

    if (!response.ok || payload.status !== "ok") {
      throw new Error(payload.detail || "Health check failed.");
    }

    let modelText = "placeholder mode";
    if (payload.model_ready) {
      modelText = "model ready";
    } else if (payload.model_file_found && payload.model_error) {
      modelText = `model file found, runtime missing: ${payload.model_error}`;
    }
    setApiStatus(`Backend connected (${modelText}).`, payload.model_ready ? "success" : "warning");
  } catch (error) {
    setApiStatus(`Backend unavailable: ${error.message}`, "error");
  }
}

function applyPrediction(prediction) {
  const defectKey = normalizeDefectKey(prediction.defect || "");
  const severity = normalizeSeverity(prediction.severity || "");

  if (defectKey) {
    state.defectKey = defectKey;
    elements.defectSelect.value = defectKey;
  }

  if (severity) {
    state.severity = severity;
  }

  state.prediction = prediction;
  renderDiagnosis();

  const confidence = Math.round((prediction.confidence || 0) * 100);
  const confidenceText = confidence > 0 ? ` Confidence: ${confidence}%.` : "";
  const modelText = prediction.model_ready ? "Model response received." : "Backend placeholder response received.";
  setApiStatus(`${modelText}${confidenceText}`, prediction.model_ready ? "success" : "warning");
}

async function predictUploadedImage(file) {
  if (!file) return;

  if (state.uploadedImageUrl) {
    URL.revokeObjectURL(state.uploadedImageUrl);
  }
  state.uploadedImageUrl = URL.createObjectURL(file);
  state.uploadedImageDataUrl = "";
  state.prediction = null;
  elements.uploadLabel.textContent = file.name;
  setApiStatus("Sending image to backend...", "loading");
  renderDiagnosis();

  readFileAsDataUrl(file)
    .then((dataUrl) => {
      state.uploadedImageDataUrl = dataUrl;
    })
    .catch(() => {
      state.uploadedImageDataUrl = "";
    });

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${apiBaseUrl}/predict`, {
      method: "POST",
      body: formData
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || "Prediction failed.");
    }

    applyPrediction(payload);
    showToast("Backend prediction applied.");
  } catch (error) {
    setApiStatus(`Backend unavailable: ${error.message}`, "error");
    showToast("Could not reach backend prediction API.");
  }
}

function populateDefectSelect() {
  elements.defectSelect.innerHTML = Object.entries(defectData)
    .map(([key, defect]) => `<option value="${key}">${defect.name}</option>`)
    .join("");
  elements.defectSelect.value = state.defectKey;
}

function renderSeverityThumbs() {
  const defect = defectData[state.defectKey];
  elements.severityThumbs.innerHTML = ["low", "medium", "high"]
    .map((level) => `
      <button class="severity-thumb ${level === state.severity ? "active" : ""}" type="button" data-thumb="${level}">
        <img src="${defect.images[level]}" alt="${defect.name} ${level} severity reference">
        <span>${level}</span>
      </button>
    `)
    .join("");
}

function renderDiagnosis() {
  const { defect, finding, image } = getCurrentFinding();
  elements.resultImage.src = image;
  elements.resultSourceLabel.textContent = state.uploadedImageUrl || state.uploadedImageDataUrl ? "Uploaded image" : "Reference";

  document.querySelectorAll("[data-severity]").forEach((button) => {
    button.classList.toggle("active", button.dataset.severity === state.severity);
  });

  renderSeverityThumbs();
  renderReport();
}

function renderLibrary(filter = "") {
  const normalizedFilter = filter.trim().toLowerCase();
  elements.libraryGrid.innerHTML = Object.entries(defectData)
    .filter(([, defect]) => {
      return `${defect.name} ${defect.category} ${defect.description}`.toLowerCase().includes(normalizedFilter);
    })
    .map(([key, defect]) => `
      <article class="defect-card">
        <div class="defect-image-grid">
          ${["low", "medium", "high"].map((level) => `
            <button class="defect-severity-image" type="button" data-use-defect="${key}" data-use-severity="${level}">
              <img src="${defect.images[level]}" alt="${defect.name} ${level} severity reference">
              <span class="${level}">${titleCase(level)}</span>
            </button>
          `).join("")}
        </div>
        <div class="defect-card-body">
          <h2>${defect.name}</h2>
          <p>${defect.description}</p>
          <button class="ghost-action" data-use-defect="${key}">
            <span class="material-symbols-outlined">biotech</span>
            Use in Diagnosis
          </button>
        </div>
      </article>
    `)
    .join("");
}

function getHistoryRecords() {
  try {
    const records = JSON.parse(localStorage.getItem(historyStorageKey) || "[]");
    return Array.isArray(records) ? records : [];
  } catch {
    return [];
  }
}

function setHistoryRecords(records) {
  localStorage.setItem(historyStorageKey, JSON.stringify(records));
}

function getSelectedHistoryUser() {
  return elements.historyUserFilter.value || "all";
}

function renderHistory() {
  const records = getHistoryRecords();
  const inspectorSet = new Set(records.map((record) => record.inspector || "Inspector not set"));
  if (state.currentUser?.name) {
    inspectorSet.add(state.currentUser.name);
  }
  const inspectors = [...inspectorSet].sort();
  const preferredUser = state.currentUser?.name || "all";
  const selectedUser = inspectors.includes(getSelectedHistoryUser()) ? getSelectedHistoryUser() : preferredUser;

  elements.historyUserFilter.innerHTML = [
    '<option value="all">All inspectors</option>',
    ...inspectors.map((inspector) => `<option value="${escapeHtml(inspector)}">${escapeHtml(inspector)}</option>`)
  ].join("");
  elements.historyUserFilter.value = selectedUser;

  const visibleRecords = records.filter((record) => {
    return selectedUser === "all" || (record.inspector || "Inspector not set") === selectedUser;
  });

  elements.historyCount.textContent = `${visibleRecords.length} saved ${visibleRecords.length === 1 ? "record" : "records"}`;
  elements.historyEmpty.hidden = visibleRecords.length > 0;
  elements.historyGrid.innerHTML = visibleRecords
    .map((record) => {
      const createdAt = new Date(record.createdAt);
      const dateText = Number.isNaN(createdAt.getTime()) ? "Date unavailable" : createdAt.toLocaleString();
      const confidence = record.prediction?.confidence ? `${Math.round(record.prediction.confidence * 100)}%` : "Manual";

      return `
        <article class="history-card">
          <img src="${escapeHtml(record.image)}" alt="${escapeHtml(record.defect)} history image">
          <div class="history-card-body">
            <div class="history-card-top">
              <div>
                <small>${escapeHtml(record.id)}</small>
                <h2>${escapeHtml(record.defect)}</h2>
              </div>
              <span class="severity-pill ${escapeHtml(record.severity)}">${escapeHtml(titleCase(record.severity))}</span>
            </div>
            <div class="history-meta">
              <span><strong>Inspector</strong>${escapeHtml(record.inspector || "Inspector not set")}</span>
              <span><strong>Batch</strong>${escapeHtml(record.batch || "Not specified")}</span>
              <span><strong>Material</strong>${escapeHtml(record.material || "Not specified")}</span>
              <span><strong>Confidence</strong>${escapeHtml(confidence)}</span>
            </div>
            <p>${escapeHtml(record.notes || "No additional notes recorded.")}</p>
            <div class="history-card-actions">
              <span>${escapeHtml(dateText)}</span>
              <button class="ghost-action" type="button" data-history-load="${escapeHtml(record.id)}">
                <span class="material-symbols-outlined">open_in_new</span>
                Open
              </button>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderReport() {
  const { defect, finding, image } = getCurrentFinding();
  const date = new Date();
  document.getElementById("reportId").textContent = state.reportId;
  document.getElementById("reportDate").textContent = date.toLocaleDateString();
  document.getElementById("reportInspector").textContent = elements.inspectorInput.value || "Inspector not set";
  document.getElementById("reportDefect").textContent = defect.name;
  document.getElementById("reportSeverity").textContent = titleCase(state.severity);
  document.getElementById("reportMaterial").textContent = elements.materialInput.value || "Not specified";
  document.getElementById("reportBatch").textContent = elements.batchInput.value || "Not specified";
  document.getElementById("reportImage").src = image;
  document.getElementById("reportRoot").textContent = finding.root;
  document.getElementById("reportRemedy").textContent = finding.remedy;
  document.getElementById("reportNotes").textContent = elements.notesInput.value || "No additional notes recorded.";
  document.getElementById("reportPrevention").innerHTML = finding.prevention.map((item) => `<li>${item}</li>`).join("");
}

function showPage(page) {
  const availablePages = [...document.querySelectorAll(".page")].map((section) => section.dataset.page);
  const nextPage = availablePages.includes(page) ? page : "diagnose";

  document.querySelectorAll(".page").forEach((section) => {
    section.classList.toggle("active", section.dataset.page === nextPage);
  });
  document.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === nextPage);
  });
  document.querySelectorAll(".side-link").forEach((button) => {
    button.classList.toggle("active", button.dataset.jump === nextPage);
  });
  window.location.hash = nextPage;
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2200);
}

function openGuide() {
  elements.guideModal.hidden = false;
  document.body.classList.add("guide-open");
  elements.guideModal.querySelector("[data-guide-close]").focus();
}

function closeGuide() {
  elements.guideModal.hidden = true;
  document.body.classList.remove("guide-open");
  elements.guideButton.focus();
}

function getLoginUserByRole(role) {
  return loginUsers.find((user) => user.role === role) || loginUsers[0];
}

function renderLoginRoles() {
  elements.loginRoleGroup.innerHTML = loginUsers
    .map((user) => `
      <button class="login-user ${user.role === state.selectedLoginRole ? "active" : ""}" type="button" data-login-role="${escapeHtml(user.role)}">
        <span class="material-symbols-outlined">${escapeHtml(user.icon)}</span>
        <strong>${escapeHtml(user.role)}</strong>
        <small>${escapeHtml(user.label)}</small>
      </button>
    `)
    .join("");
}

function selectLoginRole(role) {
  const user = getLoginUserByRole(role);
  state.selectedLoginRole = user.role;
  if (!elements.loginNameInput.value.trim()) {
    elements.loginNameInput.value = user.name;
  }
  renderLoginRoles();
}

function applyCurrentUser(user) {
  state.currentUser = user;
  elements.authUserName.textContent = user.name;
  elements.inspectorInput.value = user.name;
  elements.historyUserFilter.value = user.name;
  document.body.classList.remove("auth-pending");
  renderReport();
  renderHistory();
}

function signIn(user) {
  localStorage.setItem(userStorageKey, JSON.stringify(user));
  applyCurrentUser(user);
  showToast(`Signed in as ${user.name}.`);
}

function restoreCurrentUser() {
  try {
    const user = JSON.parse(localStorage.getItem(userStorageKey) || "null");
    if (user?.name && user?.role) {
      state.selectedLoginRole = user.role;
      elements.loginNameInput.value = user.name;
      renderLoginRoles();
      applyCurrentUser(user);
      return;
    }
  } catch {
    localStorage.removeItem(userStorageKey);
  }

  selectLoginRole(state.selectedLoginRole);
  document.body.classList.add("auth-pending");
}

function signOut() {
  localStorage.removeItem(userStorageKey);
  state.currentUser = null;
  elements.authUserName.textContent = "Guest";
  elements.loginNameInput.value = getLoginUserByRole(state.selectedLoginRole).name;
  document.body.classList.add("auth-pending");
  renderLoginRoles();
  showToast("Signed out.");
}

function saveResult() {
  const { defect, finding, image } = getCurrentFinding();
  const saved = {
    id: state.reportId,
    defectKey: state.defectKey,
    defect: defect.name,
    severity: state.severity,
    inspector: elements.inspectorInput.value.trim() || "Inspector not set",
    batch: elements.batchInput.value.trim(),
    material: elements.materialInput.value.trim(),
    location: elements.locationInput.value.trim(),
    notes: elements.notesInput.value.trim(),
    image: state.uploadedImageDataUrl || image,
    root: finding.root,
    remedy: finding.remedy,
    prevention: finding.prevention,
    prediction: state.prediction,
    createdAt: new Date().toISOString()
  };

  localStorage.setItem("anomlyx-last-report", JSON.stringify(saved));
  setHistoryRecords([saved, ...getHistoryRecords().filter((record) => record.id !== saved.id)].slice(0, 100));
  renderHistory();
  showToast("Diagnosis saved to history.");
}

function applyTheme(theme) {
  const nextTheme = theme === "dark" ? "dark" : "light";
  document.body.dataset.theme = nextTheme;
  elements.themeIcon.textContent = nextTheme === "dark" ? "light_mode" : "dark_mode";
  elements.themeLabel.textContent = nextTheme === "dark" ? "Light" : "Dark";
  elements.themeToggle.setAttribute(
    "aria-label",
    nextTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"
  );
}

function generateDiagnosisReport() {
  renderDiagnosis();
  saveResult();
  showPage("report");
  window.scrollTo({ top: 0, behavior: "smooth" });
  showToast("Diagnosis generated.");
}

function bindEvents() {
  elements.loginRoleGroup.addEventListener("click", (event) => {
    const button = event.target.closest("[data-login-role]");
    if (!button) return;
    selectLoginRole(button.dataset.loginRole);
  });

  elements.loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const roleUser = getLoginUserByRole(state.selectedLoginRole);
    const name = elements.loginNameInput.value.trim() || roleUser.name;
    signIn({ role: roleUser.role, name });
  });

  elements.logoutButton.addEventListener("click", signOut);

  elements.defectSelect.addEventListener("change", (event) => {
    state.defectKey = event.target.value;
    state.prediction = null;
    renderDiagnosis();
  });

  elements.severityGroup.addEventListener("click", (event) => {
    const button = event.target.closest("[data-severity]");
    if (!button) return;
    state.severity = button.dataset.severity;
    state.prediction = null;
    renderDiagnosis();
  });

  elements.severityThumbs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-thumb]");
    if (!button) return;
    state.severity = button.dataset.thumb;
    state.prediction = null;
    renderDiagnosis();
  });

  elements.imageInput.addEventListener("change", (event) => {
    predictUploadedImage(event.target.files[0]);
  });

  document.getElementById("updateBtn").addEventListener("click", generateDiagnosisReport);

  document.getElementById("resetBtn").addEventListener("click", () => {
    window.setTimeout(() => {
      state.defectKey = "porosity";
      state.severity = "medium";
      state.prediction = null;
      if (state.uploadedImageUrl) {
        URL.revokeObjectURL(state.uploadedImageUrl);
      }
      state.uploadedImageUrl = "";
      state.uploadedImageDataUrl = "";
      elements.imageInput.value = "";
      elements.uploadLabel.textContent = "Upload inspection image";
      setApiStatus("Backend ready for image prediction.");
      elements.defectSelect.value = state.defectKey;
      renderDiagnosis();
    }, 0);
  });

  document.getElementById("printBtn")?.addEventListener("click", () => {
    renderReport();
    showPage("report");
    window.setTimeout(() => window.print(), 120);
  });

  document.getElementById("reportPrintBtn").addEventListener("click", () => {
    renderReport();
    window.print();
  });

  document.getElementById("saveBtn")?.addEventListener("click", saveResult);

  elements.guideButton.addEventListener("click", openGuide);

  elements.guideModal.addEventListener("click", (event) => {
    if (event.target === elements.guideModal || event.target.closest("[data-guide-close]")) {
      closeGuide();
    }
  });

  elements.themeToggle.addEventListener("click", () => {
    const nextTheme = document.body.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    localStorage.setItem(themeStorageKey, nextTheme);
  });

  ["inspectorInput", "batchInput", "materialInput", "locationInput", "notesInput"].forEach((key) => {
    elements[key].addEventListener("input", renderReport);
  });

  elements.historyUserFilter.addEventListener("change", renderHistory);

  elements.clearHistoryBtn.addEventListener("click", () => {
    setHistoryRecords([]);
    renderHistory();
    showToast("History cleared.");
  });

  document.addEventListener("click", (event) => {
    const jump = event.target.closest("[data-jump]");
    if (jump) {
      showPage(jump.dataset.jump);
      return;
    }

    const useDefect = event.target.closest("[data-use-defect]");
    if (useDefect) {
      state.defectKey = useDefect.dataset.useDefect;
      if (useDefect.dataset.useSeverity) {
        state.severity = useDefect.dataset.useSeverity;
      }
      state.prediction = null;
      elements.defectSelect.value = state.defectKey;
      renderDiagnosis();
      showPage("diagnose");
      showToast(`${defectData[state.defectKey].name} loaded into diagnosis.`);
    }

    const historyLoad = event.target.closest("[data-history-load]");
    if (historyLoad) {
      const record = getHistoryRecords().find((item) => item.id === historyLoad.dataset.historyLoad);
      if (!record) return;
      state.reportId = record.id;
      state.defectKey = record.defectKey || normalizeDefectKey(record.defect) || "porosity";
      state.severity = normalizeSeverity(record.severity) || "medium";
      state.prediction = record.prediction || null;
      state.uploadedImageUrl = "";
      state.uploadedImageDataUrl = record.image || "";
      elements.defectSelect.value = state.defectKey;
      elements.inspectorInput.value = record.inspector || "";
      elements.batchInput.value = record.batch || "";
      elements.materialInput.value = record.material || "";
      elements.locationInput.value = record.location || "";
      elements.notesInput.value = record.notes || "";
      elements.uploadLabel.textContent = "History image loaded";
      renderDiagnosis();
      showPage("report");
      showToast(`${record.id} opened.`);
    }
  });

  elements.librarySearch.addEventListener("input", (event) => {
    renderLibrary(event.target.value);
  });

  window.addEventListener("hashchange", () => {
    const page = window.location.hash.replace("#", "") || "diagnose";
    showPage(page);
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !elements.guideModal.hidden) {
      closeGuide();
    }
  });
}

function init() {
  state.reportId = createReportId();
  applyTheme(localStorage.getItem(themeStorageKey) || "dark");
  renderLoginRoles();
  populateDefectSelect();
  renderLibrary();
  renderHistory();
  renderDiagnosis();
  bindEvents();
  restoreCurrentUser();
  checkBackendConnection();
  showPage(window.location.hash.replace("#", "") || "diagnose");
}

init();
