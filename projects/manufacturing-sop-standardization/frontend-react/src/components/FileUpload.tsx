import React, { useState, useRef, useCallback } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { apiService, formatFileSize } from '../services/api';
import { FileData, ProcessingJob } from '../types';

interface FileUploadProps {
  onFilesUploaded: (files: FileData[]) => void;
  onJobsCreated: (jobs: ProcessingJob[]) => void;
  onProcessingStart: () => void;
  onError: (error: string) => void;
  uploadedFiles: FileData[];
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFilesUploaded,
  onJobsCreated,
  onProcessingStart,
  onError,
  uploadedFiles,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback(async (files: FileList) => {
    // Validate files
    const validFiles = Array.from(files).filter(file => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      return ['pdf', 'docx'].includes(extension || '');
    });

    if (validFiles.length === 0) {
      onError('Please select valid PDF or DOCX files.');
      return;
    }

    setIsUploading(true);
    try {
      // Use the new async upload endpoint
      const result = await apiService.uploadFilesVector(files);
      
      // Convert the job response to file data format
      const fileData: FileData[] = result.jobs.map(job => ({
        filename: job.filename,
        size: 0, // We don't have size info from the job
        filepath: job.filename
      }));
      
      onFilesUploaded(fileData);
      
      // Pass jobs to parent for monitoring
      onJobsCreated(result.jobs);
      
      // Start processing monitoring
      onProcessingStart();
      
    } catch (error: any) {
      onError(error.response?.data?.error || 'Upload failed: ' + error.message);
    } finally {
      setIsUploading(false);
    }
  }, [onFilesUploaded, onError, onProcessingStart]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files);
    }
  }, [handleFileSelect]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
  }, [handleFileSelect]);

  const handleProcessDocuments = async () => {
    onProcessingStart();
    try {
      const result = await apiService.processDocuments();
      onProcessingStart(); // Will be handled by parent to show results
      // Parent will handle the result through the processing state
      window.dispatchEvent(new CustomEvent('analysisComplete', { detail: result }));
    } catch (error: any) {
      onError(error.response?.data?.error || 'Processing failed: ' + error.message);
    }
  };

  const removeFile = (filename: string) => {
    const updatedFiles = uploadedFiles.filter(file => file.filename !== filename);
    onFilesUploaded(updatedFiles);
  };

  return (
    <div className="file-upload-container">
      <div
        className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-content">
          <Upload size={48} className="upload-icon" />
          <h3>Click to upload or drag & drop SOP files</h3>
          <p>Supports PDF and DOCX files (Max 16MB each)</p>
          {isUploading && <p className="uploading-text">Uploading...</p>}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx"
          onChange={handleFileInputChange}
          className="file-input"
        />
      </div>

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h3>Uploaded Files ({uploadedFiles.length})</h3>
          <div className="files-list">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="file-item">
                <div className="file-info">
                  <FileText size={20} className="file-icon" />
                  <div className="file-details">
                    <span className="file-name">{file.filename}</span>
                    <span className="file-size">{formatFileSize(file.size)}</span>
                  </div>
                </div>
                <button
                  className="remove-file-btn"
                  onClick={() => removeFile(file.filename)}
                  title="Remove file"
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>

          <button
            className={`process-btn ${uploadedFiles.length < 2 ? 'disabled' : ''}`}
            onClick={handleProcessDocuments}
            disabled={uploadedFiles.length < 2 || isUploading}
          >
            {uploadedFiles.length < 2
              ? `Upload ${2 - uploadedFiles.length} more file(s) to analyze`
              : 'Analyze SOPs with AI'
            }
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
