// ABOUTME: External frontend script for the MCP exam: loads /exam, submits to /exam/submit.
// ABOUTME: Builds the DOM with createElement/textContent (no innerHTML sink); external so a strict CSP applies.
const examEl = document.getElementById("exam");
const submitBtn = document.getElementById("submit");
const resultEl = document.getElementById("result");

// Build one question block via the DOM API. Every field is set with textContent or as an input
// value, never interpolated into markup, so question content cannot inject HTML or script.
function renderQuestion(q) {
  const div = document.createElement("div");
  div.className = "q";

  const tag = document.createElement("div");
  tag.className = "tag";
  tag.textContent = `${q.domain} · ${q.difficulty}`;

  const stem = document.createElement("div");
  stem.className = "stem";
  stem.textContent = q.stem;

  div.append(tag, stem);

  for (const option of q.options) {
    const label = document.createElement("label");
    label.className = "opt";
    const input = document.createElement("input");
    input.type = "radio";
    input.name = q.id;
    input.value = option;
    label.append(input, document.createTextNode(" " + option));
    div.append(label);
  }
  return div;
}

async function loadExam() {
  resultEl.classList.add("hidden");
  examEl.classList.remove("hidden");
  examEl.textContent = "Loading questions...";
  submitBtn.textContent = "Submit exam";
  let questions;
  try {
    const res = await fetch("/exam");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    questions = await res.json();
  } catch (err) {
    examEl.textContent = "Could not load the exam. Please retry.";
    return;
  }
  examEl.textContent = "";
  for (const q of questions) examEl.append(renderQuestion(q));
  submitBtn.classList.remove("hidden");
}

submitBtn.addEventListener("click", async () => {
  const answers = {};
  for (const input of document.querySelectorAll("input[type=radio]:checked")) {
    answers[input.name] = input.value;
  }
  let result;
  try {
    const res = await fetch("/exam/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    result = await res.json();
  } catch (err) {
    submitBtn.textContent = "Submit failed, please retry";
    return;
  }
  examEl.classList.add("hidden");
  submitBtn.classList.add("hidden");
  document.getElementById("score").textContent =
    `${result.correct} / ${result.total}  (${result.score_pct}%)`;

  const detail = document.getElementById("detail");
  detail.textContent = "";
  const table = document.createElement("table");
  for (const d of result.by_domain) {
    const row = document.createElement("tr");
    const domainCell = document.createElement("td");
    domainCell.textContent = d.domain;
    const scoreCell = document.createElement("td");
    scoreCell.textContent = `${d.correct} / ${d.total}`;
    row.append(domainCell, scoreCell);
    table.append(row);
  }
  detail.append(table);
  resultEl.classList.remove("hidden");
});

document.getElementById("retry").addEventListener("click", loadExam);
loadExam();
