// analyzer.js
// Логика для страницы анализа релаксограммы.
// Предназначено для использования в FastAPI + Jinja2.

// ---------------- ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ ----------------
const { SciChartSurface, NumericAxis, FastLineRenderableSeries, XyDataSeries } = SciChart;
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

async function initCharts() {
  if (typeof scichart === "undefined") {
    console.warn("SciChart.js не найден (объект scichart не определён). Пропускаю инициализацию графиков.");
    return;
  }

  const {
    SciChartSurface,
    NumericAxis,
    LogarithmicAxis,
    XyDataSeries,
    XyScatterRenderableSeries,
    EllipsePointMarker,
    ZoomPanModifier,
    RubberBandXyZoomModifier,
    MouseWheelZoomModifier,
    ZoomExtentsModifier,
    LegendModifier,
    XAxisDragModifier,
    YAxisDragModifier,
    RolloverModifier,
    VerticalLineAnnotation
  } = scichart;

  // Основной левый график (Sensor_Scope): логарифмическая ось Y, два набора точек
  if (document.getElementById("sensor-scope")) {
    try {
      const { sciChartSurface, wasmContext } = await SciChartSurface.create("sensor-scope");

      const xAxis = new NumericAxis(wasmContext, {
        visibleRange: new scichart.NumberRange(0, 1025),
        axisTitle: "Время (мс)"
      });

      const yAxis = new LogarithmicAxis(wasmContext, {
        visibleRange: new scichart.NumberRange(1, 400),
        axisTitle: "Амплитуда СЭ (у.е.)",
        base: 10
      });

      sciChartSurface.xAxes.add(xAxis);
      sciChartSurface.yAxes.add(yAxis);

      // Серия Sensor_Data (SteelBlue)
      const dataSeriesSensor = new XyDataSeries(wasmContext, { xValues: [], yValues: [] });
      const rsSensor = new XyScatterRenderableSeries(wasmContext, {
        dataSeries: dataSeriesSensor,
        pointMarker: new EllipsePointMarker(wasmContext, {
          width: 3,
          height: 3,
          strokeThickness: 0,
          fill: "SteelBlue"
        })
      });

      // Серия Sensor_AVG (Orange)
      const dataSeriesAvg = new XyDataSeries(wasmContext, { xValues: [], yValues: [] });
      const rsAvg = new XyScatterRenderableSeries(wasmContext, {
        dataSeries: dataSeriesAvg,
        pointMarker: new EllipsePointMarker(wasmContext, {
          width: 3,
          height: 3,
          strokeThickness: 0,
          fill: "Orange"
        })
      });

      sciChartSurface.renderableSeries.add(rsSensor, rsAvg);

      // Базовые модификаторы навигации
      sciChartSurface.chartModifiers.add(
        new RubberBandXyZoomModifier({ executeOn: "MouseLeftButton" }),
        new ZoomPanModifier({ executeOn: "MouseRightButton" }),
        new MouseWheelZoomModifier(),
        new ZoomExtentsModifier()
      );

      // Сохраняем ссылки глобально при необходимости
      window.sensorScopeSurface = sciChartSurface;
      window.sensorScopeSeries = { rsSensor, rsAvg };
    } catch (e) {
      console.error("Ошибка инициализации графика sensor-scope:", e);
    }
  }

  // Правый верхний график (Sensor_Scope2): несколько серий, вертикальные линии (аналог VerticalSliceModifier)
  if (document.getElementById("sensor-scope-2")) {
    try {
      const { sciChartSurface, wasmContext } = await SciChartSurface.create("sensor-scope-2");

      const xAxis2 = new NumericAxis(wasmContext, {
        visibleRange: new scichart.NumberRange(0, 1025),
        axisTitle: "Время (мс)"
      });

      const yAxis2 = new NumericAxis(wasmContext, {
        visibleRange: new scichart.NumberRange(0, 256),
        axisTitle: "Амплитуда СЭ (у.е.)"
      });

      sciChartSurface.xAxes.add(xAxis2);
      sciChartSurface.yAxes.add(yAxis2);

      const colors = ["Red", "SteelBlue", "Green", "Red", "Blue", "Red"];
      const seriesNames = ["Sensor_Data2", "Sensor_Data3", "Sensor_Data4", "Sensor_Data5", "Sensor_Data6", "Sensor_Data7"];
      const seriesMap = {};

      seriesNames.forEach((name, idx) => {
        const ds = new XyDataSeries(wasmContext, { xValues: [], yValues: [] });
        const rs = new XyScatterRenderableSeries(wasmContext, {
          dataSeries: ds,
          pointMarker: new EllipsePointMarker(wasmContext, {
            width: 3,
            height: 3,
            strokeThickness: 0,
            fill: colors[idx]
          })
        });
        sciChartSurface.renderableSeries.add(rs);
        seriesMap[name] = { dataSeries: ds, series: rs };
      });

      // Вертикальные линии (Line1_s, Line2_s, Line3_s)
      sciChartSurface.annotations.add(
        new VerticalLineAnnotation({
          x1: 3,
          stroke: "#FF4682B4",
          strokeThickness: 1
        }),
        new VerticalLineAnnotation({
          x1: 2,
          stroke: "#FF008000",
          strokeThickness: 1
        }),
        new VerticalLineAnnotation({
          x1: 2,
          stroke: "#FF0000FF",
          strokeThickness: 1
        })
      );

      sciChartSurface.chartModifiers.add(
        new RolloverModifier({ showTooltip: true }),
        new LegendModifier({ showLegend: false }),
        new ZoomPanModifier({ executeOn: "MouseRightButton" }),
        new MouseWheelZoomModifier(),
        new ZoomExtentsModifier()
      );

      window.sensorScope2Surface = sciChartSurface;
      window.sensorScope2Series = seriesMap;
    } catch (e) {
      console.error("Ошибка инициализации графика sensor-scope-2:", e);
    }
  }

  // Правый нижний график (Sensor_Scope3): до 6 зависимостей, полноценная навигация
  if (document.getElementById("sensor-scope-3")) {
    try {
      const { sciChartSurface, wasmContext } = await SciChartSurface.create("sensor-scope-3");

      const xAxis3 = new NumericAxis(wasmContext, {
        visibleRange: new scichart.NumberRange(0, 100),
        axisTitle: "X"
      });

      const yAxis3 = new NumericAxis(wasmContext, {
        visibleRange: new scichart.NumberRange(0, 100),
        axisTitle: "Y"
      });

      sciChartSurface.xAxes.add(xAxis3);
      sciChartSurface.yAxes.add(yAxis3);

      const depColors = ["Red", "Blue", "Yellow", "Green", "pink", "white"];
      const depNames = ["Graphic_1", "Graphic_2", "Graphic_3", "Graphic_4", "Graphic_5", "Graphic_6"];
      const depSeriesMap = {};

      depNames.forEach((name, idx) => {
        const ds = new XyDataSeries(wasmContext, { xValues: [], yValues: [] });
        const rs = new XyScatterRenderableSeries(wasmContext, {
          dataSeries: ds,
          pointMarker: new EllipsePointMarker(wasmContext, {
            width: 3,
            height: 3,
            strokeThickness: 0,
            fill: depColors[idx]
          })
        });
        sciChartSurface.renderableSeries.add(rs);
        depSeriesMap[name] = { dataSeries: ds, series: rs };
      });

      sciChartSurface.chartModifiers.add(
        new RubberBandXyZoomModifier({ executeOn: "MouseLeftButton" }),
        new ZoomPanModifier({ executeOn: "MouseRightButton" }),
        new YAxisDragModifier({ dragMode: scichart.EAxisDragMode.Scale }),
        new XAxisDragModifier({ dragMode: scichart.EAxisDragMode.Pan }),
        new MouseWheelZoomModifier(),
        new ZoomExtentsModifier({ executeOn: "MouseDoubleClick" }),
        new LegendModifier({
          showLegend: true,
          orientation: scichart.ELegendOrientation.Vertical
        })
      );

      window.sensorScope3Surface = sciChartSurface;
      window.sensorScope3Series = depSeriesMap;
    } catch (e) {
      console.error("Ошибка инициализации графика sensor-scope-3:", e);
    }
  }
}


