/**
 * Notification Component - Toast and in-app notifications
 */

'use client';

import React, { useEffect } from 'react';
import { X, Info, CheckCircle, AlertTriangle, AlertCircle } from 'lucide-react';
import { useNotificationStore, type Notification } from '@/store/notification-store';

interface NotificationItemProps {
    notification: Notification;
    onClose: (id: string) => void;
}

const NotificationItem: React.FC<NotificationItemProps> = ({ notification, onClose }) => {
    const iconMap = {
        info: Info,
        success: CheckCircle,
        warning: AlertTriangle,
        error: AlertCircle,
    };

    const colorMap = {
        info: 'bg-blue-50 border-blue-200 text-blue-900',
        success: 'bg-green-50 border-green-200 text-green-900',
        warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
        error: 'bg-red-50 border-red-200 text-red-900',
    };

    const iconColorMap = {
        info: 'text-blue-600',
        success: 'text-green-600',
        warning: 'text-yellow-600',
        error: 'text-red-600',
    };

    const Icon = iconMap[notification.type];

    return (
        <div
            className={`flex gap-3 p-4 rounded-lg border shadow-lg ${colorMap[notification.type]} 
        animate-in slide-in-from-right-full duration-300`}
            role="alert"
            aria-live="polite"
        >
            <Icon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${iconColorMap[notification.type]}`} />

            <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-sm mb-1">{notification.title}</h4>
                <p className="text-sm opacity-90">{notification.message}</p>

                {notification.action && (
                    <a
                        href={notification.action.url}
                        className="text-sm font-medium underline mt-2 inline-block hover:opacity-80"
                    >
                        {notification.action.label}
                    </a>
                )}
            </div>

            <button
                onClick={() => onClose(notification.id)}
                className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
                aria-label="Close notification"
            >
                <X className="w-4 h-4" />
            </button>
        </div>
    );
};

/**
 * Toast Notifications - Floating notifications
 */
export const ToastNotifications: React.FC = () => {
    const notifications = useNotificationStore((state) => state.notifications);
    const deleteNotification = useNotificationStore((state) => state.deleteNotification);

    // Show only the first 5 notifications
    const visibleNotifications = notifications.slice(0, 5);

    return (
        <div
            className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full"
            aria-label="Notifications"
        >
            {visibleNotifications.map((notification) => (
                <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onClose={deleteNotification}
                />
            ))}
        </div>
    );
};

/**
 * Notification Center - In-app notification panel
 */
interface NotificationCenterProps {
    isOpen: boolean;
    onClose: () => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ isOpen, onClose }) => {
    const notifications = useNotificationStore((state) => state.notifications);
    const unreadCount = useNotificationStore((state) => state.unreadCount);
    const markAsRead = useNotificationStore((state) => state.markAsRead);
    const markAllAsRead = useNotificationStore((state) => state.markAllAsRead);
    const deleteNotification = useNotificationStore((state) => state.deleteNotification);

    useEffect(() => {
        if (isOpen) {
            // Mark all as read when opening
            const timer = setTimeout(() => {
                notifications.forEach((n) => {
                    if (!n.read) markAsRead(n.id);
                });
            }, 1000);
            return () => clearTimeout(timer);
        }
    }, [isOpen, notifications, markAsRead]);

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 z-40 animate-in fade-in duration-200"
                onClick={onClose}
                aria-hidden="true"
            />

            {/* Panel */}
            <div
                className="fixed top-0 right-0 h-full w-full max-w-md bg-white shadow-2xl z-50
          animate-in slide-in-from-right duration-300"
                role="dialog"
                aria-label="Notification Center"
                aria-modal="true"
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b">
                    <div>
                        <h2 className="text-lg font-semibold">Notifications</h2>
                        {unreadCount > 0 && (
                            <p className="text-sm text-gray-600">{unreadCount} unread</p>
                        )}
                    </div>

                    <div className="flex items-center gap-2">
                        {notifications.length > 0 && (
                            <button
                                onClick={markAllAsRead}
                                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                            >
                                Mark all read
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                            aria-label="Close"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Notification List */}
                <div className="overflow-y-auto h-[calc(100%-5rem)]">
                    {notifications.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-gray-500">
                            <Info className="w-12 h-12 mb-2 opacity-50" />
                            <p>No notifications yet</p>
                        </div>
                    ) : (
                        <div className="divide-y">
                            {notifications.map((notification) => (
                                <div
                                    key={notification.id}
                                    className={`p-4 hover:bg-gray-50 transition-colors ${!notification.read ? 'bg-blue-50/50' : ''
                                        }`}
                                >
                                    <div className="flex gap-3">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-start justify-between gap-2">
                                                <h4 className="font-semibold text-sm">{notification.title}</h4>
                                                {!notification.read && (
                                                    <span className="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-1" />
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                                            <p className="text-xs text-gray-400 mt-2">
                                                {new Date(notification.createdAt).toLocaleString()}
                                            </p>

                                            {notification.action && (
                                                <a
                                                    href={notification.action.url}
                                                    className="text-sm text-blue-600 hover:text-blue-800 font-medium mt-2 inline-block"
                                                    onClick={() => {
                                                        if (!notification.read) markAsRead(notification.id);
                                                    }}
                                                >
                                                    {notification.action.label} →
                                                </a>
                                            )}
                                        </div>

                                        <button
                                            onClick={() => deleteNotification(notification.id)}
                                            className="flex-shrink-0 opacity-40 hover:opacity-100 transition-opacity"
                                            aria-label="Delete notification"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
};

/**
 * Notification Badge - Show unread count
 */
export const NotificationBadge: React.FC<{ className?: string }> = ({ className = '' }) => {
    const unreadCount = useNotificationStore((state) => state.unreadCount);

    if (unreadCount === 0) return null;

    return (
        <span
            className={`absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold 
        rounded-full min-w-[1.25rem] h-5 flex items-center justify-center px-1 ${className}`}
            aria-label={`${unreadCount} unread notifications`}
        >
            {unreadCount > 99 ? '99+' : unreadCount}
        </span>
    );
};
