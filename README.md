# Multi-Project Repository

This repository contains multiple AI, MLOps, and web application projects organized in a monorepo structure. Each project addresses a specific problem with a practical solution.

## Projects

### 🏭 DocQA
**Location**: `projects/manufacturing-sop-standardization/`

**Problem**: Manufacturing companies often struggle with inconsistent Standard Operating Procedures (SOPs) across different facilities, departments, or time periods. Manually comparing hundreds of documents to identify similarities and differences is time-consuming and error-prone, making standardization efforts nearly impossible at scale.

This problem scales to different industries, but this Proof-of-Concept can demonstrate value for manufacturing companies first.

**Solution**: An AI-powered document analysis system that automatically processes SOPs, identifies semantically similar procedures, clusters related documents, and highlights key differences. This enables organizations to standardize their operations efficiently and maintain consistency across their manufacturing processes.

**Key Value**:
- Automatically identifies which SOPs cover similar procedures
- Highlights critical differences that need standardization
- Enables data-driven decision making for SOP consolidation
- Scales to handle hundreds of documents simultaneously

---


### 🤖 MLOps Orchestration
**Location**: `projects/MLOps-orchestration/`

**Problem**: Machine Learning Operations (MLOps) workflows are notoriously complex, requiring data scientists and ML engineers to master multiple tools (orchestrators, model registries, experiment trackers) and DevOps practices. This complexity slows down the ML lifecycle, creates bottlenecks, and prevents teams from deploying models efficiently.

**Solution**: A conversational MLOps agent that acts as an intelligent interface to the entire MLOps stack. Instead of learning complex APIs and configurations, users can simply describe what they want to do in natural language. The agent handles pipeline registration, execution, model tracking, and promotion—making MLOps as easy as having a conversation.

**Key Value**:
- Upload pipeline scripts and have them automatically configured and registered
- Trigger model training and retraining through simple commands
- Query model performance metrics conversationally
- Promote models to staging/production without manual configuration
- Reduces MLOps expertise required from weeks of learning to minutes of conversation

---

## Repository Structure

```
├── projects/
│   ├── manufacturing-sop-standardization/    # AI-powered SOP analysis
│   ├── Health Tracker/                      # Personal health monitoring
│   ├── mditations_rag/                      # RAG system for philosophical texts
│   ├── MLOps-orchestration/                 # Conversational MLOps agent
│   ├── Portfolio/                           # Portfolio template
│   ├── Predictive_Maintenance/              # IoT predictive maintenance
│   └── separate_files/                      # Predictive maintenance backend
├── shared/                                  # Shared utilities (future)
├── docs/                                    # Repository-wide documentation (future)
└── README.md                               # This file
```


