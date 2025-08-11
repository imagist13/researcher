"use client";

import React, { useState, useMemo } from 'react';
import { TrendData } from '@/types/data';

interface KeywordTrendsChartProps {
  trendData: TrendData[];
  maxKeywords?: number;
}

export default function KeywordTrendsChart({
  trendData,
  maxKeywords = 10,
}: KeywordTrendsChartProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState<'all' | 'recent'>('recent');
  
  // 处理关键词趋势数据
  const keywordData = useMemo(() => {
    if (!trendData || trendData.length === 0) return [];
    
    // 选择数据范围
    const dataToAnalyze = selectedTimeframe === 'recent' 
      ? trendData.slice(-5) // 最近5次数据
      : trendData;
    
    // 收集所有关键词和其趋势值
    const keywordMap = new Map<string, number[]>();
    
    dataToAnalyze.forEach(data => {
      if (data.keyword_trends) {
        Object.entries(data.keyword_trends).forEach(([keyword, value]) => {
          if (!keywordMap.has(keyword)) {
            keywordMap.set(keyword, []);
          }
          keywordMap.get(keyword)!.push(typeof value === 'number' ? value : 0);
        });
      }
    });
    
    // 计算每个关键词的平均值、最大值和变化趋势
    const keywords = Array.from(keywordMap.entries()).map(([keyword, values]) => {
      const average = values.reduce((sum, val) => sum + val, 0) / values.length;
      const maximum = Math.max(...values);
      const minimum = Math.min(...values);
      const trend = values.length > 1 ? values[values.length - 1] - values[0] : 0;
      const variance = values.reduce((sum, val) => sum + Math.pow(val - average, 2), 0) / values.length;
      
      return {
        keyword,
        average,
        maximum,
        minimum,
        trend,
        variance,
        values,
        isNew: values.length < dataToAnalyze.length * 0.5, // 新兴关键词
        isHot: average > 7 || trend > 2, // 热门关键词
      };
    });
    
    // 按平均值排序并限制数量
    return keywords
      .sort((a, b) => b.average - a.average)
      .slice(0, maxKeywords);
  }, [trendData, selectedTimeframe, maxKeywords]);

  // 计算颜色强度
  const getHeatmapColor = (value: number, max: number) => {
    const intensity = Math.min(value / Math.max(max, 1), 1);
    const hue = 180 - (intensity * 60); // 从青色到红色
    return `hsl(${hue}, 70%, ${40 + intensity * 20}%)`;
  };

  // 获取趋势箭头
  const getTrendIcon = (trend: number) => {
    if (trend > 1) return { icon: '↗️', color: 'text-green-400', label: '上升' };
    if (trend < -1) return { icon: '↘️', color: 'text-red-400', label: '下降' };
    return { icon: '➡️', color: 'text-gray-400', label: '稳定' };
  };

  const maxValue = Math.max(...keywordData.map(k => k.maximum), 1);

  if (keywordData.length === 0) {
    return (
      <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6">
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-white mb-2">暂无关键词数据</h3>
          <p className="text-gray-400">
            当有趋势分析数据后，这里将显示关键词热度变化
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
      {/* 标题和控制 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">关键词热度分析</h3>
          <p className="text-sm text-gray-400">
            显示关键词的热度变化和趋势方向
          </p>
        </div>
        
        <div className="flex gap-2 mt-4 sm:mt-0">
          <button
            onClick={() => setSelectedTimeframe('recent')}
            className={`
              px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
              ${selectedTimeframe === 'recent'
                ? 'bg-teal-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
              }
            `}
          >
            近期
          </button>
          <button
            onClick={() => setSelectedTimeframe('all')}
            className={`
              px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
              ${selectedTimeframe === 'all'
                ? 'bg-teal-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
              }
            `}
          >
            全部
          </button>
        </div>
      </div>

      {/* 关键词热力图 */}
      <div className="space-y-3">
        {keywordData.map((item, index) => {
          const trendInfo = getTrendIcon(item.trend);
          const heatColor = getHeatmapColor(item.average, maxValue);
          
          return (
            <div
              key={item.keyword}
              className="flex items-center gap-4 p-3 rounded-lg transition-all duration-200 hover:bg-gray-700/30"
            >
              {/* 排名 */}
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700/50 flex items-center justify-center text-sm font-medium text-gray-300">
                {index + 1}
              </div>
              
              {/* 关键词和标签 */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-white truncate">
                    {item.keyword}
                  </span>
                  
                  {/* 特殊标签 */}
                  <div className="flex gap-1">
                    {item.isNew && (
                      <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded-full">
                        新兴
                      </span>
                    )}
                    {item.isHot && (
                      <span className="px-2 py-1 text-xs bg-red-500/20 text-red-400 rounded-full">
                        热门
                      </span>
                    )}
                  </div>
                </div>
                
                {/* 统计信息 */}
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  <span>平均: {item.average.toFixed(1)}</span>
                  <span>最高: {item.maximum.toFixed(1)}</span>
                  <span>数据点: {item.values.length}</span>
                </div>
              </div>
              
              {/* 热度条 */}
              <div className="flex-shrink-0 w-24">
                <div className="relative h-6 bg-gray-700/50 rounded-full overflow-hidden">
                  <div
                    className="absolute left-0 top-0 h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${(item.average / maxValue) * 100}%`,
                      backgroundColor: heatColor,
                    }}
                  ></div>
                  
                  {/* 数值显示 */}
                  <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white mix-blend-difference">
                    {item.average.toFixed(1)}
                  </div>
                </div>
              </div>
              
              {/* 趋势指示器 */}
              <div className="flex-shrink-0 flex items-center gap-2">
                <span className="text-lg" title={trendInfo.label}>
                  {trendInfo.icon}
                </span>
                <span className={`text-sm font-medium ${trendInfo.color}`}>
                  {item.trend > 0 ? '+' : ''}{item.trend.toFixed(1)}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* 图例说明 */}
      <div className="mt-6 pt-4 border-t border-gray-700/50">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500/20 border border-blue-400"></div>
            <span className="text-gray-300">新兴关键词</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-400"></div>
            <span className="text-gray-300">热门关键词</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-green-400">↗️</span>
            <span className="text-gray-300">上升趋势</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-red-400">↘️</span>
            <span className="text-gray-300">下降趋势</span>
          </div>
        </div>
      </div>

      {/* 数据概览 */}
      <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-400">
        <span>
          总关键词: {keywordData.length}
        </span>
        <span>
          热门关键词: {keywordData.filter(k => k.isHot).length}
        </span>
        <span>
          新兴关键词: {keywordData.filter(k => k.isNew).length}
        </span>
        <span>
          时间范围: {selectedTimeframe === 'recent' ? '近期5次' : '全部数据'}
        </span>
      </div>
    </div>
  );
}
