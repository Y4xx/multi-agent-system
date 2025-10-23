import { CheckCircle2, XCircle, AlertCircle, X } from 'lucide-react';
import { Button } from './ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';

export type NotificationType = 'success' | 'error' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
}

interface ApplicationStatusProps {
  notifications: Notification[];
  onDismiss: (id: string) => void;
}

export function ApplicationStatus({ notifications, onDismiss }: ApplicationStatusProps) {
  if (notifications.length === 0) {
    return null;
  }

  const getIcon = (type: NotificationType) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'info':
        return <AlertCircle className="h-5 w-5 text-blue-600" />;
    }
  };

  const getBorderColor = (type: NotificationType) => {
    switch (type) {
      case 'success':
        return 'border-green-500';
      case 'error':
        return 'border-red-500';
      case 'info':
        return 'border-blue-500';
    }
  };

  const getBgColor = (type: NotificationType) => {
    switch (type) {
      case 'success':
        return 'bg-green-50';
      case 'error':
        return 'bg-red-50';
      case 'info':
        return 'bg-blue-50';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 max-w-md">
      {notifications.map((notification) => (
        <Card
          key={notification.id}
          className={`${getBorderColor(notification.type)} ${getBgColor(notification.type)} border-l-4 shadow-lg animate-in slide-in-from-right`}
        >
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2 flex-1">
                {getIcon(notification.type)}
                <CardTitle className="text-base">{notification.title}</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => onDismiss(notification.id)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pb-4 pt-0">
            <CardDescription className="text-sm text-foreground">
              {notification.message}
            </CardDescription>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
