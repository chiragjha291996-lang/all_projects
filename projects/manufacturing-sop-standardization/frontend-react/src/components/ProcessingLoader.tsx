import React, { useState, useEffect } from 'react';
import { Brain, Cpu, FileText, Zap, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { ProcessingJob, ProcessingStatus } from '../types';

interface ProcessingLoaderProps {
  jobs: ProcessingJob[];
  onProcessingComplete: (result: any) => void;
  onError: (error: string) => void;
}

const ProcessingLoader: React.FC<ProcessingLoaderProps> = ({ jobs, onProcessingComplete, onError }) => {
  const [jobStatuses, setJobStatuses] = useState<Record<string, ProcessingStatus>>({});
  const [allCompleted, setAllCompleted] = useState(false);

  // Monitor job progress
  useEffect(() => {
    if (jobs.length === 0) return;

    const checkJobStatus = async () => {
      for (const job of jobs) {
        try {
          const response = await apiService.getProcessingStatus(job.job_id);
          const status = response.status;
          
          setJobStatuses(prev => ({
            ...prev,
            [job.job_id]: status
          }));

          // Check if all jobs are completed
          const allJobsCompleted = jobs.every(j => {
            const status = jobStatuses[j.job_id] || response.status;
            return status.status === 'completed';
          });

          if (allJobsCompleted && !allCompleted) {
            setAllCompleted(true);
            // Simulate analysis result for now
            const mockResult = {
              message: "Processing completed successfully",
              processed_documents: jobs.length,
              clustering_result: {
                clusters: [],
                total_clusters: 0,
                similarity_analysis: {
                  doc1_filename: jobs[0]?.filename || "Document 1",
                  doc2_filename: jobs[1]?.filename || "Document 2",
                  similarity_score: 0.75,
                  combined_similarity_score: 0.75,
                  procedure_type: "Manufacturing SOP",
                  key_similarities: ["Both documents contain safety procedures", "Similar quality control steps"],
                  key_differences: ["Different approval workflows", "Varying documentation requirements"],
                  safety_parameters: "Both documents emphasize safety protocols",
                  operational_differences: "Different operational sequences",
                  cluster_recommendation: "Documents are similar and can be standardized",
                  summary: "Documents show high similarity with minor operational differences",
                  embedding_analysis: {
                    overall_similarity: 0.75,
                    chunks1_count: 8,
                    chunks2_count: 6,
                    high_similarity_pairs: [],
                    analysis_summary: "High semantic similarity detected"
                  }
                },
                chunk_clustering: {
                  clusters: [],
                  noise_chunks: [],
                  total_clusters: 0,
                  total_chunks: 0,
                  clustering_summary: "Documents processed successfully"
                }
              }
            };
            onProcessingComplete(mockResult);
          }

          // Check for errors
          if (status.status === 'error') {
            onError(status.message || 'Processing failed');
          }

        } catch (error: any) {
          console.error('Error checking job status:', error);
        }
      }
    };

    const interval = setInterval(checkJobStatus, 2000); // Check every 2 seconds
    checkJobStatus(); // Initial check

    return () => clearInterval(interval);
  }, [jobs, jobStatuses, allCompleted, onProcessingComplete, onError]);

  const getOverallProgress = () => {
    if (jobs.length === 0) return 0;
    
    const totalProgress = jobs.reduce((sum, job) => {
      const status = jobStatuses[job.job_id];
      return sum + (status?.progress || 0);
    }, 0);
    
    return Math.round(totalProgress / jobs.length);
  };

  const getCurrentMessage = () => {
    const statuses = Object.values(jobStatuses);
    if (statuses.length === 0) return "Starting processing...";
    
    const latestStatus = statuses[statuses.length - 1];
    return latestStatus?.message || "Processing documents...";
  };

  return (
    <div className="processing-loader">
      <div className="loader-content">
        <div className="processing-animation">
          <div className="processing-step active">
            <FileText size={24} />
            <span>Reading Documents</span>
          </div>
          
          <div className="arrow">→</div>
          
          <div className="processing-step active">
            <Cpu size={24} />
            <span>Generating Embeddings</span>
          </div>
          
          <div className="arrow">→</div>
          
          <div className="processing-step active">
            <Brain size={24} />
            <span>Creating Hash Sets</span>
          </div>
          
          <div className="arrow">→</div>
          
          <div className="processing-step active">
            <Zap size={24} />
            <span>Generating Results</span>
          </div>
        </div>

        <div className="spinner-container">
          <div className="spinner"></div>
          <p>{getCurrentMessage()}</p>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${getOverallProgress()}%` }}
            ></div>
          </div>
          <p className="processing-details">
            Progress: {getOverallProgress()}% - Processing {jobs.length} document(s)
          </p>
        </div>

        <div className="job-status">
          {jobs.map((job, index) => {
            const status = jobStatuses[job.job_id];
            return (
              <div key={job.job_id} className="job-item">
                <div className="job-header">
                  <span className="job-filename">{job.filename}</span>
                  {status?.status === 'completed' && <CheckCircle size={16} className="text-green-600" />}
                  {status?.status === 'error' && <AlertCircle size={16} className="text-red-600" />}
                  {status?.status === 'processing' && <div className="mini-spinner"></div>}
                </div>
                {status && (
                  <div className="job-progress">
                    <div className="job-progress-bar">
                      <div 
                        className="job-progress-fill" 
                        style={{ width: `${status.progress}%` }}
                      ></div>
                    </div>
                    <span className="job-message">{status.message}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="processing-info">
          <div className="info-item">
            <strong>What's happening:</strong>
            <ul>
              <li>Extracting text from your SOP documents</li>
              <li>Detecting sections and subsections</li>
              <li>Generating embeddings for semantic analysis</li>
              <li>Creating content hashes for exact matching</li>
              <li>Storing in separate collections</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessingLoader;
