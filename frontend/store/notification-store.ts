/**
 * Notification Store - Zustand state management for notifications
 */

import { create } from 'zustand';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
    id: string;
    type: NotificationType;
    title: string;
    message: string;
    read: boolean;
    createdAt: Date;
    action?: {
        label: string;
        url: string;
    };
}

interface NotificationStore {
    // State
    notifications: Notification[];
    unreadCount: number;

    // Actions
    setNotifications: (notifications: Notification[]) => void;
    addNotification: (notification: Omit<Notification, 'id' | 'createdAt'>) => void;
    markAsRead: (notificationId: string) => void;
    markAllAsRead: () => void;
    deleteNotification: (notificationId: string) => void;
    clearAll: () => void;

    // Toast notifications (temporary)
    showToast: (
        type: NotificationType,
        title: string,
        message: string,
        duration?: number
    ) => void;
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
    // Initial state
    notifications: [],
    unreadCount: 0,

    // Actions
    setNotifications: (notifications) => {
        const unreadCount = notifications.filter((n) => !n.read).length;
        set({ notifications, unreadCount });
    },

    addNotification: (notificationData) => {
        const notification: Notification = {
            ...notificationData,
            id: `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            createdAt: new Date(),
        };

        set((state) => ({
            notifications: [notification, ...state.notifications],
            unreadCount: notification.read ? state.unreadCount : state.unreadCount + 1,
        }));
    },

    markAsRead: (notificationId) => {
        set((state) => {
            const notification = state.notifications.find((n) => n.id === notificationId);
            if (!notification || notification.read) {
                return state;
            }

            return {
                notifications: state.notifications.map((n) =>
                    n.id === notificationId ? { ...n, read: true } : n
                ),
                unreadCount: Math.max(0, state.unreadCount - 1),
            };
        });
    },

    markAllAsRead: () => {
        set((state) => ({
            notifications: state.notifications.map((n) => ({ ...n, read: true })),
            unreadCount: 0,
        }));
    },

    deleteNotification: (notificationId) => {
        set((state) => {
            const notification = state.notifications.find((n) => n.id === notificationId);
            const wasUnread = notification && !notification.read;

            return {
                notifications: state.notifications.filter((n) => n.id !== notificationId),
                unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
            };
        });
    },

    clearAll: () => {
        set({ notifications: [], unreadCount: 0 });
    },

    showToast: (type, title, message, duration = 5000) => {
        const { addNotification, deleteNotification } = get();

        const notificationData = {
            type,
            title,
            message,
            read: false,
        };

        addNotification(notificationData);

        // Auto-remove toast after duration
        if (duration > 0) {
            const notifications = get().notifications;
            const lastNotification = notifications[0];

            setTimeout(() => {
                if (lastNotification) {
                    deleteNotification(lastNotification.id);
                }
            }, duration);
        }
    },
}));

// Selectors
export const useUnreadCount = () => {
    return useNotificationStore((state) => state.unreadCount);
};

export const useUnreadNotifications = () => {
    return useNotificationStore((state) =>
        state.notifications.filter((n) => !n.read)
    );
};

export const useToast = () => {
    const showToast = useNotificationStore((state) => state.showToast);

    return {
        success: (title: string, message: string, duration?: number) =>
            showToast('success', title, message, duration),
        error: (title: string, message: string, duration?: number) =>
            showToast('error', title, message, duration),
        warning: (title: string, message: string, duration?: number) =>
            showToast('warning', title, message, duration),
        info: (title: string, message: string, duration?: number) =>
            showToast('info', title, message, duration),
    };
};
