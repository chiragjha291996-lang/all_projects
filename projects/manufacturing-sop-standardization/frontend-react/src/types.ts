export interface FileData {
  filename: string;
  size: number;
  filepath?: string;
}

export interface ChunkData {
  chunk_id: string;
  text: string;
  section_index: number;
  filename: string;
  char_count: number;
  chunk_type: string;
  embedding?: number[];
}

export interface DocumentData {
  filename: string;
  filepath: string;
  text_content: string;
  word_count: number;
  char_count: number;
  file_type: string;
  chunks: ChunkData[];
  chunk_count: number;
}

export interface EmbeddingAnalysis {
  overall_similarity: number;
  chunk_matches: Array<{
    chunk1_id: string;
    chunk1_text: string;
    chunk2_id: string;
    chunk2_text: string;
    similarity_score: number;
    match_type: string;
  }>;
  high_similarity_pairs: Array<{
    chunk1_id: string;
    chunk2_id: string;
    similarity: number;
    chunk1_section: number;
    chunk2_section: number;
  }>;
  similarity_matrix_shape: [number, number];
  chunks1_count: number;
  chunks2_count: number;
  analysis_summary: string;
}

export interface SimilarityAnalysis {
  doc1_filename: string;
  doc2_filename: string;
  similarity_score: number;
  combined_similarity_score: number;
  procedure_type: string;
  key_similarities: string[];
  key_differences: string[];
  safety_parameters: string;
  operational_differences: string;
  cluster_recommendation: string;
  summary: string;
  embedding_analysis: EmbeddingAnalysis;
  raw_analysis: string;
}

export interface ClusterData {
  cluster_id: string;
  cluster_label: string;
  documents: DocumentData[];
  similarity_score?: number;
  document_count: number;
}

export interface ChunkCluster {
  cluster_id: number;
  chunks: ChunkData[];
  chunk_count: number;
  documents_involved: string[];
  sections_involved: number[];
  cluster_summary: string;
}

export interface ChunkClustering {
  clusters: ChunkCluster[];
  noise_chunks: ChunkData[];
  total_clusters: number;
  total_chunks: number;
  clustering_summary: string;
}

export interface ClusteringResult {
  clusters: ClusterData[];
  total_clusters: number;
  similarity_analysis: SimilarityAnalysis;
  chunk_clustering: ChunkClustering;
}

export interface AnalysisResult {
  message: string;
  processed_documents: number;
  clustering_result: ClusteringResult;
}

// New types for our enhanced backend
export interface VectorDBStats {
  total_chunks: number;
  total_documents: number;
  document_chunk_counts: Record<string, number>;
  base_collection_name: string;
  persist_directory: string;
  collections: string[];
}

export interface ExactMatchStats {
  total_documents: number;
  total_section_hashes: number;
  total_sentence_hashes: number;
  documents: string[];
  duplicate_sections: number;
  duplicate_sentences: number;
}

export interface ExactMatchResult {
  doc1: string;
  doc2: string;
  doc1_total_sections: number;
  doc2_total_sections: number;
  common_sections: number;
  exact_match_score: number;
  matches: Array<{
    content_hash: string;
    doc1_section: any;
    doc2_section: any;
  }>;
}

export interface SentenceMatchResult {
  doc1: string;
  doc2: string;
  doc1_total_sentences: number;
  doc2_total_sentences: number;
  common_sentences: number;
  sentence_match_score: number;
  sentence_matches: Array<{
    sentence_hash: string;
    doc1_sentence: any;
    doc2_sentence: any;
  }>;
}

export interface SemanticComparisonResult {
  similarity_score: number;
  chunk_count_1: number;
  chunk_count_2: number;
  top_similar_chunks: Array<{
    chunk1_index: number;
    chunk2_index: number;
    similarity: number;
    chunk1_section: string;
    chunk2_section: string;
  }>;
  avg_chunk_similarity: number;
}

export interface ProcessingJob {
  job_id: string;
  filename: string;
  status: string;
}

export interface ProcessingStatus {
  status: string;
  filename: string;
  progress: number;
  message: string;
  result?: any;
  error?: string;
}

export interface UploadVectorResponse {
  message: string;
  jobs: ProcessingJob[];
  note: string;
}

export interface UploadResponse {
  message: string;
  files: FileData[];
  count: number;
}
