"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Bell, Shield, Globe, LogOut, User } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";

export default function SettingsPage() {
  const router = useRouter();
  const { logout, isAuthenticated } = useAuthStore();
  const { currentLanguage } = useLanguageStore();

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null;
  }

  const handleLogout = async () => {
    if (confirm("Are you sure you want to logout?")) {
      await logout();
      router.push("/");
    }
  };

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
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account settings and preferences
          </p>
        </div>

        {/* Account Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5" />
              <span>Account</span>
            </CardTitle>
            <CardDescription>
              Manage your account information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link href="/dashboard/profile">
              <Button variant="outline" className="w-full justify-start">
                Edit Profile
              </Button>
            </Link>
            <Link href="/dashboard/change-password">
              <Button variant="outline" className="w-full justify-start">
                Change Password
              </Button>
            </Link>
            <Link href="/dashboard/settings/mfa">
              <Button variant="outline" className="w-full justify-start">
                <Shield className="mr-2 h-4 w-4" />
                Multi-Factor Authentication
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bell className="h-5 w-5" />
              <span>Notifications</span>
            </CardTitle>
            <CardDescription>
              Manage your notification preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Email Notifications</p>
                  <p className="text-sm text-muted-foreground">
                    Receive email updates about your trips
                  </p>
                </div>
                <input type="checkbox" defaultChecked className="toggle" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Push Notifications</p>
                  <p className="text-sm text-muted-foreground">
                    Receive push notifications on your device
                  </p>
                </div>
                <input type="checkbox" className="toggle" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Privacy */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5" />
              <span>Privacy</span>
            </CardTitle>
            <CardDescription>
              Control your privacy settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/privacy">
              <Button variant="outline" className="w-full justify-start">
                Privacy Controls
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Language */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="h-5 w-5" />
              <span>Language</span>
            </CardTitle>
            <CardDescription>
              Select your preferred language
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Current language: {currentLanguage === "en" ? "English" : currentLanguage === "si" ? "සිංහල" : currentLanguage === "ta" ? "தமிழ்" : currentLanguage}
            </p>
            <p className="text-xs text-muted-foreground">
              You can change the language using the language selector in the navigation bar.
            </p>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Danger Zone</CardTitle>
            <CardDescription>
              Irreversible and destructive actions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              variant="destructive"
              onClick={handleLogout}
              className="w-full"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
            <Link href="/dashboard/delete-account">
              <Button variant="outline" className="w-full text-destructive border-destructive">
                Delete Account
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


