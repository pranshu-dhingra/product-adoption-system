# System Architecture

## Overview

The Product Adoption & Expansion Intelligence Copilot is built as an **agentic intelligence system** with clear separation of concerns between reasoning, tools, and memory. The architecture is inspired by modern agent frameworks (like Amazon Bedrock AgentCore) but implemented from scratch to demonstrate core principles.

## Core Components

### 1. Agent Core (`src/agent/core.py`)

The `AdoptionCopilotAgent` is the central orchestrator that:
- Coordinates tool invocations
- Manages reasoning flow
- Stores context in memory
- Generates structured intelligence outputs

**Key Methods**:
- `analyze_customer()`: Main entry point for full intelligence analysis
- `answer_question()`: Natural language question answering
- `_generate_onboarding_playbook()`: Creates personalized onboarding steps

### 2. Tools Layer (`src/tools/`)

**DataAccessTool** (`data_access.py`):
- Provides clean interface to customer and feature data
- Abstracts data source (currently mock data, easily replaceable with DB/API)
- Methods: `get_customer()`, `get_feature()`, `list_customers()`

**AnalysisTool** (`analysis.py`):
- Implements business logic for recommendations
- Explainable heuristics (not black-box ML)
- Methods:
  - `analyze_feature_adoption()`: Generates prioritized recommendations
  - `assess_churn_risk()`: Calculates risk with explainable signals

### 3. Memory System (`src/memory/context.py`)

**MemoryStore**:
- Stores customer context and historical patterns
- Tracks recommendation history for trend analysis
- Enables risk trend detection (increasing/decreasing/stable)
- In-memory for MVP, designed for easy persistence layer integration

### 4. Data Models (`src/data/models.py`)

Structured business entities:
- `Customer`: Profile with subscription and usage context
- `Feature`: Product feature definitions
- `FeatureUsage`: Usage metrics per customer-feature
- `Recommendation`: Structured adoption recommendation
- `ChurnRiskAssessment`: Risk analysis with signals
- `CustomerIntelligence`: Complete output structure

### 5. Mock Data (`src/data/mock_data.py`)

Realistic data generator with:
- 5 mock customers with varied profiles (healthy, at-risk, champion, etc.)
- 10 product features across categories (core, collaboration, analytics, etc.)
- Configurable usage patterns and adoption probabilities

## Design Principles

### 1. Explainability First
Every recommendation includes:
- **Reason**: Clear explanation of why
- **Suggested Action**: Concrete next step
- **Expected Impact**: Business value description
- **Confidence**: Transparency in certainty

### 2. Tool-Based Architecture
- Tools are stateless, composable functions
- Easy to test in isolation
- Can be swapped or extended without changing agent logic
- Follows single responsibility principle

### 3. Memory for Context
- Stores historical patterns for trend analysis
- Enables personalized recommendations based on past interactions
- Supports "what changed?" queries

### 4. Separation of Concerns
```
Agent (Reasoning)
    ↓ uses
Tools (Capabilities)
    ↓ reads/writes
Memory (Context)
    ↓ queries
Data (Source of Truth)
```

## Data Flow

### Full Analysis Flow

```
1. User requests analysis for customer_id
2. Agent retrieves customer via DataAccessTool
3. Agent stores context in MemoryStore
4. Agent calls AnalysisTool.analyze_feature_adoption()
   → Tool analyzes usage patterns
   → Tool generates recommendations with reasons
5. Agent calls AnalysisTool.assess_churn_risk()
   → Tool evaluates risk signals
   → Tool generates assessment with explanations
6. Agent generates onboarding playbook from recommendations
7. Agent stores outputs in MemoryStore
8. Agent returns CustomerIntelligence object
9. Formatter converts to human-readable output
```

### Question Answering Flow

```
1. User asks question about customer
2. Agent parses question intent
3. Agent routes to appropriate tool method
4. Tool returns answer with explanation
5. Agent formats response
```

## Extensibility Points

### Adding New Analysis Capabilities

1. Create new method in `AnalysisTool`
2. Add corresponding tool call in `AdoptionCopilotAgent`
3. Update data models if new output structure needed

### Integrating Real Data Sources

1. Replace `DataAccessTool` implementation
2. Keep same interface (methods return same model types)
3. Agent code remains unchanged

### Adding ML Models

1. Create new tool: `MLPredictionTool`
2. Integrate model inference
3. Combine ML outputs with rule-based logic in `AnalysisTool`
4. Maintain explainability (e.g., SHAP values)

### Adding Persistence

1. Replace `MemoryStore` with database-backed implementation
2. Use same interface
3. Add migration scripts for schema

## Assumptions Made

1. **Mock Data Acceptable**: System uses generated mock data for demonstration
2. **Single Customer Focus**: Analysis is per-customer (not portfolio-level)
3. **Synchronous Processing**: All operations are synchronous (no async/streaming)
4. **Rule-Based First**: Explainable heuristics preferred over black-box ML
5. **Internal Tool**: Designed for CSMs/Account Managers, not end users

## Future Integration Points

When ready to scale, this architecture easily integrates with:

- **Amazon Bedrock AgentCore Runtime**: Agent becomes a runtime function
- **Gateway Tools**: Existing tools can be exposed as MCP-compatible tools
- **Memory Services**: MemoryStore can connect to persistent storage
- **Observability**: Add tracing/logging at agent orchestration layer
- **Identity**: Add customer context from identity provider

## Testing Strategy

Current implementation is designed for:
- **Unit Tests**: Each tool can be tested independently
- **Integration Tests**: Agent + Tools + Memory can be tested together
- **Mock Data Tests**: Realistic scenarios via configurable mock data

Future: Add pytest test suite with fixtures for customer data.

