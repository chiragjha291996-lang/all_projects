class HealthTracker {
    constructor() {
        this.currentDate = new Date();
        this.selectedDate = null;
        this.calendarData = new Map(); // Store data for each date
        this.isEditing = false;
        this.apiBaseUrl = 'http://localhost:5002/api';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.renderCalendar();
        this.setupFormHandlers();
        this.setupCustomDropdowns();
        this.loadCalendarData();
    }

    setupEventListeners() {
        // Calendar navigation
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.renderCalendar();
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.renderCalendar();
        });

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Running radio button handler
        document.querySelectorAll('input[name="didRun"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const distanceInput = document.getElementById('distanceInput');
                if (e.target.value === 'yes') {
                    distanceInput.style.display = 'block';
                } else {
                    distanceInput.style.display = 'none';
                    document.getElementById('distance').value = '';
                }
            });
        });

        // Form submission
        document.getElementById('healthForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveHealthData();
        });

        // Clear form
        document.getElementById('clearForm').addEventListener('click', () => {
            this.clearForm();
        });

        // Edit button
        document.getElementById('editBtn').addEventListener('click', () => {
            this.toggleEditMode();
        });
    }

    setupCustomDropdowns() {
        // Setup mood dropdown
        this.setupDropdown('moodDropdown', 'moodSelected', 'moodOptions', 'mood');
        
        // Setup energy dropdown
        this.setupDropdown('energyDropdown', 'energySelected', 'energyOptions', 'energy');
    }

    setupDropdown(dropdownId, selectedId, optionsId, hiddenInputId) {
        const dropdown = document.getElementById(dropdownId);
        const selected = document.getElementById(selectedId);
        const options = document.getElementById(optionsId);
        const hiddenInput = document.getElementById(hiddenInputId);

        // Toggle dropdown - make entire dropdown clickable
        dropdown.addEventListener('click', (e) => {
            e.stopPropagation();
            console.log('Dropdown clicked:', dropdownId);
            if (dropdown.classList.contains('disabled')) return;
            
            // Close other dropdowns
            document.querySelectorAll('.custom-dropdown').forEach(dd => {
                if (dd !== dropdown) {
                    dd.classList.remove('open');
                }
            });
            
            dropdown.classList.toggle('open');
            console.log('Dropdown open state:', dropdown.classList.contains('open'));
        });

        // Handle option selection
        options.addEventListener('click', (e) => {
            const option = e.target.closest('.dropdown-option');
            if (!option) return;

            const value = option.dataset.value;
            const text = option.textContent;

            // Update selected text
            const textSpan = selected.querySelector('span');
            if (textSpan) {
                textSpan.textContent = text;
            } else {
                selected.textContent = text;
            }
            
            // Update hidden input
            hiddenInput.value = value;

            // Update visual selection
            options.querySelectorAll('.dropdown-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            option.classList.add('selected');

            // Close dropdown
            dropdown.classList.remove('open');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });
    }

    renderCalendar() {
        const calendar = document.getElementById('calendar');
        const currentMonth = document.getElementById('currentMonth');
        
        // Update month display
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        currentMonth.textContent = `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;

        // Clear calendar
        calendar.innerHTML = '';

        // Add day headers
        const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        dayHeaders.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day day-header';
            dayHeader.textContent = day;
            dayHeader.style.fontWeight = 'bold';
            dayHeader.style.background = '#f8f9fa';
            dayHeader.style.borderBottom = '2px solid #e0e0e0';
            calendar.appendChild(dayHeader);
        });

        // Get first day of month and number of days
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();

        // Add empty cells for days before the first day of the month
        for (let i = 0; i < startingDayOfWeek; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'calendar-day other-month';
            calendar.appendChild(emptyDay);
        }

        // Add days of the month
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            const currentDayDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), day);
            const dateString = this.formatDate(currentDayDate);
            
            dayElement.className = 'calendar-day';
            dayElement.innerHTML = `
                <div class="day-name">${dayHeaders[currentDayDate.getDay()]}</div>
                <div class="day-number">${day}</div>
            `;

            // Add classes for today, past/future
            if (this.isSameDate(currentDayDate, today)) {
                dayElement.classList.add('today');
            } else if (currentDayDate > today) {
                dayElement.classList.add('future');
            }

            // Check if this date has data and apply appropriate styling
            const isToday = this.isSameDate(currentDayDate, new Date());
            const isPast = currentDayDate < new Date();
            
            if (this.calendarData.has(dateString)) {
                const dayData = this.calendarData.get(dateString);
                if (dayData.hasData) {
                    if (isPast) {
                        dayElement.classList.add('has-data'); // Green for past dates with data
                    }
                    // Today with data stays blue (no additional class needed)
                } else {
                    if (isPast) {
                        dayElement.classList.add('no-data'); // Yellow for past dates without data
                    }
                    // Today without data stays blue (no additional class needed)
                }
            } else {
                // For dates not yet checked
                if (isPast) {
                    dayElement.classList.add('no-data'); // Default to yellow for past dates
                }
                // Today stays blue by default
            }

            // Add click handler
            dayElement.addEventListener('click', () => {
                this.selectDate(currentDayDate);
            });

            calendar.appendChild(dayElement);
        }
    }

    selectDate(date) {
        // Remove previous selection
        document.querySelectorAll('.calendar-day.selected').forEach(day => {
            day.classList.remove('selected');
        });

        // Add selection to clicked day
        event.target.closest('.calendar-day').classList.add('selected');

        this.selectedDate = date;
        const dateString = this.formatDate(date);
        
        // Update selected date display
        const selectedDateText = document.getElementById('selectedDateText');
        const isFuture = date > new Date();
        
        if (isFuture) {
            selectedDateText.textContent = `Selected: ${this.formatDateDisplay(date)} (Cannot enter data for future dates)`;
            document.getElementById('trackingForm').style.display = 'none';
        } else {
            const isToday = this.isSameDate(date, new Date());
            if (isToday) {
                selectedDateText.textContent = `Today: ${this.formatDateDisplay(date)} - Start fresh entry`;
            } else {
                selectedDateText.textContent = `Selected: ${this.formatDateDisplay(date)}`;
            }
            document.getElementById('trackingForm').style.display = 'block';
            this.loadExistingData(dateString);
        }
    }

    async loadExistingData(dateString) {
        // Check if the selected date is today
        const today = new Date();
        const selectedDate = new Date(dateString);
        const isToday = this.isSameDate(selectedDate, today);
        
        // Always try to load data from API first
        const data = await this.loadHealthData(dateString);
        
        if (data) {
            // Data exists - populate form
            this.populateForm(data);
            this.setFormReadOnly(true);
            this.isEditing = false;
            // Store in local cache
            this.calendarData.set(dateString, { ...data, hasData: true });
        } else {
            // No data exists
            this.clearForm();
            this.setFormReadOnly(false);
            this.isEditing = false;
            // Store in local cache
            this.calendarData.set(dateString, { hasData: false });
            
            if (isToday) {
                // Show special message for today when no entry exists
                const selectedDateText = document.getElementById('selectedDateText');
                selectedDateText.textContent = `Today: ${this.formatDateDisplay(selectedDate)} - Entry hasn't been made yet`;
            }
        }
    }

    populateForm(data) {
        // Populate form with existing data
        if (data.mood) {
            const moodSelected = document.getElementById('moodSelected');
            const moodHidden = document.getElementById('mood');
            const moodOption = document.querySelector(`[data-value="${data.mood}"]`);
            
            if (moodOption) {
                const textSpan = moodSelected.querySelector('span');
                if (textSpan) {
                    textSpan.textContent = moodOption.textContent;
                } else {
                    moodSelected.textContent = moodOption.textContent;
                }
                moodHidden.value = data.mood;
                
                // Update visual selection
                document.querySelectorAll('#moodOptions .dropdown-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                moodOption.classList.add('selected');
            }
        }
        
        if (data.energy) {
            const energySelected = document.getElementById('energySelected');
            const energyHidden = document.getElementById('energy');
            const energyOption = document.querySelector(`[data-value="${data.energy}"]`);
            
            if (energyOption) {
                const textSpan = energySelected.querySelector('span');
                if (textSpan) {
                    textSpan.textContent = energyOption.textContent;
                } else {
                    energySelected.textContent = energyOption.textContent;
                }
                energyHidden.value = data.energy;
                
                // Update visual selection
                document.querySelectorAll('#energyOptions .dropdown-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                energyOption.classList.add('selected');
            }
        }
        
        // Water intake
        if (data.waterIntake) {
            document.querySelector(`input[name="waterIntake"][value="${data.waterIntake}"]`).checked = true;
        }
        
        // Running data
        if (data.didRun !== undefined) {
            if (data.didRun) {
                document.getElementById('runYes').checked = true;
                document.getElementById('distanceInput').style.display = 'block';
                if (data.distance) document.getElementById('distance').value = data.distance;
            } else {
                document.getElementById('runNo').checked = true;
            }
        }
        
        // Medications
        if (data.medications) {
            data.medications.forEach(med => {
                document.getElementById(med).checked = true;
            });
        }
    }

    clearForm() {
        document.getElementById('healthForm').reset();
        document.getElementById('distanceInput').style.display = 'none';
        this.setFormReadOnly(false);
        this.isEditing = false;
    }

    setFormReadOnly(readOnly) {
        const form = document.getElementById('healthForm');
        const inputs = form.querySelectorAll('input, textarea, select');
        const buttons = form.querySelectorAll('button');
        const dropdowns = form.querySelectorAll('.custom-dropdown');
        
        inputs.forEach(input => {
            input.disabled = readOnly;
        });
        
        // Handle custom dropdowns
        dropdowns.forEach(dropdown => {
            if (readOnly) {
                dropdown.classList.add('disabled');
            } else {
                dropdown.classList.remove('disabled');
            }
        });
        
        // Update button visibility
        const saveBtn = document.getElementById('saveBtn');
        const editBtn = document.getElementById('editBtn');
        const clearBtn = document.getElementById('clearForm');
        
        if (readOnly) {
            saveBtn.style.display = 'none';
            editBtn.style.display = 'inline-block';
            clearBtn.style.display = 'none';
        } else {
            saveBtn.style.display = 'inline-block';
            editBtn.style.display = 'none';
            clearBtn.style.display = 'inline-block';
        }
    }

    toggleEditMode() {
        this.isEditing = !this.isEditing;
        this.setFormReadOnly(!this.isEditing);
        
        const editBtn = document.getElementById('editBtn');
        if (this.isEditing) {
            editBtn.textContent = 'Cancel';
            editBtn.classList.add('cancel-btn');
        } else {
            editBtn.textContent = 'Edit';
            editBtn.classList.remove('cancel-btn');
            // Reload the original data
            const dateString = this.formatDate(this.selectedDate);
            if (this.calendarData.has(dateString)) {
                const data = this.calendarData.get(dateString);
                this.populateForm(data);
            }
        }
    }

    async saveHealthData() {
        if (!this.selectedDate) {
            alert('Please select a date first');
            return;
        }

        const formData = this.collectFormData();
        const dateString = this.formatDate(this.selectedDate);
        
        // Show loading state
        this.showMessage('Saving data...', 'success');
        
        // Send to backend API
        const apiData = this.formatDataForAPI(formData);
        const success = await this.saveHealthDataToAPI(dateString, apiData);
        
        if (success) {
            // Store in local data
            this.calendarData.set(dateString, { ...formData, hasData: true });
            
            // Update calendar display
            this.renderCalendar();
            
            // Set form to read-only mode
            this.setFormReadOnly(true);
            this.isEditing = false;
            
            // Show success message
            this.showMessage('Health data saved successfully!', 'success');
        }
    }

    collectFormData() {
        const formData = {
            mood: document.getElementById('mood').value,
            energy: document.getElementById('energy').value,
            waterIntake: document.querySelector('input[name="waterIntake"]:checked')?.value,
            didRun: document.querySelector('input[name="didRun"]:checked')?.value === 'yes',
            distance: document.getElementById('distance').value || null,
            medications: Array.from(document.querySelectorAll('input[name="medications"]:checked')).map(cb => cb.value)
        };
        
        return formData;
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
    }

    showMessage(message, type) {
        // Remove existing messages
        document.querySelectorAll('.success-message, .error-message').forEach(msg => {
            msg.remove();
        });
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `${type}-message`;
        messageDiv.textContent = message;
        
        const form = document.getElementById('trackingForm');
        form.insertBefore(messageDiv, form.firstChild);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    formatDateDisplay(date) {
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        return date.toLocaleDateString('en-US', options);
    }

    isSameDate(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    // API Methods
    async loadCalendarData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health-data/dates-with-data`);
            if (response.ok) {
                const data = await response.json();
                const datesWithData = new Set(data.dates);
                
                // Get current month's date range
                const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
                const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
                
                // Check all dates in current month
                for (let d = new Date(firstDay); d <= lastDay; d.setDate(d.getDate() + 1)) {
                    const dateString = d.toISOString().split('T')[0];
                    this.calendarData.set(dateString, { 
                        hasData: datesWithData.has(dateString) 
                    });
                }
                
                this.renderCalendar();
            }
        } catch (error) {
            console.error('Error loading calendar data:', error);
            // Continue without calendar data indicators
            this.renderCalendar();
        }
    }

    async loadHealthData(dateString) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health-data/${dateString}`);
            if (response.ok) {
                const data = await response.json();
                return this.formatApiData(data);
            } else if (response.status === 404) {
                // No data exists for this date
                return null;
            }
        } catch (error) {
            console.error('Error loading health data:', error);
            this.showMessage('Error loading data from server', 'error');
        }
        return null;
    }

    async saveHealthDataToAPI(dateString, formData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health-data/${dateString}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                return true;
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to save data');
            }
        } catch (error) {
            console.error('Error saving health data:', error);
            this.showMessage(`Error saving data: ${error.message}`, 'error');
            return false;
        }
    }

    async deleteHealthDataFromAPI(dateString) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health-data/${dateString}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                return true;
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to delete data');
            }
        } catch (error) {
            console.error('Error deleting health data:', error);
            this.showMessage(`Error deleting data: ${error.message}`, 'error');
            return false;
        }
    }

    formatApiData(apiData) {
        // Convert API data format to internal format
        return {
            mood: apiData.mood,
            energy: apiData.energy_level,
            waterIntake: apiData.water_intake,
            didRun: apiData.did_run,
            distance: apiData.distance_km,
            medications: Object.keys(apiData.medications).filter(med => apiData.medications[med])
        };
    }

    formatDataForAPI(formData) {
        // Convert internal format to API format
        return {
            mood: formData.mood,
            energy: formData.energy,
            waterIntake: formData.waterIntake,
            didRun: formData.didRun,
            distance: formData.distance,
            medications: formData.medications
        };
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HealthTracker();
});
