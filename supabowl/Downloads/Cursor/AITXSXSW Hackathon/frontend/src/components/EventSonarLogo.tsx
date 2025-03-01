
import React from 'react';

const EventSonarLogo = ({ className = "", size = 50 }: { className?: string, size?: number }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="sonarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#9b87f5" />
          <stop offset="100%" stopColor="#33C3F0" />
        </linearGradient>
        
        <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="2" dy="2" stdDeviation="2" floodColor="#1A1F2C" floodOpacity="0.5"/>
        </filter>
      </defs>
      
      {/* Enhanced Sonar Waves with animation */}
      <path 
        d="M50 35 C60 40, 68 45, 70 50 C68 55, 60 60, 50 65" 
        fill="none" 
        stroke="#9b87f5" 
        strokeWidth="2" 
        strokeDasharray="2 2" 
        strokeLinecap="round"
        opacity="0.9"
      >
        <animate attributeName="opacity" values="0.6;0.9;0.6" dur="3s" repeatCount="indefinite" />
      </path>
      
      <path 
        d="M50 30 C65 38, 73 44, 75 50 C73 56, 65 62, 50 70" 
        fill="none" 
        stroke="#33C3F0" 
        strokeWidth="2" 
        strokeDasharray="2 2" 
        strokeLinecap="round"
        opacity="0.8"
      >
        <animate attributeName="opacity" values="0.5;0.8;0.5" dur="3s" begin="0.5s" repeatCount="indefinite" />
      </path>
      
      <path 
        d="M50 25 C70 35, 78 42, 80 50 C78 58, 70 65, 50 75" 
        fill="none" 
        stroke="#9b87f5" 
        strokeWidth="2" 
        strokeDasharray="2 2" 
        strokeLinecap="round"
        opacity="0.7"
      >
        <animate attributeName="opacity" values="0.4;0.7;0.4" dur="3s" begin="1s" repeatCount="indefinite" />
      </path>
      
      {/* Center point */}
      <circle cx="50" cy="50" r="3" fill="url(#sonarGradient)" filter="url(#dropShadow)" />
    </svg>
  );
};

export default EventSonarLogo;
