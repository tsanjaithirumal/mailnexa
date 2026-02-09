const loadBtn = document.getElementById("loadEmailsBtn");
const resultsEl = document.getElementById("results");

/**
 * Popup architecture:
 * - Pure HTML/CSS/JS (no frameworks)
 * - Backend provides initial classification
 * - User can override priority locally (stored in localStorage)
 */

function setResultsMessage(message, kind = "info") {
  resultsEl.textContent = "";
  const div = document.createElement("div");
  div.textContent = message;
  if (kind === "error") div.className = "error";
  resultsEl.appendChild(div);
}

function el(tag, text) {
  const node = document.createElement(tag);
  if (text != null) node.textContent = text;
  return node;
}

function priorityBadgeClass(priority) {
  const p = String(priority || "").toUpperCase();
  if (p === "HIGH") return "badge badge-high";
  if (p === "MEDIUM") return "badge badge-medium";
  if (p === "LOW") return "badge badge-low";
  return "badge";
}

function getOverrideKey(email) {
  // Stable key for localStorage
  return `priority_override_${email.id || email.subject}`;
}

function renderGroupedEmails(emails) {
  resultsEl.textContent = "";

  if (!Array.isArray(emails) || emails.length === 0) {
    resultsEl.appendChild(el("div", "No emails returned."));
    return;
  }

  /* ===============================
     APPLY USER OVERRIDES (NEW)
     =============================== */
  for (const email of emails) {
    const key = getOverrideKey(email);
    const override = localStorage.getItem(key);
    if (override) {
      email.priority = override;
    }
  }

  /* ===============================
     PRIORITY SORTING
     HIGH → MEDIUM → LOW
     =============================== */
  const priorityOrder = { HIGH: 1, MEDIUM: 2, LOW: 3 };

  emails.sort(
    (a, b) =>
      (priorityOrder[a?.priority] ?? 99) -
      (priorityOrder[b?.priority] ?? 99)
  );

  /* ===============================
     GROUP BY CATEGORY
     =============================== */
  const groups = new Map();
  for (const email of emails) {
    const category = email?.category || "UNCATEGORIZED";
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push(email);
  }

  for (const [category, items] of groups.entries()) {
    const section = el("div");
    section.className = "section";

    const header = el("div");
    header.className = "sectionHeader";
    header.appendChild(el("div", category));
    header.appendChild(el("div", String(items.length)));
    section.appendChild(header);

    for (const email of items) {
      const card = el("div");
      card.className = "card";

      const subject = el("div", email?.subject || "(No subject)");
      subject.className = "subject";
      card.appendChild(subject);

      /* ===============================
         PRIORITY BADGE + DROPDOWN
         =============================== */
      const metaRow = el("div");
      metaRow.className = "metaRow";

      const badge = el("span", email.priority);
      badge.className = priorityBadgeClass(email.priority);
      metaRow.appendChild(badge);

      const select = document.createElement("select");
      ["HIGH", "MEDIUM", "LOW"].forEach((p) => {
        const opt = document.createElement("option");
        opt.value = p;
        opt.textContent = p;
        if (p === email.priority) opt.selected = true;
        select.appendChild(opt);
      });

      select.addEventListener("change", () => {
        const key = getOverrideKey(email);
        localStorage.setItem(key, select.value);
        email.priority = select.value;
        renderGroupedEmails(emails); // re-render after change
      });

      metaRow.appendChild(select);
      card.appendChild(metaRow);

      const explText = String(email?.explanation || "").trim();
      if (explText) {
        const expl = el("div", explText);
        expl.className = "explanation";
        card.appendChild(expl);
      }

      const snippetText = String(email?.snippet || "").trim();
      if (snippetText) {
        const snippet = el("div", snippetText);
        snippet.className = "snippet";
        card.appendChild(snippet);
      }

      section.appendChild(card);
    }

    resultsEl.appendChild(section);
  }
}

async function fetchEmails() {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);

  try {
    const resp = await fetch("http://127.0.0.1:8000/emails", {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });

    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data?.detail || "Failed to fetch emails");
    }

    return data?.emails || [];
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Request timed out");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

loadBtn.addEventListener("click", async () => {
  loadBtn.disabled = true;
  setResultsMessage("Loading emails...");

  try {
    const emails = await fetchEmails();
    renderGroupedEmails(emails);
  } catch (err) {
    setResultsMessage(err.message, "error");
  } finally {
    loadBtn.disabled = false;
  }
});