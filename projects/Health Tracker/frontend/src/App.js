import React, { useState, useEffect } from 'react';
import Calendar from './components/Calendar';
import HealthForm from './components/HealthForm';
import Analytics from './components/Analytics';
import './styles.css';

const API_BASE_URL = 'http://localhost:5002/api';

function App() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [calendarData, setCalendarData] = useState(new Map());
  const [activeTab, setActiveTab] = useState('tracking');

  // Load calendar data on component mount
  useEffect(() => {
    loadCalendarData();
  }, [currentDate]);

  const loadCalendarData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health-data/dates-with-data`);
      if (response.ok) {
        const data = await response.json();
        const datesWithData = new Set(data.dates);
        
        // Get current month's date range
        const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
        const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
        
        const newCalendarData = new Map();
        // Check all dates in current month
        for (let d = new Date(firstDay); d <= lastDay; d.setDate(d.getDate() + 1)) {
          const dateString = d.toISOString().split('T')[0];
          newCalendarData.set(dateString, { 
            hasData: datesWithData.has(dateString) 
          });
        }
        
        setCalendarData(newCalendarData);
      }
    } catch (error) {
      console.error('Error loading calendar data:', error);
    }
  };

  const handleDateSelect = (date) => {
    setSelectedDate(date);
  };

  const handleMonthChange = (direction) => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  const handleDataSaved = (dateString) => {
    // Update calendar data to reflect new entry
    const newCalendarData = new Map(calendarData);
    newCalendarData.set(dateString, { hasData: true });
    setCalendarData(newCalendarData);
  };

  return (
    <div className="container">
      <header>
        <h1>Health Tracker</h1>
        
        {/* Main Tab Navigation - Top Level */}
        <div className="main-tab-nav">
          <button 
            className={`main-tab-btn ${activeTab === 'tracking' ? 'active' : ''}`}
            onClick={() => setActiveTab('tracking')}
          >
            📊 Tracking
          </button>
          <button 
            className={`main-tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            📈 Analytics
          </button>
        </div>
      </header>

      {/* Tracking Tab - Contains Calendar and Form */}
      {activeTab === 'tracking' && (
        <div className="main-tab-content">
          {/* Calendar Section */}
          <section className="calendar-section">
            <div className="calendar-header">
              <button 
                className="nav-btn" 
                onClick={() => handleMonthChange('prev')}
              >
                &lt;
              </button>
              <h2>
                {currentDate.toLocaleDateString('en-US', { 
                  month: 'long', 
                  year: 'numeric' 
                })}
              </h2>
              <button 
                className="nav-btn" 
                onClick={() => handleMonthChange('next')}
              >
                &gt;
              </button>
            </div>
            <Calendar
              currentDate={currentDate}
              selectedDate={selectedDate}
              calendarData={calendarData}
              onDateSelect={handleDateSelect}
            />
          </section>

          {/* Health Form Section */}
          <section className="form-section">
            <div className="selected-date-info">
              <h3>
                {selectedDate ? 
                  `Selected: ${selectedDate.toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}` : 
                  'Select a date to track your health'
                }
              </h3>
            </div>
            
            {selectedDate && (
              <HealthForm
                selectedDate={selectedDate}
                onDataSaved={handleDataSaved}
                apiBaseUrl={API_BASE_URL}
              />
            )}
          </section>
        </div>
      )}

      {/* Analytics Tab - Standalone Analytics Dashboard */}
      {activeTab === 'analytics' && (
        <div className="main-tab-content">
          <Analytics />
        </div>
      )}
    </div>
  );
}

export default App;
