import React from 'react';

const Calendar = ({ currentDate, selectedDate, calendarData, onDateSelect }) => {
  const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  
  // Get first day of month and number of days
  const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
  const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
  const daysInMonth = lastDay.getDate();
  const startingDayOfWeek = firstDay.getDay();

  const isSameDate = (date1, date2) => {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  };

  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };

  const getDayClasses = (day, currentDayDate) => {
    const today = new Date();
    const dateString = formatDate(currentDayDate);
    const isToday = isSameDate(currentDayDate, today);
    const isPast = currentDayDate < today;
    const isSelected = selectedDate && isSameDate(currentDayDate, selectedDate);
    const hasData = calendarData.has(dateString) && calendarData.get(dateString).hasData;
    
    let classes = 'calendar-day';
    
    if (isToday) {
      classes += ' today';
    } else if (isPast) {
      if (hasData) {
        classes += ' has-data';
      } else {
        classes += ' no-data';
      }
    }
    
    if (isSelected) {
      classes += ' selected';
    }
    
    return classes;
  };

  const renderCalendarDays = () => {
    const days = [];
    const today = new Date();
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(
        <div key={`empty-${i}`} className="calendar-day other-month">
        </div>
      );
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const currentDayDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const dateString = formatDate(currentDayDate);
      const isToday = isSameDate(currentDayDate, new Date());
      
      days.push(
        <div
          key={day}
          className={getDayClasses(day, currentDayDate)}
          onClick={() => onDateSelect(currentDayDate)}
        >
          <div className="day-name">{dayHeaders[currentDayDate.getDay()]}</div>
          <div className="day-number">{day}</div>
        </div>
      );
    }

    return days;
  };

  return (
    <div className="calendar">
      {dayHeaders.map(day => (
        <div key={day} className="calendar-day day-header">
          {day}
        </div>
      ))}
      {renderCalendarDays()}
    </div>
  );
};

export default Calendar;
