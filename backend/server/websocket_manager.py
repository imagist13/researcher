import asyncio
import datetime
import json
from typing import Dict, List

from fastapi import WebSocket

from ..report_type import BasicReport, DetailedReport
from ..chat import ChatAgentWithMemory

from gpt_researcher.utils.enum import ReportType, Tone
from multi_agents.main import run_research_task
from gpt_researcher.actions import stream_output  # Import stream_output
from .server_utils import CustomLogsHandler


class WebSocketManager:
    """Manage websockets"""

    def __init__(self):
        """Initialize the WebSocketManager class."""
        self.active_connections: List[WebSocket] = []
        self.sender_tasks: Dict[WebSocket, asyncio.Task] = {}
        self.message_queues: Dict[WebSocket, asyncio.Queue] = {}
        self.chat_agent = None

    async def start_sender(self, websocket: WebSocket):
        """Start the sender task."""
        queue = self.message_queues.get(websocket)
        if not queue:
            return

        while True:
            try:
                message = await queue.get()
                if message is None:  # Shutdown signal
                    break
                    
                if websocket in self.active_connections:
                    if message == "ping":
                        await websocket.send_text("pong")
                    else:
                        await websocket.send_text(message)
                else:
                    break
            except Exception as e:
                print(f"Error in sender task: {e}")
                break

    async def connect(self, websocket: WebSocket):
        """Connect a websocket."""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            self.message_queues[websocket] = asyncio.Queue()
            self.sender_tasks[websocket] = asyncio.create_task(
                self.start_sender(websocket))
        except Exception as e:
            print(f"Error connecting websocket: {e}")
            if websocket in self.active_connections:
                await self.disconnect(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.sender_tasks:
                self.sender_tasks[websocket].cancel()
                await self.message_queues[websocket].put(None)
                del self.sender_tasks[websocket]
            if websocket in self.message_queues:
                del self.message_queues[websocket]
            try:
                await websocket.close()
            except:
                pass  # Connection might already be closed

    async def start_streaming(self, task, report_type, report_source, source_urls, document_urls, tone, websocket, headers=None, query_domains=[], mcp_enabled=False, mcp_strategy="fast", mcp_configs=[]):
        """Start streaming the output."""
        tone = Tone[tone]
        # add customized JSON config file path here
        config_path = "default"
        
        # Pass MCP parameters to run_agent
        report = await run_agent(
            task, report_type, report_source, source_urls, document_urls, tone, websocket, 
            headers=headers, query_domains=query_domains, config_path=config_path,
            mcp_enabled=mcp_enabled, mcp_strategy=mcp_strategy, mcp_configs=mcp_configs
        )
        
        # Create new Chat Agent whenever a new report is written
        self.chat_agent = ChatAgentWithMemory(report, config_path, headers)
        return report

    async def chat(self, message, websocket):
        """Chat with the agent based message diff"""
        if self.chat_agent:
            await self.chat_agent.chat(message, websocket)
        else:
            await websocket.send_json({"type": "chat", "content": "Knowledge empty, please run the research first to obtain knowledge"})

    async def broadcast_scheduled_result(self, result_data):
        """Broadcast scheduled research results to all connected clients"""
        if not self.active_connections:
            return

        message = json.dumps({
            "type": "scheduled_result",
            "task_id": result_data.get("task_id"),
            "topic": result_data.get("topic"),
            "timestamp": result_data.get("timestamp"),
            "summary": result_data.get("summary"),
            "key_changes": result_data.get("key_changes", []),
            "trend_score": result_data.get("trend_score", 0),
            "sources_count": result_data.get("sources_count", 0),
            "status": result_data.get("status", "completed"),
            "execution_time": result_data.get("execution_time", 0)
        })

        # 发送给所有连接的客户端
        disconnected_websockets = []
        for websocket in self.active_connections:
            try:
                queue = self.message_queues.get(websocket)
                if queue:
                    await queue.put(message)
            except Exception as e:
                print(f"Error broadcasting to websocket: {e}")
                disconnected_websockets.append(websocket)

        # 清理断开的连接
        for websocket in disconnected_websockets:
            await self.disconnect(websocket)

    async def send_scheduled_notification(self, notification_data):
        """Send scheduled research notification to all connected clients"""
        if not self.active_connections:
            return

        message = json.dumps({
            "type": "scheduled_notification",
            "title": notification_data.get("title", "定时研究通知"),
            "message": notification_data.get("message"),
            "level": notification_data.get("level", "info"),  # info, warning, error
            "task_id": notification_data.get("task_id"),
            "timestamp": notification_data.get("timestamp")
        })

        # 发送通知给所有连接的客户端
        for websocket in self.active_connections:
            try:
                queue = self.message_queues.get(websocket)
                if queue:
                    await queue.put(message)
            except Exception as e:
                print(f"Error sending notification to websocket: {e}")

    async def broadcast_scheduler_status(self, status_data):
        """Broadcast scheduler status changes to all connected clients"""
        if not self.active_connections:
            return

        message = json.dumps({
            "type": "scheduler_status",
            "running": status_data.get("running", False),
            "total_jobs": status_data.get("total_jobs", 0),
            "running_tasks": status_data.get("running_tasks", []),
            "timestamp": status_data.get("timestamp")
        })

        # 发送状态更新给所有连接的客户端
        for websocket in self.active_connections:
            try:
                queue = self.message_queues.get(websocket)
                if queue:
                    await queue.put(message)
            except Exception as e:
                print(f"Error broadcasting scheduler status: {e}")

async def run_agent(task, report_type, report_source, source_urls, document_urls, tone: Tone, websocket, stream_output=stream_output, headers=None, query_domains=[], config_path="", return_researcher=False, mcp_enabled=False, mcp_strategy="fast", mcp_configs=[]):
    """Run the agent."""    
    # Create logs handler for this research task
    logs_handler = CustomLogsHandler(websocket, task)
    
    try:
        # Set up MCP configuration if enabled
        if mcp_enabled and mcp_configs:
            import os
            current_retriever = os.getenv("RETRIEVER", "tavily")
            if "mcp" not in current_retriever:
                # Add MCP to existing retrievers
                os.environ["RETRIEVER"] = f"{current_retriever},mcp"
            
            # Set MCP strategy
            os.environ["MCP_STRATEGY"] = mcp_strategy
            
            print(f"🔧 MCP enabled with strategy '{mcp_strategy}' and {len(mcp_configs)} server(s)")
            await logs_handler.send_json({
                "type": "logs",
                "content": "mcp_init",
                "output": f"🔧 MCP enabled with strategy '{mcp_strategy}' and {len(mcp_configs)} server(s)"
            })

        # Initialize researcher based on report type
        if report_type == "multi_agents":
            report = await run_research_task(
                query=task, 
                websocket=logs_handler,  # Use logs_handler instead of raw websocket
                stream_output=stream_output, 
                tone=tone, 
                headers=headers
            )
            report = report.get("report", "")

        elif report_type == ReportType.DetailedReport.value:
            researcher = DetailedReport(
                query=task,
                query_domains=query_domains,
                report_type=report_type,
                report_source=report_source,
                source_urls=source_urls,
                document_urls=document_urls,
                tone=tone,
                config_path=config_path,
                websocket=logs_handler,  # Use logs_handler instead of raw websocket
                headers=headers,
                mcp_configs=mcp_configs if mcp_enabled else None,
                mcp_strategy=mcp_strategy if mcp_enabled else None,
            )
            report = await researcher.run()
            
        else:
            researcher = BasicReport(
                query=task,
                query_domains=query_domains,
                report_type=report_type,
                report_source=report_source,
                source_urls=source_urls,
                document_urls=document_urls,
                tone=tone,
                config_path=config_path,
                websocket=logs_handler,  # Use logs_handler instead of raw websocket
                headers=headers,
                mcp_configs=mcp_configs if mcp_enabled else None,
                mcp_strategy=mcp_strategy if mcp_enabled else None,
            )
            report = await researcher.run()

        if report_type != "multi_agents" and return_researcher:
            return report, researcher.gpt_researcher
        else:
            return report
            
    except Exception as e:
        print(f"❌ Error during research: {str(e)}")
        
        # 使用错误处理器创建标准化响应
        from .error_handler import create_error_response, generate_error_report
        
        error_response = create_error_response(e, task, report_type)
        
        # 发送错误信息到前端
        await logs_handler.send_json(error_response)
        
        # 返回用户友好的错误报告
        error_report = generate_error_report(e, task, report_type)
        return error_report
