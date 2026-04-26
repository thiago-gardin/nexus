(function () {
  "use strict";

  const payloadNode = document.getElementById("workbench-payload");
  const payload = payloadNode ? JSON.parse(payloadNode.textContent || "{}") : {};
  const workspace = payload.workspace || {};

  const root = document.querySelector("[data-workbench-root]");
  const form = document.getElementById("map-controls");
  const svgEl = document.getElementById("graph");
  const emptyState = document.getElementById("graph-empty");
  const inspector = document.getElementById("inspector-panel");
  const eventStrip = document.getElementById("event-strip");
  const toggleDrawerButton = document.getElementById("toggle-drawer");
  const closeDrawerButton = document.getElementById("close-drawer");
  const actionTabs = Array.from(document.querySelectorAll("[data-action-tab]"));
  const actionPanels = Array.from(document.querySelectorAll("[data-action-panel]"));
  const presetButtons = Array.from(document.querySelectorAll("[data-preset]"));
  const controls = form ? Array.from(form.querySelectorAll("[name]")) : [];
  const controlByName = Object.fromEntries(controls.map((control) => [control.name, control]));

  let simulation = null;
  let zoomBehavior = null;
  let zoomLayer = null;
  let latestGraph = { nodes: [], edges: [], meta: {} };
  let selectedId = null;
  let currentTransform = d3.zoomIdentity;

  const statusColors = {
    proposed: "#f3bf68",
    validated: "#6fdb9a",
    rejected: "#ff7a7a",
    contested: "#bda1ff",
    active: "#6fdb9a",
  };
  const riskColors = {
    ok: "#6fdb9a",
    attention: "#f3bf68",
    critical: "#ff7a7a",
  };
  const typePalette = ["#65d9bf", "#7aa8ff", "#bda1ff", "#a3d977", "#f3bf68", "#ff9d7a", "#d98cff"];
  const domainPalette = ["#65d9bf", "#7aa8ff", "#bda1ff", "#a3d977", "#f3bf68", "#ff7a7a", "#4ade80", "#14b8a6"];

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function shortId(value) {
    const text = String(value || "");
    return text.length > 18 ? `${text.slice(0, 8)}...${text.slice(-6)}` : text;
  }

  function slugify(value) {
    return String(value || "")
      .normalize("NFKD")
      .replace(/[^\w\s-]/g, "")
      .trim()
      .toLowerCase()
      .replace(/[\s_-]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function hashColor(value, palette) {
    const text = String(value || "unknown");
    let hash = 0;
    for (let index = 0; index < text.length; index += 1) {
      hash = (hash * 31 + text.charCodeAt(index)) % palette.length;
    }
    return palette[Math.abs(hash)];
  }

  function setDrawerOpen(open) {
    if (!root) return;
    root.dataset.drawerOpen = open ? "true" : "false";
    if (toggleDrawerButton) toggleDrawerButton.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function openActionTab(tabId) {
    actionTabs.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.actionTab === tabId);
    });
    actionPanels.forEach((panel) => {
      panel.classList.toggle("is-active", panel.dataset.actionPanel === tabId);
    });
    try {
      window.localStorage.setItem("nexus.workbench.actionTab", tabId);
    } catch (_error) {
      // ignore local storage failures
    }
  }

  function readStoredActionTab() {
    try {
      return window.localStorage.getItem("nexus.workbench.actionTab");
    } catch (_error) {
      return null;
    }
  }

  function readParams() {
    return new URLSearchParams(window.location.search);
  }

  function paramsFromControls() {
    const params = new URLSearchParams();
    controls.forEach((control) => {
      const value = String(control.value || "").trim();
      if (!value) return;
      if (control.name === "depth" && value === "2") return;
      if (control.name === "view" && value === "global") return;
      if (control.name === "cross_domain" && value === "show_all") return;
      params.set(control.name, value);
    });
    return params;
  }

  function updateUrlFromControls() {
    const params = paramsFromControls();
    const query = params.toString();
    const nextUrl = `${window.location.pathname}${query ? `?${query}` : ""}`;
    window.history.pushState({}, "", nextUrl);
  }

  function applyPreset(preset) {
    const values = {
      operational: { view: "domain", cross_domain: "show_all" },
      governance: { view: "governance", cross_domain: "proposed_only" },
      evidence: { view: "evidence", cross_domain: "show_all" },
      reentry: { view: "reentry", cross_domain: "show_all" },
      cross_domain: { view: "cross_domain", cross_domain: "only" },
    }[preset];
    if (!values) return;
    Object.entries(values).forEach(([name, value]) => {
      if (controlByName[name]) controlByName[name].value = value;
    });
  }

  function nodeColor(node) {
    const mode = controlByName.color_mode ? controlByName.color_mode.value : "by_domain";
    if (mode === "by_status") return statusColors[node.validation_status] || "#a2afbd";
    if (mode === "by_risk") return riskColors[node.risk] || "#a2afbd";
    if (mode === "by_type") return hashColor(node.entity_type, typePalette);
    return hashColor(node.domain_id, domainPalette);
  }

  function nodeRadius(node) {
    const mode = controlByName.size_mode ? controlByName.size_mode.value : "by_degree";
    if (mode === "uniform") return node.is_focal ? 28 : 20;
    if (mode === "by_confidence") return Math.max(14, Math.min(32, 12 + Number(node.confidence || 0.5) * 24));
    return Math.max(14, Math.min(34, 16 + Number(node.degree || 0) * 3));
  }

  function shouldShowLabel(node) {
    const mode = controlByName.label_mode ? controlByName.label_mode.value : "key";
    if (mode === "off") return false;
    if (mode === "all") return true;
    if (mode === "zoom") return node.is_focal || currentTransform.k >= 1.25;
    return node.is_focal || Number(node.degree || 0) >= 2 || latestGraph.nodes.length <= 20;
  }

  function updateLabelVisibility() {
    if (!zoomLayer) return;
    zoomLayer.selectAll(".node-label").style("opacity", (node) => (shouldShowLabel(node) ? 1 : 0));
  }

  async function loadGraph(pushUrl) {
    if (!form) return;
    if (pushUrl) updateUrlFromControls();
    const params = paramsFromControls();
    const query = params.toString();
    const response = await fetch(`/surface/graph.json${query ? `?${query}` : ""}`);
    if (!response.ok) throw new Error(`Graph request failed: ${response.status}`);
    latestGraph = await response.json();
    renderGraph(latestGraph);
  }

  function renderGraph(graph) {
    selectedId = null;
    if (simulation) simulation.stop();
    const svg = d3.select(svgEl);
    svg.selectAll("*").remove();
    if (emptyState) emptyState.classList.toggle("visible", graph.nodes.length === 0);

    const stage = svgEl.parentElement;
    const width = Math.max(stage.clientWidth || 900, 320);
    const height = Math.max(stage.clientHeight || 620, 480);
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const defs = svg.append("defs");
    defs.append("marker")
      .attr("id", "map-arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 26)
      .attr("refY", 0)
      .attr("markerWidth", 7)
      .attr("markerHeight", 7)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#354152");

    zoomLayer = svg.append("g").attr("class", "zoom-layer");
    const linkLayer = zoomLayer.append("g").attr("class", "links");
    const nodeLayer = zoomLayer.append("g").attr("class", "nodes");

    const nodes = graph.nodes.map((node) => ({ ...node }));
    const links = graph.edges.map((edge) => ({ ...edge }));

    zoomBehavior = d3.zoom()
      .scaleExtent([0.12, 8])
      .on("zoom", (event) => {
        currentTransform = event.transform;
        zoomLayer.attr("transform", currentTransform);
        updateLabelVisibility();
      });
    svg.call(zoomBehavior);
    currentTransform = d3.zoomIdentity;

    const link = linkLayer.selectAll("line")
      .data(links, (edge) => edge.id)
      .enter()
      .append("line")
      .attr("class", (edge) => `link${edge.cross_domain ? " cross-domain" : ""}`)
      .attr("marker-end", (edge) => edge.directionality === "directed" ? "url(#map-arrow)" : null)
      .on("click", (event, edge) => {
        event.stopPropagation();
        selectedId = edge.id;
        renderEdgeInspector(edge);
        highlightSelection(edge);
      });

    const node = nodeLayer.selectAll("g")
      .data(nodes, (item) => item.id)
      .enter()
      .append("g")
      .attr("class", "node")
      .call(d3.drag()
        .on("start", (event, item) => {
          if (!event.active) simulation.alphaTarget(0.25).restart();
          item.fx = item.x;
          item.fy = item.y;
        })
        .on("drag", (event, item) => {
          item.fx = event.x;
          item.fy = event.y;
        })
        .on("end", (event, item) => {
          if (!event.active) simulation.alphaTarget(0);
          item.fx = null;
          item.fy = null;
        }))
      .on("mouseover", (_event, item) => highlightSelection(item))
      .on("mouseout", () => { if (!selectedId) clearHighlight(); })
      .on("click", (event, item) => {
        event.stopPropagation();
        selectedId = item.id;
        renderNodeInspector(item);
        highlightSelection(item);
      })
      .on("dblclick", (event, item) => {
        event.stopPropagation();
        if (controlByName.focus) controlByName.focus.value = item.id;
        if (controlByName.view) controlByName.view.value = "focus";
        if (controlByName.depth && !controlByName.depth.value) controlByName.depth.value = "2";
        loadGraph(true).catch(showError);
      });

    node.append("circle")
      .attr("r", nodeRadius)
      .attr("fill", nodeColor);

    node.append("title")
      .text((item) => `${item.label} (${item.id})`);

    node.append("text")
      .attr("class", "node-label")
      .attr("x", (item) => nodeRadius(item) + 8)
      .attr("y", 4)
      .text((item) => {
        const label = String(item.label || item.id);
        return label.length > 30 ? `${label.slice(0, 28)}...` : label;
      });

    const linkForceDistance = (edge) => edge.cross_domain ? 190 : 138;
    simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((item) => item.id).distance(linkForceDistance).strength(0.55))
      .force("charge", d3.forceManyBody().strength(-420))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius((item) => nodeRadius(item) + 18))
      .force("x", d3.forceX(width / 2).strength(0.045))
      .force("y", d3.forceY(height / 2).strength(0.045))
      .alphaDecay(0.028)
      .velocityDecay(0.42);

    simulation.on("tick", () => {
      link
        .attr("x1", (edge) => edge.source.x)
        .attr("y1", (edge) => edge.source.y)
        .attr("x2", (edge) => edge.target.x)
        .attr("y2", (edge) => edge.target.y);
      node.attr("transform", (item) => `translate(${item.x},${item.y})`);
    });

    svg.on("click", () => {
      selectedId = null;
      clearHighlight();
      renderEmptyInspector();
    });

    renderEventStrip(graph);
    renderEmptyInspector();
    updateLabelVisibility();
    window.setTimeout(fitGraph, 450);
  }

  function connectedIds(item) {
    const ids = new Set([item.id]);
    latestGraph.edges.forEach((edge) => {
      if (edge.source === item.id) ids.add(edge.target);
      if (edge.target === item.id) ids.add(edge.source);
    });
    return ids;
  }

  function highlightSelection(item) {
    if (!zoomLayer) return;
    const isEdge = Boolean(item.source && item.target);
    const ids = isEdge ? new Set([item.source.id || item.source, item.target.id || item.target]) : connectedIds(item);
    zoomLayer.selectAll(".node")
      .classed("highlighted", (node) => ids.has(node.id))
      .classed("selected", (node) => node.id === item.id)
      .classed("dimmed", (node) => !ids.has(node.id));
    zoomLayer.selectAll(".link")
      .classed("highlighted", (edge) => ids.has(edge.source.id || edge.source) && ids.has(edge.target.id || edge.target))
      .classed("selected", (edge) => edge.id === item.id)
      .classed("dimmed", (edge) => !(ids.has(edge.source.id || edge.source) && ids.has(edge.target.id || edge.target)));
  }

  function clearHighlight() {
    if (!zoomLayer) return;
    zoomLayer.selectAll(".node,.link").classed("highlighted selected dimmed", false);
  }

  function renderEmptyInspector() {
    if (!inspector) return;
    inspector.innerHTML = `
      <h2>Nothing selected</h2>
      <p>Select a node or relation to inspect status, evidence, confidence, events, and context-aware next actions.</p>
    `;
  }

  function renderNodeInspector(node) {
    if (!inspector) return;
    inspector.innerHTML = `
      <h2>${escapeHtml(node.label)}</h2>
      <div class="status-pill status-${escapeHtml(node.validation_status || "unknown")}">entity / ${escapeHtml(node.entity_type || "unknown")}</div>
      <div class="meta-list">
        <div>id: ${escapeHtml(shortId(node.id))}</div>
        <div>domain: ${escapeHtml(node.domain_id || "none")}</div>
        <div>status: ${escapeHtml(node.validation_status || "unknown")}</div>
        <div>scope: ${escapeHtml(node.scope || "unknown")}</div>
        <div>confidence: ${escapeHtml(node.confidence ?? "n/a")}</div>
        <div>degree: ${escapeHtml(node.degree ?? 0)}</div>
        <div>evidence refs: ${escapeHtml(node.evidence_count ?? 0)}</div>
        <div>events: ${escapeHtml(node.event_count ?? 0)}</div>
        <div>latest event: ${escapeHtml(node.last_event_at || "none")}</div>
      </div>
      <div class="inspector-actions">
        <a class="button-link button-primary" href="${escapeHtml(node.inspector_href)}">Open Inspector</a>
        <a class="button-link button-subtle" href="${escapeHtml(node.history_href)}">History</a>
        <button type="button" class="button-subtle" data-open-tab="relation" data-source-entity="${escapeHtml(node.id)}">Create relation</button>
        <button type="button" class="button-subtle" data-open-tab="review" data-object-value="entity:${escapeHtml(node.id)}">Review object</button>
      </div>
    `;
    bindInspectorActions();
    if (eventStrip) eventStrip.textContent = `Selected entity ${node.label} (${node.validation_status || "unknown"}).`;
  }

  function renderEdgeInspector(edge) {
    if (!inspector) return;
    const source = edge.source.label || edge.source.id || edge.source;
    const target = edge.target.label || edge.target.id || edge.target;
    inspector.innerHTML = `
      <h2>${escapeHtml(edge.label || edge.relation_type || edge.id)}</h2>
      <div class="status-pill status-${escapeHtml(edge.validation_status || "unknown")}">relation${edge.cross_domain ? " / cross-domain" : ""}</div>
      <div class="meta-list">
        <div>id: ${escapeHtml(shortId(edge.id))}</div>
        <div>source: ${escapeHtml(source)}</div>
        <div>target: ${escapeHtml(target)}</div>
        <div>status: ${escapeHtml(edge.validation_status || "unknown")}</div>
        <div>confidence: ${escapeHtml(edge.confidence ?? "n/a")}</div>
        <div>evidence refs: ${escapeHtml(edge.evidence_count ?? 0)}</div>
        <div>events: ${escapeHtml(edge.event_count ?? 0)}</div>
        <div>latest event: ${escapeHtml(edge.last_event_at || "none")}</div>
      </div>
      <div class="inspector-actions">
        <a class="button-link button-primary" href="${escapeHtml(edge.inspector_href)}">Open Inspector</a>
        <a class="button-link button-subtle" href="${escapeHtml(edge.history_href)}">History</a>
        <button type="button" class="button-subtle" data-open-tab="review" data-object-value="relation:${escapeHtml(edge.id)}">Review object</button>
      </div>
    `;
    bindInspectorActions();
    if (eventStrip) eventStrip.textContent = `Selected relation ${edge.label || edge.id}.`;
  }

  function bindInspectorActions() {
    Array.from(inspector.querySelectorAll("[data-open-tab]")).forEach((button) => {
      button.addEventListener("click", () => {
        setDrawerOpen(true);
        openActionTab(button.dataset.openTab);
        if (button.dataset.sourceEntity) {
          const sourceSelect = document.getElementById("relation-source-select");
          if (sourceSelect) sourceSelect.value = button.dataset.sourceEntity;
          updateRelationPreview();
        }
        if (button.dataset.objectValue) {
          setReviewSelection("validate", button.dataset.objectValue);
          setReviewSelection("reject", button.dataset.objectValue);
        }
      });
    });
  }

  function renderEventStrip(graph) {
    if (!eventStrip) return;
    const latest = graph.nodes
      .concat(graph.edges)
      .map((item) => item.last_event_at)
      .filter(Boolean)
      .sort()
      .at(-1);
    eventStrip.textContent = latest
      ? `MAP loaded ${graph.nodes.length} nodes and ${graph.edges.length} edges. Latest event: ${latest}.`
      : `MAP loaded ${graph.nodes.length} nodes and ${graph.edges.length} edges.`;
  }

  function fitGraph() {
    if (!zoomLayer || !zoomBehavior) return;
    const bounds = zoomLayer.node().getBBox();
    const stage = svgEl.parentElement;
    const width = Math.max(stage.clientWidth || 900, 320);
    const height = Math.max(stage.clientHeight || 620, 480);
    if (!bounds.width || !bounds.height) return;
    const scale = Math.min(2.2, Math.max(0.15, 0.82 / Math.max(bounds.width / width, bounds.height / height)));
    const transform = d3.zoomIdentity
      .translate(width / 2, height / 2)
      .scale(scale)
      .translate(-(bounds.x + bounds.width / 2), -(bounds.y + bounds.height / 2));
    d3.select(svgEl).transition().duration(450).call(zoomBehavior.transform, transform);
  }

  function resetSimulation() {
    if (!simulation) return;
    simulation.alpha(0.9).restart();
  }

  function showError(error) {
    console.error(error);
    if (eventStrip) eventStrip.textContent = error.message || "Workbench graph failed to load.";
  }

  function parseInitialAttributes() {
    const container = document.getElementById("entity-dynamic-fields");
    if (!container) return {};
    try {
      return JSON.parse(container.dataset.attributesInitial || "{}");
    } catch (_error) {
      return {};
    }
  }

  function renderEntityDynamicFields() {
    const typeSelect = document.getElementById("entity-type-select");
    const container = document.getElementById("entity-dynamic-fields");
    if (!typeSelect || !container) return;
    const entityForms = workspace.ui_schema?.entity_forms || {};
    const schema = entityForms[typeSelect.value] || { fields: [] };
    const initialValues = parseInitialAttributes();
    const fragments = [];
    (schema.fields || []).forEach((field) => {
      const value = initialValues[field.name];
      const requiredAttr = field.required ? "required" : "";
      if (field.kind === "textarea") {
        fragments.push(`
          <label class="field">${escapeHtml(field.label)}
            <textarea data-attr-field="${escapeHtml(field.name)}" rows="3" ${requiredAttr}>${escapeHtml(value ?? "")}</textarea>
          </label>
        `);
        return;
      }
      if (field.kind === "select") {
        const options = (field.options || []).map((option) => `<option value="${escapeHtml(option)}" ${String(value ?? "") === String(option) ? "selected" : ""}>${escapeHtml(option)}</option>`).join("");
        fragments.push(`
          <label class="field">${escapeHtml(field.label)}
            <select data-attr-field="${escapeHtml(field.name)}" ${requiredAttr}>
              <option value="">Select</option>
              ${options}
            </select>
          </label>
        `);
        return;
      }
      if (field.kind === "checkbox") {
        fragments.push(`
          <label class="field">
            <span>${escapeHtml(field.label)}</span>
            <label class="toggle-row"><input type="checkbox" data-attr-field="${escapeHtml(field.name)}" ${value ? "checked" : ""} /> yes</label>
          </label>
        `);
        return;
      }
      const inputType = field.kind === "number" ? "number" : (field.kind === "datetime" ? "datetime-local" : "text");
      fragments.push(`
        <label class="field">${escapeHtml(field.label)}
          <input type="${inputType}" data-attr-field="${escapeHtml(field.name)}" value="${escapeHtml(value ?? "")}" ${requiredAttr} />
        </label>
      `);
    });
    container.innerHTML = fragments.join("") || `<div class="field-hint">No schema-driven attributes for this type.</div>`;
  }

  function syncEntityAttributesJson() {
    const container = document.getElementById("entity-dynamic-fields");
    const target = document.getElementById("entity-attributes-json");
    if (!container || !target) return;
    const attributes = {};
    Array.from(container.querySelectorAll("[data-attr-field]")).forEach((field) => {
      const key = field.dataset.attrField;
      let value = null;
      if (field.type === "checkbox") {
        value = field.checked;
      } else {
        value = field.value;
      }
      if (value === "" || value === null || value === undefined) return;
      attributes[key] = value;
    });
    target.value = JSON.stringify(attributes);
  }

  function setReviewSelection(kind, value) {
    const select = document.querySelector(`[data-object-picker="${kind}"]`);
    const objectType = document.getElementById(`${kind}-object-type`);
    const objectId = document.getElementById(`${kind}-object-id`);
    if (select) select.value = value;
    const [type, id] = String(value || "").split(":");
    if (objectType) objectType.value = type || "";
    if (objectId) objectId.value = id || "";
  }

  function bindReviewPickers() {
    Array.from(document.querySelectorAll("[data-object-picker]")).forEach((select) => {
      const kind = select.dataset.objectPicker;
      select.addEventListener("change", () => setReviewSelection(kind, select.value));
      if (select.value) setReviewSelection(kind, select.value);
    });
  }

  function updateDomainIdPreview() {
    const nameInput = document.getElementById("domain-name");
    const preview = document.getElementById("domain-id-preview");
    const hidden = document.getElementById("domain-id-hidden");
    if (!nameInput || !preview || !hidden) return;
    const suggested = slugify(nameInput.value);
    preview.value = suggested;
    hidden.value = suggested;
  }

  function updateRelationPreview() {
    const source = document.getElementById("relation-source-select");
    const target = document.getElementById("relation-target-select");
    const relationType = document.getElementById("relation-type-select");
    const preview = document.getElementById("relation-id-preview");
    if (!source || !target || !relationType || !preview) return;
    if (!source.value || !target.value || !relationType.value) {
      preview.value = "Generated automatically";
      return;
    }
    preview.value = "Generated automatically";
  }

  function bindHumanForms() {
    const domainNameInput = document.getElementById("domain-name");
    if (domainNameInput) {
      domainNameInput.addEventListener("input", updateDomainIdPreview);
      updateDomainIdPreview();
    }

    const entityTypeSelect = document.getElementById("entity-type-select");
    if (entityTypeSelect) {
      entityTypeSelect.addEventListener("change", renderEntityDynamicFields);
      renderEntityDynamicFields();
    }

    const entityForm = document.querySelector('[data-human-form="entity"]');
    if (entityForm) {
      entityForm.addEventListener("submit", syncEntityAttributesJson);
    }

    const sourceSelect = document.getElementById("relation-source-select");
    const targetSelect = document.getElementById("relation-target-select");
    const relationTypeSelect = document.getElementById("relation-type-select");
    [sourceSelect, targetSelect, relationTypeSelect].forEach((control) => {
      if (control) control.addEventListener("change", updateRelationPreview);
    });
    updateRelationPreview();

    bindReviewPickers();
  }

  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      loadGraph(true).catch(showError);
    });
  }

  if (toggleDrawerButton) {
    toggleDrawerButton.addEventListener("click", () => {
      setDrawerOpen(root?.dataset.drawerOpen !== "true");
    });
  }

  if (closeDrawerButton) {
    closeDrawerButton.addEventListener("click", () => setDrawerOpen(false));
  }

  actionTabs.forEach((button) => {
    button.addEventListener("click", () => {
      setDrawerOpen(true);
      openActionTab(button.dataset.actionTab);
    });
  });

  presetButtons.forEach((button) => {
    button.addEventListener("click", () => {
      applyPreset(button.dataset.preset);
      loadGraph(true).catch(showError);
    });
  });

  const resetButton = document.getElementById("reset-filters");
  if (resetButton) {
    resetButton.addEventListener("click", () => {
      if (controlByName.domain) controlByName.domain.value = workspace.domain_id || "";
      if (controlByName.focus) controlByName.focus.value = "";
      if (controlByName.depth) controlByName.depth.value = "2";
      if (controlByName.view) controlByName.view.value = workspace.domain_id ? "domain" : "global";
      if (controlByName.cross_domain) controlByName.cross_domain.value = "show_all";
      loadGraph(true).catch(showError);
    });
  }

  const copyLinkButton = document.getElementById("copy-link");
  if (copyLinkButton) {
    copyLinkButton.addEventListener("click", async () => {
      try {
        const params = paramsFromControls();
        const query = params.toString();
        const nextUrl = `${window.location.origin}${window.location.pathname}${query ? `?${query}` : ""}`;
        await navigator.clipboard.writeText(nextUrl);
        if (eventStrip) eventStrip.textContent = "Workbench link copied.";
      } catch (_error) {
        if (eventStrip) eventStrip.textContent = "Failed to copy workbench link.";
      }
    });
  }

  const zoomInButton = document.getElementById("zoom-in");
  if (zoomInButton) {
    zoomInButton.addEventListener("click", () => d3.select(svgEl).transition().duration(180).call(zoomBehavior.scaleBy, 1.18));
  }

  const zoomOutButton = document.getElementById("zoom-out");
  if (zoomOutButton) {
    zoomOutButton.addEventListener("click", () => d3.select(svgEl).transition().duration(180).call(zoomBehavior.scaleBy, 0.86));
  }

  const fitButton = document.getElementById("fit-graph");
  if (fitButton) fitButton.addEventListener("click", fitGraph);

  const refreshButton = document.getElementById("refresh-graph");
  if (refreshButton) refreshButton.addEventListener("click", () => loadGraph(false).catch(showError));

  const resetViewButton = document.getElementById("reset-view");
  if (resetViewButton) resetViewButton.addEventListener("click", resetSimulation);

  window.addEventListener("popstate", () => loadGraph(false).catch(showError));

  const storedTab = readStoredActionTab();
  if (storedTab && actionTabs.some((button) => button.dataset.actionTab === storedTab)) {
    openActionTab(storedTab);
  }

  bindHumanForms();
  loadGraph(false).catch(showError);
})();
