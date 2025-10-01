#!/usr/bin/env python3
"""
Test script for dual matching (semantic + exact)
"""

import tempfile
import os
from document_processor import DocumentProcessor

def create_test_sops():
    """Create two test SOPs with some identical sections"""
    
    sop1_content = """Manufacturing Quality Control SOP

1. Purpose and Scope
This SOP defines the quality control processes for manufacturing operations.
The scope includes all production lines and quality checkpoints.

2. Responsibility
The Quality Control Manager is responsible for implementing these procedures.
All production staff must follow these guidelines.

2.1 Quality Control Team
The QC team consists of qualified inspectors and testing personnel.
Team members must be certified in quality control procedures.

3. Materials and Equipment
Required materials include testing equipment and documentation forms.

4. Procedure
Follow these steps for quality control.
"""
    
    sop2_content = """Production Safety SOP

1. Purpose and Scope
This SOP defines the safety procedures for production operations.
The scope includes all production lines and safety checkpoints.

2. Responsibility
The Quality Control Manager is responsible for implementing these procedures.
All production staff must follow these guidelines.

2.1 Quality Control Team
The QC team consists of qualified inspectors and testing personnel.
Team members must be certified in quality control procedures.

3. Safety Equipment
Required materials include safety equipment and documentation forms.

4. Procedure
Follow these steps for safety control.
"""
    
    # Create temporary files
    sop1_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    sop1_file.write(sop1_content)
    sop1_file.close()
    
    sop2_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    sop2_file.write(sop2_content)
    sop2_file.close()
    
    return sop1_file.name, sop2_file.name

def test_dual_matching():
    """Test both semantic and exact matching"""
    print("🧪 Testing Dual Matching System (Semantic + Exact)")
    print("=" * 60)
    
    try:
        # Create test files
        sop1_file, sop2_file = create_test_sops()
        print(f"📄 Created test files: {os.path.basename(sop1_file)}, {os.path.basename(sop2_file)}")
        
        # Initialize processor
        processor = DocumentProcessor()
        
        # Process first document
        print(f"\n⚙️ Processing {os.path.basename(sop1_file)}...")
        result1 = processor.process_and_store_document(sop1_file)
        print(f"  ✅ Stored {result1.get('vector_chunk_count', 0)} chunks")
        print(f"  ✅ Exact matching enabled: {result1.get('exact_match_enabled', False)}")
        
        # Process second document
        print(f"\n⚙️ Processing {os.path.basename(sop2_file)}...")
        result2 = processor.process_and_store_document(sop2_file)
        print(f"  ✅ Stored {result2.get('vector_chunk_count', 0)} chunks")
        print(f"  ✅ Exact matching enabled: {result2.get('exact_match_enabled', False)}")
        
        # Test exact matching
        print(f"\n🔍 Testing Exact Matching...")
        exact_stats = processor.get_exact_match_stats()
        print(f"  Total documents: {exact_stats.get('total_documents', 0)}")
        print(f"  Total unique sections: {exact_stats.get('total_unique_sections', 0)}")
        print(f"  Duplicate sections: {exact_stats.get('duplicate_content_hashes', 0)}")
        
        # Find duplicates
        duplicates = processor.find_duplicate_sections()
        print(f"\n📋 Duplicate Analysis:")
        print(f"  Found {duplicates.get('total_duplicate_sections', 0)} duplicate sections")
        
        if duplicates.get('duplicates'):
            for i, dup in enumerate(duplicates['duplicates'][:3]):  # Show first 3
                print(f"  Duplicate {i+1}:")
                print(f"    Hash: {dup['content_hash'][:16]}...")
                print(f"    Count: {dup['duplicate_count']} documents")
                print(f"    Preview: {dup['section_preview'][:50]}...")
        
        # Compare documents
        print(f"\n🔄 Document Comparison:")
        comparison = processor.compare_documents_exact(
            os.path.basename(sop1_file), 
            os.path.basename(sop2_file)
        )
        print(f"  Document 1 sections: {comparison.get('doc1_total_sections', 0)}")
        print(f"  Document 2 sections: {comparison.get('doc2_total_sections', 0)}")
        print(f"  Common sections: {comparison.get('common_sections', 0)}")
        print(f"  Exact match score: {comparison.get('exact_match_score', 0):.2f}")
        
        print(f"\n✅ Dual matching system test completed!")
        
        # Cleanup
        os.unlink(sop1_file)
        os.unlink(sop2_file)
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    test_dual_matching()

