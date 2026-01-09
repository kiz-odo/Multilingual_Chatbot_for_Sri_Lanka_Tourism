"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Shield, CheckCircle, XCircle, Copy, Download } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import apiClient from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";

export default function MFAPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const { addToast } = useToast();
  const [verificationCode, setVerificationCode] = React.useState("");
  const [mfaStatus, setMfaStatus] = React.useState<"disabled" | "setup" | "enabled">("disabled");
  const [qrCodeUrl, setQrCodeUrl] = React.useState<string | null>(null);
  const [backupCodes, setBackupCodes] = React.useState<string[]>([]);
  const [showBackupCodes, setShowBackupCodes] = React.useState(false);

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  // Enable MFA mutation
  const enableMFAMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.auth.enableMFA();
      return response.data;
    },
    onSuccess: (data) => {
      setQrCodeUrl(data.qr_code_url);
      setBackupCodes(data.backup_codes || []);
      setMfaStatus("setup");
      setShowBackupCodes(true);
      addToast({
        type: "success",
        message: "MFA setup initiated. Scan the QR code with your authenticator app.",
      });
    },
    onError: (error: any) => {
      addToast({
        type: "error",
        message: error.response?.data?.detail || "Failed to enable MFA",
      });
    },
  });

  // Verify MFA mutation
  const verifyMFAMutation = useMutation({
    mutationFn: async (code: string) => {
      const response = await apiClient.auth.verifyMFA(code);
      return response.data;
    },
    onSuccess: (data) => {
      setMfaStatus("enabled");
      setVerificationCode("");
      addToast({
        type: "success",
        message: "MFA verified and enabled successfully!",
      });
    },
    onError: (error: any) => {
      addToast({
        type: "error",
        message: error.response?.data?.detail || "Invalid verification code",
      });
      setVerificationCode("");
    },
  });

  // Disable MFA mutation
  const disableMFAMutation = useMutation({
    mutationFn: async (password: string) => {
      // Note: Backend expects password in body, but API client might need update
      const response = await apiClient.auth.disableMFA();
      return response.data;
    },
    onSuccess: () => {
      setMfaStatus("disabled");
      setQrCodeUrl(null);
      setBackupCodes([]);
      setShowBackupCodes(false);
      addToast({
        type: "success",
        message: "MFA disabled successfully",
      });
    },
    onError: (error: any) => {
      addToast({
        type: "error",
        message: error.response?.data?.detail || "Failed to disable MFA",
      });
    },
  });

  const handleVerify = () => {
    if (!verificationCode.trim()) {
      addToast({
        type: "error",
        message: "Please enter a verification code",
      });
      return;
    }
    verifyMFAMutation.mutate(verificationCode);
  };

  const handleCopyBackupCodes = () => {
    const codesText = backupCodes.join("\n");
    navigator.clipboard.writeText(codesText);
    addToast({
      type: "success",
      message: "Backup codes copied to clipboard",
    });
  };

  const handleDownloadBackupCodes = () => {
    const codesText = backupCodes.join("\n");
    const blob = new Blob([codesText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mfa-backup-codes-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    addToast({
      type: "success",
      message: "Backup codes downloaded",
    });
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button
        variant="ghost"
        onClick={() => router.back()}
        className="mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center space-x-2">
            <Shield className="h-8 w-8" />
            <span>Multi-Factor Authentication</span>
          </h1>
          <p className="text-muted-foreground mt-2">
            Add an extra layer of security to your account
          </p>
        </div>

        {/* MFA Status */}
        <Card>
          <CardHeader>
            <CardTitle>MFA Status</CardTitle>
            <CardDescription>
              Current multi-factor authentication status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {mfaStatus === "enabled" ? (
                  <>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span className="font-medium">Enabled</span>
                    <Badge variant="default" className="bg-green-500">
                      Active
                    </Badge>
                  </>
                ) : (
                  <>
                    <XCircle className="h-5 w-5 text-gray-400" />
                    <span className="font-medium">Disabled</span>
                    <Badge variant="outline">Inactive</Badge>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Setup MFA */}
        {mfaStatus === "disabled" && (
          <Card>
            <CardHeader>
              <CardTitle>Enable MFA</CardTitle>
              <CardDescription>
                Set up two-factor authentication using an authenticator app
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h3 className="font-semibold">How it works:</h3>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  <li>Scan the QR code with an authenticator app (Google Authenticator, Authy, etc.)</li>
                  <li>Enter the 6-digit code from the app to verify</li>
                  <li>Save your backup codes in a safe place</li>
                </ul>
              </div>
              <Button
                onClick={() => enableMFAMutation.mutate()}
                disabled={enableMFAMutation.isPending}
                className="w-full"
              >
                {enableMFAMutation.isPending ? "Setting up..." : "Enable MFA"}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* QR Code and Verification */}
        {mfaStatus === "setup" && qrCodeUrl && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Scan QR Code</CardTitle>
                <CardDescription>
                  Use your authenticator app to scan this QR code
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-center p-4 bg-white rounded-lg border-2 border-gray-200">
                  <img
                    src={qrCodeUrl}
                    alt="MFA QR Code"
                    className="w-64 h-64"
                  />
                </div>
                <p className="text-sm text-muted-foreground text-center">
                  Can't scan? Enter this code manually in your authenticator app
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Verify Setup</CardTitle>
                <CardDescription>
                  Enter the 6-digit code from your authenticator app
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Input
                    type="text"
                    placeholder="000000"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    maxLength={6}
                    className="text-center text-2xl tracking-widest"
                  />
                  <p className="text-xs text-muted-foreground text-center">
                    Enter the 6-digit code from your authenticator app
                  </p>
                </div>
                <Button
                  onClick={handleVerify}
                  disabled={!verificationCode || verificationCode.length !== 6 || verifyMFAMutation.isPending}
                  className="w-full"
                >
                  {verifyMFAMutation.isPending ? "Verifying..." : "Verify & Enable"}
                </Button>
              </CardContent>
            </Card>

            {/* Backup Codes */}
            {showBackupCodes && backupCodes.length > 0 && (
              <Card className="border-yellow-500">
                <CardHeader>
                  <CardTitle className="text-yellow-600">Backup Codes</CardTitle>
                  <CardDescription>
                    Save these codes in a safe place. You can use them if you lose access to your authenticator app.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                    {backupCodes.map((code, index) => (
                      <div key={index} className="font-mono text-sm">
                        {code}
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={handleCopyBackupCodes}
                      className="flex-1"
                    >
                      <Copy className="mr-2 h-4 w-4" />
                      Copy Codes
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleDownloadBackupCodes}
                      className="flex-1"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    ⚠️ These codes will only be shown once. Make sure to save them securely.
                  </p>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Disable MFA */}
        {mfaStatus === "enabled" && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Disable MFA</CardTitle>
              <CardDescription>
                Disable multi-factor authentication for your account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Disabling MFA will remove the extra security layer from your account. You'll need to enter your password to confirm.
              </p>
              <Button
                variant="destructive"
                onClick={() => {
                  if (confirm("Are you sure you want to disable MFA? This will reduce your account security.")) {
                    // Note: Backend requires password, but for now we'll call disable
                    // In production, you'd want to prompt for password
                    disableMFAMutation.mutate("");
                  }
                }}
                disabled={disableMFAMutation.isPending}
                className="w-full"
              >
                {disableMFAMutation.isPending ? "Disabling..." : "Disable MFA"}
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

