import React, { useState, useRef, useEffect } from 'react';

const CustomDropdown = ({ 
  options, 
  value, 
  onChange, 
  placeholder, 
  disabled = false,
  className = '' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedText, setSelectedText] = useState(placeholder);
  const dropdownRef = useRef(null);

  // Update selected text when value changes
  useEffect(() => {
    if (value) {
      const selectedOption = options.find(option => option.value === value);
      if (selectedOption) {
        setSelectedText(selectedOption.text);
      }
    } else {
      setSelectedText(placeholder);
    }
  }, [value, options, placeholder]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  const handleOptionClick = (option) => {
    setSelectedText(option.text);
    onChange(option.value);
    setIsOpen(false);
  };

  return (
    <div 
      ref={dropdownRef}
      className={`custom-dropdown ${isOpen ? 'open' : ''} ${disabled ? 'disabled' : ''} ${className}`}
    >
      <div 
        className="dropdown-selected" 
        onClick={handleToggle}
      >
        <span>{selectedText}</span>
        <div className="dropdown-arrow">▼</div>
      </div>
      
      {isOpen && (
        <div className="dropdown-options">
          {(() => {
            const groupedOptions = {};
            options.forEach(option => {
              const group = option.group || 'Other';
              if (!groupedOptions[group]) {
                groupedOptions[group] = [];
              }
              groupedOptions[group].push(option);
            });

            return Object.entries(groupedOptions).map(([groupName, groupOptions]) => (
              <div key={groupName}>
                <div className="dropdown-group-label">{groupName}</div>
                {groupOptions.map((option, index) => (
                  <div
                    key={`${groupName}-${index}`}
                    className={`dropdown-option ${value === option.value ? 'selected' : ''}`}
                    onClick={() => handleOptionClick(option)}
                  >
                    {option.text}
                  </div>
                ))}
              </div>
            ));
          })()}
        </div>
      )}
    </div>
  );
};

export default CustomDropdown;
