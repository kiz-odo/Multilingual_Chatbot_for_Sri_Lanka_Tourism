/**
 * Chat Store - Zustand state management for chat functionality
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    language?: string;
    attachments?: {
        type: 'image' | 'audio' | 'file';
        url: string;
        name?: string;
    }[];
}

export interface Conversation {
    id: string;
    title: string;
    language: string;
    createdAt: Date;
    updatedAt: Date;
    messageCount: number;
    lastMessage?: Message;
}

interface ChatStore {
    // State
    conversations: Conversation[];
    currentConversationId: string | null;
    messages: Message[];
    isLoading: boolean;
    isTyping: boolean;

    // Actions
    setConversations: (conversations: Conversation[]) => void;
    setCurrentConversation: (conversationId: string | null) => void;
    addConversation: (conversation: Conversation) => void;
    updateConversation: (conversationId: string, updates: Partial<Conversation>) => void;
    deleteConversation: (conversationId: string) => void;

    setMessages: (messages: Message[]) => void;
    addMessage: (message: Message) => void;
    updateMessage: (messageId: string, updates: Partial<Message>) => void;
    deleteMessage: (messageId: string) => void;

    setIsLoading: (isLoading: boolean) => void;
    setIsTyping: (isTyping: boolean) => void;

    clearMessages: () => void;
    clearCurrentConversation: () => void;
    reset: () => void;
}

export const useChatStore = create<ChatStore>()(
    persist(
        (set, get) => ({
            // Initial state
            conversations: [],
            currentConversationId: null,
            messages: [],
            isLoading: false,
            isTyping: false,

            // Conversation actions
            setConversations: (conversations) => set({ conversations }),

            setCurrentConversation: (conversationId) => {
                set({ currentConversationId: conversationId, messages: [] });
            },

            addConversation: (conversation) => set((state) => ({
                conversations: [conversation, ...state.conversations],
            })),

            updateConversation: (conversationId, updates) => set((state) => ({
                conversations: state.conversations.map((conv) =>
                    conv.id === conversationId ? { ...conv, ...updates } : conv
                ),
            })),

            deleteConversation: (conversationId) => set((state) => ({
                conversations: state.conversations.filter((conv) => conv.id !== conversationId),
                currentConversationId: state.currentConversationId === conversationId
                    ? null
                    : state.currentConversationId,
                messages: state.currentConversationId === conversationId ? [] : state.messages,
            })),

            // Message actions
            setMessages: (messages) => set({ messages }),

            addMessage: (message) => set((state) => {
                const newMessages = [...state.messages, message];

                // Update conversation with last message
                if (state.currentConversationId) {
                    const conversations = state.conversations.map((conv) =>
                        conv.id === state.currentConversationId
                            ? {
                                ...conv,
                                lastMessage: message,
                                messageCount: newMessages.length,
                                updatedAt: new Date(),
                            }
                            : conv
                    );
                    return { messages: newMessages, conversations };
                }

                return { messages: newMessages };
            }),

            updateMessage: (messageId, updates) => set((state) => ({
                messages: state.messages.map((msg) =>
                    msg.id === messageId ? { ...msg, ...updates } : msg
                ),
            })),

            deleteMessage: (messageId) => set((state) => ({
                messages: state.messages.filter((msg) => msg.id !== messageId),
            })),

            // UI state actions
            setIsLoading: (isLoading) => set({ isLoading }),
            setIsTyping: (isTyping) => set({ isTyping }),

            // Utility actions
            clearMessages: () => set({ messages: [] }),

            clearCurrentConversation: () => set({
                currentConversationId: null,
                messages: [],
            }),

            reset: () => set({
                conversations: [],
                currentConversationId: null,
                messages: [],
                isLoading: false,
                isTyping: false,
            }),
        }),
        {
            name: 'chat-storage',
            partialize: (state) => ({
                conversations: state.conversations,
                currentConversationId: state.currentConversationId,
            }),
        }
    )
);

// Selectors
export const useCurrentConversation = () => {
    const { conversations, currentConversationId } = useChatStore();
    return conversations.find((conv) => conv.id === currentConversationId);
};

export const useCurrentMessages = () => {
    const { messages } = useChatStore();
    return messages;
};

export const useChatLoading = () => {
    const { isLoading, isTyping } = useChatStore();
    return { isLoading, isTyping };
};
