"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import {
  Send,
  Mic,
  Loader2,
  Bot,
  User as UserIcon,
  MessageSquare,
  Info,
  Sun,
  Train,
  UtensilsCrossed,
  TreePine,
  Image as ImageIcon,
  Globe,
  Settings,
  ChevronDown,
  Search,
  Calendar,
  Briefcase,
  X,
  Wifi,
  WifiOff,
  Cloud,
  HelpCircle,
  Trash2,
  Plus,
  MapPin,
  Clock,
  Ticket,
  Camera,
  Umbrella,
  Building2,
  DollarSign,
  Menu,
} from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { useRouter } from "next/navigation";
import Link from "next/link";
import apiClient from "@/lib/api-client";
import type { ChatMessage } from "@/types";
import { format, isToday, isYesterday, isThisWeek, subDays } from "date-fns";
import { VoiceInput } from "@/components/features/voice-input";
import { useWebSocket } from "@/hooks/use-websocket";

interface Conversation {
  id: string;
  title: string;
  last_message?: string;
  created_at: string;
  updated_at: string;
}

export default function ChatPage() {
  const { user, isAuthenticated } = useAuthStore();
  const { currentLanguage, setLanguage } = useLanguageStore();
  const queryClient = useQueryClient();
  const router = useRouter();
  const [message, setMessage] = React.useState("");
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [selectedConversation, setSelectedConversation] = React.useState<string | null>(null);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [isLangOpen, setIsLangOpen] = React.useState(false);
  const [showImageUpload, setShowImageUpload] = React.useState(false);
  const [voiceTranscript, setVoiceTranscript] = React.useState("");
  const [imageFile, setImageFile] = React.useState<File | null>(null);
  const [imagePreview, setImagePreview] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const typingTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);

  const userId = user?.id || "anonymous";

  // WebSocket integration
  const {
    isConnected: isWsConnected,
    isTyping: isBotTyping,
    sendMessage: sendWsMessage,
    sendTyping,
    joinConversation: joinWsConversation,
    leaveConversation: leaveWsConversation,
  } = useWebSocket({
    enabled: isAuthenticated,
    onMessage: (data) => {
      // Handle real-time message from WebSocket
      if (data.message || data.response) {
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
        queryClient.invalidateQueries({ queryKey: ["chat-conversations", userId] });
      }
    },
    onTyping: (typing) => {
      // Bot typing indicator handled by isBotTyping
    },
    onConnect: () => {
      if (selectedConversation) {
        joinWsConversation(selectedConversation);
      }
    },
  });

  // Fetch conversations
  const { data: conversationsData } = useQuery({
    queryKey: ["chat-conversations", userId],
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
    queryKey: ["chat-conversation", selectedConversation],
    queryFn: async () => {
      if (!selectedConversation || !isAuthenticated) return null;
      try {
        const response = await apiClient.chat.getConversation(selectedConversation);
        return response.data;
      } catch {
        return null;
      }
    },
    enabled: !!selectedConversation && isAuthenticated,
  });

  React.useEffect(() => {
    if (conversationData?.messages) {
      setMessages(conversationData.messages);
    } else if (!selectedConversation) {
      setMessages([]);
    }
  }, [conversationData, selectedConversation]);

  // Join/leave WebSocket conversation when conversation changes
  React.useEffect(() => {
    if (isWsConnected && selectedConversation) {
      joinWsConversation(selectedConversation);
    }
    return () => {
      if (selectedConversation) {
        leaveWsConversation(selectedConversation);
      }
    };
  }, [selectedConversation, isWsConnected, joinWsConversation, leaveWsConversation]);

  // Scroll to bottom when messages change
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Organize conversations by date
  const organizeConversations = (convs: Conversation[]) => {
    const today: Conversation[] = [];
    const yesterday: Conversation[] = [];

    convs.forEach((conv) => {
      const date = new Date(conv.updated_at || conv.created_at);
      if (isToday(date)) {
        today.push(conv);
      } else if (isYesterday(date)) {
        yesterday.push(conv);
      }
    });

    return { today, yesterday };
  };

  const conversations: Conversation[] = conversationsData || [];
  const { today, yesterday } = organizeConversations(conversations);

  // Generate or get session ID
  const [sessionId, setSessionId] = React.useState<string>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("chat_session_id");
      if (stored) return stored;
      const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("chat_session_id", newId);
      return newId;
    }
    return `session_${Date.now()}`;
  });

  // Update session ID when conversation changes
  React.useEffect(() => {
    if (selectedConversation) {
      // Use conversation ID as session ID for existing conversations
      setSessionId(selectedConversation);
    } else {
      // Generate new session for new conversations
      const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newId);
      if (typeof window !== "undefined") {
        localStorage.setItem("chat_session_id", newId);
      }
    }
  }, [selectedConversation]);

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (messageText: string) => {
      const response = await apiClient.chat.sendMessage({
        message: messageText,
        user_id: userId,
        language: currentLanguage,
        session_id: sessionId,
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Update session ID if conversation ID is returned
      if (data.conversation_id && !selectedConversation) {
        setSelectedConversation(data.conversation_id);
        setSessionId(data.conversation_id);
      }

      const newMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        message: message,
        response: data.response || data.message || "Response received",
        language: currentLanguage,
        intent: data.intent,
        confidence: data.confidence,
        entities: data.entities,
        suggestions: data.suggestions,
        multimedia: data.multimedia,
        timestamp: new Date().toISOString(),
        response_time_ms: data.response_time_ms,
      };
      setMessages((prev) => [...prev, newMessage]);
      setMessage("");
      inputRef.current?.focus();
      queryClient.invalidateQueries({ queryKey: ["chat-conversations", userId] });
    },
    onError: (error) => {
      console.error("Failed to send message:", error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || sendMessageMutation.isPending) return;

    // Send via WebSocket if connected, otherwise use HTTP
    if (isWsConnected) {
      sendWsMessage(message, selectedConversation || undefined);
      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        message: message,
        response: "",
        language: currentLanguage,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setMessage("");
      inputRef.current?.focus();
      queryClient.invalidateQueries({ queryKey: ["chat-conversations", userId] });
    } else {
      sendMessageMutation.mutate(message);
    }
  };

  // Handle typing indicator
  React.useEffect(() => {
    if (message.trim() && isWsConnected) {
      sendTyping(true);
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      typingTimeoutRef.current = setTimeout(() => {
        sendTyping(false);
      }, 1000);
    } else if (isWsConnected) {
      sendTyping(false);
    }
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [message, isWsConnected, sendTyping]);

  const handleNewChat = () => {
    setSelectedConversation(null);
    setMessages([]);
    setMessage("");
    queryClient.invalidateQueries({ queryKey: ["chat-conversations", userId] });
  };

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.chat.deleteConversation(conversationId);
      if (selectedConversation === conversationId) {
        handleNewChat();
      }
      queryClient.invalidateQueries({ queryKey: ["chat-conversations", userId] });
    } catch (error) {
      console.error("Failed to delete conversation:", error);
    }
  };

  const handleQuickAction = (action: string) => {
    setMessage(action);
    inputRef.current?.focus();
  };

  // Handle voice transcript
  const handleVoiceTranscript = (transcript: string) => {
    setVoiceTranscript(transcript);
    setMessage(transcript);
    inputRef.current?.focus();
  };

  // Handle image file selection
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please select an image file");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert("Image size should be less than 10MB");
      return;
    }

    setImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
    setShowImageUpload(true);
  };

  // Handle image upload for chat
  const handleImageUpload = async () => {
    if (!imageFile) return;

    try {
      const response = await apiClient.chat.uploadImage(imageFile, {
        user_id: userId,
        language: currentLanguage,
      });

      if (response.data) {
        const newMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          message: message || "Image uploaded",
          response: response.data.response || response.data.message || "Image recognized",
          language: currentLanguage,
          intent: response.data.intent,
          confidence: response.data.confidence,
          entities: response.data.entities,
          suggestions: response.data.suggestions,
          multimedia: response.data.multimedia,
          timestamp: new Date().toISOString(),
          response_time_ms: response.data.response_time_ms,
        };
        setMessages((prev) => [...prev, newMessage]);
        setMessage("");
        setImageFile(null);
        setImagePreview(null);
        setShowImageUpload(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        queryClient.invalidateQueries({ queryKey: ["chat-conversations", userId] });
      }
    } catch (error) {
      console.error("Failed to upload image:", error);
      alert("Failed to upload image. Please try again.");
    }
  };

  // Get language code for voice input
  const getVoiceLanguage = () => {
    const langMap: Record<string, string> = {
      en: "en-US",
      si: "si-LK",
      ta: "ta-IN",
    };
    return langMap[currentLanguage] || "en-US";
  };

  const languages = [
    { code: "en", name: "English (US)" },
    { code: "si", name: "සිංහල" },
    { code: "ta", name: "தமிழ்" },
  ];

  const getConversationIcon = (title: string) => {
    const lower = title.toLowerCase();
    if (lower.includes("trip") || lower.includes("sigiriya") || lower.includes("itinerary")) {
      return <TreePine className="w-4 h-4" />;
    }
    if (lower.includes("visa")) {
      return <Info className="w-4 h-4" />;
    }
    if (lower.includes("weather")) {
      return <Sun className="w-4 h-4" />;
    }
    if (lower.includes("train") || lower.includes("schedule")) {
      return <Train className="w-4 h-4" />;
    }
    if (lower.includes("food") || lower.includes("kottu") || lower.includes("restaurant")) {
      return <UtensilsCrossed className="w-4 h-4" />;
    }
    return <MessageSquare className="w-4 h-4" />;
  };

  // Extract information cards from AI response (for train routes, hotels, etc.)
  const extractInfoCards = (response: string, suggestions?: string[]) => {
    const cards: Array<{ title: string; type: string; data: any }> = [];

    // Check for train route information
    if (response.toLowerCase().includes("train") && response.toLowerCase().includes("to")) {
      const routeMatch = response.match(/(\w+)\s+to\s+(\w+)\s+train/i);
      if (routeMatch) {
        const durationMatch = response.match(/duration[:\s]+([^\.]+)/i);
        const costMatch = response.match(/cost[:\s]+([^\.]+)/i);
        cards.push({
          title: `${routeMatch[1]} to ${routeMatch[2]} Train`,
          type: "train",
          data: {
            origin: routeMatch[1],
            destination: routeMatch[2],
            duration: durationMatch ? durationMatch[1].trim() : "~6-7 hours",
            cost: costMatch ? costMatch[1].trim() : "$12 - $20 (Reserved)",
          },
        });
      }
    }

    return cards;
  };

  // Close sidebar when conversation is selected on mobile
  React.useEffect(() => {
    if (selectedConversation && window.innerWidth < 768) {
      setIsSidebarOpen(false);
    }
  }, [selectedConversation]);

  return (
    <div className="flex h-screen overflow-hidden bg-gradient-animated-slow relative">
      {/* Decorative Background Elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float-subtle"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-teal-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float-subtle" style={{ animationDelay: '2s' }}></div>
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Left Sidebar */}
      <div
        className={`fixed md:static inset-y-0 left-0 z-50 w-64 glass-white backdrop-blur-custom border-r border-white/30 flex flex-col transform transition-transform duration-300 ease-in-out shadow-premium ${isSidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
          }`}
      >
        {/* Logo and Status */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-glow">
                <Cloud className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold bg-gradient-to-r from-teal-700 to-cyan-700 bg-clip-text text-transparent">Sri Lanka Travel AI</span>
            </div>
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="md:hidden p-1 rounded-lg hover:bg-gray-100 text-gray-500"
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className="text-xs text-green-600 font-medium">Online</span>
          </div>
        </div>

        {/* New Conversation Button */}
        <div className="p-4 border-b border-gray-200">
          <Button
            onClick={handleNewChat}
            className="w-full bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white font-semibold shadow-glow hover:shadow-intense transition-all duration-300"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Conversation
          </Button>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto">
          {/* TODAY */}
          {today.length > 0 && (
            <div className="p-4">
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">TODAY</h3>
              <div className="space-y-1">
                {today.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => setSelectedConversation(conv.id)}
                    className={`w-full text-left px-3 py-2 rounded-xl flex items-center space-x-2 text-sm transition-all duration-300 ${selectedConversation === conv.id
                      ? "glass bg-gradient-to-r from-cyan-50 to-teal-50 text-teal-700 font-semibold shadow-sm"
                      : "text-gray-700 hover:bg-white/50 hover:scale-102"
                      }`}
                  >
                    {getConversationIcon(conv.title)}
                    <span className="flex-1 truncate">{conv.title}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* YESTERDAY */}
          {yesterday.length > 0 && (
            <div className="p-4 border-t border-gray-100">
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">YESTERDAY</h3>
              <div className="space-y-1">
                {yesterday.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => setSelectedConversation(conv.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-2 text-sm transition-colors ${selectedConversation === conv.id
                      ? "bg-teal-50 text-teal-700"
                      : "text-gray-700 hover:bg-gray-50"
                      }`}
                  >
                    {getConversationIcon(conv.title)}
                    <span className="flex-1 truncate">{conv.title}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {today.length === 0 && yesterday.length === 0 && (
            <div className="p-4 text-center text-sm text-gray-500">
              No conversations yet
            </div>
          )}
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-200 p-4 space-y-2">
          {/* Help & FAQ */}
          <Link
            href="/help"
            className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-700"
          >
            <HelpCircle className="w-4 h-4" />
            <span>Help & FAQ</span>
          </Link>

          {/* Settings */}
          <Link
            href="/dashboard/settings"
            className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-700"
          >
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </Link>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col bg-white w-full md:w-auto">
        {/* Header with Language Selector */}
        <div className="glass-white backdrop-blur-custom border-b border-white/30 px-4 md:px-6 py-4 flex items-center justify-between shadow-sm">
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 text-gray-600"
            aria-label="Open sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1 md:flex-none"></div>
          <div className="flex items-center space-x-3">
            <div className="relative">
              <button
                onClick={() => setIsLangOpen(!isLangOpen)}
                className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-700"
              >
                <span>{languages.find((l) => l.code === currentLanguage)?.name || "English"}</span>
                <ChevronDown className="w-4 h-4" />
              </button>
              {isLangOpen && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setIsLangOpen(false)}
                    aria-hidden="true"
                  />
                  <div className="absolute top-full right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-[180px]">
                    {languages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setLanguage(lang.code);
                          setIsLangOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg transition-colors ${currentLanguage === lang.code ? "bg-teal-50 text-teal-600" : "text-gray-700"
                          }`}
                      >
                        {lang.name}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
            {selectedConversation && (
              <button
                onClick={(e) => handleDeleteConversation(selectedConversation, e)}
                className="p-2 rounded-lg hover:bg-gray-50 transition-colors text-gray-500 hover:text-red-500"
                aria-label="Delete conversation"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center p-4 md:p-8">
            <div className="max-w-2xl w-full text-center space-y-6 md:space-y-8">
              {/* AI Greeting */}
              <div className="flex items-start space-x-3 justify-start">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-teal-500 flex-shrink-0 shadow-glow">
                  <Cloud className="h-6 w-6 text-white" />
                </div>
                <div className="flex-1 text-left">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm font-bold bg-gradient-to-r from-teal-700 to-cyan-700 bg-clip-text text-transparent">Sri Lanka Travel AI</span>
                  </div>
                  <div className="rounded-2xl rounded-tl-sm glass-white backdrop-blur-custom p-5 shadow-premium border border-white/30">
                    <p className="text-sm text-gray-800 font-medium leading-relaxed">
                      Ayubowan! I am your Sri Lanka travel guide. How can I help you explore the island today?
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-3 md:p-6">
            {/* Timestamp */}
            {messages.length > 0 && (
              <div className="text-center mb-4 md:mb-6">
                <span className="text-xs text-gray-500">
                  {isToday(new Date(messages[0].timestamp))
                    ? `Today, ${format(new Date(messages[0].timestamp), "h:mm a")}`
                    : isYesterday(new Date(messages[0].timestamp))
                      ? `Yesterday, ${format(new Date(messages[0].timestamp), "h:mm a")}`
                      : format(new Date(messages[0].timestamp), "EEEE, MMMM d, yyyy 'at' h:mm a")}
                </span>
              </div>
            )}

            <div className="space-y-4 md:space-y-6">
              {messages.map((msg, index) => {
                const infoCards = extractInfoCards(msg.response, msg.suggestions);
                const showQuickActions = index === messages.length - 1 && msg.suggestions && msg.suggestions.length > 0;

                return (
                  <div key={msg.id} className="space-y-4">
                    {/* User Message */}
                    {msg.message && (
                      <div className="flex items-start space-x-2 md:space-x-3 justify-end">
                        <div className="flex-1 max-w-[85%] md:max-w-[70%]">
                          <div className="rounded-2xl rounded-tr-sm bg-gradient-to-br from-blue-500 to-blue-600 text-white p-4 shadow-glow hover:shadow-intense transition-all duration-300">
                            <p className="text-sm leading-relaxed">{msg.message}</p>
                          </div>
                          <p className="mt-1 text-xs text-gray-500 text-right">
                            {format(new Date(msg.timestamp), "h:mm a")}
                          </p>
                        </div>
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-300 text-gray-700 flex-shrink-0">
                          <UserIcon className="h-4 w-4" />
                        </div>
                      </div>
                    )}

                    {/* AI Response */}
                    {msg.response && (
                      <div className="flex items-start space-x-2 md:space-x-3">
                        <div className="flex h-8 w-8 md:h-10 md:w-10 items-center justify-center rounded-full bg-teal-100 text-teal-600 flex-shrink-0">
                          <Cloud className="h-4 w-4 md:h-5 md:w-5" />
                        </div>
                        <div className="flex-1 max-w-[85%] md:max-w-[75%]">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-xs md:text-sm font-semibold text-gray-900">Sri Lanka Travel AI</span>
                          </div>
                          <div className="rounded-2xl rounded-tl-sm glass-white backdrop-blur-custom p-4 shadow-premium border border-white/30">
                            <p className="text-sm text-gray-900 whitespace-pre-wrap mb-2 md:mb-3 leading-relaxed">
                              {msg.response}
                            </p>

                            {/* Information Cards */}
                            {infoCards.length > 0 && (
                              <div className="space-y-2 md:space-y-3 mt-3 md:mt-4">
                                {infoCards.map((card, cardIndex) => (
                                  <div key={cardIndex} className="border border-gray-200 rounded-lg p-3 md:p-4 bg-gray-50">
                                    <h4 className="font-semibold text-xs md:text-sm text-gray-900 mb-2 md:mb-3">{card.title}</h4>
                                    {card.type === "train" && (
                                      <div className="space-y-1.5 md:space-y-2">
                                        <div className="flex items-center space-x-2 text-xs md:text-sm text-gray-600">
                                          <MapPin className="w-3 h-3 md:w-4 md:h-4" />
                                          <span className="text-xs">Route map thumbnail</span>
                                        </div>
                                        <div className="flex items-center space-x-2 text-xs md:text-sm text-gray-700">
                                          <Clock className="w-3 h-3 md:w-4 md:h-4" />
                                          <span>Duration: {card.data.duration}</span>
                                        </div>
                                        <div className="flex items-center space-x-2 text-xs md:text-sm text-gray-700">
                                          <Ticket className="w-3 h-3 md:w-4 md:h-4" />
                                          <span>Cost: {card.data.cost}</span>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* Quick Action Buttons */}
                          {showQuickActions && msg.suggestions && (
                            <div className="mt-2 md:mt-3 flex flex-wrap gap-1.5 md:gap-2">
                              {msg.suggestions.slice(0, 6).map((suggestion, idx) => {
                                const getIcon = (text: string) => {
                                  const lower = text.toLowerCase();
                                  if (lower.includes("weather") || lower.includes("sun")) return <Sun className="w-4 h-4" />;
                                  if (lower.includes("train") || lower.includes("schedule")) return <Train className="w-4 h-4" />;
                                  if (lower.includes("exchange") || lower.includes("rate") || lower.includes("currency")) return <DollarSign className="w-4 h-4" />;
                                  if (lower.includes("hotel")) return <Building2 className="w-4 h-4" />;
                                  if (lower.includes("bridge") || lower.includes("photo") || lower.includes("camera")) return <Camera className="w-4 h-4" />;
                                  if (lower.includes("beach")) return <Umbrella className="w-4 h-4" />;
                                  if (lower.includes("cultural") || lower.includes("temple")) return <TreePine className="w-4 h-4" />;
                                  return <MessageSquare className="w-4 h-4" />;
                                };

                                return (
                                  <button
                                    key={idx}
                                    onClick={() => handleQuickAction(suggestion)}
                                    className="inline-flex items-center space-x-2 px-3 py-2 rounded-xl glass hover:bg-white/40 active:bg-white/60 text-sm text-gray-800 font-medium transition-all hover:scale-105 shadow-sm hover:shadow-md touch-manipulation"
                                  >
                                    <span className="w-3 h-3 md:w-4 md:h-4">{getIcon(suggestion)}</span>
                                    <span className="truncate max-w-[120px] md:max-w-none">{suggestion}</span>
                                  </button>
                                );
                              })}
                            </div>
                          )}

                          <p className="mt-1 text-xs text-gray-500">
                            {format(new Date(msg.timestamp), "h:mm a")}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            <div ref={messagesEndRef} />

            {(sendMessageMutation.isPending || isBotTyping) && (
              <div className="flex items-start space-x-2 md:space-x-3 mt-4">
                <div className="flex h-8 w-8 md:h-10 md:w-10 items-center justify-center rounded-full bg-teal-100 text-teal-600 flex-shrink-0">
                  <Cloud className="h-4 w-4 md:h-5 md:w-5" />
                </div>
                <div className="flex-1 max-w-[85%] md:max-w-[75%]">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs md:text-sm font-semibold text-gray-900">Sri Lanka Travel AI</span>
                  </div>
                  <div className="rounded-2xl rounded-tl-sm bg-white p-3 md:p-4 shadow-sm border border-gray-100">
                    {sendMessageMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                    ) : (
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Chat Input */}
        <div className="glass-white backdrop-blur-custom border-t border-white/30 px-4 py-4 shadow-premium">
          {showImageUpload && imagePreview && (
            <div className="mb-3 md:mb-4 p-3 md:p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-gray-900">Image Preview</h3>
                <button
                  onClick={() => {
                    setShowImageUpload(false);
                    setImageFile(null);
                    setImagePreview(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = "";
                    }
                  }}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="relative mb-2">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-full h-48 object-cover rounded-lg"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleImageUpload}
                  disabled={sendMessageMutation.isPending}
                  className="flex-1 bg-teal-500 hover:bg-teal-600"
                >
                  {sendMessageMutation.isPending ? "Uploading..." : "Send Image"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowImageUpload(false);
                    setImageFile(null);
                    setImagePreview(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = "";
                    }
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
            id="chat-image-upload"
          />
          <form onSubmit={handleSubmit} className="flex items-center space-x-1.5 md:space-x-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className={`p-2 md:p-2.5 rounded-lg transition-colors touch-manipulation ${showImageUpload
                ? "bg-teal-100 text-teal-600"
                : "hover:bg-gray-100 active:bg-gray-200 text-gray-600"
                }`}
              aria-label="Upload image"
            >
              <Plus className="w-4 h-4 md:w-5 md:h-5" />
            </button>
            <input
              ref={inputRef}
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask about Sri Lanka..."
              className="flex-1 px-4 py-3 rounded-full glass-white backdrop-blur-xs border border-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-sm text-gray-900 placeholder:text-gray-500 font-medium shadow-sm focus:shadow-premium transition-all"
              disabled={sendMessageMutation.isPending}
            />
            <div className="flex items-center space-x-1 md:space-x-2">
              <VoiceInput
                onTranscript={handleVoiceTranscript}
                language={getVoiceLanguage()}
                className="p-1.5 md:p-2"
              />
              <span className="text-xs text-gray-500 hidden sm:inline">VOICE</span>
            </div>
            <button
              type="submit"
              disabled={!message.trim() || sendMessageMutation.isPending}
              className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 active:from-green-700 active:to-teal-700 text-white flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-glow hover:shadow-intense hover:scale-110 touch-manipulation"
              aria-label="Send message"
            >
              {sendMessageMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </form>
          <p className="text-xs text-gray-500 mt-2 text-center px-2">
            AI can make mistakes. Please verify travel information.
          </p>
        </div>
      </div>
    </div>
  );
}
