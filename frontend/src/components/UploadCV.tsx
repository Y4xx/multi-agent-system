import { useState } from 'react';
import { Upload, FileText, CheckCircle2 } from 'lucide-react';
import { Button } from './ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { uploadCV, type CVData } from '../api/apiClient';

interface UploadCVProps {
  onCVUploaded: (cvData: CVData) => void;
}

export function UploadCV({ onCVUploaded }: UploadCVProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cvData, setCvData] = useState<CVData | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadSuccess(false);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await uploadCV(file);
      
      if (response.success) {
        setCvData(response.data);
        setUploadSuccess(true);
        onCVUploaded(response.data);
      } else {
        setError(response.message || 'Failed to upload CV');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error uploading CV. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-6 w-6" />
          Upload Your CV
        </CardTitle>
        <CardDescription>
          Upload your CV to get started. We support PDF, DOCX, and TXT formats.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              className="flex-1 text-sm text-slate-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-primary file:text-primary-foreground
                hover:file:bg-primary/90
                cursor-pointer"
            />
            <Button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="min-w-[120px]"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </Button>
          </div>

          {error && (
            <div className="text-sm text-destructive border border-destructive rounded-md p-3">
              {error}
            </div>
          )}

          {uploadSuccess && cvData && (
            <div className="space-y-3 border border-green-500 rounded-md p-4 bg-green-50">
              <div className="flex items-center gap-2 text-green-700 font-semibold">
                <CheckCircle2 className="h-5 w-5" />
                CV Uploaded Successfully!
              </div>
              
              <div className="space-y-2 text-sm">
                {cvData.name && (
                  <div>
                    <span className="font-semibold">Name:</span> {cvData.name}
                  </div>
                )}
                {cvData.email && (
                  <div>
                    <span className="font-semibold">Email:</span> {cvData.email}
                  </div>
                )}
                {cvData.skills && cvData.skills.length > 0 && (
                  <div>
                    <span className="font-semibold">Skills:</span>{' '}
                    {cvData.skills.slice(0, 5).join(', ')}
                    {cvData.skills.length > 5 && ` (+${cvData.skills.length - 5} more)`}
                  </div>
                )}
              </div>
            </div>
          )}

          {file && !uploadSuccess && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <FileText className="h-4 w-4" />
              Selected: {file.name}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
