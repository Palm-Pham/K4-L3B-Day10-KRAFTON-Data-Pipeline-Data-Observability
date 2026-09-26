const $ = (selector) => document.querySelector(selector);
const formatPercent = (value) => `${Math.round((Number(value) || 0) * 100)}%`;
const labels = { baseline: "Baseline", corrupted: "Corrupted", repaired: "Repaired" };
let overviewData = null;
let selectedMetric = "retrieval_hit_at_1";
let selectedState = "baseline";

function showError(message) {
  const box = $("#load-error");
  box.textContent = message;
  box.hidden = false;
  window.setTimeout(() => { box.hidden = true; }, 6000);
}

function renderChart() {
  if (!overviewData) return;
  const titles = {
    retrieval_hit_at_1: ["RETRIEVAL HIT@1", "Đúng tài liệu ngay vị trí đầu tiên."],
    retrieval_hit_rate: ["RETRIEVAL HIT@4", "Tài liệu đúng nằm trong bốn kết quả đầu."],
    mean_token_f1: ["MEAN TOKEN F1", "Mức trùng khớp token của câu trả lời metadata."]
  };
  $("#chart-unit").textContent = titles[selectedMetric][0];
  $("#chart-note").textContent = titles[selectedMetric][1] + " Cùng một golden set 10 câu cho cả ba trạng thái.";
  const chart = $("#chart");
  chart.replaceChildren();
  for (const state of ["baseline", "corrupted", "repaired"]) {
    const value = Number(overviewData.states[state].metrics[selectedMetric] || 0);
    const row = document.createElement("div");
    row.className = "bar-row";
    const label = document.createElement("span");
    label.className = "bar-label";
    label.textContent = labels[state];
    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = `bar-fill ${state}`;
    fill.style.width = `${Math.max(0, Math.min(100, value * 100))}%`;
    track.append(fill);
    const number = document.createElement("span");
    number.className = "bar-value";
    number.textContent = formatPercent(value);
    row.append(label, track, number);
    chart.append(row);
  }
  chart.setAttribute("aria-label", `${titles[selectedMetric][0]}: baseline ${formatPercent(overviewData.states.baseline.metrics[selectedMetric])}, corrupted ${formatPercent(overviewData.states.corrupted.metrics[selectedMetric])}, repaired ${formatPercent(overviewData.states.repaired.metrics[selectedMetric])}`);
}

function renderQuality() {
  const grid = $("#quality-grid");
  grid.replaceChildren();
  for (const state of ["baseline", "corrupted", "repaired"]) {
    const { quality, freshness } = overviewData.states[state];
    const card = document.createElement("article");
    card.className = `quality-card${quality.success ? "" : " bad"}`;
    const top = document.createElement("div");
    top.className = "quality-top";
    const topName = document.createElement("span");
    topName.textContent = `STATE / 0${["baseline", "corrupted", "repaired"].indexOf(state) + 1}`;
    const badge = document.createElement("span");
    badge.className = "quality-status";
    badge.textContent = quality.success ? "GX PASSED" : "GX FAILED";
    top.append(topName, badge);
    const heading = document.createElement("h3");
    heading.textContent = labels[state];
    const description = document.createElement("p");
    description.textContent = `${quality.total_records} tài liệu · Freshness ${freshness.is_fresh ? "đạt SLA" : "vi phạm SLA"}`;
    const numbers = document.createElement("div");
    numbers.className = "quality-numbers";
    for (const [value, caption] of [
      [`${quality.successful_expectations}/${quality.evaluated_expectations}`, "GX checks đạt"],
      [formatPercent(freshness.stale_ratio), "tài liệu quá hạn"]
    ]) {
      const item = document.createElement("div");
      const bold = document.createElement("b");
      const small = document.createElement("small");
      bold.textContent = value;
      small.textContent = caption;
      item.append(bold, small);
      numbers.append(item);
    }
    card.append(top, heading, description, numbers);
    grid.append(card);
  }
}

function renderScenarios() {
  const grid = $("#scenario-grid");
  grid.replaceChildren();
  for (const [index, scenario] of overviewData.scenarios.entries()) {
    const card = document.createElement("article");
    card.className = "scenario-card";
    const number = document.createElement("span");
    number.textContent = String(index + 1).padStart(2, "0");
    const body = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = scenario.scenario.replaceAll("_", " ");
    const description = document.createElement("p");
    description.textContent = scenario.description;
    body.append(title, description);
    card.append(number, body);
    grid.append(card);
  }
}

function renderSamples() {
  const samples = $("#samples");
  samples.replaceChildren();
  for (const item of overviewData.questions.slice(0, 4)) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "sample-question";
    button.textContent = `${item.type.toUpperCase()} / ${item.question}`;
    button.addEventListener("click", () => {
      $("#question").value = item.question;
      $("#question").focus();
      document.querySelector("#demo").scrollIntoView({ behavior: "smooth" });
    });
    samples.append(button);
  }
}

function renderOverview() {
  const states = overviewData.states;
  const count = states.baseline.metrics.samples;
  $("#corpus-count").textContent = overviewData.corpus_count;
  $("#base-hit").textContent = Math.round(states.baseline.metrics.retrieval_hit_at_1 * count);
  $("#corrupt-hit").textContent = Math.round(states.corrupted.metrics.retrieval_hit_at_1 * count);
  $("#quality-status").textContent = states.baseline.quality.success ? "PASSED" : "FAILED";
  $("#hero-base").textContent = formatPercent(states.baseline.metrics.retrieval_hit_at_1);
  $("#hero-corrupt").textContent = formatPercent(states.corrupted.metrics.retrieval_hit_at_1);
  $("#hero-repair").textContent = formatPercent(states.repaired.metrics.retrieval_hit_at_1);
  const drop = (states.corrupted.metrics.retrieval_hit_at_1 - states.baseline.metrics.retrieval_hit_at_1) * 100;
  $("#drop-stat").textContent = `${Math.round(drop)} pp`;
  renderChart();
  renderQuality();
  renderScenarios();
  renderSamples();
}

function renderAnswer(data) {
  const answer = $("#answer-content");
  answer.replaceChildren();
  answer.classList.remove("answer-error");
  answer.textContent = data.answer;
  $("#answer-mode").textContent = `${data.state.toUpperCase()} / METADATA MODE`;
  const sources = $("#answer-sources");
  sources.replaceChildren();
  const label = document.createElement("div");
  label.className = "source-label";
  label.textContent = `RETRIEVED SOURCES / ${data.sources.length}`;
  sources.append(label);
  if (data.sources.length === 0) {
    const empty = document.createElement("span");
    empty.className = "no-sources";
    empty.textContent = "Không có tài liệu được truy xuất cho câu hỏi này.";
    sources.append(empty);
  }
  for (const source of data.sources) {
    const item = document.createElement("div");
    item.className = "source-item";
    const doi = document.createElement("strong");
    doi.textContent = source.doi;
    const title = document.createElement("span");
    title.textContent = source.title;
    item.append(doi, title);
    sources.append(item);
  }
}

document.querySelectorAll(".switch").forEach((button) => {
  button.addEventListener("click", () => {
    selectedMetric = button.dataset.metric;
    document.querySelectorAll(".switch").forEach((item) => item.classList.toggle("active", item === button));
    renderChart();
  });
});
document.querySelectorAll(".state-button").forEach((button) => {
  button.addEventListener("click", () => {
    selectedState = button.dataset.state;
    document.querySelectorAll(".state-button").forEach((item) => item.classList.toggle("selected", item === button));
  });
});
$("#ask-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = $("#question").value.trim();
  if (!question) return;
  const button = $("#ask-form button[type=submit]");
  button.disabled = true;
  button.textContent = "Đang truy xuất…";
  $("#answer-content").textContent = "Đang tìm tài liệu và tạo câu trả lời…";
  $("#answer-sources").replaceChildren();
  try {
    const response = await fetch("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, state: selectedState })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Không thể truy xuất.");
    renderAnswer(data);
  } catch (error) {
    $("#answer-content").textContent = error.message;
    $("#answer-content").classList.add("answer-error");
    showError(error.message);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Truy xuất & trả lời <span aria-hidden="true">→</span>';
  }
});
document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((item) => item.classList.toggle("active", item === link));
  });
});

fetch("/api/overview")
  .then((response) => {
    if (!response.ok) throw new Error("Không tải được artifact dự án.");
    return response.json();
  })
  .then((data) => { overviewData = data; renderOverview(); })
  .catch((error) => showError(error.message));
