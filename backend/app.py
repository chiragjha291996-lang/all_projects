from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import logging
import threading
import time
from document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = 300  # 5 minutes

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize services
document_processor = DocumentProcessor()

# Processing status tracking
processing_status = {}
processing_lock = threading.Lock()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_document_async(filepath, filename, job_id):
    """Process document asynchronously"""
    try:
        with processing_lock:
            processing_status[job_id] = {
                'status': 'processing',
                'filename': filename,
                'progress': 0,
                'message': 'Starting document processing...'
            }
        
        # Update progress
        with processing_lock:
            processing_status[job_id]['progress'] = 20
            processing_status[job_id]['message'] = 'Extracting text and detecting sections...'
        
        # Process document
        try:
            doc_data = document_processor.process_and_store_document(filepath)
            
            # Check if document processing failed
            if doc_data and doc_data.get('error'):
                raise Exception(doc_data['error'])
                
        except Exception as e:
            # Provide more specific error messages
            error_msg = str(e)
            if "No text could be extracted" in error_msg:
                error_msg = f"Failed to extract text from {filename}. The PDF may be image-based, password-protected, or corrupted. Please try a different document or convert the PDF to text format."
            elif "Unsupported file format" in error_msg:
                error_msg = f"Unsupported file format for {filename}. Please upload PDF or DOCX files only."
            elif "File not found" in error_msg:
                error_msg = f"File {filename} not found. Please try uploading again."
            else:
                error_msg = f"Failed to process {filename}: {error_msg}"
            
            raise Exception(error_msg)
        
        # Update progress
        with processing_lock:
            processing_status[job_id]['progress'] = 80
            processing_status[job_id]['message'] = 'Generating embeddings and hashes...'
        
        # Get statistics
        vector_stats = document_processor.get_vector_db_stats()
        exact_match_stats = document_processor.get_exact_match_stats()
        
        # Complete processing
        with processing_lock:
            processing_status[job_id] = {
                'status': 'completed',
                'filename': filename,
                'progress': 100,
                'message': 'Processing completed successfully',
                'result': {
                    'vector_chunk_count': doc_data.get('vector_chunk_count', 0),
                    'vector_db_stored': doc_data.get('vector_db_stored', False),
                    'exact_match_enabled': doc_data.get('exact_match_enabled', False),
                    'vector_db_stats': vector_stats,
                    'exact_match_stats': exact_match_stats
                }
            }
        
        logger.info(f"Async processing completed for {filename}")
        
    except Exception as e:
        with processing_lock:
            processing_status[job_id] = {
                'status': 'error',
                'filename': filename,
                'progress': 0,
                'message': f'Processing failed: {str(e)}',
                'error': str(e)
            }
        logger.error(f"Async processing failed for {filename}: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return "OK"

@app.route('/upload_vector', methods=['POST'])
def upload_files_vector():
    """Upload files and start async processing"""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected"}), 400
        
        processing_jobs = []
        
        for file in files:
            if file.filename and file.filename != '':
                # Save uploaded file
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Generate unique job ID
                job_id = f"{filename}_{int(time.time())}"
                
                # Start async processing
                thread = threading.Thread(
                    target=process_document_async,
                    args=(filepath, filename, job_id)
                )
                thread.start()
                
                processing_jobs.append({
                    "job_id": job_id,
                    "filename": filename,
                    "status": "started"
                })
                
                logger.info(f"Started async processing for: {filename}")
        
        return jsonify({
            "message": f"Started processing {len(processing_jobs)} files",
            "jobs": processing_jobs,
            "note": "Use /processing_status/<job_id> to check progress"
        }), 202  # 202 Accepted for async processing
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/vector_stats', methods=['GET'])
def get_vector_stats():
    """Get vector database statistics"""
    try:
        stats = document_processor.get_vector_db_stats()
        return jsonify({
            "message": "Vector database statistics",
            "stats": stats
        }), 200
        
    except Exception as e:
        logger.error(f"Vector stats error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all documents in vector database"""
    try:
        documents = document_processor.list_documents_in_vector_db()
        return jsonify({
            "message": "Document list retrieved",
            "documents": documents,
            "total_documents": len(documents)
        }), 200
        
    except Exception as e:
        logger.error(f"List documents error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/document/<document_name>', methods=['GET'])
def get_document(document_name):
    """Get a specific document and its chunks from vector database"""
    try:
        doc_data = document_processor.get_document_from_vector_db(document_name)
        if not doc_data:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "message": "Document retrieved",
            "document": doc_data
        }), 200
        
    except Exception as e:
        logger.error(f"Get document error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/document/<document_name>', methods=['DELETE'])
def delete_document(document_name):
    """Delete a document from vector database"""
    try:
        deleted_count = document_processor.delete_document_from_vector_db(document_name)
        
        if deleted_count == 0:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "message": f"Deleted {deleted_count} chunks for document '{document_name}'",
            "deleted_chunks": deleted_count
        }), 200
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/exact_matches/<document_name>', methods=['GET'])
def get_exact_matches(document_name):
    """Find exact matches for a specific document"""
    try:
        matches = document_processor.find_exact_matches(document_name)
        return jsonify({
            "message": "Exact matches analysis completed",
            "results": matches
        }), 200
        
    except Exception as e:
        logger.error(f"Exact matches error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/duplicate_sections', methods=['GET'])
def get_duplicate_sections():
    """Find all duplicate sections across documents"""
    try:
        duplicates = document_processor.find_duplicate_sections()
        return jsonify({
            "message": "Duplicate sections analysis completed",
            "results": duplicates
        }), 200
        
    except Exception as e:
        logger.error(f"Duplicate sections error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/compare_exact', methods=['POST'])
def compare_documents_exact():
    """Compare two documents for exact matches"""
    try:
        data = request.get_json()
        if not data or 'doc1' not in data or 'doc2' not in data:
            return jsonify({"error": "Both doc1 and doc2 parameters are required"}), 400
        
        doc1_name = data['doc1']
        doc2_name = data['doc2']
        
        comparison = document_processor.compare_documents_exact(doc1_name, doc2_name)
        return jsonify({
            "message": "Exact comparison completed",
            "results": comparison
        }), 200
        
    except Exception as e:
        logger.error(f"Exact comparison error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/exact_match_stats', methods=['GET'])
def get_exact_match_stats():
    """Get exact matching statistics"""
    try:
        stats = document_processor.get_exact_match_stats()
        return jsonify({
            "message": "Exact match statistics",
            "stats": stats
        }), 200
        
    except Exception as e:
        logger.error(f"Exact match stats error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/processing_status/<job_id>', methods=['GET'])
def get_processing_status(job_id):
    """Get processing status for a specific job"""
    try:
        with processing_lock:
            status = processing_status.get(job_id, {"error": "Job not found"})
        
        return jsonify({
            "job_id": job_id,
            "status": status
        }), 200
        
    except Exception as e:
        logger.error(f"Processing status error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/compare_sentence_level', methods=['POST'])
def compare_documents_sentence_level():
    """Compare two documents for exact sentence matches"""
    try:
        data = request.get_json()
        if not data or 'doc1' not in data or 'doc2' not in data:
            return jsonify({"error": "Both doc1 and doc2 parameters are required"}), 400
        
        doc1_name = data['doc1']
        doc2_name = data['doc2']
        
        comparison = document_processor.exact_match_service.compare_documents_sentence_level(doc1_name, doc2_name)
        return jsonify({
            "message": "Sentence-level comparison completed",
            "results": comparison
        }), 200
        
    except Exception as e:
        logger.error(f"Sentence-level comparison error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/get_differences', methods=['POST'])
def get_document_differences():
    """Get actual differences between two documents"""
    try:
        data = request.get_json()
        if not data or 'doc1' not in data or 'doc2' not in data:
            return jsonify({"error": "Both doc1 and doc2 parameters are required"}), 400
        
        doc1_name = data['doc1']
        doc2_name = data['doc2']
        
        differences = document_processor.exact_match_service.get_document_differences(doc1_name, doc2_name)
        return jsonify({
            "message": "Document differences retrieved",
            "results": differences
        }), 200
        
    except Exception as e:
        logger.error(f"Get differences error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/page_comparison', methods=['POST'])
def get_page_comparison():
    """Get page-by-page comparison with enhanced visual highlighting"""
    try:
        data = request.get_json()
        if not data or 'doc1' not in data or 'doc2' not in data:
            return jsonify({"error": "Both doc1 and doc2 parameters are required"}), 400
        
        doc1_name = data['doc1']
        doc2_name = data['doc2']
        
        # Get file paths
        doc1_path = os.path.join('uploads', doc1_name)
        doc2_path = os.path.join('uploads', doc2_name)
        
        if not os.path.exists(doc1_path) or not os.path.exists(doc2_path):
            return jsonify({"error": "One or both documents not found"}), 404
        
        # Perform page-by-page comparison
        from page_comparison_service import PageComparisonService
        comparison_service = PageComparisonService()
        results = comparison_service.compare_documents_page_by_page(doc1_path, doc2_path)
        
        return jsonify({
            "message": "Page comparison completed",
            "results": results
        }), 200
        
    except Exception as e:
        import traceback
        logger.error(f"Page comparison error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/converted_documents/<path:filename>')
def serve_converted_document(filename):
    """Serve converted HTML documents"""
    try:
        # URL decode the filename
        from urllib.parse import unquote
        decoded_filename = unquote(filename)
        
        file_path = os.path.join('converted_documents', decoded_filename)
        logger.info(f"Serving HTML file: {file_path}")
        
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='text/html')
        else:
            logger.error(f"File not found: {file_path}")
            return jsonify({"error": f"File not found: {decoded_filename}"}), 404
    except Exception as e:
        logger.error(f"Error serving converted document: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
