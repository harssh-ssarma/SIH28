import { useState, useEffect } from 'react';

interface ProgressData {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  stage: string;
  message: string;
  time_remaining_seconds?: number | null;
  eta?: string | null;
  timestamp?: string;
}

export function useProgress(jobId: string | null) {
  const [progress, setProgress] = useState<ProgressData>({
    job_id: jobId || '',
    status: 'queued',
    progress: 0,
    stage: 'queued',
    message: 'Initializing...'
  });

  useEffect(() => {
    if (!jobId) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_DJANGO_API_URL || 'http://localhost:8000'}/api/progress/${jobId}/`,
          { credentials: 'include' }
        );
        
        if (!response.ok) {
          console.error('Progress fetch failed:', response.status);
          return;
        }

        const data: ProgressData = await response.json();
        setProgress(data);

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(pollInterval);
        }

      } catch (error) {
        console.error('Progress poll error:', error);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [jobId]);

  return progress;
}
