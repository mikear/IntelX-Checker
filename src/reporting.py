"""Reporting helpers: build HTML content and small generators."""
import json
import logging
from analysis import clean_data_for_mandiant_report, prepare_mandiant_chart_data

logger = logging.getLogger(__name__)


def generate_modern_html_content(search_term, analysis, timestamp, data, helpers=None):
    # keep compatibility with previous signatures
    clean_data = clean_data_for_mandiant_report(data)
    chart_data = prepare_mandiant_chart_data(clean_data, analysis)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>IntelX Report - {search_term}</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f1419; color: #fff; padding: 20px; }}
    .card {{ background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 10px; }}
    .kpi {{ display:flex; gap:20px; }}
    table{{ width:100%; border-collapse:collapse; margin-top:10px; }}
    th,td{{ padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); text-align:left; }}
  </style>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
  <h1>IntelX Intelligence Report</h1>
  <div class="card kpi">
    <div>Total Records: {analysis.get('total_records', 0)}</div>
    <div>Sources: {len(analysis.get('source_distribution', {}))}</div>
  </div>
  <div class="card">
    <h2>Executive Summary</h2>
    {generate_executive_summary_html(analysis)}
  </div>
  <div class="card">
    <h2>Indicators of Compromise (sample)</h2>
    {generate_iocs_html(analysis.get('iocs', {}))}
  </div>
  <div class="card">
    <h2>Data (first 100)</h2>
    {generate_data_table_html(data[:100])}
  </div>
  <script>
    const chartData = {json.dumps(chart_data)};
    // simple pie if sources exist
        if (chartData.sources && Object.keys(chartData.sources).length>0) {{
            const data = [{{ values: Object.values(chartData.sources), labels: Object.keys(chartData.sources), type:'pie' }}];
            Plotly.newPlot('dummySourcesChart', data, {{paper_bgcolor:'transparent', plot_bgcolor:'transparent', legend: {{orientation: 'h'}} }});
        }}
  </script>
</body>
</html>"""
    return html


def generate_executive_summary_html(analysis):
    total = analysis.get('total_records', 0)
    sources = analysis.get('source_distribution', {})
    iocs = analysis.get('iocs', {})
    html = f"""
        <p>Records analyzed: {total}</p>
        <p>Unique sources: {len(sources)}</p>
        <p>Extracted IOCs: domains={len(iocs.get('domains',[]))}, ips={len(iocs.get('ips',[]))}</p>
        """
    return html


def generate_iocs_html(iocs):
    parts = []
    for k, lst in iocs.items():
        if lst:
            sample = ', '.join(str(x) for x in lst[:10])
            parts.append(f"<div><strong>{k}:</strong> {sample}</div>")
    return '\n'.join(parts) if parts else '<div>No IOCs detected</div>'


def generate_data_table_html(data):
    if not data:
        return '<div>No data</div>'
    cols = ['date','name','bucket','media','systemid']
    html = '<table><thead><tr>' + ''.join(f'<th>{c}</th>' for c in cols) + '</tr></thead><tbody>'
    for item in data:
        html += '<tr>' + ''.join(f'<td>{item.get(c,"")}</td>' for c in cols) + '</tr>'
    html += '</tbody></table>'
    return html
