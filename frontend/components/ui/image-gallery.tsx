import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { X, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "./button";

export interface ImageGalleryProps {
  images: Array<{ url: string; alt?: string } | string>;
  className?: string;
  showThumbnails?: boolean;
}

export function ImageGallery({
  images,
  className,
  showThumbnails = true,
}: ImageGalleryProps) {
  const [selectedIndex, setSelectedIndex] = React.useState(0);
  const [isFullscreen, setIsFullscreen] = React.useState(false);

  const normalizedImages = images.map((img) =>
    typeof img === "string" ? { url: img, alt: "" } : img
  );

  const currentImage = normalizedImages[selectedIndex];

  const nextImage = () => {
    setSelectedIndex((prev) => (prev + 1) % normalizedImages.length);
  };

  const prevImage = () => {
    setSelectedIndex((prev) => (prev - 1 + normalizedImages.length) % normalizedImages.length);
  };

  React.useEffect(() => {
    if (isFullscreen) {
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === "ArrowLeft") prevImage();
        if (e.key === "ArrowRight") nextImage();
        if (e.key === "Escape") setIsFullscreen(false);
      };
      window.addEventListener("keydown", handleKeyDown);
      return () => window.removeEventListener("keydown", handleKeyDown);
    }
  }, [isFullscreen, normalizedImages.length]);

  return (
    <>
      <div className={cn("space-y-4", className)}>
        <div className="relative aspect-video w-full overflow-hidden rounded-2xl bg-muted">
          {currentImage && (
            <Image
              src={currentImage.url}
              alt={currentImage.alt || "Gallery image"}
              fill
              className="object-cover cursor-pointer"
              onClick={() => setIsFullscreen(true)}
            />
          )}
          {normalizedImages.length > 1 && (
            <>
              <Button
                variant="ghost"
                size="sm"
                className="absolute left-2 top-1/2 -translate-y-1/2"
                onClick={(e) => {
                  e.stopPropagation();
                  prevImage();
                }}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-2 top-1/2 -translate-y-1/2"
                onClick={(e) => {
                  e.stopPropagation();
                  nextImage();
                }}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </>
          )}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2">
            <span className="bg-black/50 text-white px-2 py-1 rounded text-sm">
              {selectedIndex + 1} / {normalizedImages.length}
            </span>
          </div>
        </div>

        {showThumbnails && normalizedImages.length > 1 && (
          <div className="grid grid-cols-4 gap-2">
            {normalizedImages.map((img, index) => (
              <button
                key={index}
                onClick={() => setSelectedIndex(index)}
                className={cn(
                  "relative aspect-video overflow-hidden rounded-lg border-2 transition-all",
                  selectedIndex === index
                    ? "border-primary"
                    : "border-transparent opacity-60 hover:opacity-100"
                )}
              >
                <Image
                  src={img.url}
                  alt={img.alt || `Thumbnail ${index + 1}`}
                  fill
                  className="object-cover"
                />
              </button>
            ))}
          </div>
        )}
      </div>

      {isFullscreen && (
        <div
          className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4"
          onClick={() => setIsFullscreen(false)}
        >
          <Button
            variant="ghost"
            size="sm"
            className="absolute top-4 right-4 text-white hover:bg-white/20"
            onClick={() => setIsFullscreen(false)}
          >
            <X className="h-6 w-6" />
          </Button>
          {currentImage && (
            <div className="relative max-w-7xl max-h-full">
              <Image
                src={currentImage.url}
                alt={currentImage.alt || "Fullscreen image"}
                width={1920}
                height={1080}
                className="max-h-[90vh] w-auto object-contain"
              />
            </div>
          )}
          {normalizedImages.length > 1 && (
            <>
              <Button
                variant="ghost"
                size="sm"
                className="absolute left-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/20"
                onClick={(e) => {
                  e.stopPropagation();
                  prevImage();
                }}
              >
                <ChevronLeft className="h-8 w-8" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/20"
                onClick={(e) => {
                  e.stopPropagation();
                  nextImage();
                }}
              >
                <ChevronRight className="h-8 w-8" />
              </Button>
            </>
          )}
        </div>
      )}
    </>
  );
}






