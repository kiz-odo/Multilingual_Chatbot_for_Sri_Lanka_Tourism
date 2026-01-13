"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { ArrowLeftRight } from "lucide-react";
import apiClient from "@/lib/api-client";
import { formatCurrency } from "@/lib/utils";

export interface CurrencyConverterProps {
  className?: string;
}

const currencies = [
  { value: "USD", label: "USD - US Dollar" },
  { value: "EUR", label: "EUR - Euro" },
  { value: "GBP", label: "GBP - British Pound" },
  { value: "LKR", label: "LKR - Sri Lankan Rupee" },
  { value: "INR", label: "INR - Indian Rupee" },
  { value: "JPY", label: "JPY - Japanese Yen" },
  { value: "CNY", label: "CNY - Chinese Yuan" },
];

export function CurrencyConverter({ className }: CurrencyConverterProps) {
  const [amount, setAmount] = React.useState("100");
  const [from, setFrom] = React.useState("USD");
  const [to, setTo] = React.useState("LKR");

  const { data: conversion, isLoading } = useQuery({
    queryKey: ["currency-convert", amount, from, to],
    queryFn: async () => {
      const response = await apiClient.currency.convert({
        amount: parseFloat(amount),
        from,
        to,
      });
      return response.data;
    },
    enabled: !!amount && parseFloat(amount) > 0,
  });

  const swapCurrencies = () => {
    setFrom(to);
    setTo(from);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Currency Converter</CardTitle>
        <CardDescription>Convert between currencies</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Input
            type="number"
            placeholder="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="text-lg"
          />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <Select
            options={currencies}
            value={from}
            onChange={(e) => setFrom(e.target.value)}
          />
          <Button
            variant="outline"
            size="sm"
            onClick={swapCurrencies}
            className="w-full"
          >
            <ArrowLeftRight className="h-4 w-4" />
          </Button>
          <Select
            options={currencies}
            value={to}
            onChange={(e) => setTo(e.target.value)}
          />
        </div>
        {isLoading ? (
          <div className="text-center py-4">
            <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-solid border-primary border-r-transparent"></div>
          </div>
        ) : conversion ? (
          <div className="p-4 bg-muted rounded-lg">
            <div className="text-2xl font-bold">
              {formatCurrency(conversion.converted_amount || 0, to)}
            </div>
            {conversion.rate && (
              <div className="text-sm text-muted-foreground mt-1">
                1 {from} = {conversion.rate.toFixed(4)} {to}
              </div>
            )}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}







