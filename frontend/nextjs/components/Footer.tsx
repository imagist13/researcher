import React from 'react';
import Modal from './Settings/Modal';
import { ChatBoxSettings } from '@/types/data';

interface FooterProps {
  chatBoxSettings: ChatBoxSettings;
  setChatBoxSettings: React.Dispatch<React.SetStateAction<ChatBoxSettings>>;
}

const Footer: React.FC<FooterProps> = ({ chatBoxSettings, setChatBoxSettings }) => {
  // Add domain filtering from URL parameters
  if (typeof window !== 'undefined') {
    const urlParams = new URLSearchParams(window.location.search);
    const urlDomains = urlParams.get("domains");
    if (urlDomains) {
      // Split domains by comma if multiple domains are provided
      const domainArray = urlDomains.split(',').map(domain => ({
        value: domain.trim()
      }));
      localStorage.setItem('domainFilters', JSON.stringify(domainArray));
    }
  }

  return (
    <>
      <div className="relative mt-8 border-t border-gray-700/20">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-800/20 to-transparent"></div>
        
        {/* Content container */}
        <div className="container relative flex flex-col items-center justify-center px-4 py-8 lg:px-0">
          
          {/* Settings button with better positioning */}
          <div className="mb-6">
            <Modal setChatBoxSettings={setChatBoxSettings} chatBoxSettings={chatBoxSettings} />
          </div>
          
          {/* Decorative divider */}
          <div className="w-20 h-px bg-gradient-to-r from-transparent via-teal-400/50 to-transparent mb-6"></div>
          
          {/* Copyright text with better styling */}
          <div className="text-center space-y-2">
            <div className="text-sm text-gray-200 font-medium tracking-wide">
              © {new Date().getFullYear()} AI研究助手
            </div>
            <div className="text-xs text-gray-400 tracking-wider">
              智能研究 · 高效分析 · 精准洞察
            </div>
          </div>
          
          {/* Decorative dots */}
          <div className="flex items-center gap-2 mt-6 opacity-30">
            <div className="w-1 h-1 bg-teal-400 rounded-full"></div>
            <div className="w-1 h-1 bg-teal-400 rounded-full"></div>
            <div className="w-1 h-1 bg-teal-400 rounded-full"></div>
          </div>
          
        </div>
      </div>
    </>
  );
};

export default Footer;