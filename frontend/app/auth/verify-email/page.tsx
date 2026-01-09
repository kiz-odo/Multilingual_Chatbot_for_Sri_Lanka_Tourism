"use client";

import * as React from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { Compass, CheckCircle2, XCircle, Mail } from "lucide-react";

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { currentLanguage } = useLanguageStore();
  const token = searchParams.get("token");
  const [verified, setVerified] = React.useState<boolean | null>(null);

  const verifyMutation = useMutation({
    mutationFn: async (token: string) => {
      const response = await apiClient.email.verify(token);
      return response.data;
    },
    onSuccess: () => {
      setVerified(true);
    },
    onError: () => {
      setVerified(false);
    },
  });

  React.useEffect(() => {
    if (token) {
      verifyMutation.mutate(token);
    }
  }, [token]);

  if (!token) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mx-auto max-w-md">
          <div className="mb-8 text-center">
            <Link href="/" className="inline-flex items-center space-x-2">
              <Compass className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold">Sri Lanka Tourism AI</span>
            </Link>
          </div>
          <Card>
            <CardHeader className="space-y-1 text-center">
              <CardTitle className="text-2xl font-bold">Email Verification</CardTitle>
              <CardDescription>
                No verification token provided. Please check your email for the verification link.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/auth/login">
                <Button className="w-full">Go to Login</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (verifyMutation.isPending) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mx-auto max-w-md">
          <Card>
            <CardContent className="py-12 text-center">
              <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent mb-4"></div>
              <p className="text-muted-foreground">Verifying your email...</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (verified === true) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mx-auto max-w-md">
          <div className="mb-8 text-center">
            <Link href="/" className="inline-flex items-center space-x-2">
              <Compass className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold">Sri Lanka Tourism AI</span>
            </Link>
          </div>
          <Card>
            <CardHeader className="space-y-1 text-center">
              <div className="mx-auto mb-4 rounded-full bg-green-100 p-3">
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
              <CardTitle className="text-2xl font-bold">
                Email Verified Successfully!
              </CardTitle>
              <CardDescription>
                Your email has been verified. You can now log in to your account.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/auth/login">
                <Button className="w-full">Go to Login</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (verified === false) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mx-auto max-w-md">
          <div className="mb-8 text-center">
            <Link href="/" className="inline-flex items-center space-x-2">
              <Compass className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold">Sri Lanka Tourism AI</span>
            </Link>
          </div>
          <Card>
            <CardHeader className="space-y-1 text-center">
              <div className="mx-auto mb-4 rounded-full bg-destructive/10 p-3">
                <XCircle className="h-8 w-8 text-destructive" />
              </div>
              <CardTitle className="text-2xl font-bold">
                Verification Failed
              </CardTitle>
              <CardDescription>
                The verification link is invalid or has expired. Please request a new verification email.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  const email = prompt("Enter your email address:");
                  if (email) {
                    apiClient.email.resendVerification(email);
                    alert("Verification email sent! Please check your inbox.");
                  }
                }}
              >
                <Mail className="mr-2 h-4 w-4" />
                Resend Verification Email
              </Button>
              <Link href="/auth/login">
                <Button variant="ghost" className="w-full">
                  Go to Login
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return null;
}






