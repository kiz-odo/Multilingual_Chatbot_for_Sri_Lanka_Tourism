/**
 * Validation Schemas - Zod schemas for form validation
 */

import { z } from 'zod';

/**
 * Trip Planner Schema
 */
export const tripPlannerSchema = z.object({
    title: z.string().min(3, 'Title must be at least 3 characters').max(100),
    description: z.string().max(500).optional(),
    destinations: z.array(z.string()).min(1, 'At least one destination is required'),
    startDate: z.date(),
    endDate: z.date(),
    budget: z.number().positive('Budget must be positive'),
    travelers: z.number().int().positive('Must have at least 1 traveler').max(50),
    preferences: z.object({
        interests: z.array(z.string()).optional(),
        pace: z.enum(['relaxed', 'moderate', 'fast']).optional(),
        accommodation: z.enum(['budget', 'mid-range', 'luxury']).optional(),
    }).optional(),
}).refine((data) => data.endDate > data.startDate, {
    message: 'End date must be after start date',
    path: ['endDate'],
});

export type TripPlannerFormData = z.infer<typeof tripPlannerSchema>;

/**
 * User Profile Schema
 */
export const userProfileSchema = z.object({
    fullName: z.string().min(2, 'Name must be at least 2 characters').max(100),
    email: z.string().email('Invalid email address'),
    username: z.string().min(3, 'Username must be at least 3 characters').max(50)
        .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
    phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number').optional(),
    bio: z.string().max(500).optional(),
    location: z.string().max(100).optional(),
    website: z.string().url('Invalid URL').optional().or(z.literal('')),
    preferredLanguage: z.enum(['en', 'si', 'ta', 'de', 'fr', 'zh', 'ja']),
});

export type UserProfileFormData = z.infer<typeof userProfileSchema>;

/**
 * Change Password Schema
 */
export const changePasswordSchema = z.object({
    currentPassword: z.string().min(1, 'Current password is required'),
    newPassword: z.string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
        .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
        .regex(/[0-9]/, 'Password must contain at least one number')
        .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
});

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

/**
 * Login Schema
 */
export const loginSchema = z.object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(1, 'Password is required'),
    rememberMe: z.boolean().optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;

/**
 * Register Schema
 */
export const registerSchema = z.object({
    fullName: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Invalid email address'),
    username: z.string().min(3, 'Username must be at least 3 characters')
        .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
    password: z.string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
        .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
        .regex(/[0-9]/, 'Password must contain at least one number'),
    confirmPassword: z.string(),
    agreeToTerms: z.boolean().refine((val) => val === true, {
        message: 'You must agree to the terms and conditions',
    }),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
});

export type RegisterFormData = z.infer<typeof registerSchema>;

/**
 * MFA Setup Schema
 */
export const mfaSetupSchema = z.object({
    verificationCode: z.string()
        .length(6, 'Verification code must be 6 digits')
        .regex(/^\d+$/, 'Verification code must contain only numbers'),
});

export type MFASetupFormData = z.infer<typeof mfaSetupSchema>;

/**
 * Feedback Schema
 */
export const feedbackSchema = z.object({
    type: z.enum(['bug', 'feature', 'improvement', 'other']),
    subject: z.string().min(5, 'Subject must be at least 5 characters').max(100),
    message: z.string().min(20, 'Message must be at least 20 characters').max(1000),
    email: z.string().email('Invalid email address').optional(),
    attachments: z.array(z.instanceof(File)).max(5, 'Maximum 5 attachments allowed').optional(),
});

export type FeedbackFormData = z.infer<typeof feedbackSchema>;

/**
 * Forum Post Schema
 */
export const forumPostSchema = z.object({
    title: z.string().min(5, 'Title must be at least 5 characters').max(200),
    content: z.string().min(20, 'Content must be at least 20 characters').max(5000),
    category: z.string().optional(),
    tags: z.array(z.string()).max(10, 'Maximum 10 tags allowed').optional(),
});

export type ForumPostFormData = z.infer<typeof forumPostSchema>;

/**
 * Search Schema
 */
export const searchSchema = z.object({
    query: z.string().min(2, 'Search query must be at least 2 characters').max(200),
    filters: z.object({
        type: z.enum(['all', 'attractions', 'hotels', 'restaurants', 'events']).optional(),
        location: z.string().optional(),
        priceRange: z.object({
            min: z.number().nonnegative().optional(),
            max: z.number().nonnegative().optional(),
        }).optional(),
        rating: z.number().min(0).max(5).optional(),
    }).optional(),
});

export type SearchFormData = z.infer<typeof searchSchema>;

/**
 * Contact Schema
 */
export const contactSchema = z.object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Invalid email address'),
    subject: z.string().min(5, 'Subject must be at least 5 characters'),
    message: z.string().min(20, 'Message must be at least 20 characters').max(1000),
});

export type ContactFormData = z.infer<typeof contactSchema>;
