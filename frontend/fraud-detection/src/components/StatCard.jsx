import React from 'react';

const StatCard = ({ icon, title, value, percentageChange, percentageDirection }) => {
  return (
    <div className="card stat-card">
      <div className="stat-icon">
        {icon}
      </div>
      <div className="stat-info">
        <p>{title}</p>
        <h3>{value}
          {percentageChange && (
            <span className={`percentage ${percentageDirection === 'up' ? 'up' : 'down'}`}>
              {percentageDirection === 'up' ? '+' : '-'}{percentageChange}%
            </span>
          )}
        </h3>
      </div>
    </div>
  );
};

export default StatCard; 