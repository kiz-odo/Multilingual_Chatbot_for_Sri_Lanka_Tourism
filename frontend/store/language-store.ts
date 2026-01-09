import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { Language } from "@/types";

interface LanguageState {
  currentLanguage: Language;
  setLanguage: (language: Language) => void;
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set) => ({
      currentLanguage: "en",
      setLanguage: (language: Language) => {
        set({ currentLanguage: language });
        // Update HTML lang attribute
        if (typeof document !== "undefined") {
          document.documentElement.lang = language;
        }
      },
    }),
    {
      name: "language-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);

