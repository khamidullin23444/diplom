// analyzer.js
// Логика для страницы анализа релаксограммы.
// Предназначено для использования в FastAPI + Jinja2.

// ---------------- ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ ----------------

document.addEventListener("DOMContentLoaded", () => {
  initControls();
  initCharts();
});

// ---------------- УПРАВЛЕНИЕ ФОРМОЙ И КНОПКАМИ ----------------

function initControls() {
  const freqInput = document.getElementById("pc-freq");
  const gainInput = document.getElementById("gain");
  const gainValue = document.getElementById("gain-value");
  const mcPeriod = document.getElementById("mc-period");
  const mcPeriodText = document.getElementById("mc-period-text");
  const t90_180 = document.getElementById("t90-180");
  const t90_180Text = document.getElementById("t90-180-text");
  const pulseCount = document.getElementById("pulse-count");
  const pulseCountText = document.getElementById("pulse-count-text");
  const accumulations = document.getElementById("accumulations");
  const accumulationsText = document.getElementById("accumulations-text");

  // Частота — кнопки +/- и ввод
  bindStepButtons("freq-minus-50", "pc-freq", -50);
  bindStepButtons("freq-minus-1", "pc-freq", -1);
  bindStepButtons("freq-plus-1", "pc-freq", +1);
  bindStepButtons("freq-plus-50", "pc-freq", +50);

  // Отображение текущих значений слайдеров
  if (gainInput && gainValue) {
    gainInput.addEventListener("input", () => {
      gainValue.textContent = gainInput.value;
    });
  }

  if (mcPeriod && mcPeriodText) {
    mcPeriod.addEventListener("input", () => {
      mcPeriodText.textContent = `${mcPeriod.value} ms`;
    });
  }

  if (t90_180 && t90_180Text) {
    t90_180.addEventListener("input", () => {
      t90_180Text.textContent = `${t90_180.value} μs`;
    });
  }

  if (pulseCount && pulseCountText) {
    pulseCount.addEventListener("input", () => {
      pulseCountText.textContent = pulseCount.value;
    });
  }

  if (accumulations && accumulationsText) {
    accumulations.addEventListener("input", () => {
      accumulationsText.textContent = accumulations.value;
    });
  }

  // Кнопки управления измерением (здесь только заглушки)
  const btnStart = document.getElementById("btn-start");
  const btnStop = document.getElementById("btn-stop");
  const btnAnalyze = document.getElementById("btn-analyze");
  const btnAuto = document.getElementById("btn-auto");

  if (btnStart) {
    btnStart.addEventListener("click", () => {
      // TODO: вызвать эндпоинт FastAPI, который инициирует измерение.
      console.log("Start measurement requested");
    });
  }

  if (btnStop) {
    btnStop.addEventListener("click", () => {
      // TODO: остановка измерения.
      console.log("Stop measurement requested");
    });
  }

  if (btnAnalyze) {
    btnAnalyze.addEventListener("click", () => {
      // TODO: запрос анализа последнего набора данных.
      console.log("Analyze requested");
    });
  }

  if (btnAuto) {
    btnAuto.addEventListener("click", () => {
      // TODO: авто‑подбор параметров (аналог Bt_auto_Click).
      console.log("Auto configuration requested");
    });
  }

  // Кнопка соединения (Connect / Disconnect)
  const toggleConn = document.getElementById("btn-toggle-connection");
  if (toggleConn) {
    toggleConn.addEventListener("click", () => {
      const isConnected = toggleConn.classList.contains("toggle-on");
      // TODO: дернуть API для открытия/закрытия порта.
      console.log(isConnected ? "Disconnect requested" : "Connect requested");
    });
  }

  // Файловые операции (заглушки, чтобы не терять структуру XAML‑логики)
  const btnSave = document.getElementById("btn-save-result");
  const btnLoad = document.getElementById("btn-load-result");
  const btnFind = document.getElementById("btn-find-result");
  const btnSelectDir = document.getElementById("btn-select-dir");

  if (btnSave) btnSave.addEventListener("click", () => console.log("Save result requested"));
  if (btnLoad) btnLoad.addEventListener("click", () => console.log("Load result requested"));
  if (btnFind) btnFind.addEventListener("click", () => console.log("Find result requested"));
  if (btnSelectDir) btnSelectDir.addEventListener("click", () => console.log("Select directory requested"));

  // Кнопки расчётов
  const btnCalcT2eff = document.getElementById("btn-calc-t2eff");
  const btnCalcWaterConc = document.getElementById("btn-calc-water-conc");

  if (btnCalcT2eff) {
    btnCalcT2eff.addEventListener("click", () => {
      // TODO: отправить текущие данные на сервер и получить T2eff.
      console.log("T2eff calculation requested");
    });
  }

  if (btnCalcWaterConc) {
    btnCalcWaterConc.addEventListener("click", () => {
      // TODO: отправить T2н, T2в, T2* и получить W.
      console.log("Water concentration calculation requested");
    });
  }

  // Зависимости
  const btnChangeGraph = document.getElementById("btn-change-graph");
  const dependencesList = document.getElementById("dependences-list");

  if (btnChangeGraph && dependencesList) {
    btnChangeGraph.addEventListener("click", () => {
      const selectedIndex = dependencesList.selectedIndex;
      const selectedText = selectedIndex >= 0
        ? dependencesList.options[selectedIndex].text
        : null;
      console.log("Change dependence graph:", selectedText);
      // TODO: запросить на сервере нужную зависимость и отрисовать её на правом нижнем графике.
    });
  }
}

function bindStepButtons(buttonId, inputId, delta) {
  const btn = document.querySelector(`[data-action="${buttonId}"]`);
  const input = document.getElementById(inputId);
  if (!btn || !input) return;

  btn.addEventListener("click", () => {
    const current = parseFloat(input.value || "0");
    const next = current + delta;
    input.value = next.toFixed(2);
    input.dispatchEvent(new Event("input"));
  });
}

// ---------------- ИНИЦИАЛИЗАЦИЯ ГРАФИКОВ ----------------

function initCharts() {
  // Здесь предполагается использование SciChart.js либо другой JS‑библиотеки.
  // Примерная структура вызовов SciChart.js (упрощённая):
  //
  // import { SciChartSurface, NumericAxis, XyDataSeries, XyScatterRenderableSeries } from "scichart";
  //
  // SciChartSurface.create("sensor-scope").then(({ sciChartSurface, wasmContext }) => {
  //   const xAxis = new NumericAxis(wasmContext);
  //   const yAxis = new NumericAxis(wasmContext);
  //   sciChartSurface.xAxes.add(xAxis);
  //   sciChartSurface.yAxes.add(yAxis);
  //
  //   const dataSeries = new XyDataSeries(wasmContext, { xValues: [], yValues: [] });
  //   const series = new XyScatterRenderableSeries(wasmContext, { dataSeries });
  //   sciChartSurface.renderableSeries.add(series);
  // });
  //
  // Для правых графиков аналогично — IDs "sensor-scope-2" и "sensor-scope-3".
  //
  // В этом файле мы ограничимся заглушками, чтобы не навязывать конкретный способ подключения SciChart.js.

  const surfaces = [
    { id: "sensor-scope", type: "relax-signal" },
    { id: "sensor-scope-2", type: "relax-signal-2" },
    { id: "sensor-scope-3", type: "analysis" }
  ];

  surfaces.forEach(s => {
    const el = document.getElementById(s.id);
    if (!el) return;
    // При желании можно временно показать надпись‑заглушку.
    const placeholder = document.createElement("div");
    placeholder.style.display = "flex";
    placeholder.style.alignItems = "center";
    placeholder.style.justifyContent = "center";
    placeholder.style.height = "100%";
    placeholder.style.color = "#4b5563";
    placeholder.style.fontSize = "0.85rem";
    placeholder.textContent =
      "Здесь будет график (" + s.type + "). Подключите SciChart.js или другую библиотеку.";
    el.appendChild(placeholder);
  });
}


