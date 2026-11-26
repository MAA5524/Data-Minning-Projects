(() => {
  const CLASS_PALETTE = [
    "#10b981",
    "#f59e0b",
    "#38bdf8",
    "#f43f5e",
    "#a855f7",
    "#ec4899",
    "#14b8a6",
    "#84cc16",
  ];

  const state = {
    datasets: [],
    selectedDataset: null,
    trainResult: null,
    highlightedNodeIds: new Set(),
    classColorMap: {},
    zoomBehavior: null,
    svgSelection: null,
    gRoot: null,
    hierarchyRoot: null,
    d3TreeUpdate: null,
  };

  const els = {
    datasetSelect: document.getElementById("dataset-select"),
    datasetMetaPill: document.getElementById("dataset-meta-pill"),
    csvUploadInput: document.getElementById("csv-upload-input"),
    uploadDropzone: document.getElementById("upload-dropzone"),
    uploadLabel: document.getElementById("upload-label"),
    targetSelect: document.getElementById("target-select"),
    testSizeSlider: document.getElementById("test-size-slider"),
    testSizeValue: document.getElementById("test-size-value"),
    unlimitedDepthCheckbox: document.getElementById("unlimited-depth-checkbox"),
    maxDepthSlider: document.getElementById("max-depth-slider"),
    maxDepthDisplay: document.getElementById("max-depth-display"),
    minSamplesInput: document.getElementById("min-samples-input"),
    seedInput: document.getElementById("seed-input"),
    trainBtn: document.getElementById("train-btn"),
    trainSpinner: document.getElementById("train-spinner"),
    trainBtnText: document.getElementById("train-btn-text"),
    statusToast: document.getElementById("status-toast"),
    activeRunSummary: document.getElementById("active-run-summary"),
    themeToggleBtn: document.getElementById("theme-toggle-btn"),
    themeIcon: document.getElementById("theme-icon"),
    themeLabel: document.getElementById("theme-label"),

    kpiTestAcc: document.getElementById("kpi-test-acc"),
    kpiMacroF1: document.getElementById("kpi-macro-f1"),
    kpiTrainAcc: document.getElementById("kpi-train-acc"),
    kpiSplitCounts: document.getElementById("kpi-split-counts"),
    kpiDepth: document.getElementById("kpi-depth"),
    kpiDepthLimit: document.getElementById("kpi-depth-limit"),
    kpiNodes: document.getElementById("kpi-nodes"),
    kpiInternalNodes: document.getElementById("kpi-internal-nodes"),
    kpiTime: document.getElementById("kpi-time"),
    kpiRulesCount: document.getElementById("kpi-rules-count"),

    tabButtons: document.querySelectorAll(".tab-btn"),
    tabPanels: document.querySelectorAll(".tab-panel"),

    treeViewport: document.getElementById("tree-viewport"),
    treeSvg: document.getElementById("tree-svg"),
    zoomInBtn: document.getElementById("zoom-in-btn"),
    zoomOutBtn: document.getElementById("zoom-out-btn"),
    zoomResetBtn: document.getElementById("zoom-reset-btn"),
    expandAllBtn: document.getElementById("expand-all-btn"),
    collapseDepth2Btn: document.getElementById("collapse-depth2-btn"),
    nodeInspector: document.getElementById("node-inspector"),
    inspectorTitle: document.getElementById("inspector-title"),
    inspectorBody: document.getElementById("inspector-body"),
    inspectorClose: document.getElementById("inspector-close"),

    predictForm: document.getElementById("predict-form"),
    predictSubmitBtn: document.getElementById("predict-submit-btn"),
    loadSampleBtn: document.getElementById("load-sample-btn"),
    resetFormBtn: document.getElementById("reset-form-btn"),
    sampleTrueLabel: document.getElementById("sample-true-label"),
    predictionResultBox: document.getElementById("prediction-result-box"),
    jumpToTreeBtn: document.getElementById("jump-to-tree-btn"),

    confusionMatrixContainer: document.getElementById("confusion-matrix-container"),
    metricsTableContainer: document.getElementById("metrics-table-container"),

    rulesSearchInput: document.getElementById("rules-search-input"),
    rulesClassFilter: document.getElementById("rules-class-filter"),
    rulesCountBar: document.getElementById("rules-count-bar"),
    rulesList: document.getElementById("rules-list"),
    downloadRulesTxt: document.getElementById("download-rules-txt"),
    downloadRulesCsv: document.getElementById("download-rules-csv"),
  };

  function showToast(message, type = "success") {
    els.statusToast.textContent = message;
    els.statusToast.className = `status-toast ${type}`;
    els.statusToast.hidden = false;
  }

  function hideToast() {
    els.statusToast.hidden = true;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function initTheme() {
    const saved = localStorage.getItem("id3_gini_theme") || "dark";
    applyTheme(saved);
    els.themeToggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      applyTheme(current === "dark" ? "light" : "dark");
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("id3_gini_theme", theme);
    if (theme === "dark") {
      els.themeIcon.textContent = "☀️";
      els.themeLabel.textContent = "Light Mode";
    } else {
      els.themeIcon.textContent = "🌙";
      els.themeLabel.textContent = "Dark Mode";
    }
  }

  function initTabs() {
    els.tabButtons.forEach((btn) => {
      btn.addEventListener("click", () => activateTab(btn.dataset.tab));
    });
  }

  function activateTab(tabId) {
    els.tabButtons.forEach((b) => {
      const active = b.dataset.tab === tabId;
      b.classList.toggle("active", active);
      b.setAttribute("aria-selected", active ? "true" : "false");
    });
    els.tabPanels.forEach((p) => {
      p.classList.toggle("active", p.id === tabId);
    });
  }

  function initControls() {
    els.testSizeSlider.addEventListener("input", () => {
      const testPct = Number(els.testSizeSlider.value);
      els.testSizeValue.textContent = `${testPct}% Test`;
    });

    els.unlimitedDepthCheckbox.addEventListener("change", () => {
      const unlimited = els.unlimitedDepthCheckbox.checked;
      els.maxDepthSlider.disabled = unlimited;
      els.maxDepthDisplay.textContent = unlimited ? "∞" : els.maxDepthSlider.value;
    });

    els.maxDepthSlider.addEventListener("input", () => {
      els.maxDepthDisplay.textContent = els.maxDepthSlider.value;
    });

    els.datasetSelect.addEventListener("change", () => {
      const found = state.datasets.find((d) => d.dataset_id === els.datasetSelect.value);
      if (found) selectDataset(found);
    });

    els.targetSelect.addEventListener("change", () => {
      updateDatasetMetaPill();
    });

    els.csvUploadInput.addEventListener("change", async (e) => {
      const file = e.target.files?.[0];
      if (file) await uploadCsvFile(file);
      els.csvUploadInput.value = "";
    });

    ["dragenter", "dragover"].forEach((evt) => {
      els.uploadDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        els.uploadDropzone.classList.add("drag-over");
      });
    });
    ["dragleave", "drop"].forEach((evt) => {
      els.uploadDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        els.uploadDropzone.classList.remove("drag-over");
      });
    });
    els.uploadDropzone.addEventListener("drop", async (e) => {
      const file = e.dataTransfer?.files?.[0];
      if (file) await uploadCsvFile(file);
    });

    els.trainBtn.addEventListener("click", trainModel);
    els.inspectorClose.addEventListener("click", () => {
      els.nodeInspector.hidden = true;
    });

    els.predictSubmitBtn.addEventListener("click", submitPrediction);
    els.loadSampleBtn.addEventListener("click", loadRandomTestSample);
    els.resetFormBtn.addEventListener("click", () => {
      els.sampleTrueLabel.hidden = true;
      buildPredictForm();
    });
    els.jumpToTreeBtn.addEventListener("click", () => {
      activateTab("tree-tab");
    });

    els.rulesSearchInput.addEventListener("input", renderRules);
    els.rulesClassFilter.addEventListener("change", renderRules);
    els.downloadRulesTxt.addEventListener("click", () => downloadRules("txt"));
    els.downloadRulesCsv.addEventListener("click", () => downloadRules("csv"));
  }

  async function fetchDatasets(preferredDatasetId = null) {
    try {
      const res = await fetch("/api/datasets");
      if (!res.ok) throw new Error("Failed to fetch datasets");
      const data = await res.json();
      state.datasets = data.datasets || [];
      renderDatasetDropdown(preferredDatasetId);
    } catch (err) {
      showToast(`Error loading datasets: ${err.message}`, "error");
    }
  }

  function renderDatasetDropdown(preferredId = null) {
    els.datasetSelect.innerHTML = "";
    state.datasets.forEach((ds) => {
      const opt = document.createElement("option");
      opt.value = ds.dataset_id;
      const tag = ds.source === "uploaded" ? " [Uploaded]" : "";
      opt.textContent = `${ds.name}${tag} (${ds.row_count} rows · ${ds.columns.length} cols)`;
      els.datasetSelect.appendChild(opt);
    });

    const targetDs =
      state.datasets.find((d) => d.dataset_id === preferredId) ||
      state.datasets.find((d) => d.dataset_id === "car_evaluation") ||
      state.datasets[0];

    if (targetDs) {
      els.datasetSelect.value = targetDs.dataset_id;
      selectDataset(targetDs);
    }
  }

  function selectDataset(dataset) {
    state.selectedDataset = dataset;
    els.targetSelect.innerHTML = "";
    dataset.columns.forEach((col) => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.textContent = col === dataset.default_target ? `${col} (auto-detected)` : col;
      els.targetSelect.appendChild(opt);
    });
    els.targetSelect.value = dataset.default_target;
    updateDatasetMetaPill();
  }

  function updateDatasetMetaPill() {
    const ds = state.selectedDataset;
    if (!ds) return;
    const targetCol = els.targetSelect.value || ds.default_target;
    const numFeatures = ds.columns.length - 1;
    const numClasses = (ds.unique_values_per_column[targetCol] || []).length;
    const headerNote = ds.has_synthetic_header ? " · Auto-Header" : "";
    els.datasetMetaPill.textContent =
      `${ds.row_count.toLocaleString()} rows · ${numFeatures} features · ${numClasses} classes${headerNote}`;
  }

  async function uploadCsvFile(file) {
    hideToast();
    const formData = new FormData();
    formData.append("file", file);
    els.uploadLabel.textContent = "Uploading...";
    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");

      els.uploadLabel.textContent = `Uploaded: ${file.name}`;
      await fetchDatasets(data.dataset.dataset_id);
      showToast(`Loaded "${data.dataset.name}" (${data.dataset.row_count} rows).`, "success");
    } catch (err) {
      els.uploadLabel.textContent = "Upload Custom CSV";
      showToast(err.message, "error");
    }
  }

  async function trainModel() {
    if (!state.selectedDataset) {
      showToast("No dataset selected.", "error");
      return;
    }
    hideToast();
    els.trainBtn.disabled = true;
    els.trainSpinner.hidden = false;
    els.trainBtnText.textContent = "Training ID3-Gini...";

    const unlimited = els.unlimitedDepthCheckbox.checked;
    const payload = {
      dataset_id: state.selectedDataset.dataset_id,
      target_column: els.targetSelect.value,
      test_size: Number(els.testSizeSlider.value) / 100,
      random_seed: Number(els.seedInput.value) || 42,
      max_depth: unlimited ? null : Number(els.maxDepthSlider.value),
      min_samples_split: Math.max(2, Number(els.minSamplesInput.value) || 2),
    };

    try {
      const res = await fetch("/api/train", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Training failed");

      state.trainResult = data;
      state.highlightedNodeIds = new Set();
      els.jumpToTreeBtn.hidden = true;
      els.sampleTrueLabel.hidden = true;
      els.predictionResultBox.className = "prediction-result-empty";
      els.predictionResultBox.innerHTML =
        'Model trained! Click <strong>Predict Class &amp; Trace Path</strong> to test any sample.';

      assignClassColors(data.metrics.labels);
      renderKPIs(data);
      renderDecisionTree(data.tree);
      buildPredictForm();
      renderEvaluation(data.metrics);
      populateRulesFilter(data.metrics.labels);
      renderRules();

      els.activeRunSummary.textContent =
        `Dataset: ${data.dataset_name} · Target: "${data.target_column}" · ${data.feature_columns.length} features`;
      showToast(
        `Trained in ${data.metrics.training_time_ms.toFixed(1)} ms · Test Acc: ${(data.metrics.test_accuracy * 100).toFixed(2)}%`,
        "success"
      );
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      els.trainBtn.disabled = false;
      els.trainSpinner.hidden = true;
      els.trainBtnText.textContent = "Train ID3-Gini Tree";
    }
  }

  function assignClassColors(labels) {
    state.classColorMap = {};
    labels.forEach((label, idx) => {
      state.classColorMap[label] = CLASS_PALETTE[idx % CLASS_PALETTE.length];
    });
  }

  function renderKPIs(data) {
    const m = data.metrics;
    els.kpiTestAcc.textContent = `${(m.test_accuracy * 100).toFixed(2)}%`;
    els.kpiMacroF1.textContent = `Macro F1: ${(m.macro_f1 * 100).toFixed(2)}%`;

    els.kpiTrainAcc.textContent = `${(m.train_accuracy * 100).toFixed(2)}%`;
    els.kpiSplitCounts.textContent = `Train: ${m.train_samples} · Test: ${m.test_samples}`;

    els.kpiDepth.textContent = `${m.tree_depth}`;
    els.kpiDepthLimit.textContent =
      data.split_info.max_depth === null ? "Max Depth: Unlimited" : `Max Depth: ${data.split_info.max_depth}`;

    els.kpiNodes.textContent = `${m.total_nodes} / ${m.leaf_nodes}`;
    els.kpiInternalNodes.textContent = `Internal Nodes: ${m.internal_nodes}`;

    els.kpiTime.textContent = `${m.training_time_ms.toFixed(2)} ms`;
    els.kpiRulesCount.textContent = `Extracted Rules: ${data.rules.length}`;
  }

  // Convert nested {children: {branchVal: subtree}} into D3 hierarchy format
  function transformTreeToHierarchy(node, edgeLabel = null) {
    const childrenEntries = Object.entries(node.children || {});
    const transformed = {
      ...node,
      edgeLabel,
      children: childrenEntries.map(([branchVal, childNode]) =>
        transformTreeToHierarchy(childNode, branchVal)
      ),
    };
    if (transformed.children.length === 0) {
      delete transformed.children;
    }
    return transformed;
  }

  function renderDecisionTree(treeData) {
    if (typeof d3 === "undefined") {
      els.treeViewport.innerHTML =
        '<div style="padding:2rem;text-align:center;color:var(--text-secondary);">D3.js CDN unavailable offline. Tree JSON trained successfully.</div>';
      return;
    }

    const svg = d3.select("#tree-svg");
    svg.selectAll("*").remove();

    const width = els.treeViewport.clientWidth || 960;
    const height = els.treeViewport.clientHeight || 600;

    const gZoom = svg.append("g").attr("class", "zoom-layer");
    const zoom = d3
      .zoom()
      .scaleExtent([0.12, 2.8])
      .on("zoom", (event) => {
        gZoom.attr("transform", event.transform);
      });

    svg.call(zoom);
    state.zoomBehavior = zoom;
    state.svgSelection = svg;
    state.gRoot = gZoom;

    const hierarchyData = transformTreeToHierarchy(treeData);
    const root = d3.hierarchy(hierarchyData, (d) => d.children);
    root.x0 = height / 2;
    root.y0 = 0;

    // Auto-collapse very large trees beyond depth 2 for readable initial view
    const totalNodes = state.trainResult?.metrics?.total_nodes || 0;
    if (totalNodes > 45) {
      root.descendants().forEach((d) => {
        if (d.depth >= 2 && d.children) {
          d._children = d.children;
          d.children = null;
        }
      });
    }

    state.hierarchyRoot = root;
    const treeLayout = d3.tree().nodeSize([88, 230]);

    function update(source) {
      treeLayout(root);
      const nodes = root.descendants();
      const links = root.links();

      // Links
      const linkSel = gZoom
        .selectAll("g.tree-link-group")
        .data(links, (d) => d.target.data.node_id);

      const linkEnter = linkSel.enter().append("g").attr("class", "tree-link-group");
      linkEnter
        .append("path")
        .attr("class", "tree-link-path")
        .attr("fill", "none");

      linkEnter
        .append("rect")
        .attr("class", "edge-pill-bg")
        .attr("rx", 5)
        .attr("ry", 5);

      linkEnter
        .append("text")
        .attr("class", "edge-pill-text")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central");

      const linkMerge = linkEnter.merge(linkSel);
      linkMerge
        .select("path.tree-link-path")
        .attr("d", (d) => {
          const sy = d.source.y;
          const sx = d.source.x;
          const ty = d.target.y;
          const tx = d.target.x;
          const midY = (sy + ty) / 2;
          return `M${sy},${sx} C${midY},${sx} ${midY},${tx} ${ty},${tx}`;
        })
        .attr("stroke", (d) =>
          state.highlightedNodeIds.has(d.source.data.node_id) &&
          state.highlightedNodeIds.has(d.target.data.node_id)
            ? "#f59e0b"
            : "var(--link-stroke)"
        )
        .attr("stroke-width", (d) =>
          state.highlightedNodeIds.has(d.source.data.node_id) &&
          state.highlightedNodeIds.has(d.target.data.node_id)
            ? 3.2
            : 1.6
        );

      linkMerge.each(function (d) {
        const label = d.target.data.edgeLabel || "";
        const midY = (d.source.y + d.target.y) / 2;
        const midX = (d.source.x + d.target.x) / 2;
        const pillW = Math.max(36, label.length * 7.4 + 14);
        const grp = d3.select(this);
        const onPath =
          state.highlightedNodeIds.has(d.source.data.node_id) &&
          state.highlightedNodeIds.has(d.target.data.node_id);

        grp
          .select("rect.edge-pill-bg")
          .attr("x", midY - pillW / 2)
          .attr("y", midX - 10)
          .attr("width", pillW)
          .attr("height", 20)
          .attr("fill", onPath ? "#f59e0b" : "var(--bg-sidebar)")
          .attr("stroke", onPath ? "#fbbf24" : "var(--border-strong)")
          .attr("stroke-width", 1);

        grp
          .select("text.edge-pill-text")
          .attr("x", midY)
          .attr("y", midX)
          .attr("font-size", "11px")
          .attr("font-family", "JetBrains Mono, monospace")
          .attr("font-weight", "600")
          .attr("fill", onPath ? "#0b1120" : "var(--text-primary)")
          .text(label);
      });

      linkSel.exit().remove();

      // Nodes
      const nodeSel = gZoom
        .selectAll("g.tree-node")
        .data(nodes, (d) => d.data.node_id);

      const nodeEnter = nodeSel
        .enter()
        .append("g")
        .attr("class", "tree-node")
        .attr("cursor", "pointer")
        .on("click", (event, d) => {
          event.stopPropagation();
          showNodeInspector(d.data);
          if (d.children) {
            d._children = d.children;
            d.children = null;
            update(d);
          } else if (d._children) {
            d.children = d._children;
            d._children = null;
            update(d);
          }
        });

      nodeEnter.append("rect").attr("class", "node-box").attr("rx", 10).attr("ry", 10);
      nodeEnter.append("text").attr("class", "node-title");
      nodeEnter.append("text").attr("class", "node-sub");
      nodeEnter.append("text").attr("class", "node-toggle-indicator");

      const nodeMerge = nodeEnter.merge(nodeSel);
      nodeMerge.attr("transform", (d) => `translate(${d.y},${d.x})`);

      nodeMerge.each(function (d) {
        const grp = d3.select(this);
        const nd = d.data;
        const isLeaf = nd.is_leaf;
        const onPath = state.highlightedNodeIds.has(nd.node_id);
        const boxW = isLeaf ? 148 : 168;
        const boxH = 54;

        const leafColor = state.classColorMap[nd.prediction] || "#10b981";
        const strokeColor = onPath
          ? "#f59e0b"
          : isLeaf
          ? leafColor
          : "var(--node-internal-stroke)";

        grp
          .select("rect.node-box")
          .attr("x", -boxW / 2)
          .attr("y", -boxH / 2)
          .attr("width", boxW)
          .attr("height", boxH)
          .attr("fill", isLeaf ? leafColor : "var(--node-internal-fill)")
          .attr("fill-opacity", isLeaf ? 0.16 : 1)
          .attr("stroke", strokeColor)
          .attr("stroke-width", onPath ? 3 : 1.8);

        grp
          .select("text.node-title")
          .attr("x", 0)
          .attr("y", -6)
          .attr("text-anchor", "middle")
          .attr("font-size", "12.5px")
          .attr("font-weight", "700")
          .attr("fill", isLeaf ? leafColor : "var(--text-primary)")
          .text(isLeaf ? `Class: ${nd.prediction}` : nd.attribute);

        const subText = isLeaf
          ? `n=${nd.samples} · Gini=${nd.gini.toFixed(3)}`
          : `n=${nd.samples} · ΔG=${nd.delta_gini.toFixed(3)}`;

        grp
          .select("text.node-sub")
          .attr("x", 0)
          .attr("y", 13)
          .attr("text-anchor", "middle")
          .attr("font-size", "10.5px")
          .attr("font-family", "JetBrains Mono, monospace")
          .attr("fill", "var(--text-secondary)")
          .text(subText);

        const hasHidden = Boolean(d._children);
        const hasVisible = Boolean(d.children);
        grp
          .select("text.node-toggle-indicator")
          .attr("x", boxW / 2 - 12)
          .attr("y", -boxH / 2 + 13)
          .attr("text-anchor", "middle")
          .attr("font-size", "12px")
          .attr("font-weight", "700")
          .attr("fill", "var(--accent-indigo)")
          .text(hasHidden ? "+" : hasVisible ? "−" : "");
      });

      nodeSel.exit().remove();
    }

    state.d3TreeUpdate = () => update(root);
    update(root);
    fitTreeToViewport();

    els.zoomInBtn.onclick = () => svg.transition().duration(200).call(zoom.scaleBy, 1.25);
    els.zoomOutBtn.onclick = () => svg.transition().duration(200).call(zoom.scaleBy, 0.8);
    els.zoomResetBtn.onclick = () => fitTreeToViewport();
    els.expandAllBtn.onclick = () => {
      root.descendants().forEach((d) => {
        if (d._children) {
          d.children = d._children;
          d._children = null;
        }
      });
      update(root);
      fitTreeToViewport();
    };
    els.collapseDepth2Btn.onclick = () => {
      root.descendants().forEach((d) => {
        if (d.depth >= 2 && d.children) {
          d._children = d.children;
          d.children = null;
        } else if (d.depth < 2 && d._children) {
          d.children = d._children;
          d._children = null;
        }
      });
      update(root);
      fitTreeToViewport();
    };
  }

  function fitTreeToViewport() {
    if (!state.svgSelection || !state.gRoot || !state.zoomBehavior) return;
    const width = els.treeViewport.clientWidth || 960;
    const height = els.treeViewport.clientHeight || 600;
    const bounds = state.gRoot.node().getBBox();
    if (!bounds || bounds.width === 0 || bounds.height === 0) return;

    const pad = 60;
    const scale = Math.min(
      1.1,
      Math.max(0.18, Math.min((width - pad) / bounds.width, (height - pad) / bounds.height))
    );
    const tx = width / 2 - scale * (bounds.x + bounds.width / 2);
    const ty = height / 2 - scale * (bounds.y + bounds.height / 2);

    state.svgSelection
      .transition()
      .duration(260)
      .call(state.zoomBehavior.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
  }

  function expandPathOnTree(pathNodeIds) {
    if (!state.hierarchyRoot || !state.d3TreeUpdate) return;
    const idSet = new Set(pathNodeIds);
    state.hierarchyRoot.descendants().forEach((d) => {
      if (idSet.has(d.data.node_id) && d._children) {
        d.children = d._children;
        d._children = null;
      }
    });
    state.d3TreeUpdate();
  }

  function showNodeInspector(nd) {
    els.inspectorTitle.textContent = nd.is_leaf
      ? `Leaf Node #${nd.node_id} (${nd.prediction})`
      : `Split: ${nd.attribute} (#${nd.node_id})`;

    const distEntries = Object.entries(nd.class_distribution || {});
    const distHtml =
      distEntries.length > 0
        ? distEntries
            .map(
              ([cls, cnt]) =>
                `<div class="dist-row"><span>${escapeHtml(cls)}</span><span>${cnt}</span></div>`
            )
            .join("")
        : '<div class="dist-row"><span>Empty branch (parent majority)</span><span>0</span></div>';

    els.inspectorBody.innerHTML = `
      <div class="dist-row"><strong>Samples</strong><span>${nd.samples}</span></div>
      <div class="dist-row"><strong>Gini(D)</strong><span>${nd.gini.toFixed(4)}</span></div>
      ${
        !nd.is_leaf
          ? `<div class="dist-row"><strong>Gini_A(D)</strong><span>${(nd.weighted_gini ?? 0).toFixed(4)}</span></div>
             <div class="dist-row"><strong>&Delta;Gini</strong><span>${nd.delta_gini.toFixed(4)}</span></div>`
          : ""
      }
      <div class="dist-row"><strong>Majority Class</strong><span>${escapeHtml(nd.majority_class)}</span></div>
      <div style="margin-top:0.3rem;font-weight:600;">Class Distribution</div>
      ${distHtml}
    `;
    els.nodeInspector.hidden = false;
  }

  function buildPredictForm() {
    const data = state.trainResult;
    if (!data) return;
    els.predictForm.innerHTML = "";

    data.feature_columns.forEach((col) => {
      const wrapper = document.createElement("div");
      wrapper.className = "predict-field";

      const label = document.createElement("label");
      label.className = "field-label";
      label.htmlFor = `pred-field-${col}`;
      label.textContent = col;

      const select = document.createElement("select");
      select.className = "input-control mono";
      select.id = `pred-field-${col}`;
      select.name = col;

      const values = data.unique_values_per_column[col] || [];
      values.forEach((val) => {
        const opt = document.createElement("option");
        opt.value = val;
        opt.textContent = val;
        select.appendChild(opt);
      });

      wrapper.appendChild(label);
      wrapper.appendChild(select);
      els.predictForm.appendChild(wrapper);
    });
  }

  function loadRandomTestSample() {
    const data = state.trainResult;
    if (!data || !data.sample_rows || data.sample_rows.length === 0) return;
    const sample = data.sample_rows[Math.floor(Math.random() * data.sample_rows.length)];

    data.feature_columns.forEach((col) => {
      const select = document.getElementById(`pred-field-${col}`);
      if (select && sample[col] !== undefined) {
        select.value = sample[col];
      }
    });

    if (sample[data.target_column] !== undefined) {
      els.sampleTrueLabel.textContent = `Ground Truth: ${sample[data.target_column]}`;
      els.sampleTrueLabel.hidden = false;
    }
  }

  async function submitPrediction() {
    const data = state.trainResult;
    if (!data) {
      showToast("Train a model first before predicting.", "error");
      return;
    }

    const samplePayload = {};
    data.feature_columns.forEach((col) => {
      const el = document.getElementById(`pred-field-${col}`);
      if (el) samplePayload[col] = el.value;
    });

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(samplePayload),
      });
      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || "Prediction failed");

      state.highlightedNodeIds = new Set(result.path_node_ids || []);
      expandPathOnTree(result.path_node_ids || []);
      els.jumpToTreeBtn.hidden = false;

      renderPredictionResult(result);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  function renderPredictionResult(result) {
    const fallbackHtml = result.unseen_fallback
      ? '<span class="fallback-badge">Unseen Value Fallback Used</span>'
      : "";

    const pathStepsHtml =
      result.path.length > 0
        ? result.path
            .map(
              (step, idx) => `
          <div class="path-step ${step.is_fallback ? "fallback" : ""}">
            <div>
              <strong>Step ${idx + 1}:</strong>
              <code>${escapeHtml(step.attribute)} = ${escapeHtml(step.value)}</code>
              ${step.is_fallback ? "<em>(unseen &rarr; majority fallback)</em>" : ""}
            </div>
            <div class="mono" style="color:var(--text-secondary);font-size:0.75rem;">
              Gini=${step.gini.toFixed(3)} · n=${step.samples}
            </div>
          </div>`
            )
            .join("")
        : '<div class="path-step">Predicted directly at root leaf node.</div>';

    els.predictionResultBox.className = "";
    els.predictionResultBox.innerHTML = `
      <div class="pred-banner">
        <div>
          <div style="font-size:0.76rem;color:var(--text-secondary);text-transform:uppercase;">
            Predicted ${escapeHtml(result.target_column || "Class")}
          </div>
          <div class="pred-class-value">${escapeHtml(result.prediction)}</div>
        </div>
        ${fallbackHtml}
      </div>
      <div class="path-list">${pathStepsHtml}</div>
    `;
  }

  function renderEvaluation(metrics) {
    const labels = metrics.labels || [];
    const matrix = metrics.confusion_matrix || [];
    const maxVal = Math.max(1, ...matrix.flat());

    let cmHtml = '<table class="data-table"><thead><tr><th>True \\ Pred</th>';
    labels.forEach((lbl) => {
      cmHtml += `<th>${escapeHtml(lbl)}</th>`;
    });
    cmHtml += "</tr></thead><tbody>";

    matrix.forEach((row, rIdx) => {
      cmHtml += `<tr><td class="row-header">${escapeHtml(labels[rIdx])}</td>`;
      row.forEach((val, cIdx) => {
        const intensity = val / maxVal;
        const bg =
          rIdx === cIdx
            ? `rgba(16, 185, 129, ${0.12 + intensity * 0.52})`
            : val > 0
            ? `rgba(244, 63, 94, ${0.08 + intensity * 0.42})`
            : "transparent";
        cmHtml += `<td class="mono" style="background:${bg};font-weight:${val > 0 ? 600 : 400};">${val}</td>`;
      });
      cmHtml += "</tr>";
    });
    cmHtml += "</tbody></table>";
    els.confusionMatrixContainer.innerHTML = cmHtml;

    let mHtml =
      '<table class="data-table"><thead><tr><th>Class</th><th>Precision</th><th>Recall</th><th>F1-Score</th><th>Support</th></tr></thead><tbody>';
    (metrics.per_class_metrics || []).forEach((row) => {
      mHtml += `<tr>
        <td class="row-header">${escapeHtml(row.label)}</td>
        <td class="mono">${(row.precision * 100).toFixed(2)}%</td>
        <td class="mono">${(row.recall * 100).toFixed(2)}%</td>
        <td class="mono">${(row.f1_score * 100).toFixed(2)}%</td>
        <td class="mono">${row.support}</td>
      </tr>`;
    });
    const totalSupport = (metrics.per_class_metrics || []).reduce((s, r) => s + r.support, 0);
    mHtml += `<tr class="summary-row">
      <td class="row-header">Macro Average</td>
      <td class="mono">${(metrics.macro_precision * 100).toFixed(2)}%</td>
      <td class="mono">${(metrics.macro_recall * 100).toFixed(2)}%</td>
      <td class="mono">${(metrics.macro_f1 * 100).toFixed(2)}%</td>
      <td class="mono">${totalSupport}</td>
    </tr></tbody></table>`;
    els.metricsTableContainer.innerHTML = mHtml;
  }

  function populateRulesFilter(labels) {
    els.rulesClassFilter.innerHTML = '<option value="ALL">All Classes</option>';
    labels.forEach((lbl) => {
      const opt = document.createElement("option");
      opt.value = lbl;
      opt.textContent = `Class: ${lbl}`;
      els.rulesClassFilter.appendChild(opt);
    });
  }

  function getFilteredRules() {
    const rules = state.trainResult?.rules || [];
    const q = (els.rulesSearchInput.value || "").trim().toLowerCase();
    const cls = els.rulesClassFilter.value;

    return rules.filter((r) => {
      if (cls !== "ALL" && r.prediction !== cls) return false;
      if (q && !r.text.toLowerCase().includes(q)) return false;
      return true;
    });
  }

  function renderRules() {
    const allRules = state.trainResult?.rules || [];
    const filtered = getFilteredRules();
    els.rulesCountBar.textContent = `Showing ${filtered.length} of ${allRules.length} extracted rules`;

    if (filtered.length === 0) {
      els.rulesList.innerHTML =
        '<div class="prediction-result-empty">No decision rules match the current filter.</div>';
      return;
    }

    const targetCol = state.trainResult.target_column;
    els.rulesList.innerHTML = filtered
      .map((rule) => {
        const condHtml =
          rule.conditions.length > 0
            ? rule.conditions
                .map(
                  (c) =>
                    `<span class="rule-cond">${escapeHtml(c.attribute)} = <strong>${escapeHtml(
                      c.value
                    )}</strong></span>`
                )
                .join(' <span class="rule-kw">AND</span> ')
            : "<strong>TRUE</strong>";
        return `
          <div class="rule-item">
            <div class="rule-code">
              <span class="rule-kw">IF</span> ${condHtml}
              <span class="rule-then">THEN</span> ${escapeHtml(targetCol)} = <strong>${escapeHtml(
                rule.prediction
              )}</strong>
            </div>
            <div class="rule-meta">
              <span class="mono-badge">n=${rule.samples}</span>
              <span class="mono-badge">${(rule.purity * 100).toFixed(1)}% pure</span>
            </div>
          </div>`;
      })
      .join("");
  }

  function downloadRules(format) {
    const filtered = getFilteredRules();
    if (filtered.length === 0) {
      showToast("No rules available to download.", "error");
      return;
    }

    let content = "";
    let mime = "text/plain";
    let ext = "txt";

    if (format === "csv") {
      mime = "text/csv";
      ext = "csv";
      const header = "rule_id,conditions,prediction,samples,purity";
      const rows = filtered.map((r) => {
        const conds = r.conditions.map((c) => `${c.attribute}=${c.value}`).join(" AND ");
        return `${r.rule_id},"${conds.replace(/"/g, '""')}","${r.prediction.replace(/"/g, '""')}",${r.samples},${r.purity}`;
      });
      content = [header, ...rows].join("\n");
    } else {
      content = filtered.map((r) => `R${r.rule_id}: ${r.text}`).join("\n");
    }

    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `id3_gini_rules.${ext}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  async function bootstrap() {
    initTheme();
    initTabs();
    initControls();
    await fetchDatasets();
    if (state.selectedDataset) {
      await trainModel();
    }
  }

  document.addEventListener("DOMContentLoaded", bootstrap);
})();
