"use client";

import * as React from "react";
import Link from "next/link";
import Image from "next/image";
import { Facebook, Twitter, Instagram, Compass } from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import type { Language } from "@/types";

const languages: { code: Language; name: string }[] = [
  { code: "en", name: "English" },
  { code: "si", name: "සිංහල" },
  { code: "ta", name: "தமிழ்" },
];

export function Footer() {
  const { currentLanguage, setLanguage } = useLanguageStore();

  return (
    <footer className="border-t border-border bg-muted/30" role="contentinfo">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="relative h-10 w-10 sm:h-12 sm:w-auto sm:min-w-[120px] sm:max-w-[160px] flex-shrink-0">
                <Image
                  src="/paradise-pointer-logo.jpeg"
                  alt="Paradise Pointer Logo"
                  fill
                  className="object-contain"
                  sizes="(max-width: 640px) 40px, 160px"
                />
              </div>
              <h3 className="text-lg font-bold text-gray-900 hidden sm:block">
                PARADISE POINTER
              </h3>
            </div>
            <p className="text-sm text-gray-600">
              Travel your dream city. The official AI-powered travel assistant for Sri Lanka Tourism. Promoting safe, smart, and sustainable travel experiences.
            </p>
            <div className="flex space-x-4">
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="Facebook"
              >
                <Facebook className="h-5 w-5" />
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="Twitter"
              >
                <Twitter className="h-5 w-5" />
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="Instagram"
              >
                <Instagram className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Explore */}
          <div>
            <h4 className="text-sm font-semibold mb-4 text-gray-900">Explore</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Home
                </Link>
              </li>
              <li>
                <Link
                  href="/explore"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Explore
                </Link>
              </li>
              <li>
                <Link
                  href="/planner"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Trip Planner
                </Link>
              </li>
              <li>
                <Link
                  href="/explore/events"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Cultural Events
                </Link>
              </li>
              <li>
                <Link
                  href="/explore/hotels"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Accommodation
                </Link>
              </li>
            </ul>
          </div>

          {/* Emergency Support */}
          <div>
            <h4 className="text-sm font-semibold mb-4 text-gray-900">Emergency Support</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="tel:1912"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Tourist Police: 1912
                </Link>
              </li>
              <li>
                <Link
                  href="tel:1990"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Ambulance: 1990
                </Link>
              </li>
              <li>
                <Link
                  href="/safety"
                  className="text-cyan-500 hover:text-cyan-600 transition-colors font-medium"
                >
                  View all emergency contacts
                </Link>
              </li>
            </ul>
          </div>

          {/* Language & Legal */}
          <div>
            <h4 className="text-sm font-semibold mb-4">Language</h4>
            <div className="space-y-2">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className={`block w-full text-left text-sm px-2 py-1 rounded transition-colors ${
                    currentLanguage === lang.code
                      ? "text-primary font-semibold bg-primary/10"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {lang.name}
                </button>
              ))}
            </div>
            <div className="mt-6 space-y-2 text-xs text-muted-foreground">
              <Link href="#" className="hover:text-foreground">
                Privacy Policy
              </Link>
              <span> • </span>
              <Link href="#" className="hover:text-foreground">
                Terms of Service
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between text-sm text-gray-600">
          <p>
            © {new Date().getFullYear()} Sri Lanka Tourism Promotion Bureau. All rights reserved.
          </p>
          <div className="flex items-center space-x-2 mt-4 sm:mt-0">
            <Link href="/privacy" className="hover:text-gray-900 transition-colors">
              Privacy Policy
            </Link>
            <span>•</span>
            <Link href="/terms" className="hover:text-gray-900 transition-colors">
              Terms of Service
            </Link>
            <span>•</span>
            <Link href="/cookies" className="hover:text-gray-900 transition-colors">
              Cookie
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}


