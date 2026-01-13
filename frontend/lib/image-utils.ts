/**
 * Image utility functions for handling attraction images
 * Provides fallback URLs when Google Maps API is not available
 */

/**
 * Get the full image URL for an attraction image
 * @param imagePath - Can be a full URL, relative path, or image object
 * @returns Full image URL or null
 */
export function getImageUrl(imagePath: string | { url?: string; photo_reference?: string } | null | undefined): string | null {
  if (!imagePath) return null;

  // If it's an object with url property
  if (typeof imagePath === 'object') {
    if (imagePath.url) return imagePath.url;
    // If it has photo_reference but no Google API, return null to use fallback
    if (imagePath.photo_reference) return null;
    return null;
  }

  // If it's already a full URL
  if (typeof imagePath === 'string') {
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      return imagePath;
    }

    // If it's a relative path, convert to absolute
    if (imagePath.startsWith('/')) {
      return imagePath;
    }
  }

  return null;
}

/**
 * Get all image URLs from an array of image paths
 * @param images - Array of image paths or objects
 * @returns Array of full image URLs
 */
export function getAllImageUrls(images: (string | { url?: string; photo_reference?: string })[] | null | undefined): string[] {
  if (!images || !Array.isArray(images)) return [];

  return images
    .map(img => getImageUrl(img))
    .filter((url): url is string => url !== null);
}

/**
 * Get a fallback image URL based on category
 * Uses Unsplash images as fallback when Google Maps API is not available
 */
export function getFallbackImageUrl(category?: string, attractionId?: string): string {
  const seed = attractionId || 'default';

  // Category-based Unsplash images (high quality, free to use)
  const fallbackImages: Record<string, string> = {
    historical: `https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=800&q=80`, // Ancient ruins
    heritage: `https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=800&q=80`, // Ancient ruins
    wildlife: `https://images.unsplash.com/photo-1549366021-9f761d450615?w=800&q=80`, // Elephants
    beaches: `https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&q=80`, // Beach
    beach: `https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&q=80`, // Beach
    cultural: `https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=800&q=80`, // Tea plantations
    adventure: `https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80`, // Mountains
    temple: `https://images.unsplash.com/photo-1597423244036-ef5020e83f3c?w=800&q=80`, // Buddhist temple
    nature: `https://images.unsplash.com/photo-1586276393635-5ecd8a851acc?w=800&q=80`, // Forest
  };

  const categoryLower = category?.toLowerCase() || 'cultural';

  return fallbackImages[categoryLower] || fallbackImages['cultural'];
}

/**
 * Collection of Sri Lankan destination images for different categories
 * These are curated, high-quality images from Unsplash
 */
export const sriLankanImages = {
  // Historical Sites
  sigiriya: 'https://images.unsplash.com/photo-1566552881560-0be862a7c445?w=800&q=80',
  polonnaruwa: 'https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=800&q=80',
  anuradhapura: 'https://images.unsplash.com/photo-1597423244036-ef5020e83f3c?w=800&q=80',

  // Beaches
  mirissa: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&q=80',
  unawatuna: 'https://images.unsplash.com/photo-1473186578172-c141e6798cf4?w=800&q=80',
  arugamBay: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',

  // Wildlife
  yala: 'https://images.unsplash.com/photo-1549366021-9f761d450615?w=800&q=80',
  udawalawe: 'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=800&q=80',

  // Tea Plantations
  nuwara_eliya: 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=800&q=80',
  ella: 'https://images.unsplash.com/photo-1586276393635-5ecd8a851acc?w=800&q=80',

  // Cities
  colombo: 'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80',
  kandy: 'https://images.unsplash.com/photo-1588184337471-c0d4e6a2e8f7?w=800&q=80',
  galle: 'https://images.unsplash.com/photo-1591622180054-e78c197ba407?w=800&q=80',

  // Default
  default: 'https://images.unsplash.com/photo-1566552881560-0be862a7c445?w=800&q=80', // Sigiriya
};

/**
 * Get a specific destination image or fallback
 */
export function getDestinationImage(destinationName?: string): string {
  if (!destinationName) return sriLankanImages.default;

  const normalized = destinationName.toLowerCase().replace(/\s+/g, '_');
  return (sriLankanImages as Record<string, string>)[normalized] || sriLankanImages.default;
}
