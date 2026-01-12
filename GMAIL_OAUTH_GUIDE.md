# Gmail OAuth 2.0 Integration Guide

This guide explains how to set up Gmail OAuth 2.0 integration to send job applications from your personal Gmail account.

## Overview

The system supports two email sending methods:
1. **Gmail OAuth 2.0** (Recommended) - Send from your Gmail account via Gmail API
2. **SMTP** (Alternative) - Traditional SMTP email sending

## Why Use Gmail OAuth 2.0?

- ✅ **Professional**: Emails sent from your personal Gmail address
- ✅ **Better Deliverability**: Gmail API provides better email deliverability
- ✅ **Tracking**: Sent emails appear in your Gmail Sent folder
- ✅ **Secure**: OAuth 2.0 is more secure than app passwords
- ✅ **Revocable**: Easy to revoke access anytime

## Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### Step 2: Enable Gmail API

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: "Multi-Agent Job System" (or your preferred name)
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/gmail.send`
   - Test users: Add your email address
4. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: "Multi-Agent Job System"
   - Authorized redirect URIs: `http://localhost:8000/auth/google/callback`
   - Click **CREATE**
5. Download the credentials JSON or copy the Client ID and Client Secret

### Step 4: Configure Environment Variables

Add the following to your `.env` file in the `backend` directory:

```env
# Google OAuth 2.0 Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### Step 5: Connect Your Gmail Account

1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open the app in your browser: `http://localhost:5173`

4. Navigate to **Settings** page

5. Click **Connect Gmail Account**

6. You'll be redirected to Google's OAuth consent screen

7. Sign in with your Google account

8. Grant the requested permissions (send emails on your behalf)

9. You'll be redirected back to the Settings page

10. Verify the connection status shows your email address

### Step 6: Test Email Sending

1. Upload a CV
2. Select a job offer
3. Generate a motivation letter
4. Send the application
5. Check your Gmail Sent folder to verify the email was sent

## Security Considerations

### What Permissions Are Granted?

The app only requests the minimum required permission:
- **`gmail.send`**: Send emails on your behalf

The app **CANNOT**:
- Read your existing emails
- Access your contacts
- Modify your emails
- Access any other Google services

### How Is the Token Stored?

- OAuth tokens are stored locally in `backend/data/gmail_credentials.json`
- This file is excluded from git via `.gitignore`
- The file contains encrypted refresh tokens
- Never commit this file to version control

### How to Revoke Access?

**Method 1: Through the App**
1. Go to Settings page
2. Click "Disconnect Gmail"

**Method 2: Through Google**
1. Go to [Google Account Security](https://myaccount.google.com/permissions)
2. Find "Multi-Agent Job System"
3. Click "Remove Access"

## Troubleshooting

### "OAuth not configured" Error

**Solution**: Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in `.env`

### "Redirect URI Mismatch" Error

**Solution**: 
1. Check that the redirect URI in Google Cloud Console matches exactly: `http://localhost:8000/auth/google/callback`
2. Ensure `GOOGLE_REDIRECT_URI` in `.env` matches the same URL

### "Access Blocked: This app's request is invalid" Error

**Solution**:
1. Ensure Gmail API is enabled in Google Cloud Console
2. Add your email to "Test users" in OAuth consent screen
3. Make sure the OAuth consent screen is configured

### "Gmail API Error" When Sending Email

**Solution**:
1. Check that the token is still valid (tokens can expire)
2. Try disconnecting and reconnecting your Gmail account
3. Verify Gmail API is still enabled

### Token Expired

**Solution**: The app automatically refreshes expired tokens. If this fails, disconnect and reconnect your Gmail account.

## Production Deployment

For production deployment:

1. **Update Redirect URI**: Change `GOOGLE_REDIRECT_URI` to your production URL
2. **Add to Google Console**: Add the production redirect URI to authorized redirect URIs
3. **Publish OAuth Consent**: Submit your app for verification if needed
4. **Secure Storage**: Consider using a more secure token storage solution (database, secrets manager)
5. **HTTPS Required**: Google OAuth requires HTTPS for production

## API Endpoints

The Gmail OAuth integration adds these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/google` | GET | Initiate OAuth flow |
| `/auth/google/callback` | GET | Handle OAuth callback |
| `/auth/google/status` | GET | Check connection status |
| `/auth/google/disconnect` | POST | Disconnect Gmail account |

## Development Notes

### Testing Without OAuth

If you don't want to set up OAuth for testing:
- Leave `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` empty
- The system will fall back to SMTP or simulation mode

### Multiple Users

The current implementation stores one set of credentials per installation. For multi-user support, you would need to:
1. Add user authentication
2. Store credentials per user in a database
3. Associate credentials with user sessions

## Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
