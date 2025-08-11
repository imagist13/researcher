"use client";

import React, { useState, useEffect } from 'react';
import { ScheduledTask, UpdateTaskRequest } from '@/types/data';
import { motion, AnimatePresence } from 'framer-motion';

interface TaskEditModalProps {
  task: ScheduledTask;
  onSave: (updateData: UpdateTaskRequest) => Promise<void>;
  onCancel: () => void;
}

export default function TaskEditModal({
  task,
  onSave,
  onCancel,
}: TaskEditModalProps) {
  const [formData, setFormData] = useState<UpdateTaskRequest>({
    topic: task.topic,
    keywords: task.keywords,
    description: task.description || '',
    interval_hours: task.interval_hours,
    analysis_depth: task.analysis_depth,
    source_types: task.source_types,
    is_active: task.is_active,
    max_sources: task.max_sources,
    enable_notifications: task.enable_notifications,
    notification_threshold: task.notification_threshold,
  });

  const [keywordInput, setKeywordInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // 处理关键词输入
  const handleAddKeyword = () => {
    if (keywordInput.trim() && !formData.keywords?.includes(keywordInput.trim())) {
      setFormData(prev => ({
        ...prev,
        keywords: [...(prev.keywords || []), keywordInput.trim()]
      }));
      setKeywordInput('');
    }
  };

  const handleRemoveKeyword = (index: number) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords?.filter((_, i) => i !== index) || []
    }));
  };

  // 处理信息源类型切换
  const handleSourceTypeToggle = (sourceType: string) => {
    setFormData(prev => {
      const currentTypes = prev.source_types || [];
      const newTypes = currentTypes.includes(sourceType)
        ? currentTypes.filter(type => type !== sourceType)
        : [...currentTypes, sourceType];
      
      return {
        ...prev,
        source_types: newTypes
      };
    });
  };

  // 表单验证
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.topic?.trim()) {
      newErrors.topic = '请输入研究话题';
    }

    if (!formData.keywords || formData.keywords.length === 0) {
      newErrors.keywords = '请至少添加一个关键词';
    }

    if (!formData.interval_hours || formData.interval_hours < 1 || formData.interval_hours > 168) {
      newErrors.interval_hours = '执行间隔必须在1-168小时之间';
    }

    if (!formData.source_types || formData.source_types.length === 0) {
      newErrors.source_types = '请至少选择一个信息源类型';
    }

    if (!formData.max_sources || formData.max_sources < 1 || formData.max_sources > 50) {
      newErrors.max_sources = '最大来源数必须在1-50之间';
    }

    if (formData.notification_threshold !== undefined && 
        (formData.notification_threshold < 0 || formData.notification_threshold > 10)) {
      newErrors.notification_threshold = '通知阈值必须在0-10之间';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 提交表单
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setSaving(true);
    try {
      await onSave(formData);
    } catch (error) {
      console.error('Failed to save task:', error);
    } finally {
      setSaving(false);
    }
  };

  // 预设配置选项
  const sourceTypeOptions = [
    { key: 'news', label: '新闻', icon: '📰' },
    { key: 'academic', label: '学术', icon: '🎓' },
    { key: 'social_media', label: '社交媒体', icon: '📱' },
    { key: 'industry_reports', label: '行业报告', icon: '📊' },
    { key: 'government', label: '政府', icon: '🏛️' },
    { key: 'financial', label: '金融', icon: '💰' },
  ];

  const intervalOptions = [
    { value: 1, label: '1小时' },
    { value: 6, label: '6小时' },
    { value: 12, label: '12小时' },
    { value: 24, label: '24小时' },
    { value: 48, label: '48小时' },
    { value: 72, label: '72小时' },
    { value: 168, label: '1周' },
  ];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        onClick={onCancel}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gray-900/95 backdrop-blur-md rounded-lg border border-gray-700/50 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 模态框头部 */}
          <div className="flex items-center justify-between p-6 border-b border-gray-700/50">
            <h2 className="text-xl font-bold text-white">编辑任务</h2>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <span className="text-2xl">×</span>
            </button>
          </div>

          {/* 表单内容 */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* 基本信息 */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">基本信息</h3>
              
              {/* 研究话题 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  研究话题 *
                </label>
                <input
                  type="text"
                  value={formData.topic || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, topic: e.target.value }))}
                  className={`w-full px-3 py-2 bg-gray-800/50 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 transition-all ${
                    errors.topic ? 'border-red-500 focus:ring-red-500/20' : 'border-gray-700/50 focus:ring-teal-500/20 focus:border-teal-500'
                  }`}
                  placeholder="例如：人工智能技术发展趋势"
                />
                {errors.topic && <p className="text-red-400 text-sm mt-1">{errors.topic}</p>}
              </div>

              {/* 任务描述 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  任务描述
                </label>
                <textarea
                  value={formData.description || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                  placeholder="描述此任务的目的和需求（可选）"
                />
              </div>

              {/* 关键词 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  关键词 *
                </label>
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={keywordInput}
                      onChange={(e) => setKeywordInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddKeyword())}
                      className="flex-1 px-3 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                      placeholder="输入关键词后按回车添加"
                    />
                    <button
                      type="button"
                      onClick={handleAddKeyword}
                      className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors"
                    >
                      添加
                    </button>
                  </div>
                  
                  {formData.keywords && formData.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {formData.keywords.map((keyword, index) => (
                        <span
                          key={index}
                          className="flex items-center gap-1 px-2 py-1 bg-teal-500/20 text-teal-300 text-sm rounded-full"
                        >
                          {keyword}
                          <button
                            type="button"
                            onClick={() => handleRemoveKeyword(index)}
                            className="text-teal-200 hover:text-white transition-colors"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                  
                  {errors.keywords && <p className="text-red-400 text-sm">{errors.keywords}</p>}
                </div>
              </div>
            </div>

            {/* 执行配置 */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">执行配置</h3>
              
              {/* 执行间隔 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  执行间隔 *
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {intervalOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, interval_hours: option.value }))}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        formData.interval_hours === option.value
                          ? 'bg-teal-600 text-white'
                          : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
                {errors.interval_hours && <p className="text-red-400 text-sm mt-1">{errors.interval_hours}</p>}
              </div>

              {/* 分析深度 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  分析深度
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { key: 'basic', label: '基础', desc: '快速概览' },
                    { key: 'detailed', label: '详细', desc: '深入分析' },
                    { key: 'deep', label: '深度', desc: '全面研究' },
                  ].map((option) => (
                    <button
                      key={option.key}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, analysis_depth: option.key as any }))}
                      className={`p-3 rounded-lg text-center transition-all ${
                        formData.analysis_depth === option.key
                          ? 'bg-teal-600 text-white'
                          : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
                      }`}
                    >
                      <div className="font-medium">{option.label}</div>
                      <div className="text-xs opacity-75">{option.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 信息源类型 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  信息源类型 *
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {sourceTypeOptions.map((option) => (
                    <button
                      key={option.key}
                      type="button"
                      onClick={() => handleSourceTypeToggle(option.key)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
                        formData.source_types?.includes(option.key)
                          ? 'bg-teal-600 text-white'
                          : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
                      }`}
                    >
                      <span>{option.icon}</span>
                      <span>{option.label}</span>
                    </button>
                  ))}
                </div>
                {errors.source_types && <p className="text-red-400 text-sm mt-1">{errors.source_types}</p>}
              </div>

              {/* 高级设置 */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    最大来源数
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={formData.max_sources || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, max_sources: parseInt(e.target.value) || 10 }))}
                    className={`w-full px-3 py-2 bg-gray-800/50 border rounded-lg text-white focus:outline-none focus:ring-2 transition-all ${
                      errors.max_sources ? 'border-red-500 focus:ring-red-500/20' : 'border-gray-700/50 focus:ring-teal-500/20 focus:border-teal-500'
                    }`}
                  />
                  {errors.max_sources && <p className="text-red-400 text-sm mt-1">{errors.max_sources}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    通知阈值
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    step="0.1"
                    value={formData.notification_threshold || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, notification_threshold: parseFloat(e.target.value) || 7.0 }))}
                    className={`w-full px-3 py-2 bg-gray-800/50 border rounded-lg text-white focus:outline-none focus:ring-2 transition-all ${
                      errors.notification_threshold ? 'border-red-500 focus:ring-red-500/20' : 'border-gray-700/50 focus:ring-teal-500/20 focus:border-teal-500'
                    }`}
                  />
                  {errors.notification_threshold && <p className="text-red-400 text-sm mt-1">{errors.notification_threshold}</p>}
                </div>
              </div>
            </div>

            {/* 任务状态 */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">任务状态</h3>
              
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_active || false}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                    className="w-5 h-5 text-teal-600 bg-gray-800 border-gray-600 rounded focus:ring-teal-500 focus:ring-2"
                  />
                  <span className="text-gray-300">启用任务</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.enable_notifications || false}
                    onChange={(e) => setFormData(prev => ({ ...prev, enable_notifications: e.target.checked }))}
                    className="w-5 h-5 text-teal-600 bg-gray-800 border-gray-600 rounded focus:ring-teal-500 focus:ring-2"
                  />
                  <span className="text-gray-300">启用通知</span>
                </label>
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-3 pt-4 border-t border-gray-700/50">
              <button
                type="button"
                onClick={onCancel}
                disabled={saving}
                className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={saving}
                className="flex-1 px-4 py-2 bg-teal-600 hover:bg-teal-700 disabled:bg-gray-600 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {saving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    保存中...
                  </>
                ) : (
                  '保存更改'
                )}
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
