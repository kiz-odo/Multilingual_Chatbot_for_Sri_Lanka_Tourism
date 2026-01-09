import { useState, useCallback, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { useWebSocket } from "@/hooks/use-websocket";
import apiClient from "@/lib/api-client";
import type { ChatMessage } from "@/types";

interface UseChatOptions {
  conversationId?: string | null;
  autoConnect?: boolean;
  onMessageReceived?: (message: ChatMessage) => void;
}

/**
 * Custom hook for chat functionality
 * Manages chat messages, conversations, and WebSocket integration
 */
export function useChat(options: UseChatOptions = {}) {
  const { conversationId, autoConnect = true, onMessageReceived } = options;
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();
  const queryClient = useQueryClient();
  
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // WebSocket integration
  const {
    isConnected: isWsConnected,
    isTyping: isBotTyping,
    sendMessage: sendWsMessage,
    sendTyping,
    joinConversation: joinWsConversation,
    leaveConversation: leaveWsConversation,
  } = useWebSocket({
    enabled: isAuthenticated && autoConnect,
    onMessage: (data) => {
      const newMessage: ChatMessage = {
        id: data.id || `msg-${Date.now()}`,
        message: data.message || "",
        response: data.response || data.message || "",
        language: data.language || currentLanguage,
        intent: data.intent,
        confidence: data.confidence,
        entities: data.entities,
        suggestions: data.suggestions,
        multimedia: data.multimedia,
        timestamp: data.timestamp || new Date().toISOString(),
        response_time_ms: data.response_time_ms,
      };
      setMessages((prev) => [...prev, newMessage]);
      onMessageReceived?.(newMessage);
      queryClient.invalidateQueries({ queryKey: ["chat-conversations", user?.id] });
    },
    onTyping: (typing) => {
      setIsTyping(typing);
    },
    onConnect: () => {
      if (conversationId) {
        joinWsConversation(conversationId);
      }
    },
  });

  // Fetch conversations
  const { data: conversations = [] } = useQuery({
    queryKey: ["chat-conversations", user?.id],
    queryFn: async () => {
      if (!isAuthenticated) return [];
      try {
        const response = await apiClient.chat.getConversations();
        return response.data || [];
      } catch {
        return [];
      }
    },
    enabled: isAuthenticated,
  });

  // Fetch current conversation messages
  const { data: conversationData } = useQuery({
    queryKey: ["chat-conversation", conversationId],
    queryFn: async () => {
      if (!conversationId || !isAuthenticated) return null;
      try {
        const response = await apiClient.chat.getConversation(conversationId);
        return response.data;
      } catch {
        return null;
      }
    },
    enabled: !!conversationId && isAuthenticated,
  });

  // Update messages when conversation data changes
  useEffect(() => {
    if (conversationData?.messages) {
      setMessages(conversationData.messages);
    }
  }, [conversationData]);

  // Join/leave conversation on WebSocket
  useEffect(() => {
    if (conversationId && isWsConnected) {
      joinWsConversation(conversationId);
      return () => {
        leaveWsConversation(conversationId);
      };
    }
  }, [conversationId, isWsConnected, joinWsConversation, leaveWsConversation]);

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (messageText: string) => {
      if (!isAuthenticated) throw new Error("Not authenticated");
      
      const payload = {
        message: messageText,
        language: currentLanguage,
        conversation_id: conversationId || undefined,
      };

      // Try WebSocket first
      if (isWsConnected && conversationId) {
        sendWsMessage(messageText, conversationId);
        return { success: true };
      }

      // Fallback to HTTP
      const response = await apiClient.chat.sendMessage(payload);
      return response.data;
    },
    onSuccess: (data) => {
      if (data.message) {
        const newMessage: ChatMessage = {
          id: data.id || `msg-${Date.now()}`,
          message: data.message || message,
          response: data.response || "",
          language: currentLanguage,
          intent: data.intent,
          confidence: data.confidence,
          entities: data.entities,
          suggestions: data.suggestions,
          multimedia: data.multimedia,
          timestamp: data.timestamp || new Date().toISOString(),
          response_time_ms: data.response_time_ms,
        };
        setMessages((prev) => [...prev, newMessage]);
        onMessageReceived?.(newMessage);
      }
      setMessage("");
      queryClient.invalidateQueries({ queryKey: ["chat-conversations", user?.id] });
      queryClient.invalidateQueries({ queryKey: ["chat-conversation", conversationId] });
    },
  });

  // Send message handler
  const handleSendMessage = useCallback(
    (messageText?: string) => {
      const textToSend = messageText || message.trim();
      if (!textToSend) return;

      sendMessageMutation.mutate(textToSend);
      setMessage("");
    },
    [message, sendMessageMutation]
  );

  // Create new conversation
  const createConversationMutation = useMutation({
    mutationFn: async (title?: string) => {
      if (!isAuthenticated) throw new Error("Not authenticated");
      const response = await apiClient.chat.createConversation({ title });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-conversations", user?.id] });
    },
  });

  // Delete conversation
  const deleteConversationMutation = useMutation({
    mutationFn: async (id: string) => {
      if (!isAuthenticated) throw new Error("Not authenticated");
      await apiClient.chat.deleteConversation(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-conversations", user?.id] });
    },
  });

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return {
    // State
    messages,
    message,
    setMessage,
    conversations,
    isTyping: isTyping || isBotTyping,
    isConnected: isWsConnected,
    isLoading: sendMessageMutation.isPending,
    
    // Actions
    sendMessage: handleSendMessage,
    createConversation: createConversationMutation.mutate,
    deleteConversation: deleteConversationMutation.mutate,
    
    // Refs
    messagesEndRef,
    
    // Helpers
    scrollToBottom,
  };
}

