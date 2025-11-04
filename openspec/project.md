# Project Context

## Purpose
Revenue Guardian is a revenue reconciliation and analytics system that helps organizations validate and align financial data across multiple sources, including fine collection, fine issuance, and accounting systems. The system enables:
- Automated reconciliation of structured data files to detect mismatches and anomalies
- Generation of accurate financial reports and key performance insights
- Interactive dashboards for data visualization and analysis
- AI-generated insights for CXO-level decision making
- Audit-compliant data management with immutable records

## Tech Stack
- **Backend Framework**: FastAPI (Python)
- **Package Manager**: UV (fast Python package installer and resolver)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (async)
- **Validation**: Pydantic
- **Migrations**: Alembic
- **Caching**: Redis
- **Testing**: pytest
- **API Specification**: OpenAPI 3.1
- **Deployment**: Docker (FastAPI, PostgreSQL, Redis)

## Project Conventions

### Code Style
- Follow PEP 8 for Python code formatting
- Use type hints throughout the codebase
- Async/await patterns for all I/O operations
- Pydantic models for request/response validation
- Clear separation between domain models (SQLAlchemy) and DTOs (Pydantic schemas)

### Dependency Management
- **UV** is used as the package manager for fast dependency resolution and installation
- Use `uv pip install` for installing packages
- Use `uv pip compile` for generating lock files
- Maintain `pyproject.toml` for project dependencies

### Architecture Patterns
**Clean Architecture** with layered separation:
- **`core/`**: Configuration, security, database setup, and cross-cutting concerns
- **`models/`**: SQLAlchemy domain models (database entities)
- **`schemas/`**: Pydantic schemas for validation and serialization
- **`crud/`**: Repository pattern for data access logic
- **`services/`**: Business logic, reconciliation workflows, and AI processing
- **`routers/`**: Versioned REST API endpoints
- **`dependencies/`**: Shared dependency injection utilities

**Key Principles**:
- Spec-driven development using OpenAPI 3.1
- Dependency injection for loose coupling
- Asynchronous operations for scalability
- Repository pattern for data persistence abstraction
- Service layer for complex business workflows

### Testing Strategy
- **Framework**: pytest with async support
- Unit tests for services and business logic
- Integration tests for API endpoints
- Repository tests for CRUD operations
- Test fixtures for database setup and teardown
- Mocking external dependencies (AI services, external APIs)

### Git Workflow
- Feature branches for new development
- OpenSpec workflow for architectural changes and proposals
- Commit messages should be clear and descriptive
- Pull requests require review before merge

## Domain Context

### Financial Reconciliation
Revenue Guardian reconciles data across three primary sources:
1. **Fine Collection System**: Records of actual payments received
2. **Fine Issuance System**: Records of fines issued to entities
3. **Accounting System**: General ledger and financial records

The reconciliation process identifies:
- Missing transactions
- Amount discrepancies
- Timing mismatches
- Data quality issues

### Role-Based Access Control (RBAC)
Three distinct user roles with specific permissions:

1. **Admin**
   - User management (create, update, delete users)
   - System configuration and settings
   - Full access to all features

2. **Operations User**
   - Upload structured data files
   - Trigger reconciliation processes
   - View reconciliation results and reports
   - Cannot modify uploaded data

3. **CXO User**
   - View analytics dashboards
   - Access AI-generated insights
   - View high-level KPIs and trends
   - Read-only access to reports

### Data Immutability
- Uploaded data files are immutable and cannot be modified within the application
- Ensures audit trail integrity and compliance
- Any corrections require new file uploads with proper versioning

## Important Constraints

### Technical Constraints
- All uploaded data must remain immutable for audit compliance
- Asynchronous processing required for large file uploads and reconciliation
- API must be versioned to support backward compatibility
- Database transactions must maintain ACID properties for financial data

### Business Constraints
- Strict role-based access control must be enforced at all layers
- Reconciliation results must be deterministic and reproducible
- All financial calculations must maintain precision (no floating-point errors)
- Audit logs required for all data access and modifications

### Regulatory Constraints
- Data retention policies must be configurable
- User access logs must be maintained
- Financial data must be encrypted at rest and in transit
- Compliance with financial reporting standards

## External Dependencies
- **AI/ML Services**: For generating insights and anomaly detection (future integration)
- **File Storage**: For uploaded data files (local or cloud storage)
- **Email Service**: For notifications and alerts (optional)
- **Authentication Provider**: For user authentication (JWT-based, can integrate with external IdP)
