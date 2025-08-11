/**
 * 定时研究WebSocket管理Hook
 * Scheduled Research WebSocket Management Hook
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { ScheduledResultMessage } from '@/types/data';
import { getHost } from '@/helpers/getHost';

interface UseScheduledWebSocketOptions {
  onScheduledResult?: (message: ScheduledResultMessage) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export const useScheduledWebSocket = (options: UseScheduledWebSocketOptions = {}) => {
  const {
    onScheduledResult,
    onError,
    onConnect,
    onDisconnect,
    autoConnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const [lastMessage, setLastMessage] = useState<ScheduledResultMessage | null>(null);
  const [error, setError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManuallyDisconnectedRef = useRef(false);
  const isConnectingRef = useRef(false);
  const connectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastConnectTimeRef = useRef(0);

  // 获取WebSocket URL
  const getWebSocketUrl = useCallback(() => {
    if (typeof window === 'undefined') return '';
    
    const host = getHost();
    const protocol = host.includes('https') ? 'wss:' : 'ws:';
    const cleanHost = host.replace('http://', '').replace('https://', '');
    return `${protocol}//${cleanHost}/ws`;
  }, []);

  // 清理重连定时器
  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  // 连接WebSocket
  const connect = useCallback(() => {
    // 防止重复连接
    if (socketRef.current?.readyState === WebSocket.OPEN || isConnectingRef.current) {
      return; // 已经连接或正在连接
    }

    // 防抖：限制连接频率
    const now = Date.now();
    if (now - lastConnectTimeRef.current < 1000) {
      return; // 1秒内只能连接一次
    }
    lastConnectTimeRef.current = now;

    const wsUrl = getWebSocketUrl();
    if (!wsUrl) return;

    try {
      isConnectingRef.current = true;
      setConnectionStatus('connecting');
      setError(null);
      isManuallyDisconnectedRef.current = false;

      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        isConnectingRef.current = false;
        setIsConnected(true);
        setConnectionStatus('connected');
        setError(null); // 清除之前的错误
        reconnectAttemptsRef.current = 0; // 重置重连计数
        onConnect?.();
        
        if (process.env.NODE_ENV === 'development') {
          console.log('📡 Scheduled WebSocket connected');
        }
      };

      socket.onmessage = (event) => {
        // 处理心跳响应
        if (event.data === 'pong') {
          // 心跳响应，不需要处理
          return;
        }
        
        try {
          const data = JSON.parse(event.data);
          
          // 处理定时研究结果消息
          if (data.type === 'scheduled_result') {
            const message = data as ScheduledResultMessage;
            setLastMessage(message);
            onScheduledResult?.(message);
          }
        } catch (err) {
          // 只在开发环境下输出非JSON消息的错误
          if (process.env.NODE_ENV === 'development' && event.data !== 'pong') {
            console.warn('Received non-JSON WebSocket message:', event.data);
          }
        }
      };

      socket.onclose = (event) => {
        isConnectingRef.current = false;
        setIsConnected(false);
        setConnectionStatus('disconnected');
        socketRef.current = null;
        onDisconnect?.();

        // 只在调试模式下输出详细日志
        if (process.env.NODE_ENV === 'development') {
          console.log('📡 Scheduled WebSocket disconnected:', event.code, event.reason);
        }

        // 自动重连（如果不是手动断开且重连次数未超限）
        // 对于连接拒绝(1006)等错误，增加重连间隔
        if (!isManuallyDisconnectedRef.current && 
            autoConnect && 
            reconnectAttemptsRef.current < maxReconnectAttempts) {
          
          reconnectAttemptsRef.current++;
          
          // 如果是连接被拒绝，使用更长的重连间隔
          const retryInterval = event.code === 1006 ? 
            Math.min(reconnectInterval * reconnectAttemptsRef.current, 30000) : // 最长30秒
            reconnectInterval;

          if (process.env.NODE_ENV === 'development') {
            console.log(`📡 Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts}) in ${retryInterval/1000}s...`);
          }
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, retryInterval);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('无法连接到服务器，请检查后端服务是否正常运行');
        }
      };

      socket.onerror = (event) => {
        isConnectingRef.current = false;
        
        // 只在开发模式下输出详细错误
        if (process.env.NODE_ENV === 'development') {
          console.error('📡 Scheduled WebSocket error:', event);
        }
        
        // 设置用户友好的错误信息
        if (reconnectAttemptsRef.current === 0) {
          setError('正在尝试连接到服务器...');
        }
        
        // 特殊处理资源不足错误
        const target = event.target as WebSocket;
        if (target.readyState === WebSocket.CONNECTING) {
          // 连接建立失败，可能是资源不足
          setError('连接失败，请稍后重试');
        }
        
        onError?.(event);
      };

    } catch (err) {
      isConnectingRef.current = false;
      console.error('Failed to create WebSocket connection:', err);
      setError('无法创建WebSocket连接');
      setConnectionStatus('disconnected');
    }
  }, [getWebSocketUrl, onConnect, onDisconnect, onScheduledResult, onError, autoConnect, reconnectInterval, maxReconnectAttempts]);

  // 断开连接
  const disconnect = useCallback(() => {
    isManuallyDisconnectedRef.current = true;
    isConnectingRef.current = false;
    clearReconnectTimeout();
    
    if (socketRef.current) {
      socketRef.current.close(1000, 'Manual disconnect');
      socketRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, [clearReconnectTimeout]);

  // 发送消息
  const sendMessage = useCallback((message: any) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      try {
        socketRef.current.send(JSON.stringify(message));
      } catch (err) {
        console.error('Failed to send WebSocket message:', err);
        setError('发送消息失败');
      }
    } else {
      console.warn('WebSocket is not connected, cannot send message');
      setError('WebSocket未连接');
    }
  }, []);

  // 重新连接
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(() => {
      connect();
    }, 1000);
  }, [disconnect, connect]);

  // 初始化连接
  useEffect(() => {
    if (autoConnect) {
      // 延迟连接，避免组件挂载时的竞态条件
      connectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 100);
    }

    return () => {
      clearReconnectTimeout();
      if (connectTimeoutRef.current) {
        clearTimeout(connectTimeoutRef.current);
      }
      if (socketRef.current) {
        isManuallyDisconnectedRef.current = true;
        socketRef.current.close();
      }
    };
  }, [autoConnect]); // 移除connect和clearReconnectTimeout依赖，避免无限循环

  // 心跳检测
  useEffect(() => {
    if (!isConnected) return;

    const heartbeatInterval = setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send('ping');
      }
    }, 30000); // 每30秒发送一次心跳

    return () => clearInterval(heartbeatInterval);
  }, [isConnected]);

  return {
    // 状态
    isConnected,
    connectionStatus,
    lastMessage,
    error,
    reconnectAttempts: reconnectAttemptsRef.current,

    // 方法
    connect,
    disconnect,
    reconnect,
    sendMessage,

    // 工具方法
    clearError: () => setError(null),
  };
};
