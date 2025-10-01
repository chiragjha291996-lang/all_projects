from flask import Flask, request, jsonify
from flask_cors import CORS
from database import HealthTrackerDB
from datetime import datetime, date, timedelta
import json

app = Flask(__name__)
CORS(app, origins=['*'])  # Enable CORS for frontend communication

# Initialize database
db = HealthTrackerDB()

@app.route('/api/health-data/<date_str>', methods=['GET'])
def get_health_data(date_str):
    """Get health data for a specific date"""
    try:
        # Validate date format
        datetime.strptime(date_str, '%Y-%m-%d')
        
        entry_data = db.get_daily_entry(date_str)
        
        # Format response
        response = {
            'date': date_str,
            'mood': None,
            'energy_level': None,
            'water_intake': None,
            'sleep_time': None,
            'wake_time': None,
            'left_bed_time': None,
            'did_run': False,
            'distance_km': None,
            'medications': {
                'thyroid': False,
                'b12': False,
                'finasteride': False
            }
        }
        
        # Extract daily entry data
        if entry_data['daily_entry']:
            daily_entry = entry_data['daily_entry']
            response.update({
                'mood': daily_entry[2],
                'energy_level': daily_entry[3],
                'water_intake': daily_entry[4],
                'sleep_time': daily_entry[7] if len(daily_entry) > 7 else None,
                'wake_time': daily_entry[8] if len(daily_entry) > 8 else None,
                'left_bed_time': daily_entry[9] if len(daily_entry) > 9 else None
            })
        
        # Extract running data
        if entry_data['running_data']:
            running_data = entry_data['running_data']
            response.update({
                'did_run': bool(running_data[2]),
                'distance_km': running_data[3]
            })
        
        # Extract medication data
        if entry_data['medication_data']:
            med_data = entry_data['medication_data']
            response['medications'] = {
                'thyroid': bool(med_data[2]),
                'b12': bool(med_data[3]),
                'finasteride': bool(med_data[4])
            }
        
        return jsonify(response)
    
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health-data/<date_str>', methods=['POST', 'PUT'])
def save_health_data(date_str):
    """Save or update health data for a specific date"""
    try:
        # Validate date format
        datetime.strptime(date_str, '%Y-%m-%d')
        
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract and save daily entry data
        mood = data.get('mood')
        energy_level = data.get('energy')
        water_intake = data.get('waterIntake')
        sleep_time = data.get('sleepTime')
        wake_time = data.get('wakeTime')
        left_bed_time = data.get('leftBedTime')
        
        db.save_daily_entry(
            date=date_str,
            mood=mood,
            energy_level=energy_level,
            water_intake=water_intake,
            sleep_time=sleep_time,
            wake_time=wake_time,
            left_bed_time=left_bed_time
        )
        
        # Extract and save running data
        did_run = data.get('didRun', False)
        distance_km = data.get('distance')
        
        db.save_running_data(
            date=date_str,
            did_run=did_run,
            distance_km=float(distance_km) if distance_km else None
        )
        
        # Extract and save medication data
        medications = data.get('medications', [])
        db.save_medication_data(
            date=date_str,
            thyroid='thyroid' in medications,
            b12='b12' in medications,
            finasteride='finasteride' in medications
        )
        
        return jsonify({
            'message': 'Health data saved successfully',
            'date': date_str
        })
    
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health-data/<date_str>', methods=['DELETE'])
def delete_health_data(date_str):
    """Delete health data for a specific date"""
    try:
        # Validate date format
        datetime.strptime(date_str, '%Y-%m-%d')
        
        success = db.delete_daily_entry(date_str)
        
        if success:
            return jsonify({
                'message': 'Health data deleted successfully',
                'date': date_str
            })
        else:
            return jsonify({'error': 'Failed to delete health data'}), 500
    
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health-data/monthly/<year>/<month>', methods=['GET'])
def get_monthly_data(year, month):
    """Get health data for a specific month"""
    try:
        year = int(year)
        month = int(month)
        
        # Validate month
        if month < 1 or month > 12:
            return jsonify({'error': 'Invalid month. Must be 1-12'}), 400
        
        monthly_data = db.get_monthly_data(year, month)
        
        # Format response
        formatted_data = []
        for row in monthly_data:
            formatted_data.append({
                'date': row[1],  # date column
                'mood': row[2],
                'energy_level': row[3],
                'water_intake': row[4],
                'did_run': bool(row[6]) if row[6] is not None else False,
                'distance_km': row[7],
                'medications': {
                    'thyroid': bool(row[9]) if row[9] is not None else False,
                    'b12': bool(row[10]) if row[10] is not None else False,
                    'finasteride': bool(row[11]) if row[11] is not None else False
                }
            })
        
        return jsonify({
            'year': year,
            'month': month,
            'data': formatted_data
        })
    
    except ValueError:
        return jsonify({'error': 'Invalid year or month format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health-data/range/<start_date>/<end_date>', methods=['GET'])
def get_date_range_data(start_date, end_date):
    """Get health data for a date range"""
    try:
        # Validate date formats
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        range_data = db.get_date_range_data(start_date, end_date)
        
        # Format response
        formatted_data = []
        for row in range_data:
            formatted_data.append({
                'date': row[1],  # date column
                'mood': row[2],
                'energy_level': row[3],
                'water_intake': row[4],
                'did_run': bool(row[6]) if row[6] is not None else False,
                'distance_km': row[7],
                'medications': {
                    'thyroid': bool(row[9]) if row[9] is not None else False,
                    'b12': bool(row[10]) if row[10] is not None else False,
                    'finasteride': bool(row[11]) if row[11] is not None else False
                }
            })
        
        return jsonify({
            'start_date': start_date,
            'end_date': end_date,
            'data': formatted_data
        })
    
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health-data/dates-with-data', methods=['GET'])
def get_dates_with_data():
    """Get all dates that have health data (for calendar indicators)"""
    try:
        # Get current year and month for default range
        current_date = date.today()
        start_date = f"{current_date.year}-{current_date.month:02d}-01"
        
        # Get last day of current month
        if current_date.month == 12:
            end_date = f"{current_date.year + 1}-01-01"
        else:
            end_date = f"{current_date.year}-{current_date.month + 1:02d}-01"
        
        dates_with_data = db.get_dates_with_data(start_date, end_date)
        
        return jsonify({
            'dates': dates_with_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Health Tracker API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get overview analytics for the last 30 days"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        data = db.get_date_range_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # Initialize counters
        total_entries = len(data)
        mood_counts = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
        energy_counts = {'High': 0, 'Moderate': 0, 'Low': 0, 'Variable': 0}
        running_stats = {'total_runs': 0, 'total_distance': 0, 'running_days': 0}
        medication_stats = {'thyroid': 0, 'b12': 0, 'finasteride': 0}
        water_intake_data = []
        sleep_data = {'total_sleep_hours': 0, 'sleep_days_tracked': 0, 'sleep_durations': [], 'time_in_bed_after_wake': []}
        
        # Positive, Neutral, and Negative mood categorization
        positive_moods = ['Happy', 'Joyful', 'Excited', 'Content', 'Grateful', 'Relaxed', 'Peaceful', 'Satisfied', 'Optimistic', 'Confident', 'Energetic', 'Motivated', 'Proud', 'Amused']
        neutral_moods = ['Calm', 'Neutral', 'Focused', 'Reflective', 'Balanced', 'Tired']
        negative_moods = ['Sad', 'Anxious', 'Stressed', 'Frustrated', 'Angry', 'Worried', 'Overwhelmed', 'Lonely', 'Disappointed', 'Irritated', 'Confused', 'Restless']
        
        # High, Moderate, Low energy categorization
        high_energy = ['Very High', 'High', 'Energetic', 'Vibrant', 'Peppy', 'Bursting']
        moderate_energy = ['Moderate', 'Steady', 'Balanced', 'Normal', 'Stable', 'Comfortable']
        low_energy = ['Low', 'Tired', 'Drained', 'Sluggish', 'Lethargic', 'Exhausted', 'Fatigued', 'Worn Out']
        variable_energy = ['Up and Down', 'Inconsistent', 'Fluctuating', 'Unpredictable']
        
        for entry in data:
            # Mood analysis - index 2 is mood
            if entry[2]:  # mood field
                if entry[2] in positive_moods:
                    mood_counts['Positive'] += 1
                elif entry[2] in neutral_moods:
                    mood_counts['Neutral'] += 1
                elif entry[2] in negative_moods:
                    mood_counts['Negative'] += 1
            
            # Energy analysis - index 3 is energy_level
            if entry[3]:  # energy_level field
                if entry[3] in high_energy:
                    energy_counts['High'] += 1
                elif entry[3] in moderate_energy:
                    energy_counts['Moderate'] += 1
                elif entry[3] in low_energy:
                    energy_counts['Low'] += 1
                elif entry[3] in variable_energy:
                    energy_counts['Variable'] += 1
            
            # Running analysis
            if entry[10]:  # did_run field (now at index 10)
                running_stats['running_days'] += 1
                if entry[11]:  # distance_km field (now at index 11)
                    running_stats['total_distance'] += float(entry[11])
                    running_stats['total_runs'] += 1
            
            # Medication analysis
            if entry[12]:  # thyroid (now at index 12)
                medication_stats['thyroid'] += 1
            if entry[13]:  # b12 (now at index 13)
                medication_stats['b12'] += 1
            if entry[14]:  # finasteride (now at index 14)
                medication_stats['finasteride'] += 1
            
            # Water intake - index 4 is water_intake
            if entry[4]:  # water_intake field
                try:
                    # Handle different water intake formats
                    water_str = str(entry[4]).replace('L', '').replace('l', '').replace('<', '').replace('>', '').strip()
                    water_amount = float(water_str)
                    water_intake_data.append(water_amount)
                except:
                    pass
            
            # Sleep tracking - calculate sleep duration if both times are available
            if len(entry) > 8 and entry[7] and entry[8]:  # sleep_time and wake_time
                try:
                    sleep_time_str = entry[7]  # sleep_time (index 7)
                    wake_time_str = entry[8]   # wake_time (index 8)
                    left_bed_time_str = entry[9] if len(entry) > 9 else None  # left_bed_time (index 9)
                    
                    # Parse times
                    sleep_time = datetime.strptime(sleep_time_str, '%H:%M').time()
                    wake_time = datetime.strptime(wake_time_str, '%H:%M').time()
                    
                    # Convert to datetime objects for calculation
                    sleep_dt = datetime.combine(datetime.today(), sleep_time)
                    wake_dt = datetime.combine(datetime.today(), wake_time)
                    
                    # If wake time is earlier than sleep time, assume next day
                    if wake_dt <= sleep_dt:
                        wake_dt += timedelta(days=1)
                    
                    # Calculate sleep duration in hours
                    sleep_duration = (wake_dt - sleep_dt).total_seconds() / 3600
                    
                    sleep_data['sleep_durations'].append(sleep_duration)
                    sleep_data['total_sleep_hours'] += sleep_duration
                    sleep_data['sleep_days_tracked'] += 1
                    
                    # Calculate time spent in bed after waking
                    if left_bed_time_str:
                        left_bed_time = datetime.strptime(left_bed_time_str, '%H:%M').time()
                        left_bed_dt = datetime.combine(datetime.today(), left_bed_time)
                        
                        # If left bed time is earlier than wake time, assume next day
                        if left_bed_dt < wake_dt:
                            left_bed_dt += timedelta(days=1)
                        
                        # Calculate time in bed after waking (in minutes)
                        time_in_bed_after = (left_bed_dt - wake_dt).total_seconds() / 60
                        if time_in_bed_after >= 0:  # Only positive values make sense
                            sleep_data['time_in_bed_after_wake'].append(time_in_bed_after)
                        
                except Exception as e:
                    print(f"Sleep calculation error: {e}")  # Debug
                    pass
        
        # Calculate averages and percentages
        avg_distance = running_stats['total_distance'] / max(running_stats['total_runs'], 1)
        avg_water_intake = sum(water_intake_data) / max(len(water_intake_data), 1) if water_intake_data else 0
        avg_sleep_hours = sleep_data['total_sleep_hours'] / max(sleep_data['sleep_days_tracked'], 1) if sleep_data['sleep_days_tracked'] > 0 else 0
        avg_time_in_bed_after_wake = sum(sleep_data['time_in_bed_after_wake']) / max(len(sleep_data['time_in_bed_after_wake']), 1) if sleep_data['time_in_bed_after_wake'] else 0
        
        response = {
            'period': f"{start_date} to {end_date}",
            'total_entries': total_entries,
            'mood_distribution': mood_counts,
            'energy_distribution': energy_counts,
            'running_stats': {
                'total_runs': running_stats['total_runs'],
                'total_distance': round(running_stats['total_distance'], 2),
                'running_days': running_stats['running_days'],
                'avg_distance_per_run': round(avg_distance, 2),
                'running_percentage': round((running_stats['running_days'] / max(total_entries, 1)) * 100, 1)
            },
            'medication_compliance': {
                'thyroid': round((medication_stats['thyroid'] / max(total_entries, 1)) * 100, 1),
                'b12': round((medication_stats['b12'] / max(total_entries, 1)) * 100, 1),
                'finasteride': round((medication_stats['finasteride'] / max(total_entries, 1)) * 100, 1)
            },
            'water_intake': {
                'avg_daily_intake': round(avg_water_intake, 2),
                'total_days_tracked': len(water_intake_data)
            },
            'sleep_stats': {
                'avg_sleep_hours': round(avg_sleep_hours, 2),
                'sleep_days_tracked': sleep_data['sleep_days_tracked'],
                'total_sleep_hours': round(sleep_data['total_sleep_hours'], 2),
                'avg_time_in_bed_after_wake_minutes': round(avg_time_in_bed_after_wake, 1),
                'left_bed_days_tracked': len(sleep_data['time_in_bed_after_wake'])
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/trends/<int:days>', methods=['GET'])
def get_trends_data(days):
    """Get trend data for specified number of days"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        data = db.get_date_range_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # Organize data by date for trends
        daily_data = {}
        for entry in data:
            date = entry[1]  # date field - index 1
            daily_data[date] = {
                'mood': entry[2],        # index 2
                'energy': entry[3],      # index 3  
                'water_intake': entry[4], # index 4
                'sleep_time': entry[7] if len(entry) > 7 else None,  # index 7
                'wake_time': entry[8] if len(entry) > 8 else None,   # index 8
                'left_bed_time': entry[9] if len(entry) > 9 else None,  # index 9
                'did_run': bool(entry[10]) if entry[10] is not None else False,
                'distance': float(entry[11]) if entry[11] else 0,
                'medications': {
                    'thyroid': bool(entry[12]) if entry[12] is not None else False,
                    'b12': bool(entry[13]) if entry[13] is not None else False,
                    'finasteride': bool(entry[14]) if entry[14] is not None else False
                }
            }
        
        return jsonify({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'daily_data': daily_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Health Tracker API',
        'version': '1.0.0',
        'endpoints': [
            'GET /api/health',
            'GET /api/health-data/<date>',
            'POST /api/health-data/<date>',
            'PUT /api/health-data/<date>',
            'DELETE /api/health-data/<date>',
            'GET /api/health-data/monthly/<year>/<month>',
            'GET /api/health-data/range/<start>/<end>',
            'GET /api/health-data/dates-with-data',
            'GET /api/analytics/overview',
            'GET /api/analytics/trends/<days>'
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Health Tracker API...")
    print("Available endpoints:")
    print("  GET  /api/health-data/<date> - Get health data for a date")
    print("  POST /api/health-data/<date> - Save health data for a date")
    print("  PUT  /api/health-data/<date> - Update health data for a date")
    print("  DELETE /api/health-data/<date> - Delete health data for a date")
    print("  GET  /api/health-data/monthly/<year>/<month> - Get monthly data")
    print("  GET  /api/health-data/range/<start>/<end> - Get date range data")
    print("  GET  /api/health-data/dates-with-data - Get dates with data")
    print("  GET  /api/analytics/overview - Get 30-day analytics overview")
    print("  GET  /api/analytics/trends/<days> - Get trend data for specified days")
    print("  GET  /api/health - Health check")
    print("\nStarting server on http://localhost:5002")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
