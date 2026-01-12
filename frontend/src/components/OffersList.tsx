import { useState } from 'react';
import { Briefcase, MapPin, Calendar, DollarSign, Check } from 'lucide-react';
import { Button } from './ui/Button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/Card';
import { Badge } from './ui/Badge';
import type { JobOffer } from '../api/apiClient';

interface OffersListProps {
  offers: JobOffer[];
  onSelectOffer: (offer: JobOffer) => void;
}

export function OffersList({ offers, onSelectOffer }: OffersListProps) {
  const [selectedOffers, setSelectedOffers] = useState<Set<number>>(new Set());

  const toggleOfferSelection = (offerId: number) => {
    setSelectedOffers((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(offerId)) {
        newSet.delete(offerId);
      } else {
        newSet.add(offerId);
      }
      return newSet;
    });
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-blue-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-gray-500';
  };

  if (offers.length === 0) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center text-muted-foreground">
            <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No job offers found. Upload your CV to get matched offers.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Top Matching Opportunities</h2>
        <Badge variant="secondary">
          {offers.length} {offers.length === 1 ? 'offer' : 'offers'}
        </Badge>
      </div>

      <div className="grid gap-4">
        {offers.map((offer) => (
          <Card
            key={offer.id}
            className={`hover:shadow-md transition-shadow bg-white border-gray-100 ${selectedOffers.has(offer.id) ? 'ring-2 ring-primary' : ''
              }`}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-xl">{offer.title}</CardTitle>
                  <CardDescription className="text-base font-semibold text-foreground mt-1">
                    {offer.company || offer.organization}
                  </CardDescription>
                </div>
                {offer.match_score !== undefined && (
                  <div className="flex flex-col items-end gap-1">
                    <div className={`${getMatchScoreColor(offer.match_score)} text-white px-3 py-1 rounded-full text-sm font-bold`}>
                      {offer.match_score}% Match
                    </div>
                  </div>
                )}
              </div>
            </CardHeader>

            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {offer.location || (Array.isArray(offer.locations_derived) 
                    ? offer.locations_derived.join(', ') 
                    : offer.locations_derived) || 'Location not specified'}
                </div>
                <div className="flex items-center gap-1">
                  <Briefcase className="h-4 w-4" />
                  {offer.type || offer.employment_type || 'Type not specified'}
                </div>
                {offer.remote_derived && (
                  <Badge variant="outline" className="text-xs">{offer.remote_derived}</Badge>
                )}
                {offer.seniority && (
                  <Badge variant="outline" className="text-xs">{offer.seniority}</Badge>
                )}
                {offer.salary && (
                  <div className="flex items-center gap-1">
                    <DollarSign className="h-4 w-4" />
                    {offer.salary}
                  </div>
                )}
                {offer.posted_date && (
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    Posted: {new Date(offer.posted_date).toLocaleDateString()}
                  </div>
                )}
              </div>

              <p className="text-sm text-muted-foreground line-clamp-2">
                {offer.description || offer.description_text}
              </p>

              {offer.requirements && offer.requirements.length > 0 && (
                <div className="space-y-1">
                  <p className="text-sm font-semibold">Key Requirements:</p>
                  <ul className="text-sm text-muted-foreground list-disc list-inside space-y-0.5">
                    {offer.requirements.slice(0, 3).map((req, idx) => (
                      <li key={idx} className="line-clamp-1">
                        {req}
                      </li>
                    ))}
                    {offer.requirements.length > 3 && (
                      <li className="text-primary">+{offer.requirements.length - 3} more</li>
                    )}
                  </ul>
                </div>
              )}
            </CardContent>

            <CardFooter className="gap-2">
              {selectedOffers.has(offer.id) ? (
                <Button
                  onClick={() => toggleOfferSelection(offer.id)}
                  className="flex-1 bg-green-200 text-green-700 hover:bg-green-200 space-x-2"
                >
                  <Check className='size-5' />
                  <span>
                    Selected
                  </span>
                </Button>
              ) : (
                <Button
                  onClick={() => toggleOfferSelection(offer.id)}
                  className="flex-1 bg-gray-100"
                >
                  Select
                </Button>
              )}






              <Button
                variant="secondary"
                onClick={() => onSelectOffer(offer)}
                className="flex-1"
              >
                Generate Letter
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
