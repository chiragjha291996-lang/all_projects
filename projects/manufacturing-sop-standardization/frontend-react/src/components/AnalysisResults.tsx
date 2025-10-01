import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, FileText, AlertTriangle, CheckCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { AnalysisResult, ChunkCluster } from '../types';
import SideBySideComparison from './SideBySideComparison';

interface AnalysisResultsProps {
  result: AnalysisResult;
  onReset: () => void;
  onShowComprehensiveMetrics?: (doc1: string, doc2: string) => void;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result, onReset, onShowComprehensiveMetrics }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const navigate = useNavigate();

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  // Safety checks for data structure
  if (!result || !result.clustering_result) {
    return (
      <div className="analysis-results">
        <div className="error">
          <p>Invalid analysis result received. Please try uploading and analyzing the documents again.</p>
          <button className="reset-btn" onClick={onReset}>
            Upload New Documents
          </button>
        </div>
      </div>
    );
  }

  const { clustering_result } = result;
  const similarity = clustering_result?.similarity_analysis;
  const embeddingAnalysis = similarity?.embedding_analysis;

  const getSimilarityColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSimilarityLabel = (score: number): string => {
    if (score >= 0.8) return 'High Similarity';
    if (score >= 0.6) return 'Medium Similarity';
    return 'Low Similarity';
  };

  const renderSection = (
    id: string,
    title: string,
    icon: React.ReactNode,
    content: React.ReactNode,
    defaultExpanded = false
  ) => {
    const isExpanded = expandedSections.has(id);
    
    return (
      <div className="analysis-section">
        <div 
          className="section-header"
          onClick={() => toggleSection(id)}
        >
          <div className="section-title">
            {icon}
            <h3>{title}</h3>
          </div>
          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>
        {isExpanded && (
          <div className="section-content">
            {content}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="analysis-results">
      <div className="results-header">
        <h2>Analysis Results</h2>
        <div className="header-actions">
          {onShowComprehensiveMetrics && similarity?.doc1_filename && similarity?.doc2_filename && (
            <button 
              className="metrics-btn" 
              onClick={() => onShowComprehensiveMetrics(similarity.doc1_filename, similarity.doc2_filename)}
            >
              📊 View Comprehensive Metrics
            </button>
          )}
          <button className="reset-btn" onClick={onReset}>
            <RefreshCw size={16} />
            Analyze New Documents
          </button>
        </div>
      </div>

      <div className="results-summary">
        <div className="summary-card">
          <div className="summary-item">
            <span className="label">Documents Analyzed:</span>
            <span className="value">{result.processed_documents}</span>
          </div>
            <div className="summary-item">
              <span className="label">Overall Similarity:</span>
              <span className={`value ${getSimilarityColor(similarity?.combined_similarity_score || 0)}`}>
                {((similarity?.combined_similarity_score || 0) * 100).toFixed(1)}% 
                ({getSimilarityLabel(similarity?.combined_similarity_score || 0)})
              </span>
            </div>
          <div className="summary-item">
            <span className="label">Clusters Found:</span>
            <span className="value">{clustering_result.total_clusters}</span>
          </div>
        </div>
      </div>

      {/* Overview Section */}
      {renderSection(
        'overview',
        'Similarity Overview',
        <CheckCircle size={20} />,
        <div className="overview-content">
          <div className="comparison-card">
            <h4>Document Comparison</h4>
            <p><strong>{similarity?.doc1_filename || 'Document 1'}</strong> vs <strong>{similarity?.doc2_filename || 'Document 2'}</strong></p>
            
            <div className="score-breakdown">
              <div className="score-item">
                <span>LLM Analysis Score:</span>
                <span className={getSimilarityColor(similarity?.similarity_score || 0)}>
                  {((similarity?.similarity_score || 0) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="score-item">
                <span>Embedding Analysis Score:</span>
                <span className={getSimilarityColor(embeddingAnalysis?.overall_similarity || 0)}>
                  {((embeddingAnalysis?.overall_similarity || 0) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="score-item combined">
                <span>Combined Score:</span>
                <span className={getSimilarityColor(similarity?.combined_similarity_score || 0)}>
                  {((similarity?.combined_similarity_score || 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {similarity?.procedure_type && (
              <div className="procedure-type">
                <strong>Procedure Type:</strong> {similarity.procedure_type}
              </div>
            )}
          </div>
        </div>,
        true
      )}

      {/* Embedding Analysis Section */}
      {renderSection(
        'embedding',
        'Embedding Analysis Details',
        <Info size={20} />,
        <div className="embedding-analysis">
          <div className="embedding-stats">
            <div className="stat-item">
              <span>Chunks Analyzed:</span>
              <span>{embeddingAnalysis?.chunks1_count || 0} vs {embeddingAnalysis?.chunks2_count || 0}</span>
            </div>
            <div className="stat-item">
              <span>High Similarity Pairs:</span>
              <span>{embeddingAnalysis?.high_similarity_pairs?.length || 0}</span>
            </div>
            <div className="stat-item">
              <span>Analysis Summary:</span>
              <span>{embeddingAnalysis?.analysis_summary || 'No summary available'}</span>
            </div>
          </div>

          {embeddingAnalysis?.high_similarity_pairs?.length > 0 && (
            <div className="similarity-pairs">
              <h4>High Similarity Chunk Pairs</h4>
              {embeddingAnalysis?.high_similarity_pairs?.slice(0, 5).map((pair, index) => (
                <div key={index} className="pair-item">
                  <div className="pair-info">
                    <span className="chunk-id">{pair.chunk1_id}</span>
                    <span className="similarity-score">
                      {(pair.similarity * 100).toFixed(1)}% match
                    </span>
                    <span className="chunk-id">{pair.chunk2_id}</span>
                  </div>
                  <div className="section-info">
                    Section {pair.chunk1_section} ↔ Section {pair.chunk2_section}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Similarities Section */}
      {similarity?.key_similarities?.length > 0 && renderSection(
        'similarities',
        'Key Similarities',
        <CheckCircle size={20} />,
        <ul className="similarities-list">
          {similarity?.key_similarities?.map((sim, index) => (
            <li key={index} className="similarity-item">
              <CheckCircle size={16} className="text-green-600" />
              {sim}
            </li>
          ))}
        </ul>
      )}

      {/* Differences Section */}
      {similarity?.key_differences?.length > 0 && renderSection(
        'differences',
        'Key Differences',
        <AlertTriangle size={20} />,
        <ul className="differences-list">
          {similarity?.key_differences?.map((diff, index) => (
            <li key={index} className="difference-item">
              <AlertTriangle size={16} className="text-orange-600" />
              {diff}
            </li>
          ))}
        </ul>
      )}

      {/* Safety Parameters Section */}
      {similarity?.safety_parameters && renderSection(
        'safety',
        'Safety Parameters',
        <AlertTriangle size={20} />,
        <div className="safety-content">
          <p>{similarity?.safety_parameters}</p>
        </div>
      )}

      {/* Operational Differences Section */}
      {similarity?.operational_differences && renderSection(
        'operational',
        'Operational Differences',
        <FileText size={20} />,
        <div className="operational-content">
          <p>{similarity?.operational_differences}</p>
        </div>
      )}

      {/* Chunk Clustering Section */}
      {clustering_result.chunk_clustering?.clusters?.length > 0 && renderSection(
        'chunks',
        'Chunk-Level Clustering',
        <Info size={20} />,
        <div className="chunk-clustering">
          <p className="clustering-summary">
            {clustering_result.chunk_clustering.clustering_summary}
          </p>
          
          <div className="chunk-clusters">
            {clustering_result.chunk_clustering.clusters.map((cluster: ChunkCluster) => (
              <div key={cluster.cluster_id} className="chunk-cluster">
                <h4>Cluster {cluster.cluster_id}</h4>
                <div className="cluster-info">
                  <span>Chunks: {cluster.chunk_count}</span>
                  <span>Documents: {cluster.documents_involved.join(', ')}</span>
                  <span>Sections: {cluster.sections_involved.join(', ')}</span>
                </div>
                <p className="cluster-summary">{cluster.cluster_summary}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary Section */}
      {similarity?.summary && renderSection(
        'summary',
        'Analysis Summary',
        <FileText size={20} />,
        <div className="summary-content">
          <p>{similarity?.summary}</p>
          <div className="recommendation">
            <strong>Clustering Recommendation:</strong> {similarity?.cluster_recommendation}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {similarity && (
        <div className="analysis-actions">
          <button 
            className="detailed-analysis-btn"
            onClick={() => onShowComprehensiveMetrics?.(similarity.doc1_filename, similarity.doc2_filename)}
          >
            📊 View Comprehensive Metrics
          </button>
          <button 
            className="page-comparison-btn"
            onClick={() => {
              // Navigate to page comparison view
              navigate(`/page-comparison/${encodeURIComponent(similarity.doc1_filename)}/${encodeURIComponent(similarity.doc2_filename)}`);
            }}
          >
            📄 Show Detailed Analysis
          </button>
        </div>
      )}

      {/* Side-by-Side Comparison */}
      {similarity && <SideBySideComparison similarityAnalysis={similarity} />}
    </div>
  );
};

export default AnalysisResults;
