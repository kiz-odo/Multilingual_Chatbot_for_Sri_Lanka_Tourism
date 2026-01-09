"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useAuthStore } from "@/store/auth-store";

interface UseWebSocketOptions {
  enabled?: boolean;
  onMessage?: (message: any) => void;
  onTyping?: (isTyping: boolean) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { enabled = true, onMessage, onTyping, onConnect, onDisconnect } = options;
  const { token } = useAuthStore();
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!enabled || !token) {
      return;
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    const socket = io(wsUrl, {
      auth: {
        token: token,
      },
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    socketRef.current = socket;

    // Connection events
    socket.on("connect", () => {
      setIsConnected(true);
      onConnect?.();
    });

    socket.on("disconnect", () => {
      setIsConnected(false);
      onDisconnect?.();
    });

    // Message events
    socket.on("message", (data: any) => {
      onMessage?.(data);
    });

    socket.on("typing", (data: { isTyping: boolean }) => {
      setIsTyping(data.isTyping);
      onTyping?.(data.isTyping);
    });

    // Error handling
    socket.on("connect_error", (error) => {
      console.error("WebSocket connection error:", error);
    });

    // Cleanup
    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [enabled, token, onMessage, onTyping, onConnect, onDisconnect]);

  const sendMessage = useCallback((message: string, conversationId?: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit("message", {
        message,
        conversation_id: conversationId,
      });
    }
  }, [isConnected]);

  const sendTyping = useCallback((typing: boolean) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit("typing", { isTyping: typing });
    }
  }, [isConnected]);

  const joinConversation = useCallback((conversationId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit("join_conversation", { conversation_id: conversationId });
    }
  }, [isConnected]);

  const leaveConversation = useCallback((conversationId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit("leave_conversation", { conversation_id: conversationId });
    }
  }, [isConnected]);

  return {
    isConnected,
    isTyping,
    sendMessage,
    sendTyping,
    joinConversation,
    leaveConversation,
  };
}





