import { useState } from 'react';
import { FileText, Send, Edit, X } from 'lucide-react';
import { Button } from './ui/Button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/Card';
import { Textarea } from './ui/Textarea';
import { Badge } from './ui/Badge';
import { JobOffer } from '../api/apiClient';

interface LetterPreviewProps {
  jobOffer: JobOffer;
  motivationLetter: string;
  matchExplanation?: {
    match_score: number;
    similarity_score: number;
    matching_skills: string[];
    explanation: string;
  };
  onClose: () => void;
  onSendApplication: (letter: string) => void;
}

export function LetterPreview({
  jobOffer,
  motivationLetter,
  matchExplanation,
  onClose,
  onSendApplication,
}: LetterPreviewProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedLetter, setEditedLetter] = useState(motivationLetter);
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    setSending(true);
    try {
      await onSendApplication(editedLetter);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-6 w-6" />
                Motivation Letter Preview
              </CardTitle>
              <CardDescription className="mt-2">
                For: <span className="font-semibold">{jobOffer.title}</span> at{' '}
                <span className="font-semibold">{jobOffer.company}</span>
              </CardDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {matchExplanation && (
            <div className="mt-4 p-4 border rounded-md bg-muted/50 space-y-2">
              <div className="flex items-center gap-2">
                <Badge variant="default">
                  Match Score: {matchExplanation.match_score}%
                </Badge>
                <Badge variant="secondary">
                  Similarity: {matchExplanation.similarity_score}%
                </Badge>
              </div>
              
              {matchExplanation.matching_skills.length > 0 && (
                <div className="text-sm">
                  <span className="font-semibold">Matching Skills: </span>
                  {matchExplanation.matching_skills.join(', ')}
                </div>
              )}
              
              <p className="text-sm text-muted-foreground">
                {matchExplanation.explanation}
              </p>
            </div>
          )}
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Letter Content</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(!isEditing)}
            >
              <Edit className="h-4 w-4 mr-2" />
              {isEditing ? 'Preview' : 'Edit'}
            </Button>
          </div>

          {isEditing ? (
            <Textarea
              value={editedLetter}
              onChange={(e) => setEditedLetter(e.target.value)}
              className="min-h-[400px] font-mono text-sm"
              placeholder="Edit your motivation letter..."
            />
          ) : (
            <div className="border rounded-md p-6 bg-white min-h-[400px] whitespace-pre-wrap text-sm">
              {editedLetter}
            </div>
          )}
        </CardContent>

        <CardFooter className="flex gap-2">
          <Button variant="outline" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button
            onClick={handleSend}
            disabled={sending || !editedLetter.trim()}
            className="flex-1"
          >
            <Send className="h-4 w-4 mr-2" />
            {sending ? 'Sending...' : 'Send Application'}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
