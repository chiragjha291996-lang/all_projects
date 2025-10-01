import React, { useState, useEffect } from 'react';
import CustomDropdown from './CustomDropdown';

const HealthForm = ({ 
  selectedDate, 
  onDataSaved, 
  apiBaseUrl 
}) => {
  const [formData, setFormData] = useState({
    mood: '',
    energy: '',
    waterIntake: '',
    sleepTime: '',
    wakeTime: '',
    leftBedTime: '',
    didRun: false, // Checkbox: false = unchecked, true = checked
    distance: '',
    medications: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [hasExistingData, setHasExistingData] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // Mood options
  const moodOptions = [
    { group: 'Positive Moods', value: 'Happy', text: 'Happy' },
    { group: 'Positive Moods', value: 'Joyful', text: 'Joyful' },
    { group: 'Positive Moods', value: 'Excited', text: 'Excited' },
    { group: 'Positive Moods', value: 'Content', text: 'Content' },
    { group: 'Positive Moods', value: 'Peaceful', text: 'Peaceful' },
    { group: 'Positive Moods', value: 'Grateful', text: 'Grateful' },
    { group: 'Positive Moods', value: 'Optimistic', text: 'Optimistic' },
    { group: 'Positive Moods', value: 'Confident', text: 'Confident' },
    { group: 'Positive Moods', value: 'Energetic', text: 'Energetic' },
    { group: 'Positive Moods', value: 'Motivated', text: 'Motivated' },
    { group: 'Positive Moods', value: 'Proud', text: 'Proud' },
    { group: 'Positive Moods', value: 'Amused', text: 'Amused' },
    { group: 'Neutral Moods', value: 'Calm', text: 'Calm' },
    { group: 'Neutral Moods', value: 'Neutral', text: 'Neutral' },
    { group: 'Neutral Moods', value: 'Focused', text: 'Focused' },
    { group: 'Neutral Moods', value: 'Reflective', text: 'Reflective' },
    { group: 'Neutral Moods', value: 'Balanced', text: 'Balanced' },
    { group: 'Neutral Moods', value: 'Tired', text: 'Tired' },
    { group: 'Negative Moods', value: 'Sad', text: 'Sad' },
    { group: 'Negative Moods', value: 'Anxious', text: 'Anxious' },
    { group: 'Negative Moods', value: 'Stressed', text: 'Stressed' },
    { group: 'Negative Moods', value: 'Frustrated', text: 'Frustrated' },
    { group: 'Negative Moods', value: 'Angry', text: 'Angry' },
    { group: 'Negative Moods', value: 'Worried', text: 'Worried' },
    { group: 'Negative Moods', value: 'Overwhelmed', text: 'Overwhelmed' },
    { group: 'Negative Moods', value: 'Lonely', text: 'Lonely' },
    { group: 'Negative Moods', value: 'Disappointed', text: 'Disappointed' },
    { group: 'Negative Moods', value: 'Irritated', text: 'Irritated' },
    { group: 'Negative Moods', value: 'Confused', text: 'Confused' },
    { group: 'Negative Moods', value: 'Restless', text: 'Restless' }
  ];

  // Energy options
  const energyOptions = [
    { group: 'High Energy', value: 'Very High', text: 'Very High' },
    { group: 'High Energy', value: 'High', text: 'High' },
    { group: 'High Energy', value: 'Energetic', text: 'Energetic' },
    { group: 'High Energy', value: 'Vibrant', text: 'Vibrant' },
    { group: 'High Energy', value: 'Peppy', text: 'Peppy' },
    { group: 'High Energy', value: 'Bursting', text: 'Bursting' },
    { group: 'Moderate Energy', value: 'Moderate', text: 'Moderate' },
    { group: 'Moderate Energy', value: 'Steady', text: 'Steady' },
    { group: 'Moderate Energy', value: 'Balanced', text: 'Balanced' },
    { group: 'Moderate Energy', value: 'Normal', text: 'Normal' },
    { group: 'Moderate Energy', value: 'Stable', text: 'Stable' },
    { group: 'Moderate Energy', value: 'Comfortable', text: 'Comfortable' },
    { group: 'Low Energy', value: 'Low', text: 'Low' },
    { group: 'Low Energy', value: 'Tired', text: 'Tired' },
    { group: 'Low Energy', value: 'Drained', text: 'Drained' },
    { group: 'Low Energy', value: 'Sluggish', text: 'Sluggish' },
    { group: 'Low Energy', value: 'Lethargic', text: 'Lethargic' },
    { group: 'Low Energy', value: 'Exhausted', text: 'Exhausted' },
    { group: 'Low Energy', value: 'Fatigued', text: 'Fatigued' },
    { group: 'Low Energy', value: 'Worn Out', text: 'Worn Out' },
    { group: 'Variable Energy', value: 'Up and Down', text: 'Up and Down' },
    { group: 'Variable Energy', value: 'Inconsistent', text: 'Inconsistent' },
    { group: 'Variable Energy', value: 'Fluctuating', text: 'Fluctuating' },
    { group: 'Variable Energy', value: 'Unpredictable', text: 'Unpredictable' }
  ];

  // Load existing data when component mounts or selectedDate changes
  useEffect(() => {
    if (selectedDate) {
      console.log('New date selected, loading data...');
      loadExistingData();
    }
  }, [selectedDate]);

  const loadExistingData = async () => {
    const dateString = selectedDate.toISOString().split('T')[0];
    console.log('Checking database for date:', dateString);
    
    try {
      const response = await fetch(`${apiBaseUrl}/health-data/${dateString}`);
      console.log('API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        
        if (hasActualData(data)) {
          // DATA EXISTS: Prepopulate form + Show Edit button (form disabled)
          console.log('Data exists - prepopulating form and showing Edit button');
          const formattedData = formatApiData(data);
          setFormData(formattedData);
          setHasExistingData(true);
          setIsEditing(false); // Form is disabled, Edit button shown
          setMessage('');
        } else {
          // NO DATA: Keep form editable + No Edit button (form enabled)
          console.log('No data exists - keeping form editable');
          setFormData({
            mood: '',
            energy: '',
            waterIntake: '',
            sleepTime: '',
            wakeTime: '',
            leftBedTime: '',
            didRun: false,
            distance: '',
            medications: []
          });
          setHasExistingData(false);
          setIsEditing(true); // Form is enabled, no Edit button
          setMessage('');
        }
      }
    } catch (error) {
      console.error('Error loading health data:', error);
      setMessage('Error loading data from server');
      // On error, assume no data and make form editable
      setFormData({
        mood: '',
        energy: '',
        waterIntake: '',
        sleepTime: '',
        wakeTime: '',
        leftBedTime: '',
        didRun: false,
        distance: '',
        medications: []
      });
      setHasExistingData(false);
      setIsEditing(true);
    }
  };

  const isSameDate = (date1, date2) => {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  };

  const formatApiData = (apiData) => {
    return {
      mood: apiData.mood || '',
      energy: apiData.energy_level || '',
      waterIntake: apiData.water_intake || '',
      sleepTime: apiData.sleep_time || '',
      wakeTime: apiData.wake_time || '',
      leftBedTime: apiData.left_bed_time || '',
      didRun: apiData.did_run || false,
      distance: apiData.distance_km || '',
      medications: Object.keys(apiData.medications || {}).filter(med => apiData.medications[med])
    };
  };

  const hasActualData = (apiData) => {
    // Check if the response contains actual data or just default/null values
    return apiData.mood !== null || 
           apiData.energy_level !== null || 
           apiData.water_intake !== null || 
           apiData.sleep_time !== null ||
           apiData.wake_time !== null ||
           apiData.left_bed_time !== null ||
           apiData.did_run === true || 
           (apiData.distance_km !== null && apiData.distance_km !== 0) ||
           (apiData.medications && Object.values(apiData.medications).some(med => med === true));
  };

  const formatDataForAPI = (formData) => {
    return {
      mood: formData.mood,
      energy: formData.energy,
      waterIntake: formData.waterIntake,
      sleepTime: formData.sleepTime,
      wakeTime: formData.wakeTime,
      leftBedTime: formData.leftBedTime,
      didRun: formData.didRun,
      distance: formData.distance,
      medications: formData.medications
    };
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMedicationChange = (medication, checked) => {
    setFormData(prev => ({
      ...prev,
      medications: checked 
        ? [...prev.medications, medication]
        : prev.medications.filter(med => med !== medication)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDate) return;

    setIsLoading(true);
    setMessage('Saving data...');

    try {
      const dateString = selectedDate.toISOString().split('T')[0];
      const apiData = formatDataForAPI(formData);
      
      const response = await fetch(`${apiBaseUrl}/health-data/${dateString}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiData)
      });

      if (response.ok) {
        setMessage('Health data saved successfully!');
        setHasExistingData(true);
        setIsEditing(false); // Form becomes disabled, Edit button shown
        onDataSaved(dateString);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save data');
      }
    } catch (error) {
      console.error('Error saving health data:', error);
      setMessage(`Error saving data: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setFormData({
      mood: '',
      energy: '',
      waterIntake: '',
      didRun: false,
      distance: '',
      medications: []
    });
    setMessage('');
  };

  const isFuture = selectedDate > new Date();
  const isToday = isSameDate(selectedDate, new Date());

  if (isFuture) {
    return (
      <div className="tracking-form">
        <div className="selected-date-info">
          <h3>Cannot enter data for future dates</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="tracking-form">
      <form onSubmit={handleSubmit}>
        {message && (
          <div className={`message ${message.includes('Error') ? 'error-message' : 'success-message'}`}>
            {message}
          </div>
        )}

        {/* Mood Tracker */}
        <div className="form-group">
          <label>How was your mood today?</label>
          <CustomDropdown
            options={moodOptions}
            value={formData.mood}
            onChange={(value) => handleInputChange('mood', value)}
            placeholder="Select your mood..."
            disabled={!isEditing}
          />
        </div>

        {/* Running Tracker */}
        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.didRun === true}
              onChange={(e) => handleInputChange('didRun', e.target.checked)}
              disabled={!isEditing}
            />
            <span>Did you run today?</span>
          </label>
          {formData.didRun && (
            <div className="form-group" style={{marginTop: '15px', marginLeft: '20px'}}>
              <label htmlFor="distance">How many km?</label>
              <input
                type="number"
                id="distance"
                value={formData.distance}
                onChange={(e) => handleInputChange('distance', e.target.value)}
                step="0.1"
                min="0"
                placeholder="e.g., 5.5"
                disabled={!isEditing}
              />
            </div>
          )}
        </div>

        {/* Medication Tracker */}
        <div className="form-group">
          <label>Did you take your meds today?</label>
          <div className="checkbox-group">
            {['thyroid', 'b12', 'finasteride'].map(med => (
              <label key={med} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.medications.includes(med)}
                  onChange={(e) => handleMedicationChange(med, e.target.checked)}
                  disabled={!isEditing}
                />
                <span>{med.charAt(0).toUpperCase() + med.slice(1)}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Water Intake */}
        <div className="form-group">
          <label>How much water did you drink today?</label>
          <div className="radio-group">
            {['<1L', '<2L', '<3L'].map(amount => (
              <label key={amount} className="radio-label">
                <input
                  type="radio"
                  name="waterIntake"
                  value={amount}
                  checked={formData.waterIntake === amount}
                  onChange={(e) => handleInputChange('waterIntake', e.target.value)}
                  disabled={!isEditing}
                />
                <span>{amount}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Sleep Tracking */}
        <div className="form-group">
          <label>🛌 Sleep Tracking</label>
          <div className="sleep-time-inputs">
            <div className="time-input-group">
              <label htmlFor="sleepTime"> Previous day's Bedtime:</label>
              <input
                id="sleepTime"
                type="time"
                value={formData.sleepTime}
                onChange={(e) => handleInputChange('sleepTime', e.target.value)}
                disabled={!isEditing}
                className="time-input"
              />
            </div>
            <div className="time-input-group">
              <label htmlFor="wakeTime">Today's Wake Time:</label>
              <input
                id="wakeTime"
                type="time"
                value={formData.wakeTime}
                onChange={(e) => handleInputChange('wakeTime', e.target.value)}
                disabled={!isEditing}
                className="time-input"
              />
            </div>
            <div className="time-input-group">
              <label htmlFor="leftBedTime">Left the Bed At:</label>
              <input
                id="leftBedTime"
                type="time"
                value={formData.leftBedTime}
                onChange={(e) => handleInputChange('leftBedTime', e.target.value)}
                disabled={!isEditing}
                className="time-input"
              />
            </div>
          </div>
        </div>

        {/* Energy Level */}
        <div className="form-group">
          <label>How was your energy today?</label>
          <CustomDropdown
            options={energyOptions}
            value={formData.energy}
            onChange={(value) => handleInputChange('energy', value)}
            placeholder="Select your energy level..."
            disabled={!isEditing}
          />
        </div>

        <div className="form-actions">
          {/* Debug info */}
          <div style={{fontSize: '12px', color: '#666', marginBottom: '10px', padding: '5px', background: '#f0f0f0', borderRadius: '3px'}}>
            <div>Debug: hasExistingData={hasExistingData.toString()}, isEditing={isEditing.toString()}</div>
            <div>Show Edit Button: {(hasExistingData && !isEditing).toString()}</div>
            <div>Form Fields Disabled: {(!isEditing).toString()}</div>
            <div>Selected Date: {selectedDate ? selectedDate.toISOString().split('T')[0] : 'None'}</div>
            <div>Form Data: didRun={formData.didRun.toString()}, waterIntake={formData.waterIntake || 'empty'}</div>
            <button 
              style={{marginLeft: '10px', padding: '2px 5px', fontSize: '10px'}}
              onClick={() => {
                console.log('Manual reload triggered');
                loadExistingData();
              }}
            >
              Reload Data
            </button>
            <button 
              style={{marginLeft: '5px', padding: '2px 5px', fontSize: '10px'}}
              onClick={async () => {
                const dateString = selectedDate.toISOString().split('T')[0];
                console.log('Testing API for date:', dateString);
                try {
                  const response = await fetch(`${apiBaseUrl}/health-data/${dateString}`);
                  console.log('API Response Status:', response.status);
                  if (response.ok) {
                    const data = await response.json();
                    console.log('API Response Data:', data);
                  } else {
                    console.log('API Response Error:', response.status, response.statusText);
                  }
                } catch (error) {
                  console.error('API Test Error:', error);
                }
              }}
            >
              Test API
            </button>
          </div>
          {/* Simple logic: Show Edit button if data exists and not editing, otherwise show Save/Clear buttons */}
          {hasExistingData && !isEditing ? (
            /* Show Edit button when there's existing data and not editing */
            <button 
              type="button" 
              className="edit-btn"
              onClick={() => setIsEditing(true)}
            >
              Edit
            </button>
          ) : (
            /* Show Save/Clear buttons when no data exists OR when editing existing data */
            <>
              <button 
                type="submit" 
                className="save-btn"
                disabled={isLoading}
              >
                {isLoading ? 'Saving...' : 'Save Entry'}
              </button>
              <button 
                type="button" 
                className="clear-btn"
                onClick={handleClear}
                disabled={isLoading}
              >
                Clear
              </button>
              {/* Show Cancel button only when editing existing data */}
              {hasExistingData && isEditing && (
                <button 
                  type="button" 
                  className="edit-btn cancel-btn"
                  onClick={() => {
                    setIsEditing(false);
                    // Reload the original data
                    loadExistingData();
                  }}
                >
                  Cancel
                </button>
              )}
            </>
          )}
        </div>
      </form>
    </div>
  );
};

export default HealthForm;
