"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Mic, MicOff } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export interface VoiceInputProps {
  onTranscript?: (text: string) => void;
  onError?: (error: Error) => void;
  language?: string;
  className?: string;
}

export function VoiceInput({
  onTranscript,
  onError,
  language = "en-US",
  className,
}: VoiceInputProps) {
  const [isListening, setIsListening] = React.useState(false);
  const recognitionRef = React.useRef<SpeechRecognition | null>(null);
  const { addToast } = useToast();

  React.useEffect(() => {
    if (typeof window === "undefined") return;

    const SpeechRecognition =
      window.SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      addToast({
        type: "error",
        message: "Speech recognition is not supported in your browser",
      });
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join("");
      onTranscript?.(transcript);
    };

    recognition.onerror = (event: any) => {
      const error = new Error(event.error);
      onError?.(error);
      addToast({
        type: "error",
        message: `Speech recognition error: ${event.error}`,
      });
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [language, onTranscript, onError, addToast]);

  const toggleListening = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  return (
    <Button
      type="button"
      variant={isListening ? "default" : "outline"}
      onClick={toggleListening}
      className={className}
      aria-label={isListening ? "Stop listening" : "Start listening"}
    >
      {isListening ? (
        <>
          <MicOff className="mr-2 h-4 w-4" />
          Stop
        </>
      ) : (
        <>
          <Mic className="mr-2 h-4 w-4" />
          Voice
        </>
      )}
    </Button>
  );
}

// Type definitions for Speech Recognition API
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: any) => void;
  onend: () => void;
}

interface SpeechRecognitionEvent {
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
  [index: number]: SpeechRecognitionResult;
  length: number;
}

interface SpeechRecognitionResult {
  [index: number]: SpeechRecognitionAlternative;
  length: number;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}







