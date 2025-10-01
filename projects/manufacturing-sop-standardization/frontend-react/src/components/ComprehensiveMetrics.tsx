import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Hash, 
  FileText, 
  TrendingUp, 
  CheckCircle, 
  AlertTriangle, 
  Info,
  ChevronDown,
  ChevronUp,
  RefreshCw
} from 'lucide-react';
import { 
  VectorDBStats, 
  ExactMatchStats, 
  ExactMatchResult, 
  SentenceMatchResult, 
  SemanticComparisonResult 
} from '../types';
import { apiService } from '../services/api';

interface ComprehensiveMetricsProps {
  doc1: string;
  doc2: string;
  onReset: () => void;
}

const ComprehensiveMetrics: React.FC<ComprehensiveMetricsProps> = ({ doc1, doc2, onReset }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Data states
  const [vectorStats, setVectorStats] = useState<VectorDBStats | null>(null);
  const [exactMatchStats, setExactMatchStats] = useState<ExactMatchStats | null>(null);
  const [exactMatchResult, setExactMatchResult] = useState<ExactMatchResult | null>(null);
  const [sentenceMatchResult, setSentenceMatchResult] = useState<SentenceMatchResult | null>(null);
  const [semanticResult, setSemanticResult] = useState<SemanticComparisonResult | null>(null);

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 0.8) return 'High Match';
    if (score >= 0.6) return 'Medium Match';
    return 'Low Match';
  };

  const formatPercentage = (score: number): string => {
    return `${(score * 100).toFixed(1)}%`;
  };

  const loadAllMetrics = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all metrics in parallel
      const [
        vectorStatsRes,
        exactMatchStatsRes,
        exactMatchRes,
        sentenceMatchRes,
        semanticRes
      ] = await Promise.all([
        apiService.getVectorStats(),
        apiService.getExactMatchStats(),
        apiService.compareExact(doc1, doc2),
        apiService.compareSentenceLevel(doc1, doc2),
        apiService.compareSemantic(doc1, doc2)
      ]);

      setVectorStats(vectorStatsRes.stats);
      setExactMatchStats(exactMatchStatsRes.stats);
      setExactMatchResult(exactMatchRes.results);
      setSentenceMatchResult(sentenceMatchRes.results);
      setSemanticResult(semanticRes.results);

    } catch (err: any) {
      setError(err.message || 'Failed to load metrics');
      console.error('Error loading metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (doc1 && doc2) {
      loadAllMetrics();
    }
  }, [doc1, doc2]);

  const renderSection = (
    id: string,
    title: string,
    icon: React.ReactNode,
    content: React.ReactNode,
    defaultExpanded = false
  ) => {
    const isExpanded = expandedSections.has(id);
    
    return (
      <div className="metrics-section">
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

  if (loading) {
    return (
      <div className="comprehensive-metrics">
        <div className="loading-state">
          <RefreshCw className="animate-spin" size={24} />
          <p>Loading comprehensive metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="comprehensive-metrics">
        <div className="error-state">
          <AlertTriangle size={24} />
          <p>Error loading metrics: {error}</p>
          <button className="retry-btn" onClick={loadAllMetrics}>
            <RefreshCw size={16} />
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="comprehensive-metrics">
      <div className="metrics-header">
        <h2>📊 Comprehensive Document Analysis</h2>
        <div className="header-actions">
          <button className="refresh-btn" onClick={loadAllMetrics}>
            <RefreshCw size={16} />
            Refresh Metrics
          </button>
          <button className="reset-btn" onClick={onReset}>
            Analyze New Documents
          </button>
        </div>
      </div>

      {/* Overview Section */}
      {renderSection(
        'overview',
        'Analysis Overview',
        <TrendingUp size={20} />,
        <div className="overview-content">
          <div className="documents-comparison">
            <h4>📄 Documents Being Compared</h4>
            <div className="doc-pair">
              <span className="doc-name">{doc1}</span>
              <span className="vs">vs</span>
              <span className="doc-name">{doc2}</span>
            </div>
          </div>

          <div className="metrics-summary">
            <div className="summary-grid">
              {/* Semantic Similarity */}
              <div className="summary-card">
                <div className="card-header">
                  <BarChart3 size={20} />
                  <span>Semantic Similarity</span>
                </div>
                <div className={`score-display ${getScoreColor(semanticResult?.similarity_score || 0)}`}>
                  <span className="score-value">
                    {formatPercentage(semanticResult?.similarity_score || 0)}
                  </span>
                  <span className="score-label">
                    {getScoreLabel(semanticResult?.similarity_score || 0)}
                  </span>
                </div>
              </div>

              {/* Section-level Exact Match */}
              <div className="summary-card">
                <div className="card-header">
                  <Hash size={20} />
                  <span>Section Exact Match</span>
                </div>
                <div className={`score-display ${getScoreColor(exactMatchResult?.exact_match_score || 0)}`}>
                  <span className="score-value">
                    {formatPercentage(exactMatchResult?.exact_match_score || 0)}
                  </span>
                  <span className="score-label">
                    {getScoreLabel(exactMatchResult?.exact_match_score || 0)}
                  </span>
                </div>
              </div>

              {/* Sentence-level Exact Match */}
              <div className="summary-card">
                <div className="card-header">
                  <FileText size={20} />
                  <span>Sentence Exact Match</span>
                </div>
                <div className={`score-display ${getScoreColor(sentenceMatchResult?.sentence_match_score || 0)}`}>
                  <span className="score-value">
                    {formatPercentage(sentenceMatchResult?.sentence_match_score || 0)}
                  </span>
                  <span className="score-label">
                    {getScoreLabel(sentenceMatchResult?.sentence_match_score || 0)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>,
        true
      )}

      {/* Semantic Analysis Section */}
      {renderSection(
        'semantic',
        'Semantic Similarity Analysis',
        <BarChart3 size={20} />,
        <div className="semantic-analysis">
          <div className="analysis-stats">
            <div className="stat-row">
              <span>Overall Similarity Score:</span>
              <span className={`stat-value ${getScoreColor(semanticResult?.similarity_score || 0)}`}>
                {formatPercentage(semanticResult?.similarity_score || 0)}
              </span>
            </div>
            <div className="stat-row">
              <span>Average Chunk Similarity:</span>
              <span className={`stat-value ${getScoreColor(semanticResult?.avg_chunk_similarity || 0)}`}>
                {formatPercentage(semanticResult?.avg_chunk_similarity || 0)}
              </span>
            </div>
            <div className="stat-row">
              <span>Document 1 Chunks:</span>
              <span className="stat-value">{semanticResult?.chunk_count_1 || 0}</span>
            </div>
            <div className="stat-row">
              <span>Document 2 Chunks:</span>
              <span className="stat-value">{semanticResult?.chunk_count_2 || 0}</span>
            </div>
          </div>

          {semanticResult?.top_similar_chunks && semanticResult.top_similar_chunks.length > 0 && (
            <div className="similar-chunks">
              <h4>🔍 Top Similar Chunk Pairs</h4>
              <div className="chunk-pairs">
                {semanticResult.top_similar_chunks.slice(0, 5).map((pair, index) => (
                  <div key={index} className="chunk-pair">
                    <div className="pair-header">
                      <span className="similarity-score">
                        {formatPercentage(pair.similarity)}
                      </span>
                      <span className="pair-sections">
                        {pair.chunk1_section} ↔ {pair.chunk2_section}
                      </span>
                    </div>
                    <div className="pair-details">
                      <span>Chunk {pair.chunk1_index} ↔ Chunk {pair.chunk2_index}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Exact Match Analysis Section */}
      {renderSection(
        'exact-match',
        'Section-Level Exact Matching',
        <Hash size={20} />,
        <div className="exact-match-analysis">
          <div className="match-stats">
            <div className="stat-row">
              <span>Document 1 Sections:</span>
              <span className="stat-value">{exactMatchResult?.doc1_total_sections || 0}</span>
            </div>
            <div className="stat-row">
              <span>Document 2 Sections:</span>
              <span className="stat-value">{exactMatchResult?.doc2_total_sections || 0}</span>
            </div>
            <div className="stat-row">
              <span>Common Sections:</span>
              <span className="stat-value highlight">{exactMatchResult?.common_sections || 0}</span>
            </div>
            <div className="stat-row">
              <span>Exact Match Score:</span>
              <span className={`stat-value ${getScoreColor(exactMatchResult?.exact_match_score || 0)}`}>
                {formatPercentage(exactMatchResult?.exact_match_score || 0)}
              </span>
            </div>
          </div>

          {exactMatchResult?.matches && exactMatchResult.matches.length > 0 && (
            <div className="exact-matches">
              <h4>✅ Identical Sections Found</h4>
              <div className="matches-list">
                {exactMatchResult.matches.slice(0, 5).map((match, index) => (
                  <div key={index} className="match-item">
                    <div className="match-header">
                      <CheckCircle size={16} className="text-green-600" />
                      <span>Section {match.doc1_section.section_number}</span>
                    </div>
                    <div className="match-details">
                      <span className="section-title">{match.doc1_section.section_title}</span>
                      <span className="hash-preview">
                        Hash: {match.content_hash.substring(0, 12)}...
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sentence-Level Analysis Section */}
      {renderSection(
        'sentence-match',
        'Sentence-Level Exact Matching',
        <FileText size={20} />,
        <div className="sentence-match-analysis">
          <div className="match-stats">
            <div className="stat-row">
              <span>Document 1 Sentences:</span>
              <span className="stat-value">{sentenceMatchResult?.doc1_total_sentences || 0}</span>
            </div>
            <div className="stat-row">
              <span>Document 2 Sentences:</span>
              <span className="stat-value">{sentenceMatchResult?.doc2_total_sentences || 0}</span>
            </div>
            <div className="stat-row">
              <span>Common Sentences:</span>
              <span className="stat-value highlight">{sentenceMatchResult?.common_sentences || 0}</span>
            </div>
            <div className="stat-row">
              <span>Sentence Match Score:</span>
              <span className={`stat-value ${getScoreColor(sentenceMatchResult?.sentence_match_score || 0)}`}>
                {formatPercentage(sentenceMatchResult?.sentence_match_score || 0)}
              </span>
            </div>
          </div>

          {sentenceMatchResult?.sentence_matches && sentenceMatchResult.sentence_matches.length > 0 && (
            <div className="sentence-matches">
              <h4>📝 Identical Sentences Found</h4>
              <div className="sentences-list">
                {sentenceMatchResult.sentence_matches.slice(0, 5).map((match, index) => (
                  <div key={index} className="sentence-item">
                    <div className="sentence-header">
                      <CheckCircle size={16} className="text-green-600" />
                      <span>Sentence {match.doc1_sentence.sentence_index}</span>
                    </div>
                    <div className="sentence-text">
                      "{match.doc1_sentence.sentence_text.substring(0, 100)}..."
                    </div>
                    <div className="sentence-details">
                      <span>Words: {match.doc1_sentence.word_count}</span>
                      <span>Hash: {match.sentence_hash.substring(0, 12)}...</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Database Statistics Section */}
      {renderSection(
        'database-stats',
        'Database Statistics',
        <Info size={20} />,
        <div className="database-stats">
          <div className="stats-grid">
            <div className="stat-card">
              <h4>Vector Database</h4>
              <div className="stat-details">
                <div className="stat-item">
                  <span>Total Chunks:</span>
                  <span>{vectorStats?.total_chunks || 0}</span>
                </div>
                <div className="stat-item">
                  <span>Total Documents:</span>
                  <span>{vectorStats?.total_documents || 0}</span>
                </div>
                <div className="stat-item">
                  <span>Collections:</span>
                  <span>{vectorStats?.collections?.length || 0}</span>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <h4>Exact Match Database</h4>
              <div className="stat-details">
                <div className="stat-item">
                  <span>Section Hashes:</span>
                  <span>{exactMatchStats?.total_section_hashes || 0}</span>
                </div>
                <div className="stat-item">
                  <span>Sentence Hashes:</span>
                  <span>{exactMatchStats?.total_sentence_hashes || 0}</span>
                </div>
                <div className="stat-item">
                  <span>Duplicate Sections:</span>
                  <span>{exactMatchStats?.duplicate_sections || 0}</span>
                </div>
                <div className="stat-item">
                  <span>Duplicate Sentences:</span>
                  <span>{exactMatchStats?.duplicate_sentences || 0}</span>
                </div>
              </div>
            </div>
          </div>

          {vectorStats?.document_chunk_counts && (
            <div className="document-breakdown">
              <h4>📊 Document Breakdown</h4>
              <div className="breakdown-list">
                {Object.entries(vectorStats.document_chunk_counts).map(([doc, count]) => (
                  <div key={doc} className="breakdown-item">
                    <span className="doc-name">{doc}</span>
                    <span className="chunk-count">{count} chunks</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ComprehensiveMetrics;

