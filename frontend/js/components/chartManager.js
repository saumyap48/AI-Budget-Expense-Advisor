export class ChartManager {
  constructor() {
    this.pieChart = null;
    this.barChart = null;
    this.lineChart = null;
  }

  initPieChart(canvasId, categories = []) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    if (this.pieChart) this.pieChart.destroy();

    const labels = categories.map(c => c.category);
    const data = categories.map(c => c.total_amount);

    const colors = [
      '#6366f1', '#a855f7', '#ec4899', '#3b82f6',
      '#10b981', '#f59e0b', '#ef4444', '#14b8a6', '#8b5cf6'
    ];

    this.pieChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels.length ? labels : ['No Data'],
        datasets: [{
          data: data.length ? data : [1],
          backgroundColor: data.length ? colors.slice(0, data.length) : ['#334155'],
          borderWidth: 2,
          borderColor: '#1e293b'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } }
          }
        },
        cutout: '70%'
      }
    });
  }

  initLineChart(canvasId, dailyTrend = []) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    if (this.lineChart) this.lineChart.destroy();

    const labels = dailyTrend.map(d => d.period);
    const data = dailyTrend.map(d => d.amount);

    this.lineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels.length ? labels : ['Today'],
        datasets: [{
          label: 'Daily Spending ($)',
          data: data.length ? data : [0],
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99, 102, 241, 0.15)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#6366f1'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8' }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8' }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  updateCharts(analyticsData) {
    if (!analyticsData) return;
    this.initPieChart('categoryPieChart', analyticsData.category_breakdown || []);
    this.initLineChart('dailyLineChart', analyticsData.daily_trend || []);
  }
}

export const chartManager = new ChartManager();
