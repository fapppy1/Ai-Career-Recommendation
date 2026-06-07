import React from 'react';

function Logo({ className = "" }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Logo Icon with Animation */}
      <div className="relative w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg animate-pulse-slow">
        <span className="text-white font-bold text-lg">AI</span>
        {/* Floating particles effect */}
        <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
      </div>
      
      <div className="flex flex-col">
        <span className="text-lg font-bold bg-gradient-to-r from-blue-700 to-purple-600 bg-clip-text text-transparent leading-none">
          CareerPath
        </span>
        <span className="text-[10px] text-gray-500 font-medium tracking-wide uppercase">
          AI Recommender
        </span>
      </div>
    </div>
  );
}

export default Logo;