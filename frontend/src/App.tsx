import { useState } from 'react';
import { Briefcase, Sparkles, Settings as SettingsIcon } from 'lucide-react';
import { UploadCV } from './components/UploadCV';
import { OffersList } from './components/OffersList';
import { LetterPreview } from './components/LetterPreview';
import { ApplicationStatus, type Notification, type NotificationType } from './components/ApplicationStatus';
import { Settings } from './components/Settings';
import { Button } from './components/ui/Button';
import {
  type CVData,
  type JobOffer,
  matchOffers,
  generateMotivationLetter,
  submitApplication,
} from './api/apiClient';

type Page = 'home' | 'settings';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [cvData, setCvData] = useState<CVData | null>(null);
  const [jobOffers, setJobOffers] = useState<JobOffer[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedJob, setSelectedJob] = useState<JobOffer | null>(null);
  const [motivationLetter, setMotivationLetter] = useState<string>('');
  const [matchExplanation, setMatchExplanation] = useState<any>(null);
  const [showLetterPreview, setShowLetterPreview] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = (type: NotificationType, title: string, message: string) => {
    const notification: Notification = {
      id: Date.now().toString(),
      type,
      title,
      message,
    };
    setNotifications((prev) => [...prev, notification]);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      dismissNotification(notification.id);
    }, 5000);
  };

  const dismissNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const handleCVUploaded = async (data: CVData) => {
    setCvData(data);
    addNotification('success', 'CV Uploaded', 'Your CV has been analyzed successfully!');

    // Automatically fetch matching job offers
    await handleFindMatches(data);
  };

  const handleFindMatches = async (data?: CVData) => {
    const cvToUse = data || cvData;
    if (!cvToUse) {
      addNotification('error', 'Error', 'Please upload your CV first');
      return;
    }

    setLoading(true);
    try {
      const response = await matchOffers(cvToUse, { top_n: 10 });

      if (response.success) {
        setJobOffers(response.data);
        addNotification(
          'success',
          'Matches Found',
          `Found ${response.data.length} matching job opportunities!`
        );
      }
    } catch (error: any) {
      addNotification(
        'error',
        'Error',
        error.response?.data?.detail || 'Failed to fetch job matches'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOffer = async (offer: JobOffer) => {
    if (!cvData) {
      addNotification('error', 'Error', 'CV data not found');
      return;
    }

    setLoading(true);
    setSelectedJob(offer);

    try {
      const response = await generateMotivationLetter(cvData, offer.id);

      if (response.success) {
        setMotivationLetter(response.data.motivation_letter);
        setMatchExplanation(response.data.match_explanation);
        setShowLetterPreview(true);
      }
    } catch (error: any) {
      addNotification(
        'error',
        'Error',
        error.response?.data?.detail || 'Failed to generate motivation letter'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSendApplication = async (letter: string) => {
    if (!cvData || !selectedJob) {
      addNotification('error', 'Error', 'Missing CV data or job selection');
      return;
    }

    try {
      const response = await submitApplication(cvData, selectedJob.id, letter);

      if (response.success) {
        addNotification(
          'success',
          'Application Sent!',
          `Your application for ${selectedJob.title} at ${selectedJob.company} has been sent successfully!`
        );
        setShowLetterPreview(false);
      } else {
        addNotification('error', 'Error', response.message || 'Failed to send application');
      }
    } catch (error: any) {
      addNotification(
        'error',
        'Error',
        error.response?.data?.detail || 'Failed to send application'
      );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-primary text-primary-foreground p-2 rounded-lg">
                <Briefcase className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Multi-Agent Job System</h1>
                <p className="text-sm text-muted-foreground">
                  AI-Powered Job Discovery & Application Automation
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {cvData && currentPage === 'home' && (
                <Button onClick={() => handleFindMatches()} disabled={loading}>
                  <Sparkles className="h-4 w-4 mr-2" />
                  {loading ? 'Finding Matches...' : 'Refresh Matches'}
                </Button>
              )}
              <Button 
                variant={currentPage === 'settings' ? 'default' : 'outline'}
                onClick={() => setCurrentPage(currentPage === 'settings' ? 'home' : 'settings')}
              >
                <SettingsIcon className="h-4 w-4 mr-2" />
                {currentPage === 'settings' ? 'Back to Home' : 'Settings'}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {currentPage === 'settings' ? (
          <Settings />
        ) : (
          <div className="space-y-8">
            {/* CV Upload Section */}
            <UploadCV onCVUploaded={handleCVUploaded} />

            {/* Job Offers Section */}
            {cvData && (
              <div>
                <OffersList
                  offers={jobOffers}
                  onSelectOffer={handleSelectOffer}
                />
              </div>
            )}

            {/* Empty State */}
            {!cvData && (
              <div className="text-center py-12 text-muted-foreground">
                <Briefcase className="h-16 w-16 mx-auto mb-4 opacity-30" />
                <h2 className="text-xl font-semibold mb-2">Get Started</h2>
                <p>Upload your CV to discover perfect job opportunities matched to your skills.</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Letter Preview Modal */}
      {showLetterPreview && selectedJob && (
        <LetterPreview
          jobOffer={selectedJob}
          motivationLetter={motivationLetter}
          matchExplanation={matchExplanation}
          onClose={() => setShowLetterPreview(false)}
          onSendApplication={handleSendApplication}
        />
      )}

      {/* Notifications */}
      <ApplicationStatus
        notifications={notifications}
        onDismiss={dismissNotification}
      />

      <div className='grid grid-cols-2 w-full  px-22 space-x-4'>
        <Button className='bg-red-50 text-red-800 hover:bg-red-50'>
          Cancel
        </Button>
        <Button className='bg-green-100 text-green-700'>
          Sent emails
        </Button>
      </div>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-sm text-muted-foreground bg-white">
        <p>Multi-Agent Job Application System &copy; 2024</p>
      </footer>
    </div>
  );
}

export default App;
