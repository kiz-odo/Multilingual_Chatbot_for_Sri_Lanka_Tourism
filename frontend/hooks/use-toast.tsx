"use client";

import * as React from "react";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = React.useCallback((toast: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).substring(7);
    const newToast: Toast = { ...toast, id };
    setToasts((prev) => [...prev, newToast]);

    const duration = toast.duration || 5000;
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}

function ToastContainer({
  toasts,
  removeToast,
}: {
  toasts: Toast[];
  removeToast: (id: string) => void;
}) {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  const bgColors = {
    success: "bg-green-500",
    error: "bg-destructive",
    warning: "bg-yellow-500",
    info: "bg-primary",
  };

  return (
    <div
      className={`${bgColors[toast.type]} text-white rounded-lg shadow-lg p-4 animate-in slide-in-from-right`}
      role="alert"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {toast.title && <p className="font-semibold">{toast.title}</p>}
          <p className="text-sm">{toast.message}</p>
        </div>
        <button
          onClick={onClose}
          className="ml-4 text-white/80 hover:text-white"
          aria-label="Close"
        >
          ×
        </button>
      </div>
    </div>
  );
}
