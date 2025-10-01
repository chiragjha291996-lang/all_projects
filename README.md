# Multi-Project Repository

This repository contains multiple AI and document processing projects organized in a monorepo structure.

## Projects

### 🏭 Manufacturing SOP Standardization
**Location**: `projects/manufacturing-sop-standardization/`

AI-powered Standard Operating Procedure analysis tool for manufacturing environments.

**Features**:
- File Upload: Upload individual PDF and DOCX SOP files
- LLM-based Analysis: Uses Google Gemini API for semantic similarity analysis
- Embedding-based Processing: Breaks documents into semantic chunks using sentence transformers
- Smart Clustering: Groups semantically similar SOPs using embeddings + LLM analysis
- Difference Detection: Identifies key differences between procedures at chunk and document level

**Technologies**: Python, Flask, React, ChromaDB, OpenAI Embeddings, Google Gemini API

**Quick Start**:
```bash
cd projects/manufacturing-sop-standardization/backend
pip install -r requirements.txt
python app.py

cd ../frontend-react
npm install
PORT=3001 npm start
```

---

## Repository Structure

```
├── projects/
│   ├── manufacturing-sop-standardization/    # Manufacturing SOP analysis system
│   │   ├── backend/                         # Python Flask API
│   │   ├── frontend-react/                  # React application
│   │   ├── frontend/                        # Simple HTML frontend
│   │   ├── PRD                             # Product Requirements Document
│   │   └── README.md                        # Project-specific documentation
│   └── [future-projects]/                  # Additional projects will be added here
├── shared/                                  # Shared utilities and components (future)
├── docs/                                    # Repository-wide documentation (future)
└── README.md                               # This file
```

## Getting Started

Each project has its own setup instructions. Navigate to the specific project directory and follow the README.md file for that project.

## Contributing

When adding new projects:
1. Create a new directory under `projects/`
2. Include a comprehensive README.md
3. Update this main README.md
4. Follow consistent naming conventions
5. Use the same tech stack patterns where applicable

## Benefits of Monorepo Structure

- **Shared Dependencies**: Common libraries and utilities
- **Consistent Tooling**: Same CI/CD, linting, and testing across projects
- **Easy Cross-Project Development**: Work on multiple related projects simultaneously
- **Simplified Management**: Single repository to clone and maintain
- **Code Reuse**: Share components and utilities between projects