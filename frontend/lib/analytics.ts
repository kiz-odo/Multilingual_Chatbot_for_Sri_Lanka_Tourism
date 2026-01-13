// Analytics utility functions

export const trackEvent = (eventName: string, properties?: Record<string, any>) => {
  if (typeof window === "undefined") return;

  // Google Analytics
  if (window.gtag) {
    window.gtag("event", eventName, properties);
  }

  // Custom analytics
  console.log("Analytics Event:", eventName, properties);
};

export const trackPageView = (path: string) => {
  if (typeof window === "undefined") return;

  // Google Analytics
  if (window.gtag) {
    window.gtag("config", process.env.NEXT_PUBLIC_GA_ID || "", {
      page_path: path,
    });
  }

  // Custom analytics
  console.log("Page View:", path);
};

// Type declarations
declare global {
  interface Window {
    gtag?: (
      command: string,
      targetId: string | Date,
      config?: Record<string, any>
    ) => void;
  }
}






