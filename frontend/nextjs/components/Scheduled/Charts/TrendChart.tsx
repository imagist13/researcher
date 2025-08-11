"use client";

import React, { useMemo } from 'react';
import { TrendData } from '@/types/data';

interface TrendChartProps {
  trendData: TrendData[];
  selectedMetric: 'trend_score' | 'activity_level' | 'change_magnitude';
  onMetricChange: (metric: 'trend_score' | 'activity_level' | 'change_magnitude') => void;
}

export default function TrendChart({
  trendData,
  selectedMetric,
  onMetricChange,
}: TrendChartProps) {
  
  // 处理数据，确保按时间排序
  const chartData = useMemo(() => {
    if (!trendData || trendData.length === 0) return [];
    
    return trendData
      .filter(data => data.analysis_date)
      .sort((a, b) => new Date(a.analysis_date!).getTime() - new Date(b.analysis_date!).getTime())
      .map(data => {
        const date = new Date(data.analysis_date!);
        return {
          date: date.toLocaleDateString('zh-CN', {
            month: '2-digit',
            day: '2-digit'
          }),
          value: (data[selectedMetric as keyof TrendData] as number) || 0,
          fullDate: data.analysis_date,
          timestamp: date.getTime(),
          confidence: data.confidence_score || 0,
          anomaly: data.anomaly_detected,
          formattedTime: date.toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          })
        };
      });
  }, [trendData, selectedMetric]);

  // 计算图表尺寸和比例
  const chartWidth = 600;
  const chartHeight = 300;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  // 计算数据范围
  const maxValue = Math.max(...chartData.map(d => d.value), 1);
  const minValue = Math.min(...chartData.map(d => d.value), 0);
  const valueRange = maxValue - minValue;

  // 生成路径
  const generatePath = (data: typeof chartData) => {
    if (data.length === 0) return "";
    
    const points = data.map((d, i) => {
      const x = (i / Math.max(data.length - 1, 1)) * innerWidth;
      const y = innerHeight - ((d.value - minValue) / Math.max(valueRange, 1)) * innerHeight;
      return `${x},${y}`;
    });
    
    return `M${points.join(' L')}`;
  };

  // 生成面积路径
  const generateAreaPath = (data: typeof chartData) => {
    if (data.length === 0) return "";
    
    const points = data.map((d, i) => {
      const x = (i / Math.max(data.length - 1, 1)) * innerWidth;
      const y = innerHeight - ((d.value - minValue) / Math.max(valueRange, 1)) * innerHeight;
      return [x, y];
    });
    
    const pathStart = `M0,${innerHeight}`;
    const linePath = points.map(([x, y]) => `L${x},${y}`).join(' ');
    const pathEnd = `L${innerWidth},${innerHeight}Z`;
    
    return pathStart + ' ' + linePath + ' ' + pathEnd;
  };

  // 获取指标信息
  const getMetricInfo = (metric: string) => {
    const metricConfigs = {
      trend_score: {
        label: '趋势分数',
        color: '#0d9488',
        description: '话题活跃度和变化强度'
      },
      activity_level: {
        label: '活跃度',
        color: '#0891b2',
        description: '话题讨论和关注热度'
      },
      change_magnitude: {
        label: '变化幅度',
        color: '#7c3aed',
        description: '相对于历史数据的变化程度'
      }
    };
    return metricConfigs[metric as keyof typeof metricConfigs];
  };

  const currentMetricInfo = getMetricInfo(selectedMetric);

  if (!chartData || chartData.length === 0) {
    return (
      <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6">
        <div className="text-center py-8">
          <div className="text-4xl mb-4">📈</div>
          <h3 className="text-lg font-semibold text-white mb-2">暂无趋势数据</h3>
          <p className="text-gray-400">
            当任务执行几次后，这里将显示趋势图表
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
      {/* 标题和指标选择 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">趋势图表</h3>
          <p className="text-sm text-gray-400">{currentMetricInfo.description}</p>
        </div>
        
        <div className="flex gap-2 mt-4 sm:mt-0">
          {(['trend_score', 'activity_level', 'change_magnitude'] as const).map((metric) => {
            const info = getMetricInfo(metric);
            return (
              <button
                key={metric}
                onClick={() => onMetricChange(metric)}
                className={`
                  px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
                  ${selectedMetric === metric
                    ? 'text-white shadow-lg transform scale-105'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                  }
                `}
                style={{
                  backgroundColor: selectedMetric === metric ? info.color : 'transparent',
                  borderColor: info.color,
                  borderWidth: '1px'
                }}
              >
                {info.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* 图表区域 */}
      <div className="relative">
        <svg
          width="100%"
          height={chartHeight}
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="overflow-visible"
        >
          <defs>
            <linearGradient id={`gradient-${selectedMetric}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={currentMetricInfo.color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={currentMetricInfo.color} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          
          <g transform={`translate(${padding.left}, ${padding.top})`}>
            {/* 网格线 */}
            <g className="opacity-20">
              {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
                <line
                  key={ratio}
                  x1={0}
                  y1={innerHeight * ratio}
                  x2={innerWidth}
                  y2={innerHeight * ratio}
                  stroke="#6b7280"
                  strokeWidth={ratio === 0 || ratio === 1 ? 2 : 1}
                />
              ))}
            </g>
            
            {/* 面积 */}
            <path
              d={generateAreaPath(chartData)}
              fill={`url(#gradient-${selectedMetric})`}
            />
            
            {/* 趋势线 */}
            <path
              d={generatePath(chartData)}
              fill="none"
              stroke={currentMetricInfo.color}
              strokeWidth={3}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            
            {/* 数据点 */}
            {chartData.map((d, i) => {
              const x = (i / Math.max(chartData.length - 1, 1)) * innerWidth;
              const y = innerHeight - ((d.value - minValue) / Math.max(valueRange, 1)) * innerHeight;
              
              return (
                <g key={i}>
                  {/* 异常标记 */}
                  {d.anomaly && (
                    <circle
                      cx={x}
                      cy={y}
                      r={8}
                      fill="none"
                      stroke="#f59e0b"
                      strokeWidth={2}
                      className="animate-pulse"
                    />
                  )}
                  
                  {/* 数据点 */}
                  <circle
                    cx={x}
                    cy={y}
                    r={4}
                    fill={currentMetricInfo.color}
                    stroke="white"
                    strokeWidth={2}
                    className="hover:r-6 transition-all cursor-pointer"
                  >
                    <title>
                      {d.date}: {d.value.toFixed(2)}
                      {d.anomaly ? ' (异常检测)' : ''}
                    </title>
                  </circle>
                </g>
              );
            })}
            
            {/* Y轴标签 */}
            {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
              <text
                key={ratio}
                x={-10}
                y={innerHeight * (1 - ratio) + 4}
                textAnchor="end"
                className="text-xs fill-gray-400"
              >
                {(minValue + valueRange * ratio).toFixed(1)}
              </text>
            ))}
            
            {/* X轴标签 */}
            {chartData.map((d, i) => {
              if (chartData.length > 10 && i % Math.ceil(chartData.length / 5) !== 0) return null;
              
              const x = (i / Math.max(chartData.length - 1, 1)) * innerWidth;
              return (
                <text
                  key={i}
                  x={x}
                  y={innerHeight + 25}
                  textAnchor="middle"
                  className="text-xs fill-gray-400"
                >
                  {d.date}
                </text>
              );
            })}
          </g>
        </svg>
      </div>

      {/* 图表统计信息 */}
      <div className="mt-4 flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div 
            className="w-3 h-3 rounded-full" 
            style={{ backgroundColor: currentMetricInfo.color }}
          ></div>
          <span className="text-gray-300">
            平均值: {(chartData.reduce((sum, d) => sum + d.value, 0) / chartData.length).toFixed(2)}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full border-2 border-yellow-500"></div>
          <span className="text-gray-300">
            异常检测: {chartData.filter(d => d.anomaly).length} 次
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-gray-300">
            数据点: {chartData.length} 个
          </span>
        </div>
      </div>
    </div>
  );
}
