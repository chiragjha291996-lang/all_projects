import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Copy, FileText, Loader2 } from 'lucide-react';
import { SimilarityAnalysis } from '../types';
import { apiService } from '../services/api';

interface SideBySideComparisonProps {
  similarityAnalysis: SimilarityAnalysis;
}

interface HighlightedSection {
  type: 'difference' | 'similarity' | 'missing' | 'exact_match' | 'semantic_similar' | 'info' | 'safety' | 'operational';
  content: string;
  startIndex: number;
  endIndex: number;
  description?: string;
  source?: 'exact' | 'semantic';
  similarity_score?: number;
}

interface ComparisonData {
  exactMatches?: any;
  sentenceMatches?: any;
  semanticSimilarities?: any;
  differences?: any;
  loading: boolean;
  error?: string;
}

const SideBySideComparison: React.FC<SideBySideComparisonProps> = ({ similarityAnalysis }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [doc1Sections, setDoc1Sections] = useState<HighlightedSection[]>([]);
  const [doc2Sections, setDoc2Sections] = useState<HighlightedSection[]>([]);
  const [syncScroll, setSyncScroll] = useState(true);
  const [comparisonData, setComparisonData] = useState<ComparisonData>({ loading: false });

  useEffect(() => {
    // Fetch real comparison data and parse documents for highlighting
    fetchComparisonData();
  }, [similarityAnalysis]);

  const fetchComparisonData = async () => {
    if (!similarityAnalysis?.doc1_filename || !similarityAnalysis?.doc2_filename) {
      return;
    }

    setComparisonData({ loading: true });

    try {
      // Fetch exact matches, sentence matches, and semantic similarities
      const [exactResult, sentenceResult, differencesResult] = await Promise.all([
        apiService.compareExact(similarityAnalysis?.doc1_filename, similarityAnalysis?.doc2_filename),
        apiService.compareSentenceLevel(similarityAnalysis?.doc1_filename, similarityAnalysis?.doc2_filename),
        apiService.getDifferences(similarityAnalysis?.doc1_filename, similarityAnalysis?.doc2_filename)
      ]);

      setComparisonData({
        exactMatches: exactResult.results,
        sentenceMatches: sentenceResult.results,
        differences: differencesResult.results,
        loading: false
      });

      // Parse the real data for highlighting
      parseRealComparisonData(exactResult.results, sentenceResult.results, differencesResult.results);
    } catch (error: any) {
      console.error('Error fetching comparison data:', error);
      setComparisonData({
        loading: false,
        error: error.message || 'Failed to fetch comparison data'
      });
      // Fallback to mock data
      parseDocumentsForHighlighting();
    }
  };

  const parseRealComparisonData = (exactMatches: any, sentenceMatches: any, differences: any) => {
    const doc1Highlights: HighlightedSection[] = [];
    const doc2Highlights: HighlightedSection[] = [];

    // Process exact matches with actual content
    if (exactMatches && exactMatches.matches) {
      exactMatches.matches.forEach((match: any, index: number) => {
        const actualContent = match.matched_content || match.doc1_section?.content || 'No content available';
        const sectionTitle = match.section_title || match.doc1_section_title || 'Section';
        
        doc1Highlights.push({
          type: 'exact_match',
          content: `✅ EXACT MATCH ${index + 1}: ${sectionTitle}\n\n${actualContent.substring(0, 500)}${actualContent.length > 500 ? '...' : ''}`,
          startIndex: index * 120,
          endIndex: (index + 1) * 120,
          description: `Identical content: ${sectionTitle}`,
          source: 'exact',
          similarity_score: 1.0
        });

        doc2Highlights.push({
          type: 'exact_match',
          content: `✅ EXACT MATCH ${index + 1}: ${sectionTitle}\n\n${actualContent.substring(0, 500)}${actualContent.length > 500 ? '...' : ''}`,
          startIndex: index * 120,
          endIndex: (index + 1) * 120,
          description: `Identical content: ${sectionTitle}`,
          source: 'exact',
          similarity_score: 1.0
        });
      });
    }

    // Process sentence matches
    if (sentenceMatches && sentenceMatches.sentence_matches) {
      sentenceMatches.sentence_matches.forEach((match: any, index: number) => {
        const startIdx = (exactMatches?.matches?.length || 0) * 120 + index * 100;
        
        const actualSentence = match.matched_sentence || match.doc1_sentence?.sentence_text || 'No sentence available';
        const sectionTitle = match.section_title || 'Section';
        
        doc1Highlights.push({
          type: 'semantic_similar',
          content: `🔗 SENTENCE MATCH ${index + 1}: ${sectionTitle}\n\n"${actualSentence}"`,
          startIndex: startIdx,
          endIndex: startIdx + 100,
          description: `Matching sentence in ${sectionTitle}`,
          source: 'semantic',
          similarity_score: 1.0
        });

        doc2Highlights.push({
          type: 'semantic_similar',
          content: `🔗 SENTENCE MATCH ${index + 1}: ${sectionTitle}\n\n"${actualSentence}"`,
          startIndex: startIdx,
          endIndex: startIdx + 100,
          description: `Matching sentence in ${sectionTitle}`,
          source: 'semantic',
          similarity_score: 1.0
        });
      });
    }

    // Add semantic similarities from the original analysis
    const similarities = similarityAnalysis?.key_similarities || [];
    const startIdx = (exactMatches?.matches?.length || 0) * 120 + (sentenceMatches?.sentence_matches?.length || 0) * 100;
    
    similarities.forEach((sim, index) => {
      const simStartIdx = startIdx + index * 80;
      doc1Highlights.push({
        type: 'semantic_similar',
        content: `Semantic Similarity ${index + 1}: ${sim}`,
        startIndex: simStartIdx,
        endIndex: simStartIdx + 80,
        description: sim,
        source: 'semantic',
        similarity_score: similarityAnalysis?.combined_similarity_score || 0
      });

      doc2Highlights.push({
        type: 'semantic_similar',
        content: `Semantic Similarity ${index + 1}: ${sim}`,
        startIndex: simStartIdx,
        endIndex: simStartIdx + 80,
        description: sim,
        source: 'semantic',
        similarity_score: similarityAnalysis?.combined_similarity_score || 0
      });
    });

    // Process actual differences
    if (differences && differences.doc1_unique_sections) {
      differences.doc1_unique_sections.forEach((diff: any, index: number) => {
        const diffStartIdx = startIdx + (exactMatches?.matches?.length || 0) * 120 + (sentenceMatches?.sentence_matches?.length || 0) * 100 + index * 150;
        const actualContent = diff.content || 'No content available';
        const sectionTitle = diff.section_title || 'Section';
        
        doc1Highlights.push({
          type: 'difference',
          content: `❌ UNIQUE TO DOC1 ${index + 1}: ${sectionTitle}\n\n${actualContent.substring(0, 400)}${actualContent.length > 400 ? '...' : ''}`,
          startIndex: diffStartIdx,
          endIndex: diffStartIdx + 150,
          description: `Content unique to ${similarityAnalysis.doc1_filename}`,
          source: 'exact',
          similarity_score: 0.0
        });
      });
    }

    if (differences && differences.doc2_unique_sections) {
      differences.doc2_unique_sections.forEach((diff: any, index: number) => {
        const diffStartIdx = startIdx + (exactMatches?.matches?.length || 0) * 120 + (sentenceMatches?.sentence_matches?.length || 0) * 100 + index * 150;
        const actualContent = diff.content || 'No content available';
        const sectionTitle = diff.section_title || 'Section';
        
        doc2Highlights.push({
          type: 'difference',
          content: `❌ UNIQUE TO DOC2 ${index + 1}: ${sectionTitle}\n\n${actualContent.substring(0, 400)}${actualContent.length > 400 ? '...' : ''}`,
          startIndex: diffStartIdx,
          endIndex: diffStartIdx + 150,
          description: `Content unique to ${similarityAnalysis?.doc2_filename}`,
          source: 'exact',
          similarity_score: 0.0
        });
      });
    }

    // Add some test content to ensure scrolling works
    for (let i = 0; i < 10; i++) {
      const testStartIdx = startIdx + (exactMatches?.matches?.length || 0) * 120 + (sentenceMatches?.sentence_matches?.length || 0) * 100 + (differences?.doc1_unique_sections?.length || 0) * 150 + i * 100;
      doc1Highlights.push({
        type: 'info',
        content: `Test Content ${i + 1}: This is additional content to test scrolling functionality. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.`,
        startIndex: testStartIdx,
        endIndex: testStartIdx + 100,
        description: `Test content item ${i + 1}`,
        source: 'semantic',
        similarity_score: 0.8
      });

      doc2Highlights.push({
        type: 'info',
        content: `Test Content ${i + 1}: This is additional content to test scrolling functionality. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.`,
        startIndex: testStartIdx,
        endIndex: testStartIdx + 100,
        description: `Test content item ${i + 1}`,
        source: 'semantic',
        similarity_score: 0.8
      });
    }

    setDoc1Sections(doc1Highlights);
    setDoc2Sections(doc2Highlights);
  };

  const parseDocumentsForHighlighting = () => {
    // For now, we'll create mock highlighted sections based on the analysis
    // In a full implementation, this would use the chunk-level analysis
    const differences = similarityAnalysis?.key_differences || [];
    const similarities = similarityAnalysis?.key_similarities || [];

    // Create sections for highlighting based on the analysis
    const doc1Highlights: HighlightedSection[] = [];
    const doc2Highlights: HighlightedSection[] = [];

    // Add difference highlights
    differences.forEach((diff, index) => {
      doc1Highlights.push({
        type: 'difference',
        content: `Difference ${index + 1}: ${diff}`,
        startIndex: index * 100,
        endIndex: (index + 1) * 100,
        description: diff
      });

      doc2Highlights.push({
        type: 'difference',
        content: `Corresponding difference in ${similarityAnalysis?.doc2_filename}`,
        startIndex: index * 100,
        endIndex: (index + 1) * 100,
        description: diff
      });
    });

    // Add similarity highlights
    similarities.forEach((sim, index) => {
      const startIdx = differences.length * 100 + index * 80;
      doc1Highlights.push({
        type: 'similarity',
        content: `Similarity ${index + 1}: ${sim}`,
        startIndex: startIdx,
        endIndex: startIdx + 80,
        description: sim
      });

      doc2Highlights.push({
        type: 'similarity',
        content: `Matching section in ${similarityAnalysis?.doc2_filename}`,
        startIndex: startIdx,
        endIndex: startIdx + 80,
        description: sim
      });
    });

    setDoc1Sections(doc1Highlights);
    setDoc2Sections(doc2Highlights);
  };

  const handleScroll = (event: React.UIEvent<HTMLDivElement>, side: 'left' | 'right') => {
    if (!syncScroll) return;

    const target = event.target as HTMLDivElement;
    const otherSide = side === 'left' ? 'doc2-content' : 'doc1-content';
    const otherElement = document.getElementById(otherSide);

    if (otherElement) {
      otherElement.scrollTop = target.scrollTop;
    }
  };

  const copyToClipboard = (text: string, filename: string) => {
    navigator.clipboard.writeText(text);
    // Could add a toast notification here
  };

  const renderHighlightedContent = (sections: HighlightedSection[], filename: string) => {
    if (comparisonData.loading) {
      return (
        <div className="highlighted-content loading">
          <div className="loading-content">
            <Loader2 className="animate-spin" size={24} />
            <p>Loading comparison data...</p>
          </div>
        </div>
      );
    }

    if (comparisonData.error) {
      return (
        <div className="highlighted-content error">
          <div className="error-content">
            <p>⚠️ {comparisonData.error}</p>
            <button onClick={fetchComparisonData} className="retry-button">
              Retry
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="highlighted-content">
        {sections.map((section, index) => (
          <div 
            key={index} 
            className={`content-section ${section.type}`}
            title={section.description}
          >
            <div className="section-marker">
              {section.type === 'difference' && '⚠️ Difference'}
              {section.type === 'similarity' && '✅ Similar'}
              {section.type === 'missing' && '❌ Missing'}
              {section.type === 'exact_match' && '🎯 Exact Match'}
              {section.type === 'semantic_similar' && '🧠 Semantic Similar'}
              {section.type === 'info' && 'ℹ️ Information'}
              {section.type === 'safety' && '🛡️ Safety'}
              {section.type === 'operational' && '⚙️ Operational'}
            </div>
            <div className="section-content">
              {section.content}
              {section.similarity_score && (
                <div className="similarity-score">
                  Score: {(section.similarity_score * 100).toFixed(1)}%
                </div>
              )}
            </div>
            {section.source && (
              <div className="source-badge">
                {section.source === 'exact' ? 'Exact' : 'Semantic'}
              </div>
            )}
          </div>
        ))}
        
        {/* Add procedure type and key findings */}
        {similarityAnalysis.procedure_type && (
          <div className="content-section info">
            <div className="section-marker">📋 Procedure Type</div>
            <div className="section-content">
              {similarityAnalysis.procedure_type}
            </div>
          </div>
        )}

        {similarityAnalysis.safety_parameters && (
          <div className="content-section safety">
            <div className="section-marker">🛡️ Safety Parameters</div>
            <div className="section-content">
              {similarityAnalysis.safety_parameters}
            </div>
          </div>
        )}

        {similarityAnalysis.operational_differences && (
          <div className="content-section operational">
            <div className="section-marker">⚙️ Operational Differences</div>
            <div className="section-content">
              {similarityAnalysis.operational_differences}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (!similarityAnalysis) {
    return null;
  }

  return (
    <div className="side-by-side-comparison">
      <div className="comparison-header">
        <div className="header-left">
          <button 
            className="expand-button"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            <span>Side-by-Side Document Comparison</span>
          </button>
        </div>
        
        <div className="header-controls">
          <button 
            className="debug-button"
            onClick={() => {
              const doc1Content = document.getElementById('doc1-content');
              const doc2Content = document.getElementById('doc2-content');
              console.log('Doc1 scroll height:', doc1Content?.scrollHeight);
              console.log('Doc1 client height:', doc1Content?.clientHeight);
              console.log('Doc2 scroll height:', doc2Content?.scrollHeight);
              console.log('Doc2 client height:', doc2Content?.clientHeight);
              
              // Test scrolling programmatically
              if (doc1Content) {
                doc1Content.scrollTop = 100;
                console.log('Scrolled doc1 to 100px');
              }
              if (doc2Content) {
                doc2Content.scrollTop = 100;
                console.log('Scrolled doc2 to 100px');
              }
            }}
          >
            Debug Scroll
          </button>
          <label className="sync-scroll-toggle">
            <input 
              type="checkbox" 
              checked={syncScroll} 
              onChange={(e) => setSyncScroll(e.target.checked)}
            />
            Sync Scroll
          </label>
          
          <div className="similarity-indicator">
            <span className="similarity-label">Overall Similarity:</span>
            <span className={`similarity-value ${
              (similarityAnalysis.combined_similarity_score || 0) >= 0.7 ? 'high' : 
              (similarityAnalysis.combined_similarity_score || 0) >= 0.4 ? 'medium' : 'low'
            }`}>
              {((similarityAnalysis.combined_similarity_score || 0) * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="comparison-content">
          <div className="comparison-legend">
            <div className="legend-item">
              <span className="legend-color exact_match"></span>
              <span>Exact Matches</span>
            </div>
            <div className="legend-item">
              <span className="legend-color semantic_similar"></span>
              <span>Semantic Similar</span>
            </div>
            <div className="legend-item">
              <span className="legend-color difference"></span>
              <span>Key Differences</span>
            </div>
            <div className="legend-item">
              <span className="legend-color similarity"></span>
              <span>Similar Content</span>
            </div>
            <div className="legend-item">
              <span className="legend-color safety"></span>
              <span>Safety Related</span>
            </div>
            <div className="legend-item">
              <span className="legend-color operational"></span>
              <span>Operational</span>
            </div>
          </div>

          <div className="documents-container">
            <div className="document-pane">
              <div className="document-header">
                <div className="document-title">
                  <FileText size={16} />
                  <span>{similarityAnalysis?.doc1_filename || 'Document 1'}</span>
                </div>
                <button 
                  className="copy-button"
                  onClick={() => copyToClipboard(doc1Sections.map(s => s.content).join('\n'), similarityAnalysis?.doc1_filename || 'Document 1')}
                  title="Copy content"
                >
                  <Copy size={14} />
                </button>
              </div>
              
              <div 
                id="doc1-content"
                className="document-content"
                onScroll={(e) => handleScroll(e, 'left')}
              >
                {renderHighlightedContent(doc1Sections, similarityAnalysis.doc1_filename || 'Document 1')}
              </div>
            </div>

            <div className="comparison-divider">
              <div className="divider-line"></div>
              <div className="comparison-stats">
                <div className="stat">
                  <span className="stat-value">
                    {(comparisonData.exactMatches?.matches?.length || 0) + 
                     (comparisonData.sentenceMatches?.sentence_matches?.length || 0)}
                  </span>
                  <span className="stat-label">Exact Matches</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{similarityAnalysis.key_similarities?.length || 0}</span>
                  <span className="stat-label">Semantic Similar</span>
                </div>
                <div className="stat">
                  <span className="stat-value">
                    {(comparisonData.differences?.doc1_unique_count || 0) + 
                     (comparisonData.differences?.doc2_unique_count || 0)}
                  </span>
                  <span className="stat-label">Unique Sections</span>
                </div>
              </div>
            </div>

            <div className="document-pane">
              <div className="document-header">
                <div className="document-title">
                  <FileText size={16} />
                  <span>{similarityAnalysis?.doc2_filename || 'Document 2'}</span>
                </div>
                <button 
                  className="copy-button"
                  onClick={() => copyToClipboard(doc2Sections.map(s => s.content).join('\n'), similarityAnalysis?.doc2_filename || 'Document 2')}
                  title="Copy content"
                >
                  <Copy size={14} />
                </button>
              </div>
              
              <div 
                id="doc2-content"
                className="document-content"
                onScroll={(e) => handleScroll(e, 'right')}
              >
                {renderHighlightedContent(doc2Sections, similarityAnalysis?.doc2_filename || 'Document 2')}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SideBySideComparison;
