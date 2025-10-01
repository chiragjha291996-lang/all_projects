import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, FileText, Eye, EyeOff, Download, Search } from 'lucide-react';
import { apiService } from '../services/api';

interface PageComparisonViewerProps {
  doc1Name: string;
  doc2Name: string;
}

interface UniqueArea {
  document: 'doc1' | 'doc2';
  type: 'unique_page' | 'unique_word' | 'exact_match' | 'semantic_similar';
  content: string;
  coordinates?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  highlight_class: string;
  similarity_score?: number;
}

interface PageComparisonData {
  doc1_total_pages: number;
  doc2_total_pages: number;
  comparison_results: Array<{
    page_number: number;
    doc1_has_page: boolean;
    doc2_has_page: boolean;
    exact_matches: UniqueArea[];
    semantic_similarities: UniqueArea[];
    unique_areas: UniqueArea[];
    statistics: {
      doc1_word_count: number;
      doc2_word_count: number;
      exact_matches_count: number;
      semantic_similarities_count: number;
      unique_areas_count: number;
      exact_match_percentage: number;
      semantic_similarity_percentage: number;
      uniqueness_percentage: number;
    };
  }>;
  doc1_html_file: string;
  doc2_html_file: string;
  doc1_name: string;
  doc2_name: string;
  summary: {
    total_pages_compared: number;
    pages_with_exact_matches: number;
    pages_with_semantic_similarities: number;
    pages_with_unique_content: number;
    total_exact_matches: number;
    total_semantic_similarities: number;
    total_unique_areas: number;
    exact_match_coverage: number;
    semantic_similarity_coverage: number;
    uniqueness_coverage: number;
  };
}

const PageComparisonViewer: React.FC<PageComparisonViewerProps> = ({ doc1Name, doc2Name }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [comparisonData, setComparisonData] = useState<PageComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showHighlights, setShowHighlights] = useState(true);
  const [highlightFilter, setHighlightFilter] = useState<'all' | 'exact' | 'semantic' | 'unique'>('all');

  useEffect(() => {
    fetchComparisonData();
  }, [doc1Name, doc2Name]);

  const fetchComparisonData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.getPageComparison(doc1Name, doc2Name);
      setComparisonData(response.results);
    } catch (error: any) {
      console.error('Error fetching page comparison:', error);
      setError(error.response?.data?.error || 'Failed to load comparison data');
    } finally {
      setLoading(false);
    }
  };

  const totalPages = comparisonData ? 
    Math.max(comparisonData.doc1_total_pages, comparisonData.doc2_total_pages) : 0;

  const currentPageData = comparisonData?.comparison_results.find(
    page => page.page_number === currentPage
  );

  const getHighlightedAreas = (document: 'doc1' | 'doc2') => {
    if (!currentPageData) return [];
    
    const allAreas = [
      ...(currentPageData.exact_matches || []),
      ...(currentPageData.semantic_similarities || []),
      ...(currentPageData.unique_areas || [])
    ].filter(area => area.document === document);
    
    if (highlightFilter === 'all') return allAreas;
    if (highlightFilter === 'exact') return allAreas.filter(area => area.type === 'exact_match');
    if (highlightFilter === 'semantic') return allAreas.filter(area => area.type === 'semantic_similar');
    if (highlightFilter === 'unique') return allAreas.filter(area => area.type.includes('unique'));
    
    return allAreas;
  };

  const getHighlightColor = (type: string) => {
    switch (type) {
      case 'exact_match': return '#28a745'; // Green
      case 'semantic_similar': return '#ffc107'; // Yellow
      case 'unique_word': return '#dc3545'; // Red
      case 'unique_page': return '#17a2b8'; // Blue
      default: return '#6c757d'; // Gray
    }
  };

  if (loading) {
    return (
      <div className="page-comparison-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Converting PDFs to HTML and analyzing content...</p>
          <small>This may take a few moments for large documents</small>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-comparison-error">
        <div className="error-content">
          <h3>Error Loading Comparison</h3>
          <p>{error}</p>
          <button onClick={fetchComparisonData} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!comparisonData) {
    return (
      <div className="page-comparison-error">
        <p>No comparison data available</p>
      </div>
    );
  }

  return (
    <div className="page-comparison-viewer">
      {/* Header with Summary */}
      <div className="comparison-header">
        <div className="header-content">
          <h2>Page-by-Page Document Comparison</h2>
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-value">{comparisonData.summary.total_pages_compared}</span>
              <span className="stat-label">Pages Compared</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{comparisonData.summary.total_exact_matches}</span>
              <span className="stat-label">Exact Matches</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{comparisonData.summary.total_semantic_similarities}</span>
              <span className="stat-label">Semantic Similar</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{comparisonData.summary.total_unique_areas}</span>
              <span className="stat-label">Unique Areas</span>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="comparison-controls">
        <div className="page-navigation">
          <button 
            onClick={() => setCurrentPage(currentPage - 1)}
            disabled={currentPage === 1}
            className="nav-button"
          >
            <ChevronLeft size={20} />
            Previous
          </button>
          
          <div className="page-info">
            <span className="page-number">Page {currentPage}</span>
            <span className="page-total">of {totalPages}</span>
          </div>
          
          <button 
            onClick={() => setCurrentPage(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="nav-button"
          >
            Next
            <ChevronRight size={20} />
          </button>
        </div>

        <div className="highlight-controls">
          <button 
            onClick={() => setShowHighlights(!showHighlights)}
            className={`toggle-button ${showHighlights ? 'active' : ''}`}
          >
            {showHighlights ? <Eye size={16} /> : <EyeOff size={16} />}
            {showHighlights ? 'Hide' : 'Show'} Highlights
          </button>

          <select 
            value={highlightFilter} 
            onChange={(e) => setHighlightFilter(e.target.value as any)}
            className="filter-select"
          >
            <option value="all">All Highlights</option>
            <option value="exact">Exact Matches Only</option>
            <option value="semantic">Semantic Similar Only</option>
            <option value="unique">Unique Content Only</option>
          </select>
        </div>
      </div>

      {/* Document Comparison */}
      <div className="documents-container">
        <div className="document-pane">
          <div className="document-header">
            <div className="document-title">
              <FileText size={16} />
              <span title={comparisonData.doc1_name}>{comparisonData.doc1_name}</span>
            </div>
            <div className="page-status">
              {currentPageData?.doc1_has_page ? (
                <span className="status-indicator exists">✓ Page exists</span>
              ) : (
                <span className="status-indicator missing">✗ Page missing</span>
              )}
            </div>
          </div>
          
          <div className="document-content">
            {currentPageData?.doc1_has_page ? (
              <PDFPageViewer 
                htmlFile={comparisonData.doc1_html_file}
                pageNumber={currentPage}
                highlights={getHighlightedAreas('doc1')}
                showHighlights={showHighlights}
                documentName={comparisonData.doc1_name}
              />
            ) : (
              <div className="missing-page">
                <div className="missing-content">
                  <FileText size={48} />
                  <p>This page doesn't exist in {comparisonData.doc1_name}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="document-pane">
          <div className="document-header">
            <div className="document-title">
              <FileText size={16} />
              <span title={comparisonData.doc2_name}>{comparisonData.doc2_name}</span>
            </div>
            <div className="page-status">
              {currentPageData?.doc2_has_page ? (
                <span className="status-indicator exists">✓ Page exists</span>
              ) : (
                <span className="status-indicator missing">✗ Page missing</span>
              )}
            </div>
          </div>
          
          <div className="document-content">
            {currentPageData?.doc2_has_page ? (
              <PDFPageViewer 
                htmlFile={comparisonData.doc2_html_file}
                pageNumber={currentPage}
                highlights={getHighlightedAreas('doc2')}
                showHighlights={showHighlights}
                documentName={comparisonData.doc2_name}
              />
            ) : (
              <div className="missing-page">
                <div className="missing-content">
                  <FileText size={48} />
                  <p>This page doesn't exist in {comparisonData.doc2_name}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Page Statistics */}
      {currentPageData && (
        <div className="page-statistics">
          <h4>Page {currentPage} Statistics</h4>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-number">{currentPageData.statistics.exact_matches_count}</span>
              <span className="stat-label">Exact Matches</span>
              <span className="stat-percentage">{currentPageData.statistics.exact_match_percentage.toFixed(1)}%</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">{currentPageData.statistics.semantic_similarities_count}</span>
              <span className="stat-label">Semantic Similar</span>
              <span className="stat-percentage">{currentPageData.statistics.semantic_similarity_percentage.toFixed(1)}%</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">{currentPageData.statistics.unique_areas_count}</span>
              <span className="stat-label">Unique Areas</span>
              <span className="stat-percentage">{currentPageData.statistics.uniqueness_percentage.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="highlight-legend">
        <h4>Highlight Legend</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color exact-match"></div>
            <span>Exact Matches</span>
          </div>
          <div className="legend-item">
            <div className="legend-color semantic-similar"></div>
            <span>Semantic Similar</span>
          </div>
          <div className="legend-item">
            <div className="legend-color unique-doc1"></div>
            <span>Unique to Document 1</span>
          </div>
          <div className="legend-item">
            <div className="legend-color unique-doc2"></div>
            <span>Unique to Document 2</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// PDF Page Viewer Component
const PDFPageViewer: React.FC<{
  htmlFile: string;
  pageNumber: number;
  highlights: UniqueArea[];
  showHighlights: boolean;
  documentName: string;
}> = ({ htmlFile, pageNumber, highlights, showHighlights, documentName }) => {
  const [pageContent, setPageContent] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load actual HTML content from the backend
    const loadPageContent = async () => {
      try {
        setLoading(true);
        
        // Extract filename from htmlFile path
        const filename = htmlFile.split('/').pop();
        if (!filename) {
          throw new Error('Invalid HTML file path');
        }
        
        // Fetch the HTML content from the backend
        const response = await fetch(`http://localhost:8001/converted_documents/${filename}`);
        if (!response.ok) {
          throw new Error(`Failed to load HTML: ${response.statusText}`);
        }
        
        const htmlContent = await response.text();
        setPageContent(htmlContent);
      } catch (error) {
        console.error('Error loading page content:', error);
        // Fallback to placeholder content if HTML loading fails
        setPageContent(`
          <div style="padding: 20px; font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">${documentName} - Page ${pageNumber}</h2>
            <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
              <h3 style="color: #721c24; margin-bottom: 10px;">⚠️ Content Loading Error</h3>
              <p style="color: #721c24; margin-bottom: 10px;">Unable to load the actual document content. This may be due to:</p>
              <ul style="color: #721c24; margin-left: 20px;">
                <li>HTML file not found or not generated</li>
                <li>Backend server not serving static files</li>
                <li>Network connectivity issues</li>
              </ul>
            </div>
            <div style="background: #f3e5f5; padding: 15px; border-radius: 8px;">
              <h4 style="color: #7b1fa2; margin-bottom: 10px;">Highlighting Information</h4>
              <p>Found ${highlights.length} highlight areas on this page:</p>
              <ul style="margin-top: 10px;">
                ${highlights.map(h => `<li style="margin-bottom: 5px;"><strong>${h.type}:</strong> ${(h.content || '').substring(0, 100)}...</li>`).join('')}
              </ul>
            </div>
          </div>
        `);
      } finally {
        setLoading(false);
      }
    };
    
    loadPageContent();
  }, [pageNumber, documentName, highlights, htmlFile]);

  if (loading) {
    return (
      <div className="pdf-page-viewer">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <div className="spinner"></div>
          <span style={{ marginLeft: '10px' }}>Loading page content...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="pdf-page-viewer">
      <div 
        dangerouslySetInnerHTML={{ __html: pageContent }}
        style={{ 
          position: 'relative',
          width: '100%',
          height: '100%',
          overflow: 'auto'
        }}
      />
      
      {/* Highlight Overlays */}
      {showHighlights && highlights.map((highlight, index) => (
        <div
          key={index}
          className={`highlight-overlay ${highlight.highlight_class}`}
          style={{
            position: 'absolute',
            left: `${highlight.coordinates?.x || 0}px`,
            top: `${highlight.coordinates?.y || 0}px`,
            width: `${highlight.coordinates?.width || 0}px`,
            height: `${highlight.coordinates?.height || 0}px`,
            pointerEvents: 'none', // Allow clicks to pass through
            zIndex: 10, // Ensure highlights are above content
          }}
          title={`${highlight.type}: ${highlight.content || 'No content'}`}
        />
      ))}
    </div>
  );
};

export default PageComparisonViewer;
