"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  DollarSign,
  ArrowRightLeft,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Info,
  CreditCard,
  Banknote,
} from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import type { CurrencyRate } from "@/types";

const popularCurrencies = [
  { code: "USD", name: "US Dollar", symbol: "$", flag: "🇺🇸" },
  { code: "EUR", name: "Euro", symbol: "€", flag: "🇪🇺" },
  { code: "GBP", name: "British Pound", symbol: "£", flag: "🇬🇧" },
  { code: "AUD", name: "Australian Dollar", symbol: "A$", flag: "🇦🇺" },
  { code: "INR", name: "Indian Rupee", symbol: "₹", flag: "🇮🇳" },
  { code: "JPY", name: "Japanese Yen", symbol: "¥", flag: "🇯🇵" },
  { code: "CNY", name: "Chinese Yuan", symbol: "¥", flag: "🇨🇳" },
  { code: "SGD", name: "Singapore Dollar", symbol: "S$", flag: "🇸🇬" },
];

export default function CurrencyPage() {
  const { currentLanguage } = useLanguageStore();
  const [amount, setAmount] = React.useState<string>("100");
  const [fromCurrency, setFromCurrency] = React.useState<string>("USD");
  const [toCurrency, setToCurrency] = React.useState<string>("LKR");

  const { data: conversionResult, isLoading: isConverting, refetch: convert } = useQuery({
    queryKey: ["currency-convert", fromCurrency, toCurrency, amount],
    queryFn: async () => {
      const response = await apiClient.currency.convert({
        from: fromCurrency,
        to: toCurrency,
        amount: parseFloat(amount) || 100,
      });
      return response.data;
    },
    enabled: !!amount && parseFloat(amount) > 0,
  });

  const { data: rates, isLoading: isLoadingRates } = useQuery({
    queryKey: ["currency-rates"],
    queryFn: async () => {
      const response = await apiClient.currency.getSriLankaRates();
      return response.data;
    },
  });

  const { data: recommendations } = useQuery({
    queryKey: ["currency-recommendations"],
    queryFn: async () => {
      const response = await apiClient.currency.getRecommendations({});
      return response.data;
    },
  });

  const swapCurrencies = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
  };

  const result: CurrencyRate | null = conversionResult;

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <div className="relative mb-8 rounded-3xl bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 p-8 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/10" />
        <div className="relative z-10">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl mb-2">
            Currency Converter
          </h1>
          <p className="text-white/90 max-w-2xl">
            Convert currencies and get real-time exchange rates for Sri Lankan Rupee (LKR)
          </p>
        </div>
        <div className="absolute right-8 top-8 opacity-30">
          <DollarSign className="h-32 w-32" />
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Converter */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Convert Currency</CardTitle>
              <CardDescription>Get instant exchange rates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid gap-4 md:grid-cols-[1fr,auto,1fr]">
                  {/* From Currency */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">From</label>
                    <Input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      className="text-2xl font-bold h-14"
                      placeholder="Enter amount"
                    />
                    <select
                      value={fromCurrency}
                      onChange={(e) => setFromCurrency(e.target.value)}
                      className="w-full p-3 rounded-lg border border-border bg-background"
                    >
                      {popularCurrencies.map((currency) => (
                        <option key={currency.code} value={currency.code}>
                          {currency.flag} {currency.code} - {currency.name}
                        </option>
                      ))}
                      <option value="LKR">🇱🇰 LKR - Sri Lankan Rupee</option>
                    </select>
                  </div>

                  {/* Swap Button */}
                  <div className="flex items-center justify-center">
                    <Button
                      variant="outline"
                      className="rounded-full h-12 w-12 p-0"
                      onClick={swapCurrencies}
                    >
                      <ArrowRightLeft className="h-5 w-5" />
                    </Button>
                  </div>

                  {/* To Currency */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">To</label>
                    <div className="relative">
                      <Input
                        type="text"
                        value={
                          isConverting
                            ? "Converting..."
                            : result?.converted
                            ? result.converted.toLocaleString(undefined, {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })
                            : "--"
                        }
                        readOnly
                        className="text-2xl font-bold h-14 bg-muted"
                      />
                    </div>
                    <select
                      value={toCurrency}
                      onChange={(e) => setToCurrency(e.target.value)}
                      className="w-full p-3 rounded-lg border border-border bg-background"
                    >
                      <option value="LKR">🇱🇰 LKR - Sri Lankan Rupee</option>
                      {popularCurrencies.map((currency) => (
                        <option key={currency.code} value={currency.code}>
                          {currency.flag} {currency.code} - {currency.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {result && (
                  <div className="p-4 rounded-lg bg-muted text-center">
                    <p className="text-sm text-muted-foreground mb-1">Exchange Rate</p>
                    <p className="text-lg font-semibold">
                      1 {fromCurrency} = {result.rate?.toFixed(4)} {toCurrency}
                    </p>
                    {result.last_updated && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Last updated: {new Date(result.last_updated).toLocaleString()}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Popular Rates */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Exchange Rates to LKR</CardTitle>
              <CardDescription>Current rates for popular currencies</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingRates ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <div className="grid gap-3 sm:grid-cols-2">
                  {popularCurrencies.map((currency) => {
                    const rate = rates?.rates?.[currency.code] || rates?.[currency.code];
                    return (
                      <div
                        key={currency.code}
                        className="flex items-center justify-between p-4 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{currency.flag}</span>
                          <div>
                            <p className="font-medium">{currency.code}</p>
                            <p className="text-xs text-muted-foreground">{currency.name}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">
                            {rate ? rate.toLocaleString() : "--"} LKR
                          </p>
                          <div className="flex items-center justify-end text-xs text-green-600">
                            <TrendingUp className="h-3 w-3 mr-1" />
                            <span>+0.5%</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Convert */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Convert</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[100, 500, 1000, 5000].map((amt) => (
                <Button
                  key={amt}
                  variant="outline"
                  className="w-full justify-between"
                  onClick={() => setAmount(amt.toString())}
                >
                  <span>${amt} USD</span>
                  <span className="text-muted-foreground">
                    ≈ {(amt * 320).toLocaleString()} LKR
                  </span>
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Money Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5" />
                Money Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                <div className="flex items-center gap-2 mb-1">
                  <CreditCard className="h-4 w-4 text-blue-600" />
                  <p className="text-sm font-medium text-blue-700 dark:text-blue-300">
                    Credit Cards
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">
                  Widely accepted in hotels, restaurants, and shops in major cities
                </p>
              </div>
              <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
                <div className="flex items-center gap-2 mb-1">
                  <Banknote className="h-4 w-4 text-green-600" />
                  <p className="text-sm font-medium text-green-700 dark:text-green-300">
                    Cash is King
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">
                  Keep cash for small vendors, tuk-tuks, and rural areas
                </p>
              </div>
              <div className="p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
                <div className="flex items-center gap-2 mb-1">
                  <DollarSign className="h-4 w-4 text-yellow-600" />
                  <p className="text-sm font-medium text-yellow-700 dark:text-yellow-300">
                    Exchange Tips
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">
                  Banks and licensed money changers offer best rates. Avoid airport exchanges
                </p>
              </div>
            </CardContent>
          </Card>

          {/* ATM Info */}
          <Card>
            <CardHeader>
              <CardTitle>ATM Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Max Withdrawal</span>
                  <span className="font-medium">40,000 - 100,000 LKR</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">ATM Fee</span>
                  <span className="font-medium">200 - 500 LKR</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Best Banks</span>
                  <span className="font-medium">Commercial, HNB</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
