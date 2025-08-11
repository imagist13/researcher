"use client";

import React, { useState } from 'react';
import { ScheduledTask, CreateTaskRequest } from '@/types/data';

interface TaskConfigurationProps {
  onTaskCreated: (task: ScheduledTask) => void;
  onCreateTask: (taskData: CreateTaskRequest) => Promise<ScheduledTask | null>;
}

export default function TaskConfiguration({
  onTaskCreated,
  onCreateTask,
}: TaskConfigurationProps) {
  const [formData, setFormData] = useState<CreateTaskRequest>({
    topic: '',
    keywords: [],
    description: '',
    interval_hours: 24,
    analysis_depth: 'basic',
    source_types: ['web'],
    report_type: 'research_report',
    report_source: 'web',
    tone: 'objective',
    query_domains: [],
    max_sources: 10,
    language: 'zh-CN',
    enable_notifications: true,
    notification_threshold: 0.0,
  });

  const [keywordInput, setKeywordInput] = useState('');
  const [domainInput, setDomainInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 报告类型选项
  const reportTypeOptions = [
    { value: 'research_report', label: '研究报告', description: '标准的研究报告格式' },
    { value: 'detailed_report', label: '详细报告', description: '包含更多细节的深入分析' },
    { value: 'deep', label: '深度研究', description: '使用 Deep Research 的递归研究模式' },
    { value: 'outline_report', label: '大纲报告', description: '结构化的研究大纲' },
    { value: 'subtopic_report', label: '子主题报告', description: '专注于特定子主题的分析' },
  ];

  // 分析深度选项
  const analysisDepthOptions = [
    { value: 'basic', label: '基础分析', description: '快速概览和基本趋势' },
    { value: 'detailed', label: '详细分析', description: '深入分析和多维度对比' },
    { value: 'deep', label: '深度分析', description: '最全面的分析和洞察' },
  ];

  // 语调选项
  const toneOptions = [
    { value: 'objective', label: '客观', description: '中立、无偏见的陈述' },
    { value: 'analytical', label: '分析性', description: '批判性评估和详细检查' },
    { value: 'informative', label: '信息性', description: '清晰全面的信息提供' },
    { value: 'formal', label: '正式', description: '学术标准的高级语言' },
  ];

  const handleInputChange = (field: keyof CreateTaskRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const addKeyword = () => {
    if (keywordInput.trim() && !formData.keywords.includes(keywordInput.trim())) {
      setFormData(prev => ({
        ...prev,
        keywords: [...prev.keywords, keywordInput.trim()]
      }));
      setKeywordInput('');
    }
  };

  const removeKeyword = (index: number) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords.filter((_, i) => i !== index)
    }));
  };

  const addDomain = () => {
    if (domainInput.trim() && !(formData.query_domains || []).includes(domainInput.trim())) {
      setFormData(prev => ({
        ...prev,
        query_domains: [...(prev.query_domains || []), domainInput.trim()]
      }));
      setDomainInput('');
    }
  };

  const removeDomain = (index: number) => {
    setFormData(prev => ({
      ...prev,
      query_domains: (prev.query_domains || []).filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const newTask = await onCreateTask(formData);
      if (newTask) {
        onTaskCreated(newTask);
        // 重置表单
        setFormData({
          topic: '',
          keywords: [],
          description: '',
          interval_hours: 24,
          analysis_depth: 'basic',
          source_types: ['web'],
          report_type: 'research_report',
          report_source: 'web',
          tone: 'objective',
          query_domains: [],
          max_sources: 10,
          language: 'zh-CN',
          enable_notifications: true,
          notification_threshold: 0.0,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建任务失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">创建新任务</h2>
        <p className="text-gray-300">
          配置新的定时研究任务，设置话题、关键词和执行参数
        </p>
      </div>

      {/* 配置表单 */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 基础配置 */}
        <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-semibold text-white mb-4">基础配置</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                研究话题 *
              </label>
              <input
                type="text"
                required
                value={formData.topic}
                onChange={(e) => handleInputChange('topic', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="输入研究话题..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                执行间隔 (小时)
              </label>
              <select
                value={formData.interval_hours}
                onChange={(e) => handleInputChange('interval_hours', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>1 小时</option>
                <option value={6}>6 小时</option>
                <option value={12}>12 小时</option>
                <option value={24}>24 小时</option>
                <option value={48}>48 小时</option>
                <option value={168}>1 周</option>
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              任务描述
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="描述研究目标和重点..."
            />
          </div>
        </div>

        {/* 研究配置 */}
        <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-semibold text-white mb-4">研究配置</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                报告类型 *
              </label>
              <select
                value={formData.report_type}
                onChange={(e) => handleInputChange('report_type', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {reportTypeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {formData.report_type === 'deep' && (
                <p className="text-xs text-blue-400 mt-1">
                  🌟 Deep Research 模式：使用递归研究，深度探索主题
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                分析深度
              </label>
              <select
                value={formData.analysis_depth}
                onChange={(e) => handleInputChange('analysis_depth', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {analysisDepthOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                报告语调
              </label>
              <select
                value={formData.tone}
                onChange={(e) => handleInputChange('tone', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {toneOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                最大信息源数量
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={formData.max_sources}
                onChange={(e) => handleInputChange('max_sources', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 关键词配置 */}
        <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-semibold text-white mb-4">关键词配置</h3>
          
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addKeyword())}
              className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入关键词..."
            />
            <button
              type="button"
              onClick={addKeyword}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              添加
            </button>
          </div>

          {formData.keywords.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {formData.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-600 text-white"
                >
                  {keyword}
                  <button
                    type="button"
                    onClick={() => removeKeyword(index)}
                    className="ml-2 text-blue-200 hover:text-white"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* 高级配置 */}
        <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-semibold text-white mb-4">高级配置</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                查询域名限制
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={domainInput}
                  onChange={(e) => setDomainInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDomain())}
                  className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="输入域名 (如: example.com)"
                />
                <button
                  type="button"
                  onClick={addDomain}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  添加
                </button>
              </div>
              
              {formData.query_domains && formData.query_domains.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.query_domains.map((domain, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-600 text-gray-300"
                    >
                      {domain}
                      <button
                        type="button"
                        onClick={() => removeDomain(index)}
                        className="ml-1 text-gray-400 hover:text-white"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                通知设置
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.enable_notifications}
                    onChange={(e) => handleInputChange('enable_notifications', e.target.checked)}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-300">启用通知</span>
                </label>
                
                {formData.enable_notifications && (
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">
                      趋势变化阈值 (0-10)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={formData.notification_threshold}
                      onChange={(e) => handleInputChange('notification_threshold', parseFloat(e.target.value))}
                      className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 提交按钮 */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !formData.topic.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '创建中...' : '创建定时任务'}
          </button>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4 text-red-300">
            <p className="font-medium">创建任务失败</p>
            <p className="text-sm">{error}</p>
          </div>
        )}
      </form>
    </div>
  );
}
