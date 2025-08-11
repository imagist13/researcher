"use client";

import React, { useState, Suspense } from 'react';
import dynamic from 'next/dynamic';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { ChatBoxSettings } from '@/types/data';

// 懒加载ScheduledDashboard组件
const ScheduledDashboard = dynamic(() => import('@/components/Scheduled/ScheduledDashboard'), {
  loading: () => <ScheduledDashboardSkeleton />,
  ssr: false
});

// 骨架屏组件
function ScheduledDashboardSkeleton() {
  return (
    <div className="container mx-auto px-4 lg:px-0 max-w-7xl animate-pulse">
      {/* 标题骨架 */}
      <div className="mb-8">
        <div className="h-10 bg-gray-700 rounded-lg w-1/2 mb-4"></div>
        <div className="h-6 bg-gray-700 rounded-lg w-3/4"></div>
      </div>

      {/* 状态栏骨架 */}
      <div className="mb-6 p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 bg-gray-600 rounded-full"></div>
            <div className="h-4 bg-gray-600 rounded w-32"></div>
          </div>
          <div className="flex gap-4">
            <div className="h-4 bg-gray-600 rounded w-20"></div>
            <div className="h-4 bg-gray-600 rounded w-20"></div>
          </div>
        </div>
      </div>

      {/* 标签页骨架 */}
      <div className="mb-8">
        <div className="flex gap-2 p-1 bg-gray-800/50 rounded-lg border border-gray-700/50">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-gray-600 rounded-md flex-1"></div>
          ))}
        </div>
      </div>

      {/* 内容区域骨架 */}
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="p-6 bg-gray-800/30 rounded-lg border border-gray-700/50">
            <div className="flex justify-between items-center mb-4">
              <div className="h-6 bg-gray-600 rounded w-1/3"></div>
              <div className="h-8 bg-gray-600 rounded w-20"></div>
            </div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-700 rounded w-full"></div>
              <div className="h-4 bg-gray-700 rounded w-2/3"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ScheduledPage() {
  // 为Footer组件提供默认的chatBox设置（定时研究页面不需要聊天功能）
  const [chatBoxSettings, setChatBoxSettings] = useState<ChatBoxSettings>({
    report_type: 'research_report',
    report_source: 'web',
    tone: 'Objective',
    domains: [],
    defaultReportType: 'research_report',
    mcp_enabled: false,
    mcp_configs: []
  });

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 pt-20 lg:pt-24">
        <ScheduledDashboard />
      </main>
      
      <Footer 
        chatBoxSettings={chatBoxSettings}
        setChatBoxSettings={setChatBoxSettings}
      />
    </div>
  );
}
