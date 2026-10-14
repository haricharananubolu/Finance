/**
 * ALTO - Dashboard Chart.js Visualizations
 * Initializes responsive financial charts with custom tooltips and styling.
 */

function initDashboardCharts(trendData, categoryData, currencySymbol) {
  Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  Chart.defaults.color = '#64748b';

  // 1. Monthly Income vs Expenses Trend Chart
  const trendCanvas = document.getElementById('trendChart');
  if (trendCanvas && trendData) {
    new Chart(trendCanvas, {
      type: 'bar',
      data: {
        labels: trendData.labels,
        datasets: [
          {
            label: 'Income',
            data: trendData.income,
            backgroundColor: 'rgba(16, 185, 129, 0.85)',
            hoverBackgroundColor: '#10b981',
            borderRadius: 6,
            borderSkipped: false
          },
          {
            label: 'Expenses',
            data: trendData.expenses,
            backgroundColor: 'rgba(239, 68, 68, 0.85)',
            hoverBackgroundColor: '#ef4444',
            borderRadius: 6,
            borderSkipped: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              boxWidth: 12,
              boxHeight: 12,
              useBorderRadius: true,
              borderRadius: 3,
              font: { weight: '600', size: 12 }
            }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            titleFont: { size: 13, weight: '700' },
            bodyFont: { size: 13 },
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                return ` ${context.dataset.label}: ${currencySymbol} ${context.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false }
          },
          y: {
            grid: { color: '#f1f5f9' },
            ticks: {
              callback: function(value) {
                return `${currencySymbol} ${value.toLocaleString()}`;
              }
            }
          }
        }
      }
    });
  }

  // 2. Category Expense Breakdown Doughnut Chart
  const categoryCanvas = document.getElementById('categoryChart');
  if (categoryCanvas && categoryData && categoryData.labels.length > 0) {
    const palette = [
      '#0284c7', '#0d9488', '#f59e0b', '#8b5cf6',
      '#ec4899', '#06b6d4', '#84cc16', '#f97316',
      '#6366f1', '#14b8a6', '#64748b'
    ];

    new Chart(categoryCanvas, {
      type: 'doughnut',
      data: {
        labels: categoryData.labels,
        datasets: [{
          data: categoryData.values,
          backgroundColor: palette.slice(0, categoryData.labels.length),
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 10,
              boxHeight: 10,
              useBorderRadius: true,
              borderRadius: 2,
              padding: 14,
              font: { size: 11, weight: '500' }
            }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const val = context.parsed;
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${currencySymbol} ${val.toLocaleString(undefined, { minimumFractionDigits: 2 })} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }
}
