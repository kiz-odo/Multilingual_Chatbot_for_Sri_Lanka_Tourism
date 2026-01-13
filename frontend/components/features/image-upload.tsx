"use client";

import * as React from "react";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import apiClient from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";

export interface ImageUploadProps {
  onUploadComplete?: (result: any) => void;
  onUploadError?: (error: any) => void;
  maxSize?: number; // in MB
  acceptedTypes?: string[];
  className?: string;
}

export function ImageUpload({
  onUploadComplete,
  onUploadError,
  maxSize = 5,
  acceptedTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"],
  className,
}: ImageUploadProps) {
  const [preview, setPreview] = React.useState<string | null>(null);
  const [file, setFile] = React.useState<File | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const { addToast } = useToast();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const response = await apiClient.landmarks.recognize(file);
      return response.data;
    },
    onSuccess: (data) => {
      addToast({
        type: "success",
        message: "Image uploaded successfully!",
      });
      onUploadComplete?.(data);
      setPreview(null);
      setFile(null);
    },
    onError: (error: any) => {
      addToast({
        type: "error",
        message: error.response?.data?.error?.message || "Failed to upload image",
      });
      onUploadError?.(error);
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    if (!acceptedTypes.includes(selectedFile.type)) {
      addToast({
        type: "error",
        message: `Invalid file type. Accepted types: ${acceptedTypes.join(", ")}`,
      });
      return;
    }

    if (selectedFile.size > maxSize * 1024 * 1024) {
      addToast({
        type: "error",
        message: `File size exceeds ${maxSize}MB limit`,
      });
      return;
    }

    setFile(selectedFile);
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleUpload = () => {
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const handleRemove = () => {
    setPreview(null);
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <Card className={className}>
      <CardContent className="p-6">
        {!preview ? (
          <div className="border-2 border-dashed border-muted rounded-lg p-8 text-center">
            <ImageIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-sm text-muted-foreground mb-4">
              Drag and drop an image here, or click to select
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept={acceptedTypes.join(",")}
              onChange={handleFileSelect}
              className="hidden"
              id="image-upload"
            />
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="mr-2 h-4 w-4" />
              Select Image
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={preview}
                alt="Preview"
                className="w-full h-64 object-cover rounded-lg"
              />
              <Button
                variant="destructive"
                size="sm"
                className="absolute top-2 right-2"
                onClick={handleRemove}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleUpload}
                disabled={uploadMutation.isPending}
                className="flex-1"
              >
                {uploadMutation.isPending ? "Uploading..." : "Upload"}
              </Button>
              <Button variant="outline" onClick={handleRemove}>
                Cancel
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}







