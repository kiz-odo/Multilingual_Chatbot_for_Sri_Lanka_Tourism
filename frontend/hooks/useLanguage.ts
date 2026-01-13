import { useLanguageStore } from "@/store/language-store";
import type { Language } from "@/types";
import { t } from "@/lib/i18n";

/**
 * Custom hook for language state and translations
 * Provides convenient access to language store with translation helper
 */
export function useLanguage() {
  const { currentLanguage, setLanguage } = useLanguageStore();

  return {
    // State
    currentLanguage,
    language: currentLanguage,
    
    // Actions
    setLanguage,
    changeLanguage: setLanguage,
    
    // Translation helper
    t: (key: string, params?: Record<string, any>) => t(key, currentLanguage, params),
    
    // Helpers
    isEnglish: currentLanguage === "en",
    isSinhala: currentLanguage === "si",
    isTamil: currentLanguage === "ta",
  };
}


