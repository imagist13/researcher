// 性能优化配置
export const PERFORMANCE_CONFIG = {
  // 懒加载配置
  LAZY_LOADING: {
    // 组件懒加载延迟（毫秒）
    COMPONENT_DELAY: 100,
    // 图表懒加载延迟
    CHART_DELAY: 200,
    // 图片懒加载配置
    IMAGE_LOADING: 'lazy' as const,
  },

  // 虚拟化配置
  VIRTUALIZATION: {
    // 任务列表虚拟化
    TASK_LIST: {
      ITEM_HEIGHT: 120,
      MAX_VISIBLE_ITEMS: 10,
      BUFFER_SIZE: 3,
    },
    // 历史记录虚拟化
    HISTORY_LIST: {
      ITEM_HEIGHT: 80,
      MAX_VISIBLE_ITEMS: 15,
      BUFFER_SIZE: 5,
    },
  },

  // 数据更新配置
  DATA_REFRESH: {
    // 防抖延迟（毫秒）
    DEBOUNCE_DELAY: 1000,
    // 自动刷新间隔（毫秒）
    AUTO_REFRESH_INTERVAL: 30000,
    // 最大重试次数
    MAX_RETRY_COUNT: 3,
  },

  // WebSocket配置
  WEBSOCKET: {
    // 重连延迟（毫秒）
    RECONNECT_DELAY: 5000,
    // 最大重连次数
    MAX_RECONNECT_ATTEMPTS: 5,
    // 心跳间隔（毫秒）
    HEARTBEAT_INTERVAL: 30000,
  },

  // 缓存配置
  CACHE: {
    // 组件缓存时间（毫秒）
    COMPONENT_CACHE_TTL: 300000, // 5分钟
    // 数据缓存时间
    DATA_CACHE_TTL: 60000, // 1分钟
    // 最大缓存条目数
    MAX_CACHE_ENTRIES: 100,
  },

  // 动画配置
  ANIMATIONS: {
    // 是否启用动画
    ENABLED: true,
    // 动画持续时间
    DURATION: {
      SHORT: 200,
      MEDIUM: 300,
      LONG: 500,
    },
    // 缓动函数
    EASING: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // 内存管理
  MEMORY: {
    // 组件卸载时清理延迟
    CLEANUP_DELAY: 5000,
    // 最大并发请求数
    MAX_CONCURRENT_REQUESTS: 5,
    // 图片压缩质量
    IMAGE_QUALITY: 0.8,
  },
} as const;

// 性能监控配置
export const PERFORMANCE_MONITORING = {
  // 是否启用性能监控
  ENABLED: process.env.NODE_ENV === 'development',
  
  // 监控指标
  METRICS: {
    // 组件渲染时间
    COMPONENT_RENDER_TIME: true,
    // 数据加载时间
    DATA_LOADING_TIME: true,
    // 内存使用情况
    MEMORY_USAGE: true,
    // WebSocket连接状态
    WEBSOCKET_STATUS: true,
  },

  // 警告阈值
  THRESHOLDS: {
    // 组件渲染时间警告阈值（毫秒）
    RENDER_TIME_WARNING: 100,
    // 数据加载时间警告阈值
    LOADING_TIME_WARNING: 2000,
    // 内存使用警告阈值（MB）
    MEMORY_WARNING: 100,
  },
} as const;

// 导出类型
export type PerformanceConfig = typeof PERFORMANCE_CONFIG;
export type PerformanceMonitoring = typeof PERFORMANCE_MONITORING;
