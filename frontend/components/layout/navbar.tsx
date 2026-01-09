"use client";

import * as React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { Button } from "@/components/ui/button";
import {
  User,
  LogOut,
  Globe,
  Menu,
  X,
  Settings,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { t } from "@/lib/i18n";
import type { Language } from "@/types";

const languages: { code: Language; name: string }[] = [
  { code: "en", name: "English" },
  { code: "si", name: "සිංහල" },
  { code: "ta", name: "தமிழ்" },
];

export function Navbar() {
  const pathname = usePathname();
  const { isAuthenticated, user, logout } = useAuthStore();
  const { currentLanguage, setLanguage } = useLanguageStore();
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const [isLangOpen, setIsLangOpen] = React.useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = React.useState(false);

  const navItems = [
    { href: "/", label: "Home" },
    { href: "/chat", label: "Chat" },
    { href: "/explore", label: "Explore" },
    { href: "/planner", label: "Planner" },
    { href: "/safety", label: "Safety" },
    { href: "/dashboard", label: "Dashboard" },
  ];


  const isActive = (href: string) => pathname === href;

  return (
    <nav
      className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center space-x-2 sm:space-x-3 text-xl font-bold text-gray-900 hover:opacity-80 transition-opacity group"
            aria-label="Paradise Pointer - Home"
          >
            <div className="relative h-10 w-10 sm:h-12 sm:w-auto sm:min-w-[140px] sm:max-w-[200px] flex-shrink-0">
              <Image
                src="/paradise-pointer-logo.jpeg"
                alt="Paradise Pointer Logo"
                fill
                className="object-contain"
                priority
                sizes="(max-width: 640px) 40px, 200px"
              />
            </div>
            <span className="hidden lg:inline text-sm font-bold text-gray-900">
              PARADISE POINTER
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-1">
            {navItems.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "px-4 py-2 text-sm font-medium transition-colors rounded-lg",
                    active
                      ? "text-cyan-500 bg-cyan-50"
                      : "text-gray-700 hover:text-cyan-500 hover:bg-gray-50"
                  )}
                  aria-current={active ? "page" : undefined}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-2">
            {/* Theme Toggle */}
            <ThemeToggle />
            
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setIsLangOpen(!isLangOpen)}
                className="flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                aria-label="Select language"
                aria-expanded={isLangOpen}
                aria-haspopup="true"
              >
                <Globe className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {languages.find((l) => l.code === currentLanguage)?.name ||
                    "EN"}
                </span>
              </button>
              {isLangOpen && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setIsLangOpen(false)}
                    aria-hidden="true"
                  />
                  <div className="absolute right-0 mt-2 w-48 rounded-xl border border-gray-200 bg-white shadow-lg z-50">
                    {languages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setLanguage(lang.code);
                          setIsLangOpen(false);
                        }}
                        className={cn(
                          "w-full text-left px-4 py-2 text-sm hover:bg-gray-50 first:rounded-t-xl last:rounded-b-xl transition-colors",
                          currentLanguage === lang.code && "bg-cyan-50 text-cyan-600"
                        )}
                      >
                        {lang.name}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            {/* User Menu / Auth Buttons */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center space-x-2 rounded-lg px-3 py-2 hover:bg-gray-50 transition-colors"
                  aria-label="User menu"
                  aria-expanded={isUserMenuOpen}
                >
                  <div className="h-8 w-8 rounded-full bg-orange-400 flex items-center justify-center text-white text-sm font-semibold">
                    {user?.full_name?.[0] || user?.username[0] || "U"}
                  </div>
                  <span className="hidden sm:inline text-sm font-medium text-gray-700">
                    {user?.full_name || user?.username}
                  </span>
                </button>
                {isUserMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setIsUserMenuOpen(false)}
                      aria-hidden="true"
                    />
                    <div className="absolute right-0 mt-2 w-48 rounded-xl border border-gray-200 bg-white shadow-lg z-50">
                      <Link
                        href="/dashboard"
                        className="flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-50 first:rounded-t-xl transition-colors text-gray-700"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        <User className="h-4 w-4" />
                        <span>{t("nav.dashboard", currentLanguage)}</span>
                      </Link>
                      {user?.role === "admin" && (
                        <Link
                          href="/admin"
                          className="flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-50 transition-colors text-gray-700"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          <Settings className="h-4 w-4" />
                          <span>Admin</span>
                        </Link>
                      )}
                      <button
                        onClick={async () => {
                          await logout();
                          setIsUserMenuOpen(false);
                        }}
                        className="flex w-full items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-50 last:rounded-b-xl text-red-600 transition-colors"
                      >
                        <LogOut className="h-4 w-4" />
                        <span>{t("nav.logout", currentLanguage)}</span>
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="hidden sm:flex sm:items-center sm:space-x-2">
                <Link href="/auth/login">
                  <Button variant="ghost" size="sm" className="text-gray-700 hover:text-cyan-500">
                    {t("nav.login", currentLanguage)}
                  </Button>
                </Link>
                <Link href="/auth/register">
                  <Button size="sm" className="bg-cyan-500 hover:bg-cyan-600 text-white">
                    {t("nav.register", currentLanguage)}
                  </Button>
                </Link>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 rounded-lg hover:bg-gray-50 text-gray-700 transition-colors"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label="Toggle menu"
              aria-expanded={isMenuOpen}
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4 bg-white">
            <div className="flex flex-col space-y-2">
              {navItems.map((item) => {
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsMenuOpen(false)}
                    className={cn(
                      "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
                      active
                        ? "text-cyan-500 bg-cyan-50"
                        : "text-gray-700 hover:text-cyan-500 hover:bg-gray-50"
                    )}
                  >
                    {item.label}
                  </Link>
                );
              })}
              {!isAuthenticated && (
                <div className="flex flex-col space-y-2 pt-2 border-t border-gray-200">
                  <Link
                    href="/auth/login"
                    onClick={() => setIsMenuOpen(false)}
                    className="rounded-lg px-4 py-2 text-sm font-medium text-center border border-gray-200 hover:bg-gray-50 text-gray-700 transition-colors"
                  >
                    {t("nav.login", currentLanguage)}
                  </Link>
                  <Link
                    href="/auth/register"
                    onClick={() => setIsMenuOpen(false)}
                    className="rounded-lg px-4 py-2 text-sm font-medium text-center bg-cyan-500 hover:bg-cyan-600 text-white transition-colors"
                  >
                    {t("nav.register", currentLanguage)}
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

