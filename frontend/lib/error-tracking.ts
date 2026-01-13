// Error tracking utility

export const logError = (error: Error, context?: Record<string, any>) => {
  // Log to console in development
  if (process.env.NODE_ENV === "development") {
    console.error("Error:", error, context);
    return;
  }

  // Sentry integration (if configured)
  if (typeof window !== "undefined" && (window as any).Sentry) {
    (window as any).Sentry.captureException(error, {
      contexts: {
        custom: context,
      },
    });
  }

  // Custom error logging
  // You can send to your own error tracking service here
};

export const logMessage = (message: string, level: "info" | "warning" | "error" = "info") => {
  if (process.env.NODE_ENV === "development") {
    if (level === "warning") {
      console.warn(message);
    } else if (level === "error") {
      console.error(message);
    } else {
      console.log(message);
    }
    return;
  }

  // Sentry integration
  if (typeof window !== "undefined" && (window as any).Sentry) {
    (window as any).Sentry.captureMessage(message, level);
  }
};

