"""
OAuth 2.0 routes for Google integration.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from services.google_oauth_service import google_oauth_service

# Create router
oauth_router = APIRouter(prefix="/auth", tags=["OAuth"])


@oauth_router.get("/google")
async def google_auth():
    """
    Initiate Google OAuth flow.
    
    Returns:
        Redirect to Google OAuth consent screen
    """
    try:
        auth_url = google_oauth_service.get_authorization_url()
        
        if not auth_url:
            raise HTTPException(
                status_code=500,
                detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file."
            )
        
        return RedirectResponse(url=auth_url)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error initiating OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="Error initiating OAuth flow")


@oauth_router.get("/google/callback")
async def google_auth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    error: str = Query(None, description="Error message if authorization failed")
):
    """
    Handle Google OAuth callback.
    
    Args:
        code: Authorization code from Google
        error: Error message if authorization failed
        
    Returns:
        Redirect to frontend with success/error status
    """
    try:
        # Check for errors
        if error:
            return RedirectResponse(url=f"http://localhost:5173/settings?error={error}")
        
        # Exchange code for tokens
        result = google_oauth_service.exchange_code_for_tokens(code)
        
        if result.get('success'):
            return RedirectResponse(url="http://localhost:5173/settings?success=true")
        else:
            return RedirectResponse(url=f"http://localhost:5173/settings?error={result.get('message')}")
            
    except Exception as e:
        print(f"Error in OAuth callback: {str(e)}")
        return RedirectResponse(url="http://localhost:5173/settings?error=callback_failed")


@oauth_router.get("/google/status")
async def google_auth_status():
    """
    Check Google OAuth connection status.
    
    Returns:
        Connection status with user email if connected
    """
    try:
        status = google_oauth_service.get_connection_status()
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        print(f"Error checking OAuth status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking connection status")


@oauth_router.post("/google/disconnect")
async def google_auth_disconnect():
    """
    Disconnect Google OAuth connection.
    
    Returns:
        Success message
    """
    try:
        result = google_oauth_service.disconnect()
        
        return {
            "success": result.get('success'),
            "message": result.get('message')
        }
        
    except Exception as e:
        print(f"Error disconnecting: {str(e)}")
        raise HTTPException(status_code=500, detail="Error disconnecting Gmail account")
