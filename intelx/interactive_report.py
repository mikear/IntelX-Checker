"""
Interactive HTML Report Generator
Generates modern, interactive HTML reports with filtering and visualization capabilities.
"""

import os
import json
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, OrderedDict

from .api import MEDIA_TYPE_MAP
from .svg_charts import SVGVisualizationGenerator

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data processing and analysis for reports."""
    
    @staticmethod
    def analyze_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze records and extract statistics and distributions."""
        analysis = {
            "total_results": len(records),
            "source_distribution": Counter(),
            "type_distribution": Counter(),
            "media_distribution": Counter(),
            "exposure_levels": {"public": 0, "indexed": 0, "sensitive": 0},
            "kpis": {
                "leaks_percentage": 0.0,
                "complete_metadata_percentage": 0.0,
                "downloadable_documents_count": 0
            },
            "temporal_data": Counter(),
            "data_types": Counter(),
            "unique_sources": set()
        }

        leaks_count = 0
        complete_metadata_count = 0
        downloadable_count = 0

        for r in records:
            # Source analysis
            bucket = r.get("bucket", "N/A")
            analysis["source_distribution"][bucket] += 1
            analysis["unique_sources"].add(bucket)

            # Type analysis
            rtype = r.get("type", "N/A")
            analysis["type_distribution"][rtype] += 1

            # Media analysis
            media = r.get("media", "N/A")
            analysis["media_distribution"][media] += 1

            # Data type classification
            data_type = DataProcessor._classify_data_type(r)
            analysis["data_types"][data_type] += 1

            # Exposure levels
            tags_lower = str(r.get("tags", "")).lower()
            if "public" in tags_lower:
                analysis["exposure_levels"]["public"] += 1
            if r.get("indexed", False):
                analysis["exposure_levels"]["indexed"] += 1
            if "sensitive" in tags_lower or (r.get("xscore", 0) or 0) > 70:
                analysis["exposure_levels"]["sensitive"] += 1

            # Leak detection
            if "leak" in bucket.lower() or "paste" in bucket.lower():
                leaks_count += 1

            # Metadata completeness
            required_fields = ["date", "name", "size", "type", "media", "bucket", "xscore", "systemid"]
            if all(r.get(f) is not None for f in required_fields):
                complete_metadata_count += 1

            # Downloadable content
            if isinstance(media, int) and media in {15, 16, 17, 18, 19, 22, 23, 24, 27, 32}:
                downloadable_count += 1

            # Temporal analysis
            date_str = r.get("date")
            if date_str and len(date_str) >= 7:
                analysis["temporal_data"][date_str[:7]] += 1

        # Calculate KPIs
        total = analysis["total_results"] or 1
        if analysis["total_results"]:
            analysis["kpis"]["leaks_percentage"] = (leaks_count / total) * 100
            analysis["kpis"]["complete_metadata_percentage"] = (complete_metadata_count / total) * 100
        analysis["kpis"]["downloadable_documents_count"] = downloadable_count
        
        # Sort temporal data
        analysis["temporal_data"] = dict(sorted(analysis["temporal_data"].items()))
        analysis["unique_sources"] = len(analysis["unique_sources"])
        
        return analysis

    @staticmethod
    def _classify_data_type(record: Dict[str, Any]) -> str:
        """Classify record into data type categories."""
        name = str(record.get("name", "")).lower()
        bucket = str(record.get("bucket", "")).lower()
        media = record.get("media", 0)
        
        # Email detection - más específico
        if "@" in name or "email" in name or "mail" in name:
            return "Email"
        
        # Domain detection
        domain_patterns = [".com", ".org", ".net", ".gov", ".edu", ".ar", ".co.uk"]
        if any(tld in name for tld in domain_patterns) and "@" not in name and not name.endswith(('.txt', '.csv', '.rar', '.zip')):
            return "Dominio"
        
        # IP detection
        import re
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        if re.search(ip_pattern, name):
            return "IP"
        
        # Database/CSV files - más específico
        if any(ext in name for ext in [".csv", ".sql", ".db", ".sqlite"]) or "database" in bucket or "db" in bucket:
            return "Base de Datos"
        
        # Document types based on name extension
        doc_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"]
        if any(ext in name for ext in doc_extensions):
            return "Documento"
        
        # Code/Source
        code_extensions = [".py", ".js", ".php", ".html", ".css", ".java", ".cpp", ".c", ".rb", ".go"]
        if any(ext in name for ext in code_extensions):
            return "Código"
        
        # Document types based on media
        if isinstance(media, int):
            doc_media_types = {15, 16, 17, 18, 19, 22, 23, 24}  # PDF, DOC, XLS, etc.
            if media in doc_media_types:
                return "Documento"
        
        return "Otro"

    @staticmethod
    def prepare_chart_data(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for chart visualization."""
        
        def top_n_with_others(counter: Counter, n: int = 5) -> Tuple[List[str], List[int]]:
            """Get top N items plus 'Others' category."""
            items = counter.most_common()
            if not items:
                return [], []
            
            top = items[:n]
            rest = items[n:]
            
            labels = [str(k) for k, _ in top]
            values = [v for _, v in top]
            
            if rest:
                labels.append("Otros")
                values.append(sum(v for _, v in rest))
            
            return labels, values

        # Data types distribution
        data_type_labels, data_type_values = top_n_with_others(analysis["data_types"])
        
        # Media distribution with proper labels
        media_items = analysis["media_distribution"].items()
        grouped = {}
        for raw, count in media_items:
            label = DataProcessor._media_label(raw)
            grouped[label] = grouped.get(label, 0) + count
        
        media_counter = Counter(grouped)
        media_labels, media_values = top_n_with_others(media_counter)
        
        # Source distribution
        source_labels, source_values = top_n_with_others(analysis["source_distribution"])
        
        # Temporal evolution (last 5 years)
        temporal_data = DataProcessor._prepare_temporal_data(analysis["temporal_data"])
        
        return {
            "dataTypes": {"labels": data_type_labels, "values": data_type_values},
            "sources": {"labels": source_labels, "values": source_values},
            "temporal": temporal_data,
            "kpis": analysis["kpis"],
            "exposure": analysis["exposure_levels"]
        }

    @staticmethod
    def _media_label(value: Any) -> str:
        """Convert media value to human-readable label."""
        if value is None:
            return "Sin dato"
        if isinstance(value, int):
            return MEDIA_TYPE_MAP.get(value, "Desconocido")
        if isinstance(value, str):
            try:
                iv = int(value)
                return MEDIA_TYPE_MAP.get(iv, "Desconocido")
            except ValueError:
                return value
        return str(value)

    @staticmethod
    def _prepare_temporal_data(temporal_counter: Counter) -> Dict[str, Any]:
        """Prepare temporal data for the last 5 years."""
        from datetime import datetime, timedelta
        
        # Generate last 5 years by quarters (trimestres)
        today = datetime.now()
        periods = []
        for year_offset in range(5):
            year = today.year - year_offset
            for quarter in [1, 2, 3, 4]:
                # Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec
                quarter_months = {
                    1: ['01', '02', '03'],
                    2: ['04', '05', '06'], 
                    3: ['07', '08', '09'],
                    4: ['10', '11', '12']
                }
                periods.append({
                    'year': year,
                    'quarter': quarter,
                    'label': f'{year} Q{quarter}',
                    'months': [f'{year}-{month}' for month in quarter_months[quarter]]
                })
        
        periods.reverse()  # Chronological order
        
        # Aggregate counts by quarter
        period_counts = []
        period_labels = []
        
        for period in periods:
            quarter_count = 0
            for month in period['months']:
                quarter_count += temporal_counter.get(month, 0)
            period_counts.append(quarter_count)
            period_labels.append(period['label'])
        
        return {
            "labels": period_labels,
            "values": period_counts
        }


class VisualizationGenerator:
    """Generates HTML and JavaScript for interactive SVG visualizations."""
    
    def __init__(self):
        self.svg_generator = SVGVisualizationGenerator()
    
    def generate_charts_html(self, chart_data: Dict[str, Any]) -> str:
        """Generate HTML structure with SVG charts."""
        return self.svg_generator.generate_charts_html(chart_data)

    def generate_charts_js(self, chart_data: Dict[str, Any]) -> str:
        """Generate minimal JavaScript for SVG interactivity."""
        return self.svg_generator.generate_charts_js(chart_data)


class TableGenerator:
    """Generates interactive HTML tables with filtering capabilities."""
    
    @staticmethod
    def generate_table_html(records: List[Dict[str, Any]]) -> str:
        """Generate interactive table HTML with filters."""
        # Prepare records for display
        processed_records = TableGenerator._process_records_for_table(records)
        
        # Get unique values for filters
        unique_types = sorted(set(r.get('data_type', 'N/A') for r in processed_records))
        unique_sources = sorted(set(r.get('bucket', 'N/A') for r in processed_records))
        
        filters_html = f"""
        <div class="filters-container">
            <div class="filters-row">
                <div class="filter-group">
                    <label for="typeFilter">Tipo de Dato:</label>
                    <select id="typeFilter">
                        <option value="">Todos los tipos</option>
                        {chr(10).join(f'<option value="{t}">{t}</option>' for t in unique_types)}
                    </select>
                </div>
                <div class="filter-group">
                    <label for="sourceFilter">Fuente:</label>
                    <select id="sourceFilter">
                        <option value="">Todas las fuentes</option>
                        {chr(10).join(f'<option value="{s}">{s}</option>' for s in unique_sources)}
                    </select>
                </div>
                <div class="filter-group">
                    <label for="dateFromFilter">Desde:</label>
                    <input type="date" id="dateFromFilter">
                </div>
                <div class="filter-group">
                    <label for="dateToFilter">Hasta:</label>
                    <input type="date" id="dateToFilter">
                </div>
                <div class="filter-group">
                    <button id="clearFilters" class="btn-secondary">Limpiar Filtros</button>
                </div>
            </div>
            <div class="search-row">
                <div class="search-group">
                    <label for="searchInput">Buscar:</label>
                    <input type="text" id="searchInput" placeholder="Buscar en nombre, tipo o fuente...">
                </div>
                <div class="results-info">
                    <span id="resultsCount">Mostrando {len(processed_records)} resultados</span>
                </div>
            </div>
        </div>
        """
        
        table_html = """
        <div class="table-container">
            <table id="resultsTable">
                <thead>
                    <tr>
                        <th class="sortable" data-column="date">
                            Fecha <span class="sort-icon">↕</span>
                        </th>
                        <th class="sortable" data-column="name">
                            Nombre <span class="sort-icon">↕</span>
                        </th>
                        <th class="sortable" data-column="data_type">
                            Tipo de Dato <span class="sort-icon">↕</span>
                        </th>
                        <th class="sortable" data-column="bucket">
                            Fuente <span class="sort-icon">↕</span>
                        </th>
                        <th class="sortable" data-column="media_label">
                            Media <span class="sort-icon">↕</span>
                        </th>
                        <th class="sortable" data-column="xscore">
                            Puntuación <span class="sort-icon">↕</span>
                        </th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </div>
        """
        
        return filters_html + table_html

    @staticmethod
    def generate_table_js(records: List[Dict[str, Any]]) -> str:
        """Generate JavaScript code for table functionality."""
        processed_records = TableGenerator._process_records_for_table(records)
        
        return f"""
        // Table data and functionality
        const tableData = {json.dumps(processed_records)};
        let filteredData = [...tableData];
        let currentSort = {{ column: 'date', direction: 'desc' }};

        function renderTable(data) {{
            const tbody = document.querySelector('#resultsTable tbody');
            tbody.innerHTML = '';
            
            data.forEach(record => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{record.date || 'N/A'}}</td>
                    <td class="name-cell" title="${{record.name || 'N/A'}}">${{truncateText(record.name || 'N/A', 40)}}</td>
                    <td><span class="badge badge-${{record.data_type.toLowerCase().replace(/\\s+/g, '-')}}">${{record.data_type}}</span></td>
                    <td class="source-cell" title="${{record.bucket || 'N/A'}}">${{truncateText(record.bucket || 'N/A', 30)}}</td>
                    <td>${{record.media_label || 'N/A'}}</td>
                    <td class="score-cell">
                        <span class="score score-${{getScoreClass(record.xscore)}}">${{record.xscore || '–'}}</span>
                    </td>
                    <td>
                        ${{record.systemid ? 
                            `<a href="https://intelx.io/?s=${{record.systemid}}" target="_blank" class="btn-link">Ver</a>` : 
                            'N/A'
                        }}
                    </td>
                `;
                tbody.appendChild(row);
            }});
            
            // Update results count
            document.getElementById('resultsCount').textContent = `Mostrando ${{data.length}} de ${{tableData.length}} resultados`;
        }}

        function truncateText(text, maxLength) {{
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength) + '...';
        }}

        function getScoreClass(score) {{
            if (!score || score === '–') return 'low';
            const numScore = parseInt(score);
            if (numScore >= 80) return 'high';
            if (numScore >= 50) return 'medium';
            return 'low';
        }}

        function sortData(column, direction) {{
            filteredData.sort((a, b) => {{
                let aVal = a[column] || '';
                let bVal = b[column] || '';
                
                // Handle numeric values
                if (column === 'xscore') {{
                    aVal = parseInt(aVal) || 0;
                    bVal = parseInt(bVal) || 0;
                }}
                
                // Handle dates
                if (column === 'date') {{
                    aVal = new Date(aVal || '1970-01-01');
                    bVal = new Date(bVal || '1970-01-01');
                }}
                
                if (aVal < bVal) return direction === 'asc' ? -1 : 1;
                if (aVal > bVal) return direction === 'asc' ? 1 : -1;
                return 0;
            }});
        }}

        function applyFilters() {{
            const typeFilter = document.getElementById('typeFilter').value;
            const sourceFilter = document.getElementById('sourceFilter').value;
            const dateFromFilter = document.getElementById('dateFromFilter').value;
            const dateToFilter = document.getElementById('dateToFilter').value;
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            
            filteredData = tableData.filter(record => {{
                // Type filter
                if (typeFilter && record.data_type !== typeFilter) return false;
                
                // Source filter
                if (sourceFilter && record.bucket !== sourceFilter) return false;
                
                // Date range filter
                if (dateFromFilter || dateToFilter) {{
                    const recordDate = new Date(record.date || '1970-01-01');
                    if (dateFromFilter && recordDate < new Date(dateFromFilter)) return false;
                    if (dateToFilter && recordDate > new Date(dateToFilter)) return false;
                }}
                
                // Search filter
                if (searchInput) {{
                    const searchFields = [
                        record.name || '',
                        record.data_type || '',
                        record.bucket || '',
                        record.media_label || ''
                    ].join(' ').toLowerCase();
                    
                    if (!searchFields.includes(searchInput)) return false;
                }}
                
                return true;
            }});
            
            // Apply current sort
            sortData(currentSort.column, currentSort.direction);
            renderTable(filteredData);
        }}

        function initializeTable() {{
            // Initial sort and render
            sortData('date', 'desc');
            renderTable(filteredData);
            
            // Add event listeners for filters
            ['typeFilter', 'sourceFilter', 'dateFromFilter', 'dateToFilter', 'searchInput'].forEach(id => {{
                document.getElementById(id).addEventListener('change', applyFilters);
                document.getElementById(id).addEventListener('input', applyFilters);
            }});
            
            // Clear filters button
            document.getElementById('clearFilters').addEventListener('click', () => {{
                document.getElementById('typeFilter').value = '';
                document.getElementById('sourceFilter').value = '';
                document.getElementById('dateFromFilter').value = '';
                document.getElementById('dateToFilter').value = '';
                document.getElementById('searchInput').value = '';
                applyFilters();
            }});
            
            // Sortable headers
            document.querySelectorAll('.sortable').forEach(header => {{
                header.addEventListener('click', () => {{
                    const column = header.dataset.column;
                    const newDirection = (currentSort.column === column && currentSort.direction === 'asc') ? 'desc' : 'asc';
                    
                    // Update sort indicators
                    document.querySelectorAll('.sort-icon').forEach(icon => {{
                        icon.textContent = '↕';
                    }});
                    header.querySelector('.sort-icon').textContent = newDirection === 'asc' ? '↑' : '↓';
                    
                    currentSort = {{ column, direction: newDirection }};
                    sortData(column, newDirection);
                    renderTable(filteredData);
                }});
            }});
        }}

        // Initialize table when DOM is ready
        document.addEventListener('DOMContentLoaded', initializeTable);
        """

    @staticmethod
    def _process_records_for_table(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process records for table display."""
        processed = []
        
        for record in records:
            processed_record = {
                'date': record.get('date', ''),
                'name': record.get('name', 'N/A'),
                'bucket': record.get('bucket', 'N/A'),
                'type': record.get('type', 'N/A'),
                'media': record.get('media', ''),
                'media_label': DataProcessor._media_label(record.get('media')),
                'xscore': record.get('xscore', ''),
                'systemid': record.get('systemid', ''),
                'data_type': DataProcessor._classify_data_type(record)
            }
            processed.append(processed_record)
        
        return processed


class StyleGenerator:
    """Generates modern CSS styles for the report."""
    
    @staticmethod
    def generate_css() -> str:
        """Generate comprehensive CSS for modern UI."""
        return """
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', 'SF Pro Display', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
        }

        /* Container and layout */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.2);
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }

        .header-meta {
            font-size: 1rem;
            opacity: 0.9;
        }

        /* KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.1);
        }

        .kpi-label {
            font-size: 0.875rem;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1f2937;
        }

        .kpi-change {
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }

        .kpi-change.positive { color: #059669; }
        .kpi-change.negative { color: #dc2626; }

        /* Charts section */
        .charts-section {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .charts-container {
            width: 100%;
        }

        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .chart-grid-three {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }

        .chart-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 0.75rem;
            padding: 1.5rem;
            height: 450px;
        }

        .chart-card.chart-wide {
            grid-column: 1 / -1;
            height: 550px;
            margin-top: 1rem;
        }

        .chart-card h3 {
            font-size: 1.125rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 1rem;
            text-align: center;
        }

        .chart-card svg {
            max-height: 380px;
            width: 100%;
            display: block;
            margin: 0 auto;
        }

        .chart-wide svg {
            max-height: 480px;
            width: 100%;
            display: block;
            margin: 0 auto;
        }

        /* Table section */
        .table-section {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
        }

        /* Filters */
        .filters-container {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .filters-row, .search-row {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: end;
        }

        .search-row {
            margin-top: 1rem;
            justify-content: space-between;
        }

        .filter-group, .search-group {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            min-width: 150px;
        }

        .search-group {
            flex: 1;
            max-width: 400px;
        }

        .filter-group label, .search-group label {
            font-size: 0.875rem;
            font-weight: 600;
            color: #374151;
        }

        .filter-group select, .filter-group input, .search-group input {
            padding: 0.5rem 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .filter-group select:focus, .filter-group input:focus, .search-group input:focus {
            outline: none;
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .btn-secondary {
            padding: 0.5rem 1rem;
            background: #6b7280;
            color: white;
            border: none;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        .btn-secondary:hover {
            background: #4b5563;
        }

        .results-info {
            font-size: 0.875rem;
            color: #6b7280;
            font-weight: 500;
        }

        /* Table styles */
        .table-container {
            overflow-x: auto;
            border-radius: 0.75rem;
            border: 1px solid #e5e7eb;
        }

        #resultsTable {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        #resultsTable th {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 1rem 0.75rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.875rem;
            letter-spacing: 0.025em;
            border-bottom: 1px solid #e5e7eb;
        }

        #resultsTable th.sortable {
            cursor: pointer;
            user-select: none;
            transition: background-color 0.2s ease;
        }

        #resultsTable th.sortable:hover {
            background: linear-gradient(135deg, #5855eb 0%, #7c3aed 100%);
        }

        .sort-icon {
            margin-left: 0.25rem;
            font-size: 0.75rem;
        }

        #resultsTable td {
            padding: 0.75rem;
            border-bottom: 1px solid #f3f4f6;
            font-size: 0.875rem;
        }

        #resultsTable tbody tr:hover {
            background: #f9fafb;
        }

        #resultsTable tbody tr:nth-child(even) {
            background: #fafafa;
        }

        #resultsTable tbody tr:nth-child(even):hover {
            background: #f3f4f6;
        }

        /* Table cell specific styles */
        .name-cell, .source-cell {
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .score-cell {
            text-align: center;
        }

        /* Badges and scores */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }

        .badge-email { background: #dbeafe; color: #1e40af; }
        .badge-dominio { background: #dcfce7; color: #166534; }
        .badge-ip { background: #fef3c7; color: #92400e; }
        .badge-documento { background: #e0e7ff; color: #3730a3; }
        .badge-código { background: #f3e8ff; color: #6b21a8; }
        .badge-base-de-datos { background: #fed7d7; color: #c53030; }
        .badge-otro { background: #f3f4f6; color: #374151; }

        .score {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .score-high { background: #fee2e2; color: #dc2626; }
        .score-medium { background: #fef3c7; color: #d97706; }
        .score-low { background: #dcfce7; color: #059669; }

        .btn-link {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: #6366f1;
            color: white;
            text-decoration: none;
            border-radius: 0.375rem;
            font-size: 0.75rem;
            font-weight: 600;
            transition: background-color 0.2s ease;
        }

        .btn-link:hover {
            background: #4f46e5;
        }

        /* Footer */
        .footer {
            background: #1f2937;
            color: #9ca3af;
            padding: 2rem;
            border-radius: 1rem;
            margin-top: 2rem;
            text-align: center;
            font-size: 0.875rem;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }

            .header {
                padding: 2rem 1rem;
            }

            .header h1 {
                font-size: 2rem;
            }

            .kpi-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }

            .chart-grid,
            .chart-grid-three {
                grid-template-columns: 1fr;
            }

            .chart-card.chart-wide {
                grid-column: 1;
            }

            .filters-row {
                flex-direction: column;
                align-items: stretch;
            }

            .filter-group {
                min-width: unset;
            }

            .search-row {
                flex-direction: column;
                align-items: stretch;
                gap: 1rem;
            }

            .search-group {
                max-width: unset;
            }

            #resultsTable {
                font-size: 0.75rem;
            }

            #resultsTable th, #resultsTable td {
                padding: 0.5rem 0.25rem;
            }
        }

        /* Print styles */
        @media print {
            body {
                background: white;
            }

            .container {
                max-width: none;
                padding: 0;
            }

            .header {
                background: #6366f1 !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }

            .charts-section, .table-section {
                break-inside: avoid;
            }

            .btn-link {
                background: #6366f1 !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
        }
        """


class InteractiveReportGenerator:
    """Main class for generating interactive HTML reports."""
    
    def __init__(self, app_version: str = "2.0.0"):
        self.app_version = app_version
        self.data_processor = DataProcessor()
        self.visualization_generator = VisualizationGenerator()
        self.table_generator = TableGenerator()
        self.style_generator = StyleGenerator()

    def generate_report(self, 
                       records: List[Dict[str, Any]], 
                       output_filepath: str, 
                       search_term: str) -> str:
        """
        Generate a complete interactive HTML report.
        
        Args:
            records: List of search result records
            output_filepath: Path where to save the HTML file
            search_term: The search term used
            
        Returns:
            Path to the generated HTML file
        """
        try:
            # Process data
            analysis = self.data_processor.analyze_records(records)
            chart_data = self.data_processor.prepare_chart_data(analysis)
            
            # Generate HTML components
            html_content = self._build_html_document(records, analysis, chart_data, search_term)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            
            # Write to file
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Interactive HTML report generated: {output_filepath}")
            return output_filepath
            
        except Exception as e:
            logger.error(f"Error generating interactive report: {e}")
            raise

    def _build_html_document(self, 
                           records: List[Dict[str, Any]], 
                           analysis: Dict[str, Any], 
                           chart_data: Dict[str, Any], 
                           search_term: str) -> str:
        """Build the complete HTML document."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Build KPI cards
        kpi_cards = self._build_kpi_cards(analysis)
        
        # Build charts section
        charts_html = self.visualization_generator.generate_charts_html(chart_data)
        charts_js = self.visualization_generator.generate_charts_js(chart_data)
        
        # Build table section
        table_html = self.table_generator.generate_table_html(records)
        table_js = self.table_generator.generate_table_js(records)
        
        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IntelX Report - {search_term}</title>
    <style>
    {self.style_generator.generate_css()}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1>📊 IntelX Intelligence Report</h1>
            <div class="header-meta">
                <strong>Término de búsqueda:</strong> {search_term or 'N/A'} • 
                <strong>Resultados:</strong> {analysis['total_results']} • 
                <strong>Generado:</strong> {timestamp} • 
                <strong>Versión:</strong> {self.app_version}
            </div>
        </header>

        <!-- KPI Section -->
        <section class="kpi-section">
            <div class="kpi-grid">
                {kpi_cards}
            </div>
        </section>

        <!-- Charts Section -->
        <section class="charts-section">
            <h2 class="section-title">📈 Análisis Visual</h2>
            {charts_html}
        </section>

        <!-- Table Section -->
        <section class="table-section">
            <h2 class="section-title">🔍 Datos Detallados</h2>
            {table_html}
        </section>

        <!-- Footer -->
        <footer class="footer">
            <p>
                🛡️ IntelX Checker V2 • Versión {self.app_version} • 
                Generado el {timestamp} • 
                Reporte interactivo standalone
            </p>
        </footer>
    </div>

    <script>
    {charts_js}
    {table_js}
    </script>
</body>
</html>"""
        
        return html

    def _build_kpi_cards(self, analysis: Dict[str, Any]) -> str:
        """Build KPI cards HTML."""
        kpis = analysis['kpis']
        exposure = analysis['exposure_levels']
        
        cards = [
            ("📝 Total de Registros", f"{analysis['total_results']:,}", ""),
            ("📊 Fuentes Únicas", f"{analysis['unique_sources']}", ""),
            ("📄 Documentos Descargables", f"{kpis['downloadable_documents_count']}", ""),
            ("✅ Metadatos Completos", f"{kpis['complete_metadata_percentage']:.1f}%", ""),
            ("⚠️ Posibles Leaks", f"{kpis['leaks_percentage']:.1f}%", ""),
            ("🌐 Exposición Pública", f"{exposure['public']}", ""),
            ("🔍 Indexados", f"{exposure['indexed']}", ""),
            ("🔒 Sensibles", f"{exposure['sensitive']}", "")
        ]
        
        cards_html = []
        for title, value, change in cards:
            change_html = f'<div class="kpi-change {change.split()[0] if change else ""}">{change}</div>' if change else ''
            cards_html.append(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{title}</div>
                    <div class="kpi-value">{value}</div>
                    {change_html}
                </div>
            """)
        
        return '\n'.join(cards_html)


def generate_interactive_html_report(records: List[Dict[str, Any]], 
                                   output_filepath: str, 
                                   search_term: str, 
                                   app_version: str = "2.0.0") -> str:
    """
    Main function to generate an interactive HTML report.
    
    This function provides a simple interface to generate a complete
    interactive HTML report with all the requested features.
    """
    generator = InteractiveReportGenerator(app_version)
    return generator.generate_report(records, output_filepath, search_term)
