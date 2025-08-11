"use client";

import React, { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ResearchHistoryRecord, ScheduledTask } from '@/types/data';
import { scheduledApiService } from '@/services/scheduledApiService';
import { markdownToHtml } from '@/helpers/markdownHelper';

interface AnalysisResultViewerProps {
  tasks: ScheduledTask[];
  selectedTaskId: string | null;
  onSelectTask: (taskId: string | null) => void;
  onRefresh: () => void;
}

export default function AnalysisResultViewer({
  tasks,
  selectedTaskId,
  onSelectTask,
  onRefresh,
}: AnalysisResultViewerProps) {
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null);
  const [historyData, setHistoryData] = useState<ResearchHistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'detail'>('list');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [renderedContent, setRenderedContent] = useState<{[key: string]: string}>({});

  // 选中的任务
  const selectedTask = selectedTaskId ? tasks.find(task => task.id === selectedTaskId) : null;

  // 选中的历史记录
  const selectedHistory = selectedHistoryId 
    ? historyData.find(history => history.id === selectedHistoryId)
    : null;

  // 渲染markdown内容
  useEffect(() => {
    const renderMarkdownContent = async () => {
      if (selectedHistory) {
        const newRenderedContent: {[key: string]: string} = {};
        
        // 渲染摘要
        if (selectedHistory.summary) {
          try {
            newRenderedContent.summary = await markdownToHtml(selectedHistory.summary);
          } catch (error) {
            console.error('Failed to render summary markdown:', error);
            newRenderedContent.summary = selectedHistory.summary;
          }
        }
        
        // 渲染原始结果
        if (selectedHistory.raw_result) {
          try {
            newRenderedContent.raw_result = await markdownToHtml(selectedHistory.raw_result);
          } catch (error) {
            console.error('Failed to render raw_result markdown:', error);
            newRenderedContent.raw_result = selectedHistory.raw_result;
          }
        }
        
        setRenderedContent(newRenderedContent);
      }
    };
    
    renderMarkdownContent();
  }, [selectedHistory]);

  // 获取任务的历史记录
  const fetchTaskHistory = async (taskId: string) => {
    if (!taskId) return;
    
    setLoading(true);
    try {
      const response = await scheduledApiService.getTaskHistory(taskId, 1, 50);
      setHistoryData(response.items || []);
    } catch (error) {
      console.error('Error fetching task history:', error);
      setHistoryData([]);
    } finally {
      setLoading(false);
    }
  };

  // 当选中任务变化时，获取历史记录
  React.useEffect(() => {
    if (selectedTaskId) {
      fetchTaskHistory(selectedTaskId);
      setSelectedHistoryId(null);
    } else {
      setHistoryData([]);
      setSelectedHistoryId(null);
    }
  }, [selectedTaskId]);

  // 切换展开状态
  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  // 格式化JSON显示
  const formatJSON = (data: any) => {
    if (!data) return '无数据';
    if (typeof data === 'string') {
      try {
        return JSON.stringify(JSON.parse(data), null, 2);
      } catch {
        return data;
      }
    }
    return JSON.stringify(data, null, 2);
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'failed':
        return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'partial':
        return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      default:
        return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  // 渲染JSON数据
  const renderJSONSection = (title: string, data: any, sectionKey: string) => {
    const isExpanded = expandedSections.has(sectionKey);
    const hasData = data && (Array.isArray(data) ? data.length > 0 : Object.keys(data).length > 0);

    return (
      <div className="border border-gray-700/50 rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full px-4 py-3 bg-gray-800/30 hover:bg-gray-800/50 flex items-center justify-between transition-colors"
        >
          <div className="flex items-center gap-2">
            <span className="font-medium text-white">{title}</span>
            {hasData && (
              <span className="text-xs px-2 py-1 bg-teal-500/20 text-teal-400 rounded">
                {Array.isArray(data) ? `${data.length} 项` : '有数据'}
              </span>
            )}
          </div>
          <span className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </button>
        
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0 }}
              animate={{ height: 'auto' }}
              exit={{ height: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="p-4 bg-gray-900/50">
                {hasData ? (
                  sectionKey === 'raw_result' && renderedContent.raw_result ? (
                    <div className="text-sm text-gray-300 overflow-x-auto markdown-content">
                      <div dangerouslySetInnerHTML={{ __html: renderedContent.raw_result }} />
                    </div>
                  ) : (
                    <pre className="text-sm text-gray-300 overflow-x-auto whitespace-pre-wrap">
                      {formatJSON(data)}
                    </pre>
                  )
                ) : (
                  <p className="text-gray-500 italic">暂无数据</p>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* 标题和任务选择 */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">AI分析结果</h2>
          <p className="text-gray-300">
            查看每次定时研究的详细AI分析结果和JSON数据
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4">
          <select
            value={selectedTaskId || ''}
            onChange={(e) => onSelectTask(e.target.value || null)}
            className="px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
          >
            <option value="">选择任务查看分析结果</option>
            {tasks.map((task) => (
              <option key={task.id} value={task.id}>
                {task.topic} ({task.total_runs} 次执行)
              </option>
            ))}
          </select>
          
          <button
            onClick={onRefresh}
            className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors"
          >
            🔄 刷新
          </button>
        </div>
      </div>

      {!selectedTaskId ? (
        /* 未选择任务状态 */
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-white mb-2">选择任务查看分析结果</h3>
          <p className="text-gray-400">
            从上方下拉菜单中选择一个任务，查看其AI分析的详细结果
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 历史记录列表 */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">执行历史</h3>
                <span className="text-sm text-gray-400">
                  {historyData.length} 条记录
                </span>
              </div>
              
              {loading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-16 bg-gray-700/50 rounded-lg"></div>
                    </div>
                  ))}
                </div>
              ) : historyData.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">📝</div>
                  <p className="text-gray-400">暂无执行记录</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {historyData.map((history) => (
                    <div
                      key={history.id}
                      onClick={() => setSelectedHistoryId(history.id)}
                      className={`
                        p-3 rounded-lg border cursor-pointer transition-all
                        ${selectedHistoryId === history.id
                          ? 'border-teal-500/50 bg-teal-500/10'
                          : 'border-gray-700/50 hover:border-gray-600/50 hover:bg-gray-800/30'
                        }
                      `}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className={`text-xs px-2 py-1 rounded border ${getStatusColor(history.status)}`}>
                          {history.status === 'success' ? '成功' : 
                           history.status === 'failed' ? '失败' : '部分成功'}
                        </span>
                        <span className="text-xs text-gray-400">
                          {history.executed_at ? new Date(history.executed_at).toLocaleString('zh-CN', {
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit'
                          }) : '未知时间'}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-300 line-clamp-2 mb-2">
                        {history.summary || '无摘要'}
                      </p>
                      
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <span>🔗 {history.sources_count} 源</span>
                        <span>🎯 {history.trend_score?.toFixed(1) || 'N/A'}</span>
                        {history.execution_duration && (
                          <span>⏱️ {history.execution_duration.toFixed(1)}s</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* 详细分析结果 */}
          <div className="lg:col-span-2">
            {selectedHistory ? (
              <div className="space-y-6">
                {/* 基本信息 */}
                <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">执行信息</h3>
                  
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    <div>
                      <span className="text-sm text-gray-400">状态</span>
                      <div className={`mt-1 text-xs px-2 py-1 rounded border inline-block ${getStatusColor(selectedHistory.status)}`}>
                        {selectedHistory.status === 'success' ? '执行成功' : 
                         selectedHistory.status === 'failed' ? '执行失败' : '部分成功'}
                      </div>
                    </div>
                    
                    <div>
                      <span className="text-sm text-gray-400">执行时间</span>
                      <p className="text-white font-medium">
                        {selectedHistory.executed_at ? new Date(selectedHistory.executed_at).toLocaleString('zh-CN') : '未知时间'}
                      </p>
                    </div>
                    
                    <div>
                      <span className="text-sm text-gray-400">耗时</span>
                      <p className="text-white font-medium">
                        {selectedHistory.execution_duration?.toFixed(2) || 'N/A'}s
                      </p>
                    </div>
                    
                    <div>
                      <span className="text-sm text-gray-400">Token使用</span>
                      <p className="text-white font-medium">
                        {selectedHistory.tokens_used || 0}
                      </p>
                    </div>
                  </div>

                  {selectedHistory.summary && (
                    <div>
                      <span className="text-sm text-gray-400">AI摘要</span>
                      <div className="mt-2 text-gray-300 bg-gray-900/50 p-3 rounded-lg markdown-content">
                        {renderedContent.summary ? (
                          <div dangerouslySetInnerHTML={{ __html: renderedContent.summary }} />
                        ) : (
                          selectedHistory.summary
                        )}
                      </div>
                    </div>
                  )}

                  {selectedHistory.error_message && (
                    <div className="mt-4">
                      <span className="text-sm text-red-400">错误信息</span>
                      <p className="mt-2 text-red-300 bg-red-500/10 p-3 rounded-lg border border-red-500/30">
                        {selectedHistory.error_message}
                      </p>
                    </div>
                  )}
                </div>

                {/* JSON数据展示 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white">详细分析数据</h3>
                  
                  {renderJSONSection('关键发现', selectedHistory.key_findings, 'key_findings')}
                  {renderJSONSection('关键变化', selectedHistory.key_changes, 'key_changes')}
                  {renderJSONSection('使用的信息源', selectedHistory.sources_used, 'sources_used')}
                  {renderJSONSection('研究配置', selectedHistory.research_config, 'research_config')}
                  
                  {selectedHistory.raw_result && (
                    renderJSONSection('原始研究结果', selectedHistory.raw_result, 'raw_result')
                  )}
                </div>

                {/* 统计指标 */}
                <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">分析指标</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-teal-400">
                        {selectedHistory.trend_score?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-400">趋势分数</div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">
                        {selectedHistory.sentiment_score?.toFixed(2) || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-400">情感分数</div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-400">
                        {selectedHistory.sources_count}
                      </div>
                      <div className="text-sm text-gray-400">信息源数量</div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-12 text-center">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-white mb-2">选择执行记录</h3>
                <p className="text-gray-400">
                  从左侧列表中选择一个执行记录，查看详细的AI分析结果
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
