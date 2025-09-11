
        // Chart configuration
        Chart.defaults.font.family = "'Segoe UI', 'SF Pro Display', system-ui, sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#64748b';

        const chartColors = [
            '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
            '#06b6d4', '#f97316', '#84cc16', '#ef4444', '#6b7280'
        ];

        const chartData = {"dataTypes": {"labels": ["Documento", "IP", "C\u00f3digo", "Otro", "Email", "Otros"], "values": [171, 91, 29, 22, 20, 1]}, "media": {"labels": ["Text File", "Source Code", "PDF Document", "Word Document", "Paste Document"], "values": [280, 51, 1, 1, 1]}, "sources": {"labels": ["leaks.logs", "leaks.private.general", "leaks.public.general", "dns", "pastes"], "values": [198, 132, 2, 1, 1]}, "temporal": {"labels": ["2024-10", "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09"], "values": [7, 7, 7, 25, 10, 20, 11, 5, 10, 6, 9, 8]}, "kpis": {"leaks_percentage": 99.7005988023952, "complete_metadata_percentage": 100.0, "downloadable_documents_count": 333}, "exposure": {"public": 0, "indexed": 0, "sensitive": 22}};

        function createChart(canvasId, type, data, options = {}) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            return new Chart(ctx, {
                type: type,
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 12,
                                padding: 15,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#6366f1',
                            borderWidth: 1
                        }
                    },
                    ...options
                }
            });
        }

        function initializeCharts() {
            // Data Types Chart (Doughnut)
            createChart('dataTypesChart', 'doughnut', {
                labels: chartData.dataTypes.labels,
                datasets: [{
                    data: chartData.dataTypes.values,
                    backgroundColor: chartColors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            }, {
                cutout: '60%'
            });

            // Media Chart (Pie)
            createChart('mediaChart', 'pie', {
                labels: chartData.media.labels,
                datasets: [{
                    data: chartData.media.values,
                    backgroundColor: chartColors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            });

            // Sources Chart (Bar)
            createChart('sourcesChart', 'bar', {
                labels: chartData.sources.labels,
                datasets: [{
                    label: 'Registros',
                    data: chartData.sources.values,
                    backgroundColor: '#6366f1',
                    borderColor: '#4f46e5',
                    borderWidth: 1
                }]
            }, {
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        },
                        grid: {
                            color: '#f1f5f9'
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45
                        }
                    }
                }
            });

            // Temporal Chart (Line)
            createChart('temporalChart', 'line', {
                labels: chartData.temporal.labels,
                datasets: [{
                    label: 'Registros por Mes',
                    data: chartData.temporal.values,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            }, {
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        },
                        grid: {
                            color: '#f1f5f9'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            });
        }

        // Initialize charts when DOM is ready
        document.addEventListener('DOMContentLoaded', initializeCharts);
        