# backend/app/api/routes/websocket.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

from ...core.security import get_current_user_ws
from ...services.github_service import GitHubService
from ...models.schemas import WebSocketMessage
from ...db.session import get_db

router = APIRouter(tags=["websocket"])

# Store active connections
class ConnectionManager:
    def __init__(self):
        # Store WebSocket connections by user ID
        self.active_connections: Dict[int, WebSocket] = {}
        # Store PR subscriptions by user ID
        self.pr_subscriptions: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.pr_subscriptions[user_id] = set()
    
    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
        self.pr_subscriptions.pop(user_id, None)
    
    def subscribe_to_pr(self, user_id: int, pr_id: int):
        if user_id in self.pr_subscriptions:
            self.pr_subscriptions[user_id].add(pr_id)
    
    def unsubscribe_from_pr(self, user_id: int, pr_id: int):
        if user_id in self.pr_subscriptions:
            self.pr_subscriptions[user_id].discard(pr_id)
    
    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast_to_pr(self, message: dict, pr_id: int):
        for user_id, subscribed_prs in self.pr_subscriptions.items():
            if pr_id in subscribed_prs:
                await self.send_personal_message(message, user_id)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = None
):
    try:
        # Authenticate user
        user = await get_current_user_ws(token)
        if not user:
            await websocket.close(code=4001, reason="Unauthorized")
            return
        
        # Connect to WebSocket
        await manager.connect(websocket, user.id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_websocket_message(message, user.id)
                
        except WebSocketDisconnect:
            manager.disconnect(user.id)
            
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))

async def handle_websocket_message(message: dict, user_id: int):
    """Handle incoming WebSocket messages"""
    try:
        message_type = message.get("type")
        payload = message.get("payload", {})
        
        if message_type == "subscribe_pr":
            pr_id = payload.get("pr_id")
            if pr_id:
                manager.subscribe_to_pr(user_id, pr_id)
                await manager.send_personal_message({
                    "type": "subscribed",
                    "payload": {"pr_id": pr_id}
                }, user_id)
        
        elif message_type == "unsubscribe_pr":
            pr_id = payload.get("pr_id")
            if pr_id:
                manager.unsubscribe_from_pr(user_id, pr_id)
                await manager.send_personal_message({
                    "type": "unsubscribed",
                    "payload": {"pr_id": pr_id}
                }, user_id)
        
        elif message_type == "new_comment":
            pr_id = payload.get("pr_id")
            if pr_id:
                await manager.broadcast_to_pr({
                    "type": "comment_added",
                    "payload": payload
                }, pr_id)
        
        elif message_type == "suggestion_status":
            pr_id = payload.get("pr_id")
            if pr_id:
                await manager.broadcast_to_pr({
                    "type": "suggestion_updated",
                    "payload": payload
                }, pr_id)

    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "payload": {"message": str(e)}
        }, user_id)

async def notify_analysis_complete(analysis_id: int, pr_id: int):
    """Notify subscribers when analysis is complete"""
    await manager.broadcast_to_pr({
        "type": "analysis_complete",
        "payload": {
            "analysis_id": analysis_id,
            "pr_id": pr_id,
            "completed_at": datetime.utcnow().isoformat()
        }
    }, pr_id)

async def notify_analysis_error(analysis_id: int, pr_id: int, error: str):
    """Notify subscribers when analysis fails"""
    await manager.broadcast_to_pr({
        "type": "analysis_error",
        "payload": {
            "analysis_id": analysis_id,
            "pr_id": pr_id,
            "error": error
        }
    }, pr_id)

# Helper function for other routes to broadcast messages
async def broadcast_pr_update(pr_id: int, update_type: str, data: dict):
    """Broadcast pull request updates to subscribers"""
    await manager.broadcast_to_pr({
        "type": update_type,
        "payload": {
            "pr_id": pr_id,
            **data
        }
    }, pr_id)