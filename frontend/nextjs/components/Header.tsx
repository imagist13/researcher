import React from 'react';
import Image from "next/image";

interface HeaderProps {
  loading?: boolean;      // Indicates if research is currently in progress
  isStopped?: boolean;    // Indicates if research was manually stopped
  showResult?: boolean;   // Controls if research results are being displayed
  onStop?: () => void;    // Handler for stopping ongoing research
  onNewResearch?: () => void;  // Handler for starting fresh research
}

const Header = ({ loading, isStopped, showResult, onStop, onNewResearch }: HeaderProps) => {
  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      {/* Pure transparent blur background */}
      <div className="absolute inset-0 backdrop-blur-sm bg-transparent"></div>
      
      {/* Header container */}
      <div className="container relative h-[60px] px-4 lg:h-[80px] lg:px-0 pt-4 pb-4">
        <div className="flex justify-between items-center w-full">
          {/* Logo/Home link */}
          <a href="/">
            <img
              src="/img/gptr-logo.svg"
              alt="GPT Researcher Logo"
              width={60}
              height={60}
              className="lg:h-16 lg:w-16"
            />
          </a>

          {/* Navigation Menu */}
          <nav className="hidden md:flex items-center gap-6">
            <a
              href="/"
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors duration-200"
            >
              <span>🏠</span>
              研究
            </a>
            <a
              href="/scheduled"
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-300 hover:text-teal-400 transition-colors duration-200 border border-gray-700/50 rounded-lg hover:border-teal-500/30 hover:bg-teal-500/10"
            >
              <span>📊</span>
              定时研究
            </a>
          </nav>

          {/* Mobile Navigation Button */}
          <button
            className="md:hidden flex items-center justify-center w-10 h-10 text-gray-300 hover:text-white transition-colors"
            onClick={() => {/* TODO: Add mobile menu toggle */}}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
        
        <div className="flex justify-center mt-2">
          
          {/* Action buttons container */}
          <div className="flex gap-2 mt-2 transition-all duration-300 ease-in-out">
            {/* Stop button - shown only during active research */}
            {loading && !isStopped && (
              <button
                onClick={onStop}
                className="flex items-center justify-center px-4 sm:px-6 h-9 sm:h-10 text-sm text-white bg-red-500 rounded-full hover:bg-red-600 transform hover:scale-105 transition-all duration-200 shadow-lg whitespace-nowrap min-w-[80px]"
              >
                停止
              </button>
            )}
            {/* New Research button - shown after stopping or completing research */}
            {(isStopped || !loading) && showResult && (
              <button
                onClick={onNewResearch}
                className="flex items-center justify-center px-4 sm:px-6 h-9 sm:h-10 text-sm text-white bg-teal-500 rounded-full hover:bg-teal-600 transform hover:scale-105 transition-all duration-200 shadow-lg whitespace-nowrap min-w-[120px]"
              >
                新研究
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
