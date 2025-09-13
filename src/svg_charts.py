"""
SVG Chart Generator - Generador de gráficos SVG puros sin dependencias JavaScript
"""

import math
from typing import List, Dict, Any, Tuple
import json


class SVGChartGenerator:
    """Generador de gráficos SVG puros sin dependencias externas."""
    
    def __init__(self, width: int = 500, height: int = 400):
        self.width = width
        self.height = height
        self.colors = [
            '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
            '#06b6d4', '#f97316', '#84cc16', '#ef4444', '#6b7280'
        ]
    
    def create_donut_chart(self, labels: List[str], values: List[int], title: str = "") -> str:
        """Crea un gráfico de donut en SVG."""
        if not values or sum(values) == 0:
            return self._create_empty_chart(title, "No hay datos disponibles")
        
        total = sum(values)
        cx, cy = self.width // 2, self.height // 2
        outer_radius = min(cx, cy) - 40
        inner_radius = outer_radius * 0.6
        
        svg_parts = [
            f'<svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '.chart-text { font-family: "Segoe UI", Arial, sans-serif; font-size: 11px; fill: #374151; }',
            '.chart-title { font-family: "Segoe UI", Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #1f2937; }',
            '.legend-text { font-family: "Segoe UI", Arial, sans-serif; font-size: 11px; fill: #6b7280; }',
            '.slice:hover { opacity: 0.8; cursor: pointer; }',
            '</style>'
        ]
        
        if title:
            svg_parts.append(f'<text x="{self.width//2}" y="20" text-anchor="middle" class="chart-title">{title}</text>')
        
        # Crear segmentos del donut
        start_angle = -90  # Empezar desde arriba
        for i, (label, value) in enumerate(zip(labels, values)):
            if value <= 0:
                continue
                
            angle = (value / total) * 360
            end_angle = start_angle + angle
            
            # Calcular coordenadas del arco
            large_arc = 1 if angle > 180 else 0
            
            # Puntos del arco exterior
            x1_outer = cx + outer_radius * math.cos(math.radians(start_angle))
            y1_outer = cy + outer_radius * math.sin(math.radians(start_angle))
            x2_outer = cx + outer_radius * math.cos(math.radians(end_angle))
            y2_outer = cy + outer_radius * math.sin(math.radians(end_angle))
            
            # Puntos del arco interior
            x1_inner = cx + inner_radius * math.cos(math.radians(start_angle))
            y1_inner = cy + inner_radius * math.sin(math.radians(start_angle))
            x2_inner = cx + inner_radius * math.cos(math.radians(end_angle))
            y2_inner = cy + inner_radius * math.sin(math.radians(end_angle))
            
            # Path del segmento
            path = f"""M {x1_outer} {y1_outer}
                      A {outer_radius} {outer_radius} 0 {large_arc} 1 {x2_outer} {y2_outer}
                      L {x2_inner} {y2_inner}
                      A {inner_radius} {inner_radius} 0 {large_arc} 0 {x1_inner} {y1_inner}
                      Z"""
            
            color = self.colors[i % len(self.colors)]
            percentage = (value / total) * 100
            
            svg_parts.append(f'''
            <path d="{path}" fill="{color}" class="slice">
                <title>{label}: {value} ({percentage:.1f}%)</title>
            </path>''')
            
            start_angle = end_angle
        
        # Agregar leyenda
        legend_y = self.height - 120
        cols = 1 if len(labels) > 4 else 2
        col_width = self.width // cols
        
        for i, (label, value) in enumerate(zip(labels, values)):
            if value <= 0:
                continue
                
            col = i % cols
            row = i // cols
            x = 20 + col * col_width
            y = legend_y + row * 22
            
            color = self.colors[i % len(self.colors)]
            percentage = (value / total) * 100
            
            # Truncar etiquetas largas
            display_label = label[:30] + "..." if len(label) > 30 else label
            
            svg_parts.extend([
                f'<rect x="{x}" y="{y-8}" width="12" height="12" fill="{color}"/>',
                f'<text x="{x+18}" y="{y+1}" class="legend-text">{display_label}: {value} ({percentage:.1f}%)</text>'
            ])
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    
    def create_bar_chart(self, labels: List[str], values: List[int], title: str = "") -> str:
        """Crea un gráfico de barras en SVG."""
        if not values or max(values) == 0:
            return self._create_empty_chart(title, "No hay datos disponibles")
        
        margin = 60
        chart_width = self.width - 2 * margin
        chart_height = self.height - 2 * margin - 40  # Extra espacio para título
        
        max_value = max(values)
        bar_width = chart_width / len(values) * 0.8
        bar_spacing = chart_width / len(values)
        
        svg_parts = [
            f'<svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '.chart-text { font-family: "Segoe UI", Arial, sans-serif; font-size: 11px; fill: #374151; }',
            '.chart-title { font-family: "Segoe UI", Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #1f2937; }',
            '.axis-line { stroke: #e5e7eb; stroke-width: 1; }',
            '.bar:hover { opacity: 0.8; cursor: pointer; }',
            '</style>'
        ]
        
        if title:
            svg_parts.append(f'<text x="{self.width//2}" y="25" text-anchor="middle" class="chart-title">{title}</text>')
        
        chart_top = 40 if title else 20
        
        # Líneas de la cuadrícula
        for i in range(0, 6):
            y = chart_top + margin + (chart_height * i / 5)
            grid_value = max_value * (5 - i) / 5
            svg_parts.extend([
                f'<line x1="{margin}" y1="{y}" x2="{self.width - margin}" y2="{y}" class="axis-line"/>',
                f'<text x="{margin - 10}" y="{y + 4}" text-anchor="end" class="chart-text">{int(grid_value)}</text>'
            ])
        
        # Barras
        for i, (label, value) in enumerate(zip(labels, values)):
            if value < 0:
                continue
                
            x = margin + i * bar_spacing + (bar_spacing - bar_width) / 2
            bar_height = (value / max_value) * chart_height
            y = chart_top + margin + chart_height - bar_height
            
            color = self.colors[0]  # Color principal para barras
            
            svg_parts.append(f'''
            <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" class="bar">
                <title>{label}: {value}</title>
            </rect>''')
            
            # Etiquetas del eje X
            label_x = x + bar_width / 2
            label_y = chart_top + margin + chart_height + 20
            
            # Rotar etiquetas si son muy largas para evitar superposición
            if len(label) > 8:
                truncated_label = label[:8] + "..."
                svg_parts.append(f'''
                <text x="{label_x}" y="{label_y}" text-anchor="middle" class="chart-text" 
                      transform="rotate(-45, {label_x}, {label_y})">{truncated_label}</text>''')
            else:
                svg_parts.append(f'<text x="{label_x}" y="{label_y}" text-anchor="middle" class="chart-text">{label}</text>')
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    
    def create_line_chart(self, labels: List[str], values: List[int], title: str = "") -> str:
        """Crea un gráfico de líneas en SVG."""
        if not values or len(values) < 2:
            return self._create_empty_chart(title, "Datos insuficientes para gráfico de líneas")
        
        margin = 60
        chart_width = self.width - 2 * margin
        chart_height = self.height - 2 * margin - 40
        
        max_value = max(values) if values else 1
        min_value = min(values) if values else 0
        value_range = max_value - min_value if max_value != min_value else 1
        
        svg_parts = [
            f'<svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '.chart-text { font-family: "Segoe UI", Arial, sans-serif; font-size: 11px; fill: #374151; }',
            '.chart-title { font-family: "Segoe UI", Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #1f2937; }',
            '.axis-line { stroke: #e5e7eb; stroke-width: 1; }',
            '.line-path { fill: none; stroke: #6366f1; stroke-width: 3; }',
            '.point { fill: #6366f1; stroke: #ffffff; stroke-width: 2; }',
            '.point:hover { r: 6; cursor: pointer; }',
            '</style>'
        ]
        
        if title:
            svg_parts.append(f'<text x="{self.width//2}" y="25" text-anchor="middle" class="chart-title">{title}</text>')
        
        chart_top = 40 if title else 20
        
        # Líneas de la cuadrícula
        for i in range(0, 6):
            y = chart_top + margin + (chart_height * i / 5)
            grid_value = max_value - (value_range * i / 5)
            svg_parts.extend([
                f'<line x1="{margin}" y1="{y}" x2="{self.width - margin}" y2="{y}" class="axis-line"/>',
                f'<text x="{margin - 10}" y="{y + 4}" text-anchor="end" class="chart-text">{int(grid_value)}</text>'
            ])
        
        # Crear puntos y línea
        points = []
        point_width = chart_width / (len(values) - 1) if len(values) > 1 else chart_width
        
        for i, (label, value) in enumerate(zip(labels, values)):
            x = margin + i * point_width
            y = chart_top + margin + chart_height - ((value - min_value) / value_range) * chart_height
            points.append((x, y))
            
            # Punto
            svg_parts.append(f'''
            <circle cx="{x}" cy="{y}" r="4" class="point">
                <title>{label}: {value}</title>
            </circle>''')
            
            # Etiqueta del eje X (cada 2 puntos para evitar solapamiento)
            if i % max(1, len(values) // 8) == 0 or i == len(values) - 1:
                label_y = chart_top + margin + chart_height + 20
                # Truncar etiquetas para fechas
                display_label = label[:7] if len(label) > 7 else label  # Formato YYYY-MM
                svg_parts.append(f'<text x="{x}" y="{label_y}" text-anchor="middle" class="chart-text">{display_label}</text>')
        
        # Línea conectando puntos
        if len(points) >= 2:
            path_data = f"M {points[0][0]} {points[0][1]}"
            for x, y in points[1:]:
                path_data += f" L {x} {y}"
            svg_parts.append(f'<path d="{path_data}" class="line-path"/>')
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    
    def _create_empty_chart(self, title: str, message: str) -> str:
        """Crea un gráfico vacío con mensaje."""
        return f'''
        <svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">
            <style>
                .chart-title {{ font-family: "Segoe UI", Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #1f2937; }}
                .empty-message {{ font-family: "Segoe UI", Arial, sans-serif; font-size: 12px; fill: #6b7280; }}
            </style>
            <rect width="{self.width}" height="{self.height}" fill="#f9fafb" stroke="#e5e7eb"/>
            {f'<text x="{self.width//2}" y="30" text-anchor="middle" class="chart-title">{title}</text>' if title else ''}
            <text x="{self.width//2}" y="{self.height//2}" text-anchor="middle" class="empty-message">{message}</text>
        </svg>'''


class SVGVisualizationGenerator:
    """Generador de visualizaciones usando SVG puro."""
    
    def __init__(self):
        self.chart_generator = SVGChartGenerator()
    
    def generate_charts_html(self, chart_data: Dict[str, Any]) -> str:
        """Genera HTML con gráficos SVG."""
        
        # Gráfico de tipos de datos (donut)
        data_types_svg = self.chart_generator.create_donut_chart(
            labels=chart_data.get('dataTypes', {}).get('labels', []),
            values=chart_data.get('dataTypes', {}).get('values', []),
            title="Distribución por Tipo de Dato"
        )
        
        # Gráfico de fuentes (barras)
        sources_svg = self.chart_generator.create_bar_chart(
            labels=chart_data.get('sources', {}).get('labels', []),
            values=chart_data.get('sources', {}).get('values', []),
            title="Fuentes Principales"
        )
        
        # Gráfico temporal (líneas) - tamaño extra grande
        self.chart_generator.width = 1000  # Aumentar más el ancho para temporal
        self.chart_generator.height = 450   # Aumentar más la altura para temporal
        temporal_svg = self.chart_generator.create_line_chart(
            labels=chart_data.get('temporal', {}).get('labels', []),
            values=chart_data.get('temporal', {}).get('values', []),
            title="Evolución Temporal (Últimos 5 Años)"
        )
        # Restaurar tamaño normal (ahora más grande)
        self.chart_generator.width = 500
        self.chart_generator.height = 400
        
        return f"""
        <div class="charts-container">
            <div class="chart-grid-three">
                <div class="chart-card">
                    {data_types_svg}
                </div>
                <div class="chart-card">
                    {sources_svg}
                </div>
            </div>
            <div class="chart-card chart-wide">
                {temporal_svg}
            </div>
        </div>
        """
    
    def generate_charts_js(self, chart_data: Dict[str, Any]) -> str:
        """Genera JavaScript mínimo para interactividad SVG."""
        return """
        // Interactividad básica para gráficos SVG
        document.addEventListener('DOMContentLoaded', function() {
            console.log('SVG charts loaded');
            
            // Agregar efectos hover mejorados
            const svgElements = document.querySelectorAll('svg');
            svgElements.forEach(svg => {
                svg.style.transition = 'transform 0.2s ease';
            });
            
            // Log para debugging
            console.log('SVG charts initialized successfully');
        });
        """
