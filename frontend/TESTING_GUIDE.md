# 🧪 Testing Guide - Sri Lanka Tourism AI

## Quick Start Testing

### Prerequisites
- ✅ Backend server running on `http://localhost:8000`
- ✅ Frontend dev server running on `http://localhost:3000`
- ✅ User account created (or use registration)

---

## 📋 Feature Testing Checklist

### 1. ✅ Voice Input Integration

**Test Location**: `/chat`

**Steps:**
1. Navigate to `http://localhost:3000/chat`
2. Look for the voice input button (microphone icon) in the chat input area
3. Click the voice button
4. **Expected**: Button should show "Stop" or change appearance
5. Speak a question: "Tell me about Sigiriya"
6. **Expected**: Your speech should be transcribed and appear in the input field
7. Click stop or wait for it to stop automatically
8. Click send
9. **Expected**: Message is sent and AI responds

**Browser Compatibility:**
- ✅ Chrome/Edge: Should work
- ✅ Firefox: May need permissions
- ⚠️ Safari: Limited support
- ⚠️ Mobile: Works on Chrome Mobile

**Troubleshooting:**
- If button doesn't work: Check browser console for errors
- If no transcription: Check microphone permissions in browser
- If error: Ensure HTTPS (required for some browsers)

---

### 2. ✅ Image Upload Integration

**Test Location**: `/chat`

**Steps:**
1. Navigate to `http://localhost:3000/chat`
2. Click the image icon (📷) in the chat input area
3. **Expected**: File picker opens
4. Select an image file (JPG, PNG, etc.)
5. **Expected**: Image preview appears above input
6. Verify preview shows your image
7. Click "Send Image" button
8. **Expected**: 
   - Image is uploaded
   - Loading indicator appears
   - AI responds with image recognition/description

**Test Cases:**
- ✅ Small image (< 1MB)
- ✅ Medium image (1-5MB)
- ✅ Large image (5-10MB)
- ❌ Very large image (> 10MB) - Should show error
- ❌ Non-image file - Should show error

**Troubleshooting:**
- If upload fails: Check file size (max 10MB)
- If no preview: Check browser console
- If API error: Verify backend endpoint is accessible

---

### 3. ✅ MFA Setup UI

**Test Location**: `/dashboard/settings/mfa`

**Prerequisites:**
- Must be logged in

**Steps:**
1. Login to your account
2. Navigate to `http://localhost:3000/dashboard/settings/mfa`
3. **Expected**: Page loads showing "MFA Status: Disabled"
4. Click "Enable MFA" button
5. **Expected**: 
   - QR code appears
   - Backup codes are displayed
   - Status changes to "Setup"
6. Open authenticator app (Google Authenticator, Authy, etc.)
7. Scan the QR code
8. **Expected**: Account appears in authenticator app
9. Enter the 6-digit code from authenticator app
10. Click "Verify & Enable"
11. **Expected**: 
    - MFA is enabled
    - Status shows "Enabled"
    - Success message appears

**Additional Tests:**
- ✅ Copy backup codes
- ✅ Download backup codes
- ✅ Disable MFA (requires password)
- ❌ Invalid code - Should show error
- ❌ Expired code - Should show error

**Troubleshooting:**
- If QR code doesn't appear: Check backend MFA endpoint
- If verification fails: Check code is current (30-second window)
- If disable fails: Verify password is correct

---

### 4. ✅ Favorites/Bookmarks System

**Test Location**: `/explore/attractions/[id]` and `/dashboard`

**Prerequisites:**
- Must be logged in

**Steps:**
1. Navigate to any attraction page (e.g., `/explore/attractions/sigiriya`)
2. Find the heart icon button (❤️) near the title
3. **Expected**: Heart icon is outlined (not filled)
4. Click the heart icon
5. **Expected**: 
   - Heart icon turns red/filled
   - Success toast: "Added to favorites"
6. Navigate to `/dashboard`
7. **Expected**: Attraction appears in "Saved Attractions" section
8. Go back to the attraction page
9. Click heart icon again
10. **Expected**: 
    - Heart icon becomes outlined again
    - Success toast: "Removed from favorites"
11. Go back to dashboard
12. **Expected**: Attraction no longer appears in favorites

**Test Cases:**
- ✅ Add favorite (logged in)
- ✅ Remove favorite (logged in)
- ❌ Add favorite (not logged in) - Should prompt login
- ✅ Multiple favorites
- ✅ Dashboard shows all favorites

**Troubleshooting:**
- If heart doesn't change: Check user is logged in
- If not saving: Check API endpoint
- If not showing in dashboard: Refresh page or check API

---

### 5. ✅ Social Sharing

**Test Location**: `/explore/attractions/[id]` and `/planner/[id]`

**Steps for Attractions:**
1. Navigate to any attraction detail page
2. Find the share button (↗️) near the title
3. Click the share button
4. **Expected**: 
   - Native share dialog appears (mobile/Chrome)
   - OR link is copied to clipboard (desktop)
   - Success toast: "Link copied to clipboard!"

**Steps for Itineraries:**
1. Create or navigate to an itinerary
2. Find the "Share" button in the top actions
3. Click share button
4. **Expected**: Same behavior as attractions

**Test Cases:**
- ✅ Share attraction (mobile with native share)
- ✅ Share attraction (desktop with clipboard)
- ✅ Share itinerary (mobile)
- ✅ Share itinerary (desktop)
- ✅ Shared link works when opened

**Troubleshooting:**
- If share doesn't work: Check browser supports Web Share API
- If clipboard fails: Check browser permissions
- If link doesn't work: Verify URL is correct

---

## 🔍 Comprehensive Testing

### Authentication Flow

**Test Registration:**
1. Go to `/auth/register`
2. Fill in form
3. Submit
4. **Expected**: Account created, redirected to login or dashboard

**Test Login:**
1. Go to `/auth/login`
2. Enter credentials
3. Submit
4. **Expected**: Logged in, redirected to dashboard

**Test Password Reset:**
1. Go to `/auth/forgot-password`
2. Enter email
3. Submit
4. **Expected**: Reset email sent (check backend logs)

**Test MFA Login:**
1. Login with MFA-enabled account
2. **Expected**: Prompted for MFA code
3. Enter code from authenticator
4. **Expected**: Logged in successfully

---

### Chat Interface

**Test Basic Chat:**
1. Go to `/chat`
2. Type a message: "Tell me about Kandy"
3. Send
4. **Expected**: AI responds with information

**Test Chat History:**
1. Send multiple messages
2. Refresh page
3. **Expected**: Previous messages are loaded

**Test Conversation Sidebar:**
1. Check left sidebar
2. **Expected**: Recent conversations listed
3. Click a conversation
4. **Expected**: Messages load

---

### Explore Features

**Test Attraction Search:**
1. Go to `/explore`
2. Use search bar
3. **Expected**: Results filter as you type

**Test Attraction Filters:**
1. Use category filters
2. **Expected**: Results update

**Test Attraction Detail:**
1. Click any attraction
2. **Expected**: Detail page loads with all information

---

### Dashboard Features

**Test Dashboard:**
1. Go to `/dashboard`
2. **Expected**: 
   - User profile shown
   - Saved attractions listed
   - Itineraries listed
   - Quick actions available

**Test Profile Edit:**
1. Go to `/dashboard/profile`
2. Edit information
3. Save
4. **Expected**: Changes saved

---

## 🐛 Common Issues & Solutions

### Issue: Voice Input Not Working

**Symptoms:**
- Button doesn't respond
- No transcription appears
- Error message

**Solutions:**
1. Check browser console for errors
2. Verify microphone permissions
3. Try different browser (Chrome recommended)
4. Check HTTPS (required for some browsers)
5. Verify Speech Recognition API is supported

### Issue: Image Upload Fails

**Symptoms:**
- Upload button doesn't work
- Preview doesn't appear
- Upload fails with error

**Solutions:**
1. Check file size (max 10MB)
2. Verify file type (images only)
3. Check backend endpoint: `POST /api/v1/chat/upload-image`
4. Verify CORS settings
5. Check browser console for errors

### Issue: MFA QR Code Not Showing

**Symptoms:**
- QR code doesn't appear
- Error message
- Page doesn't load

**Solutions:**
1. Check backend MFA endpoint is working
2. Verify `pyotp` and `qrcode` packages installed in backend
3. Check browser console for errors
4. Verify authentication token is valid
5. Try refreshing the page

### Issue: Favorites Not Saving

**Symptoms:**
- Heart icon doesn't change
- Not appearing in dashboard
- Error message

**Solutions:**
1. Verify user is logged in
2. Check API endpoint: `POST /api/v1/users/me/favorites/attractions/{id}`
3. Check browser console for errors
4. Verify user profile endpoint works
5. Try refreshing dashboard

### Issue: Share Not Working

**Symptoms:**
- Share button doesn't respond
- No share dialog
- Link not copied

**Solutions:**
1. Check browser supports Web Share API
2. Try different browser
3. Check clipboard permissions
4. Verify URL is correct
5. Check browser console for errors

---

## 📊 Test Results Template

Use this template to track your testing:

```
Date: ___________
Tester: ___________

Feature: Voice Input
Status: [ ] Pass [ ] Fail [ ] Partial
Notes: _________________________________

Feature: Image Upload
Status: [ ] Pass [ ] Fail [ ] Partial
Notes: _________________________________

Feature: MFA Setup
Status: [ ] Pass [ ] Fail [ ] Partial
Notes: _________________________________

Feature: Favorites
Status: [ ] Pass [ ] Fail [ ] Partial
Notes: _________________________________

Feature: Social Sharing
Status: [ ] Pass [ ] Fail [ ] Partial
Notes: _________________________________

Overall Status: [ ] Ready [ ] Needs Fixes
```

---

## 🎯 Quick Test Script

Run this quick test in 5 minutes:

1. **Login** → `/auth/login`
2. **Chat** → `/chat` → Send message → ✅
3. **Voice** → Click mic → Speak → ✅
4. **Image** → Click image → Upload → ✅
5. **MFA** → `/dashboard/settings/mfa` → Enable → ✅
6. **Favorite** → Go to attraction → Click heart → ✅
7. **Share** → Click share → ✅
8. **Dashboard** → Check favorites appear → ✅

**All green?** ✅ Ready for production!

---

## 📝 Reporting Issues

If you find issues, document:

1. **Feature**: Which feature failed
2. **Steps**: What you did
3. **Expected**: What should happen
4. **Actual**: What actually happened
5. **Browser**: Which browser/version
6. **Console**: Any console errors
7. **Screenshots**: If applicable

---

## ✅ Success Criteria

All features pass if:
- ✅ Voice input transcribes speech
- ✅ Image upload shows preview and sends
- ✅ MFA QR code displays and verifies
- ✅ Favorites save and appear in dashboard
- ✅ Share copies link or opens native share
- ✅ No console errors
- ✅ All features work on Chrome/Edge
- ✅ Mobile responsive

**Ready to proceed?** Move to Step 2: Deployment! 🚀





