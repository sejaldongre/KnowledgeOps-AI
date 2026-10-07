# KnowledgeOps AI Database Schema

## Purpose

PostgreSQL stores application and business data.
ChromaDB stores embeddings and retrieval-oriented document chunks.

## Core Entities

### Users

Stores application users.

### Roles

Defines user roles for RBAC.

### User Roles

Associates users with roles.

### Documents

Stores document metadata and lifecycle state.

### Document Versions

Stores document version information.

### Folders

Provides hierarchical document organization.

### Tags

Provides flexible document classification.

### Document Tags

Many-to-many relationship between documents and tags.

### Document Permissions

Controls which users/roles can access documents.

### Conversations

Stores AI conversation sessions.

### Messages

Stores individual conversation messages.

### Audit Logs

Stores security and activity events.

## Data Ownership

PostgreSQL:

- Users
- Roles
- Documents
- Permissions
- Conversations
- Audit logs

ChromaDB:

- Embeddings
- Searchable chunks
- Retrieval metadata
