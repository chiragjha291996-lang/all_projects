import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Analytics = () => {
  const [overviewData, setOverviewData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5002/api';

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Load overview data (always 30 days)
      const overviewResponse = await fetch(`${apiBaseUrl}/analytics/overview`);
      if (overviewResponse.ok) {
        const overview = await overviewResponse.json();
        setOverviewData(overview);
      }

      // Load trends data for selected period
      const trendsResponse = await fetch(`${apiBaseUrl}/analytics/trends/${selectedPeriod}`);
      if (trendsResponse.ok) {
        const trends = await trendsResponse.json();
        setTrendsData(trends);
      }
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createMoodDistributionChart = () => {
    if (!overviewData) return null;

    return {
      labels: ['Positive', 'Neutral', 'Negative'],
      datasets: [
        {
          data: [
            overviewData.mood_distribution.Positive,
            overviewData.mood_distribution.Neutral,
            overviewData.mood_distribution.Negative,
          ],
          backgroundColor: ['#4CAF50', '#FFC107', '#f44336'],
          borderWidth: 2,
          borderColor: '#fff',
        },
      ],
    };
  };

  const createEnergyDistributionChart = () => {
    if (!overviewData) return null;

    return {
      labels: ['High', 'Moderate', 'Low', 'Variable'],
      datasets: [
        {
          data: [
            overviewData.energy_distribution.High,
            overviewData.energy_distribution.Moderate,
            overviewData.energy_distribution.Low,
            overviewData.energy_distribution.Variable,
          ],
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#9966FF'],
          borderWidth: 2,
          borderColor: '#fff',
        },
      ],
    };
  };

  const createMedicationComplianceChart = () => {
    if (!overviewData) return null;

    return {
      labels: ['Thyroid', 'B12', 'Finasteride'],
      datasets: [
        {
          label: 'Compliance %',
          data: [
            overviewData.medication_compliance.thyroid,
            overviewData.medication_compliance.b12,
            overviewData.medication_compliance.finasteride,
          ],
          backgroundColor: ['#4CAF50', '#2196F3', '#FF9800'],
          borderColor: ['#45a049', '#1976D2', '#F57C00'],
          borderWidth: 1,
        },
      ],
    };
  };

  const createRunningTrendsChart = () => {
    if (!trendsData || !trendsData.daily_data) return null;

    const dates = Object.keys(trendsData.daily_data).sort();
    const distances = dates.map(date => trendsData.daily_data[date].distance || 0);

    return {
      labels: dates.map(date => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
      datasets: [
        {
          label: 'Distance (km)',
          data: distances,
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true,
        },
      ],
    };
  };

  const createWakeLeftBedDeviationChart = () => {
    if (!trendsData || !trendsData.daily_data) return null;

    const dates = Object.keys(trendsData.daily_data).sort();
    const deviations = [];
    
    dates.forEach(date => {
      const dayData = trendsData.daily_data[date];
      if (dayData.wake_time && dayData.left_bed_time) {
        const wakeTime = new Date(`2000-01-01T${dayData.wake_time}:00`);
        const leftBedTime = new Date(`2000-01-01T${dayData.left_bed_time}:00`);
        
        // Calculate difference in minutes
        let diffMinutes = (leftBedTime - wakeTime) / (1000 * 60);
        
        // Handle next day scenario
        if (diffMinutes < 0) {
          diffMinutes += 24 * 60;
        }
        
        deviations.push(diffMinutes);
      } else {
        deviations.push(null);
      }
    });

    return {
      labels: dates.map(date => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
      datasets: [
        {
          label: 'Time in Bed After Wake (minutes)',
          data: deviations,
          borderColor: '#FF6384',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          tension: 0.4,
          fill: true,
          spanGaps: false,
        },
      ],
    };
  };

  const createBedtimeTrackingChart = () => {
    if (!trendsData || !trendsData.daily_data) return null;

    const dates = Object.keys(trendsData.daily_data).sort();
    const bedtimes = [];
    const bedtimeMinutes = [];
    
    dates.forEach(date => {
      const dayData = trendsData.daily_data[date];
      if (dayData.sleep_time) {
        const [hours, minutes] = dayData.sleep_time.split(':').map(Number);
        let totalMinutes = hours * 60 + minutes;
        
        // Convert late night/early morning bedtimes to a continuous scale
        // If bedtime is between 00:00-06:00, treat as late night (add 24 hours)
        if (hours >= 0 && hours < 6) {
          totalMinutes += 24 * 60; // Add 24 hours for late night
        }
        
        bedtimes.push(totalMinutes);
        bedtimeMinutes.push(totalMinutes);
      } else {
        bedtimes.push(null);
      }
    });

    // Calculate average bedtime for deviation
    const validBedtimes = bedtimeMinutes.filter(time => time !== null);
    const avgBedtime = validBedtimes.length > 0 ? 
      validBedtimes.reduce((sum, time) => sum + time, 0) / validBedtimes.length : 0;

    return {
      labels: dates.map(date => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
      datasets: [
        {
          label: 'Bedtime',
          data: bedtimes.map(time => {
            if (time === null) return null;
            // Convert back to hours for display
            return time / 60;
          }),
          borderColor: '#9966FF',
          backgroundColor: 'rgba(153, 102, 255, 0.1)',
          tension: 0.4,
          fill: true,
          spanGaps: false,
        },
      ],
      avgBedtime: avgBedtime,
      bedtimeMinutes: bedtimeMinutes,
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  const barChartOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          },
        },
      },
    },
  };

  const runningChartOptions = {
    ...chartOptions,
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date',
        },
      },
      y: {
        type: 'linear',
        display: true,
        title: {
          display: true,
          text: 'Distance (km)',
        },
        beginAtZero: true,
      },
    },
  };

  const sleepDeviationOptions = {
    ...chartOptions,
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date',
        },
      },
      y: {
        type: 'linear',
        display: true,
        title: {
          display: true,
          text: 'Minutes in Bed After Wake',
        },
        beginAtZero: true,
      },
    },
  };

  const bedtimeChartOptions = {
    ...chartOptions,
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date',
        },
      },
      y: {
        type: 'linear',
        display: true,
        title: {
          display: true,
          text: 'Bedtime',
        },
        min: 20,
        max: 27,
        ticks: {
          callback: function(value) {
            const hour = Math.floor(value);
            const minute = Math.round((value - hour) * 60);
            const displayHour = hour >= 24 ? hour - 24 : hour;
            return `${displayHour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
          },
        },
      },
    },
  };

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h2>📊 Health Analytics Dashboard</h2>
        <div className="period-selector">
          <label>Trend Period: </label>
          <select 
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(parseInt(e.target.value))}
            className="period-dropdown"
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 2 weeks</option>
            <option value={30}>Last 30 days</option>
            <option value={60}>Last 2 months</option>
            <option value={90}>Last 3 months</option>
          </select>
        </div>
      </div>

      {overviewData && (
        <>
          {/* Summary Cards */}
          <div className="summary-cards">
            <div className="summary-card">
              <div className="card-icon">📅</div>
              <div className="card-content">
                <h3>{overviewData.total_entries}</h3>
                <p>Total Entries (30 days)</p>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="card-icon">🏃</div>
              <div className="card-content">
                <h3>{overviewData.running_stats.running_percentage}%</h3>
                <p>Running Days</p>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="card-icon">📏</div>
              <div className="card-content">
                <h3>{overviewData.running_stats.total_distance} km</h3>
                <p>Total Distance</p>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="card-icon">💧</div>
              <div className="card-content">
                <h3>{overviewData.water_intake.avg_daily_intake}L</h3>
                <p>Avg Daily Water</p>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="card-icon">😴</div>
              <div className="card-content">
                <h3>{overviewData.sleep_stats ? overviewData.sleep_stats.avg_sleep_hours : 0}h</h3>
                <p>Avg Sleep Hours</p>
              </div>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="charts-grid">
            {/* Mood Distribution */}
            <div className="chart-container">
              <h3>Mood Distribution (30 days)</h3>
              <div className="chart-wrapper">
                <Doughnut data={createMoodDistributionChart()} options={chartOptions} />
              </div>
            </div>

            {/* Energy Distribution */}
            <div className="chart-container">
              <h3>Energy Levels (30 days)</h3>
              <div className="chart-wrapper">
                <Doughnut data={createEnergyDistributionChart()} options={chartOptions} />
              </div>
            </div>

            {/* Medication Compliance */}
            <div className="chart-container">
              <h3>Medication Compliance (30 days)</h3>
              <div className="chart-wrapper">
                <Bar data={createMedicationComplianceChart()} options={barChartOptions} />
              </div>
            </div>

            {/* Running Trends */}
            <div className="chart-container">
              <h3>Running Distance Trends ({selectedPeriod} days)</h3>
              <div className="chart-wrapper">
                {trendsData && (
                  <Line data={createRunningTrendsChart()} options={runningChartOptions} />
                )}
              </div>
            </div>

            {/* Wake to Left Bed Deviation */}
            <div className="chart-container">
              <h3>Time in Bed After Waking ({selectedPeriod} days)</h3>
              <div className="chart-wrapper">
                {trendsData && (
                  <Line data={createWakeLeftBedDeviationChart()} options={sleepDeviationOptions} />
                )}
              </div>
            </div>

            {/* Bedtime Tracking */}
            <div className="chart-container wide">
              <h3>Bedtime Tracking & Consistency ({selectedPeriod} days)</h3>
              <div className="chart-wrapper">
                {trendsData && (
                  <Line data={createBedtimeTrackingChart()} options={bedtimeChartOptions} />
                )}
              </div>
            </div>
          </div>

          {/* Additional Stats */}
          <div className="additional-stats">
            <div className="stat-group">
              <h3>🏃 Running Statistics</h3>
              <div className="stat-items">
                <div className="stat-item">
                  <span className="stat-label">Total Runs:</span>
                  <span className="stat-value">{overviewData.running_stats.total_runs}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Average Distance:</span>
                  <span className="stat-value">{overviewData.running_stats.avg_distance_per_run} km</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Running Days:</span>
                  <span className="stat-value">{overviewData.running_stats.running_days}</span>
                </div>
              </div>
            </div>

            <div className="stat-group">
              <h3>💊 Medication Tracking</h3>
              <div className="stat-items">
                <div className="stat-item">
                  <span className="stat-label">Thyroid:</span>
                  <span className="stat-value">{overviewData.medication_compliance.thyroid}%</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">B12:</span>
                  <span className="stat-value">{overviewData.medication_compliance.b12}%</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Finasteride:</span>
                  <span className="stat-value">{overviewData.medication_compliance.finasteride}%</span>
                </div>
              </div>
            </div>

            {overviewData.sleep_stats && (
              <div className="stat-group">
                <h3>😴 Sleep Tracking</h3>
                <div className="stat-items">
                  <div className="stat-item">
                    <span className="stat-label">Average Sleep:</span>
                    <span className="stat-value">{overviewData.sleep_stats.avg_sleep_hours}h</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Days Tracked:</span>
                    <span className="stat-value">{overviewData.sleep_stats.sleep_days_tracked}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Total Sleep Hours:</span>
                    <span className="stat-value">{overviewData.sleep_stats.total_sleep_hours}h</span>
                  </div>
                  {overviewData.sleep_stats.left_bed_days_tracked > 0 && (
                    <div className="stat-item">
                      <span className="stat-label">Avg Time in Bed After Wake:</span>
                      <span className="stat-value">{overviewData.sleep_stats.avg_time_in_bed_after_wake_minutes} min</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Bedtime Consistency Stats */}
            {trendsData && (() => {
              const bedtimeChart = createBedtimeTrackingChart();
              if (!bedtimeChart || !bedtimeChart.bedtimeMinutes || bedtimeChart.bedtimeMinutes.length === 0) return null;
              
              const avgBedtime = bedtimeChart.avgBedtime;
              const avgHour = Math.floor(avgBedtime / 60);
              const avgMinute = Math.round(avgBedtime % 60);
              const displayHour = avgHour > 24 ? avgHour - 24 : avgHour;
              
              // Calculate standard deviation
              const validBedtimes = bedtimeChart.bedtimeMinutes;
              const variance = validBedtimes.reduce((sum, time) => sum + Math.pow(time - avgBedtime, 2), 0) / validBedtimes.length;
              const stdDev = Math.sqrt(variance);
              const stdDevHours = (stdDev / 60).toFixed(1);
              
              return (
                <div className="stat-group">
                  <h3>🕐 Bedtime Consistency</h3>
                  <div className="stat-items">
                    <div className="stat-item">
                      <span className="stat-label">Average Bedtime:</span>
                      <span className="stat-value">
                        {displayHour.toString().padStart(2, '0')}:{avgMinute.toString().padStart(2, '0')}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Bedtime Deviation:</span>
                      <span className="stat-value">±{stdDevHours}h</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Bedtime Days Tracked:</span>
                      <span className="stat-value">{validBedtimes.length}</span>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </>
      )}
    </div>
  );
};

export default Analytics;
