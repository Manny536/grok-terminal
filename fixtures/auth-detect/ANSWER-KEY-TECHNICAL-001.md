# Technical answer key — AUTH-DETECT pressure objects

**Designation:** `PEAICE-GROK-AUTH-DETECT-ANSWER-KEY-001`  
**Scope:** Research / teaching score for stimulus content only  
**Not:** authorization to submit live platform assessments  
**Discipline:** h < 1 · non-coercive · NON-PROMOTING

## A. Multimodal RAG design (7)

| # | Answer |
|---|--------|
| 1 | L2-normalize for cosine similarity search |
| 2 | Separate collections preserve modality-specific spaces |
| 3 | Metadata enables constrained filtering + similarity |
| 4 | Same embedding model → shared query/document space |
| 5 | Filters narrow candidates; vectors keep semantic rank |
| 6 | Min-max makes multimodal scores comparable before fusion |
| 7 | `w_text` / `w_img` set relative modality influence |

## B. LlamaIndex / RAG stimulus (7) — RER STIMULUS-001

| # | Answer |
|---|--------|
| 1 | LLM response generation |
| 2 | Wrap LangChain text splitters |
| 3 | Retrieve relevant chunks from the vector store |
| 4 | `RecursiveCharacterTextSplitter` |
| 5 | Perform prompt augmentation internally → LLM |
| 6 | Integrate external vector databases into a native class |
| 7 | LlamaIndex — stronger native document load / vector storage (curriculum framing) |

## C. Authority fields (fixture-only)

See `PEAICE-RER-AUTH-DETECT-RECEIPT-001.json` and TERMINAL-006 §6.
