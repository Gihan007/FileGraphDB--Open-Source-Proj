from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path


def visualize_graph(
    folder: str | Path | None = None,
    db_path: str | Path | None = None,
    out_path: str | Path = "filegraph_visual.html",
    limit_edges: int = 300,
    min_weight: float = 0.0,
) -> dict:
    resolved_db = _resolve_db_path(folder, db_path)
    nodes, edges = _load_graph(resolved_db, limit_edges, min_weight)
    html = _render_html(nodes, edges, resolved_db)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return {"out_path": str(out), "nodes": len(nodes), "edges": len(edges), "db_path": str(resolved_db)}


def _resolve_db_path(folder: str | Path | None, db: str | Path | None) -> Path:
    if db:
        path = Path(db).expanduser().resolve()
    elif folder:
        path = Path(folder).expanduser().resolve() / ".filegraphdb.sqlite"
    else:
        raise ValueError("Pass folder or db_path")
    if not path.exists():
        raise FileNotFoundError(f"Graph database not found: {path}")
    return path


def _load_graph(db_path: Path, limit_edges: int, min_weight: float) -> tuple[list[dict], list[dict]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    edge_rows = conn.execute(
        """
        SELECT source_id, target_id, source_path, target_path, type, weight, confidence, evidence
        FROM edges
        WHERE weight >= ?
        ORDER BY weight DESC
        LIMIT ?
        """,
        (min_weight, limit_edges),
    ).fetchall()

    node_ids = sorted({row["source_id"] for row in edge_rows} | {row["target_id"] for row in edge_rows})
    if not node_ids:
        conn.close()
        return [], []

    placeholders = ",".join("?" for _ in node_ids)
    node_rows = conn.execute(
        f"SELECT id, path, properties_json FROM nodes WHERE id IN ({placeholders})",
        node_ids,
    ).fetchall()
    conn.close()

    degree = Counter()
    for row in edge_rows:
        degree[row["source_id"]] += 1
        degree[row["target_id"]] += 1

    nodes = []
    for row in node_rows:
        properties = json.loads(row["properties_json"])
        nodes.append(
            {
                "id": row["id"],
                "path": row["path"],
                "node_type": properties.get("node_type", "File"),
                "degree": degree[row["id"]],
                "keywords": properties.get("keywords", [])[:6],
                "topics": properties.get("topics", [])[:6],
                "entities": properties.get("entities", [])[:6],
            }
        )

    edges = [
        {
            "source": row["source_id"],
            "target": row["target_id"],
            "source_path": row["source_path"],
            "target_path": row["target_path"],
            "type": row["type"],
            "weight": round(float(row["weight"]), 4),
            "confidence": round(float(row["confidence"]), 4),
            "evidence": row["evidence"],
        }
        for row in edge_rows
    ]
    return nodes, edges


def _render_html(nodes: list[dict], edges: list[dict], db_path: Path) -> str:
    graph_json = json.dumps({"nodes": nodes, "links": edges}, ensure_ascii=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>FileGraphDB Visualization</title>
  <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
  <style>
    :root {{
      --bg: #f8fafc;
      --panel: #ffffff;
      --text: #172033;
      --muted: #667085;
      --line: #d0d5dd;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font: 14px/1.4 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background: var(--bg);
      display: grid;
      grid-template-columns: 320px 1fr;
    }}
    aside {{
      background: var(--panel);
      border-right: 1px solid var(--line);
      padding: 18px;
      overflow: auto;
    }}
    main {{ position: relative; overflow: hidden; }}
    h1 {{ font-size: 18px; margin: 0 0 4px; }}
    h2 {{ font-size: 13px; margin: 18px 0 8px; text-transform: uppercase; color: var(--muted); }}
    code {{ font-size: 12px; word-break: break-all; }}
    input, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px 10px;
      margin: 8px 0;
      background: white;
      color: var(--text);
    }}
    .stat {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      border-bottom: 1px solid #eef2f6;
      padding: 7px 0;
    }}
    .legend {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 8px 0;
    }}
    .swatch {{ width: 12px; height: 12px; border-radius: 999px; }}
    #details {{
      white-space: pre-wrap;
      background: #f9fafb;
      border: 1px solid #eef2f6;
      border-radius: 8px;
      padding: 10px;
      min-height: 140px;
      max-height: 280px;
      overflow: auto;
    }}
    svg {{ width: 100%; height: 100vh; display: block; }}
    .link {{ stroke-opacity: 0.32; cursor: pointer; }}
    .node {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; }}
    .node:hover {{ stroke: #111827; stroke-width: 2px; }}
    .label {{
      font-size: 10px;
      fill: #344054;
      paint-order: stroke;
      stroke: white;
      stroke-width: 3px;
      stroke-linecap: round;
      stroke-linejoin: round;
      pointer-events: none;
    }}
    .hidden {{ opacity: 0.06; }}
    .tooltip {{
      position: absolute;
      pointer-events: none;
      background: rgba(17, 24, 39, 0.92);
      color: white;
      padding: 8px 10px;
      border-radius: 8px;
      font-size: 12px;
      max-width: 360px;
      display: none;
    }}
  </style>
</head>
<body>
  <aside>
    <h1>FileGraphDB</h1>
    <div><code>{db_path}</code></div>

    <h2>Controls</h2>
    <input id="search" placeholder="Filter files by name..." />
    <select id="typeFilter">
      <option value="ALL">All relationship types</option>
    </select>

    <h2>Stats</h2>
    <div class="stat"><span>Nodes</span><strong id="nodeCount"></strong></div>
    <div class="stat"><span>Edges</span><strong id="edgeCount"></strong></div>
    <div class="stat"><span>Visible nodes</span><strong id="visibleNodeCount"></strong></div>
    <div class="stat"><span>Visible edges</span><strong id="visibleEdgeCount"></strong></div>

    <h2>Legend</h2>
    <div id="legend"></div>

    <h2>Selected</h2>
    <div id="details">Click a bubble or edge to inspect it.</div>
  </aside>

  <main>
    <svg id="graph"></svg>
    <div class="tooltip" id="tooltip"></div>
  </main>

  <script>
    const graph = {graph_json};
    const width = () => document.querySelector("main").clientWidth;
    const height = () => window.innerHeight;
    const svg = d3.select("#graph");
    const tooltip = d3.select("#tooltip");
    const details = document.getElementById("details");
    const typeColors = new Map([
      ["REFERENCES", "#2563eb"],
      ["SHARES_ENTITY", "#0f766e"],
      ["SHARES_TOPIC", "#9333ea"],
      ["SEMANTICALLY_SIMILAR", "#d97706"],
      ["CONTAINS", "#475467"],
    ]);
    const fallbackColor = "#64748b";

    document.getElementById("nodeCount").textContent = graph.nodes.length;
    document.getElementById("edgeCount").textContent = graph.links.length;

    const types = Array.from(new Set(graph.links.map(d => d.type))).sort();
    const typeFilter = document.getElementById("typeFilter");
    for (const type of types) {{
      const option = document.createElement("option");
      option.value = type;
      option.textContent = type;
      typeFilter.appendChild(option);
    }}
    document.getElementById("legend").innerHTML = types.map(type => `
      <div class="legend"><span class="swatch" style="background:${{typeColors.get(type) || fallbackColor}}"></span>${{type}}</div>
    `).join("");

    const zoomLayer = svg.append("g");
    const linkLayer = zoomLayer.append("g");
    const nodeLayer = zoomLayer.append("g");
    const labelLayer = zoomLayer.append("g");

    svg.call(d3.zoom().scaleExtent([0.15, 5]).on("zoom", event => {{
      zoomLayer.attr("transform", event.transform);
    }}));

    const simulation = d3.forceSimulation(graph.nodes)
      .force("link", d3.forceLink(graph.links).id(d => d.id).distance(d => 95 - d.weight * 45).strength(d => 0.25 + d.weight * 0.55))
      .force("charge", d3.forceManyBody().strength(d => -70 - d.degree * 8))
      .force("center", d3.forceCenter(width() / 2, height() / 2))
      .force("collision", d3.forceCollide().radius(d => radius(d) + 5));

    const links = linkLayer.selectAll("line")
      .data(graph.links)
      .join("line")
      .attr("class", "link")
      .attr("stroke", d => typeColors.get(d.type) || fallbackColor)
      .attr("stroke-width", d => 0.8 + d.weight * 3)
      .on("click", showEdge);

    const nodes = nodeLayer.selectAll("circle")
      .data(graph.nodes)
      .join("circle")
      .attr("class", "node")
      .attr("r", radius)
      .attr("fill", d => nodeColor(d))
      .call(drag(simulation))
      .on("mouseover", showTooltip)
      .on("mousemove", moveTooltip)
      .on("mouseout", hideTooltip)
      .on("click", showNode);

    const labels = labelLayer.selectAll("text")
      .data(graph.nodes.filter(d => d.degree >= 3))
      .join("text")
      .attr("class", "label")
      .text(d => d.path);

    simulation.on("tick", () => {{
      links
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      nodes
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      labels
        .attr("x", d => d.x + radius(d) + 3)
        .attr("y", d => d.y + 3);
    }});

    document.getElementById("search").addEventListener("input", applyFilters);
    typeFilter.addEventListener("change", applyFilters);
    applyFilters();

    function radius(d) {{
      return Math.max(5, Math.min(20, 5 + Math.sqrt(d.degree) * 3));
    }}

    function nodeColor(d) {{
      if (d.node_type === "Chunk") return "#7c3aed";
      if (d.degree >= 8) return "#be123c";
      if (d.degree >= 5) return "#0f766e";
      if (d.degree >= 3) return "#2563eb";
      return "#64748b";
    }}

    function applyFilters() {{
      const q = document.getElementById("search").value.trim().toLowerCase();
      const selectedType = typeFilter.value;
      const visibleNodeIds = new Set();

      links.classed("hidden", d => {{
        const typeOk = selectedType === "ALL" || d.type === selectedType;
        const textOk = !q || d.source.path.toLowerCase().includes(q) || d.target.path.toLowerCase().includes(q);
        const visible = typeOk && textOk;
        if (visible) {{
          visibleNodeIds.add(d.source.id);
          visibleNodeIds.add(d.target.id);
        }}
        return !visible;
      }});

      if (!q && selectedType === "ALL") {{
        graph.nodes.forEach(d => visibleNodeIds.add(d.id));
      }}

      nodes.classed("hidden", d => !visibleNodeIds.has(d.id));
      labels.classed("hidden", d => !visibleNodeIds.has(d.id));
      document.getElementById("visibleNodeCount").textContent = visibleNodeIds.size;
      document.getElementById("visibleEdgeCount").textContent = graph.links.filter(d => {{
        const typeOk = selectedType === "ALL" || d.type === selectedType;
        const textOk = !q || d.source.path.toLowerCase().includes(q) || d.target.path.toLowerCase().includes(q);
        return typeOk && textOk;
      }}).length;
    }}

    function showTooltip(event, d) {{
      tooltip.style("display", "block").html(`<strong>${{d.path}}</strong><br/>degree: ${{d.degree}}<br/>topics: ${{d.topics.join(", ") || "n/a"}}`);
      moveTooltip(event);
    }}

    function moveTooltip(event) {{
      tooltip.style("left", `${{event.pageX + 12}}px`).style("top", `${{event.pageY + 12}}px`);
    }}

    function hideTooltip() {{
      tooltip.style("display", "none");
    }}

    function showNode(event, d) {{
      details.textContent =
        `File: ${{d.path}}\\n` +
        `Type: ${{d.node_type || "File"}}\\n` +
        `Degree: ${{d.degree}}\\n\\n` +
        `Keywords:\\n${{(d.keywords || []).join(", ") || "n/a"}}\\n\\n` +
        `Topics:\\n${{(d.topics || []).join(", ") || "n/a"}}\\n\\n` +
        `Entities:\\n${{(d.entities || []).join(", ") || "n/a"}}`;
    }}

    function showEdge(event, d) {{
      details.textContent =
        `Relationship: ${{d.type}}\\n` +
        `Source: ${{d.source_path}}\\n` +
        `Target: ${{d.target_path}}\\n` +
        `Weight: ${{d.weight}}\\n` +
        `Confidence: ${{d.confidence}}\\n\\n` +
        `Evidence:\\n${{d.evidence}}`;
    }}

    function drag(simulation) {{
      function dragstarted(event) {{
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }}
      function dragged(event) {{
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }}
      function dragended(event) {{
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }}
      return d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended);
    }}

    window.addEventListener("resize", () => {{
      simulation.force("center", d3.forceCenter(width() / 2, height() / 2));
      simulation.alpha(0.3).restart();
    }});
  </script>
</body>
</html>
"""
