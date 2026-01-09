"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, AlertTriangle, Trash2, Lock } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useToast } from "@/hooks/use-toast";
import apiClient from "@/lib/api-client";

const deleteAccountSchema = z.object({
  password: z.string().min(1, "Password is required to confirm account deletion"),
  confirmText: z.string().refine((val) => val === "DELETE", {
    message: "Please type DELETE to confirm",
  }),
});

type DeleteAccountFormData = z.infer<typeof deleteAccountSchema>;

export default function DeleteAccountPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const { addToast } = useToast();
  const [isDeleting, setIsDeleting] = React.useState(false);

  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<DeleteAccountFormData>({
    resolver: zodResolver(deleteAccountSchema),
  });

  // Delete account mutation
  const deleteAccountMutation = useMutation({
    mutationFn: async (data: DeleteAccountFormData) => {
      await apiClient.users.deleteMe();
    },
    onSuccess: async () => {
      addToast({
        title: "Account Deleted",
        description: "Your account has been permanently deleted",
        variant: "success",
      });
      await logout();
      router.push("/");
    },
    onError: (error: any) => {
      addToast({
        title: "Error",
        description: error?.response?.data?.detail || "Failed to delete account",
        variant: "error",
      });
    },
  });

  const onSubmit = (data: DeleteAccountFormData) => {
    if (
      !confirm(
        "Are you absolutely sure? This action cannot be undone. All your data will be permanently deleted."
      )
    ) {
      return;
    }
    setIsDeleting(true);
    deleteAccountMutation.mutate(data);
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link href="/dashboard/settings">
        <Button variant="ghost" className="mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Settings
        </Button>
      </Link>

      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <h1 className="text-3xl font-bold tracking-tight text-red-600">
              Delete Account
            </h1>
          </div>
          <p className="text-muted-foreground mt-2">
            Permanently delete your account and all associated data
          </p>
        </div>

        {/* Warning Card */}
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-900 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Warning: This action is irreversible
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-red-900">
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>All your personal data will be permanently deleted</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>All your saved trips, bookmarks, and preferences will be lost</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>Your chat history and conversations will be deleted</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>This action cannot be undone</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        {/* Delete Form */}
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle>Confirm Account Deletion</CardTitle>
            <CardDescription>
              To delete your account, please enter your password and type DELETE to confirm
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Enter Your Password
                </label>
                <Input
                  type="password"
                  {...register("password")}
                  className={errors.password ? "border-red-500" : ""}
                  placeholder="Your current password"
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Type <strong>DELETE</strong> to confirm
                </label>
                <Input
                  type="text"
                  {...register("confirmText")}
                  className={errors.confirmText ? "border-red-500" : ""}
                  placeholder="Type DELETE"
                />
                {errors.confirmText && (
                  <p className="mt-1 text-sm text-red-600">{errors.confirmText.message}</p>
                )}
              </div>

              <div className="flex gap-4 pt-4">
                <Button
                  type="submit"
                  variant="destructive"
                  disabled={isSubmitting || deleteAccountMutation.isPending || isDeleting}
                  className="flex-1"
                >
                  {isSubmitting || deleteAccountMutation.isPending || isDeleting ? (
                    "Deleting Account..."
                  ) : (
                    <>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Permanently Delete Account
                    </>
                  )}
                </Button>
                <Link href="/dashboard/settings">
                  <Button type="button" variant="outline">
                    Cancel
                  </Button>
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Alternative Options */}
        <Card>
          <CardHeader>
            <CardTitle>Before You Go</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              If you're having issues with your account, consider these alternatives:
            </p>
            <div className="space-y-2">
              <Link href="/dashboard/settings">
                <Button variant="outline" className="w-full justify-start">
                  <Lock className="mr-2 h-4 w-4" />
                  Change Password Instead
                </Button>
              </Link>
              <Link href="/dashboard/profile">
                <Button variant="outline" className="w-full justify-start">
                  Update Profile Information
                </Button>
              </Link>
              <Link href="/dashboard/privacy">
                <Button variant="outline" className="w-full justify-start">
                  Adjust Privacy Settings
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

