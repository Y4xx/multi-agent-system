import { useState, useEffect } from 'react';
import { Mail, CheckCircle, XCircle, AlertCircle, Settings as SettingsIcon } from 'lucide-react';
import { Button } from './ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import {
  getGoogleAuthStatus,
  initiateGoogleAuth,
  disconnectGoogleAuth,
  type OAuthStatus,
} from '../api/apiClient';

interface SettingsProps {
  onStatusChange?: (status: OAuthStatus) => void;
}

export function Settings({ onStatusChange }: SettingsProps) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<OAuthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    checkConnectionStatus();
    
    // Check for OAuth callback parameters
    const params = new URLSearchParams(window.location.search);
    const successParam = params.get('success');
    const errorParam = params.get('error');
    
    if (successParam) {
      setSuccess('Gmail account connected successfully!');
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
      checkConnectionStatus();
    }
    
    if (errorParam) {
      setError(`Failed to connect Gmail: ${errorParam}`);
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const checkConnectionStatus = async () => {
    try {
      const response = await getGoogleAuthStatus();
      if (response.success) {
        setStatus(response.data);
        if (onStatusChange) {
          onStatusChange(response.data);
        }
      }
    } catch (err: any) {
      console.error('Error checking status:', err);
      setError('Failed to check connection status');
    }
  };

  const handleConnect = async () => {
    setLoading(true);
    setError(null);
    try {
      initiateGoogleAuth();
    } catch (err: any) {
      setError('Failed to initiate OAuth flow');
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect your Gmail account?')) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await disconnectGoogleAuth();
      if (response.success) {
        setSuccess('Gmail account disconnected successfully');
        await checkConnectionStatus();
      } else {
        setError(response.message || 'Failed to disconnect Gmail account');
      }
    } catch (err: any) {
      setError('Failed to disconnect Gmail account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="bg-primary text-primary-foreground p-2 rounded-lg">
          <SettingsIcon className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-sm text-muted-foreground">
            Manage your account connections and preferences
          </p>
        </div>
      </div>

      {/* Notifications */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg flex items-start gap-3">
          <AlertCircle className="h-5 w-5 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800"
          >
            ×
          </button>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-start gap-3">
          <CheckCircle className="h-5 w-5 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium">Success</p>
            <p className="text-sm">{success}</p>
          </div>
          <button
            onClick={() => setSuccess(null)}
            className="text-green-600 hover:text-green-800"
          >
            ×
          </button>
        </div>
      )}

      {/* Gmail Connection Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Gmail Integration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Connect your Gmail account to send job applications directly from your email address
            using the Gmail API. This provides a more professional and personal touch to your
            applications.
          </p>

          {status?.connected ? (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-green-900">Gmail Connected</p>
                    <p className="text-sm text-green-700 mt-1">
                      Connected as: <span className="font-mono">{status.email}</span>
                    </p>
                    {status.connected_at && (
                      <p className="text-xs text-green-600 mt-1">
                        Connected on: {new Date(status.connected_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={handleDisconnect}
                  disabled={loading}
                  className="border-red-300 text-red-700 hover:bg-red-50"
                >
                  {loading ? 'Disconnecting...' : 'Disconnect Gmail'}
                </Button>
                <Button
                  variant="outline"
                  onClick={checkConnectionStatus}
                  disabled={loading}
                >
                  Refresh Status
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <XCircle className="h-5 w-5 text-slate-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-slate-900">Gmail Not Connected</p>
                    <p className="text-sm text-slate-700 mt-1">
                      Connect your Gmail account to send applications from your email address.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="text-sm space-y-2">
                  <p className="font-medium">Benefits of connecting Gmail:</p>
                  <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2">
                    <li>Send applications from your personal email address</li>
                    <li>Better deliverability and professional appearance</li>
                    <li>Applications appear in your Sent folder</li>
                    <li>Secure OAuth 2.0 authentication</li>
                  </ul>
                </div>

                <Button onClick={handleConnect} disabled={loading}>
                  <Mail className="h-4 w-4 mr-2" />
                  {loading ? 'Connecting...' : 'Connect Gmail Account'}
                </Button>
              </div>
            </div>
          )}

          <div className="pt-4 border-t">
            <details className="text-sm">
              <summary className="cursor-pointer font-medium text-slate-700 hover:text-slate-900">
                How does this work?
              </summary>
              <div className="mt-3 space-y-2 text-muted-foreground">
                <p>
                  When you connect your Gmail account, we use Google's secure OAuth 2.0 protocol.
                  You'll be redirected to Google where you can grant permission to send emails on
                  your behalf.
                </p>
                <p>
                  We only request the minimum permissions needed to send emails. We never access
                  your existing emails or any other data from your account.
                </p>
                <p>
                  You can revoke access at any time by disconnecting here or through your Google
                  Account settings.
                </p>
              </div>
            </details>
          </div>
        </CardContent>
      </Card>

      {/* Additional Settings Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Email Preferences</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Additional email and application preferences will be available here in future updates.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
