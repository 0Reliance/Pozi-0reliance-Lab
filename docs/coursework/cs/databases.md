---
title: Database Systems
description: Comprehensive guide to database design, implementation, and management
---

# Database Systems

## Overview

Database systems are fundamental to modern applications, providing efficient storage, retrieval, and management of data. This guide covers database concepts, design principles, SQL and NoSQL systems, and best practices.

## Learning Objectives

By the end of this guide, you will understand:
- Database design principles and normalization
- SQL and relational database concepts
- NoSQL databases and their use cases
- Database performance optimization
- Transaction management and concurrency

## Database Fundamentals

### What is a Database?
A database is an organized collection of structured information, typically stored electronically in a computer system. Databases are controlled by a Database Management System (DBMS).

### Key Concepts
- **Data**: Raw facts and figures
- **Information**: Processed data with context
- **Database**: Organized collection of related data
- **DBMS**: Software for managing databases
- **Schema**: Structure of the database

### Database Types

| Type | Description | Examples | Use Cases |
|-------|-------------|-----------|-----------|
| Relational | Structured data with relationships | MySQL, PostgreSQL | Financial systems, ERP |
| Document | JSON/BSON documents | MongoDB, CouchDB | Content management, catalogs |
| Key-Value | Simple key-value pairs | Redis, DynamoDB | Caching, session storage |
| Column-Family | Wide column storage | Cassandra, HBase | Time series, analytics |
| Graph | Node and relationship data | Neo4j, Amazon Neptune | Social networks, fraud detection |
| Search | Full-text search capabilities | Elasticsearch, Solr | Search engines, analytics |

## Relational Databases

### SQL Fundamentals

#### Basic SQL Operations
```sql
-- Create table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert data
INSERT INTO users (username, email) 
VALUES ('john_doe', 'john@example.com');

-- Query data
SELECT id, username, email 
FROM users 
WHERE created_at >= '2024-01-01';

-- Update data
UPDATE users 
SET email = 'newemail@example.com' 
WHERE id = 1;

-- Delete data
DELETE FROM users 
WHERE id = 1;
```

#### Advanced SQL
```sql
-- JOIN operations
SELECT u.username, p.title, p.created_at
FROM users u
JOIN posts p ON u.id = p.user_id
WHERE u.created_at >= '2024-01-01'
ORDER BY p.created_at DESC;

-- Aggregate functions
SELECT 
    u.username,
    COUNT(p.id) as post_count,
    MAX(p.created_at) as last_post
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id, u.username
HAVING COUNT(p.id) > 0;

-- Window functions
SELECT 
    username,
    post_count,
    ROW_NUMBER() OVER (ORDER BY post_count DESC) as rank,
    LAG(post_count) OVER (ORDER BY post_count DESC) as prev_count
FROM user_post_counts;
```

### Database Design

#### Entity-Relationship Diagram
```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string email
        timestamp created_at
    }
    
    POSTS {
        int id PK
        int user_id FK
        string title
        text content
        timestamp created_at
    }
    
    COMMENTS {
        int id PK
        int post_id FK
        int user_id FK
        text content
        timestamp created_at
    }
    
    USERS ||--o{ POSTS : creates
    USERS ||--o{ COMMENTS : writes
    POSTS ||--o{ COMMENTS : has
```

#### Normalization

**First Normal Form (1NF)**
- Each cell contains atomic values
- No repeating groups

```sql
-- Before 1NF
CREATE TABLE orders_bad (
    order_id INT,
    customer_name VARCHAR(100),
    products TEXT  -- "product1,product2,product3"
);

-- After 1NF
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100)
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT,
    product_name VARCHAR(100),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

**Second Normal Form (2NF)**
- In 1NF
- No partial dependencies

**Third Normal Form (3NF)**
- In 2NF
- No transitive dependencies

```sql
-- Before 3NF
CREATE TABLE employees_bad (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    dept_name VARCHAR(100),  -- Transitive dependency
    dept_location VARCHAR(100)
);

-- After 3NF
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    dept_id INT
);

CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(100),
    dept_location VARCHAR(100)
);
```

### Indexing

#### Create Indexes
```sql
-- Single column index
CREATE INDEX idx_users_email ON users(email);

-- Composite index
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Full-text index
CREATE FULLTEXT INDEX idx_posts_content ON posts(title, content);
```

#### Index Types
- **B-Tree**: Default for most databases
- **Hash**: Equality queries only
- **GiST**: Geometric data, full-text search
- **SP-GiST**: Partitioned data
- **GIN**: Composite values (arrays, JSON)

## NoSQL Databases

### Document Databases (MongoDB)

#### Basic Operations
```javascript
// Insert document
db.users.insertOne({
    username: "john_doe",
    email: "john@example.com",
    profile: {
        firstName: "John",
        lastName: "Doe",
        age: 30
    },
    interests: ["programming", "databases", "ai"],
    createdAt: new Date()
});

// Query documents
db.users.find({
    "profile.age": { $gte: 25 },
    interests: "programming"
});

// Update document
db.users.updateOne(
    { username: "john_doe" },
    { 
        $push: { interests: "mongodb" },
        $set: { updatedAt: new Date() }
    }
);

// Aggregation pipeline
db.posts.aggregate([
    { $match: { createdAt: { $gte: ISODate("2024-01-01") } } },
    { $group: { 
        _id: "$userId", 
        postCount: { $sum: 1 },
        lastPost: { $max: "$createdAt" }
    }},
    { $sort: { postCount: -1 } },
    { $limit: 10 }
]);
```

### Key-Value Stores (Redis)

#### Data Operations
```python
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# String operations
r.set('user:1:name', 'John Doe')
name = r.get('user:1:name')

# Hash operations
r.hset('user:1', {
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30
})
user_data = r.hgetall('user:1')

# List operations
r.lpush('user:1:posts', 'Post 1', 'Post 2', 'Post 3')
posts = r.lrange('user:1:posts', 0, -1)

# Set operations
r.sadd('user:1:tags', 'programming', 'databases', 'ai')
tags = r.smembers('user:1:tags')

# Expire keys
r.expire('user:1:session', 3600)  # 1 hour TTL
```

### Graph Databases (Neo4j)

#### Cypher Queries
```cypher
// Create nodes and relationships
CREATE (john:User {name: 'John Doe', email: 'john@example.com'})
CREATE (jane:User {name: 'Jane Smith', email: 'jane@example.com'})
CREATE (post1:Post {title: 'Database Guide', content: '...'})
CREATE (post2:Post {title: 'SQL Tutorial', content: '...'})

CREATE (john)-[:WROTE]->(post1)
CREATE (jane)-[:WROTE]->(post2)
CREATE (john)-[:FOLLOWS]->(jane)
CREATE (jane)-[:LIKES]->(post1)

// Query relationships
MATCH (user:User {name: 'John Doe'})-[:WROTE]->(posts:Post)
RETURN posts.title, posts.content

// Find friends of friends
MATCH (user:User {name: 'John Doe'})-[:FOLLOWS]->(friends)-[:FOLLOWS]->(fof:User)
WHERE user <> fof
RETURN DISTINCT fof.name

// Aggregate queries
MATCH (user:User)-[:WROTE]->(post:Post)<-[:LIKES]-(liker:User)
RETURN user.name, COUNT(liker) as likes
ORDER BY likes DESC
LIMIT 10
```

## Database Performance Optimization

### Query Optimization

#### Query Analysis
```sql
-- Explain query execution plan
EXPLAIN ANALYZE
SELECT u.username, COUNT(p.id) as post_count
FROM users u
JOIN posts p ON u.id = p.user_id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.id, u.username;

-- Identify slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### Optimization Techniques
```sql
-- Covering indexes
CREATE INDEX idx_posts_covering ON posts(user_id, created_at, id);

-- Partitioning
CREATE TABLE sales (
    id INT,
    sale_date DATE,
    amount DECIMAL(10,2),
    customer_id INT
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2024_q1 PARTITION OF sales
FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- Materialized views
CREATE MATERIALIZED VIEW user_post_counts AS
SELECT 
    user_id,
    COUNT(*) as post_count,
    MAX(created_at) as last_post
FROM posts
GROUP BY user_id;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW user_post_counts;
```

### Connection Pooling

#### Python Example
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Create connection pool
engine = create_engine(
    'postgresql://user:password@localhost/mydb',
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Use connection pool
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = result.fetchone()
```

## Transaction Management

### ACID Properties
- **Atomicity**: All or nothing execution
- **Consistency**: Database remains in valid state
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed changes persist

### Transaction Examples

#### SQL Transactions
```sql
-- Begin transaction
BEGIN;

-- Update account balances
UPDATE accounts 
SET balance = balance - 100 
WHERE id = 1;

UPDATE accounts 
SET balance = balance + 100 
WHERE id = 2;

-- Check constraint
SELECT balance FROM accounts WHERE id = 1;
-- If balance >= 0, commit; otherwise rollback

-- Commit or rollback
COMMIT;  -- or ROLLBACK;
```

#### Python with SQLAlchemy
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://user:password@localhost/mydb')
Session = sessionmaker(bind=engine)

def transfer_funds(from_account, to_account, amount):
    session = Session()
    try:
        # Check sufficient funds
        from_acc = session.query(Account).filter_by(id=from_account).with_for_update().first()
        if from_acc.balance < amount:
            raise ValueError("Insufficient funds")
        
        # Transfer funds
        from_acc.balance -= amount
        to_acc = session.query(Account).filter_by(id=to_account).with_for_update().first()
        to_acc.balance += amount
        
        # Commit transaction
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
```

## Database Security

### Authentication and Authorization

#### User Management
```sql
-- Create users
CREATE USER app_user WITH PASSWORD 'secure_password';
CREATE USER readonly_user WITH PASSWORD 'readonly_password';

-- Grant privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Row-level security
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_orders_policy ON orders
FOR ALL TO app_user
USING (customer_id = current_setting('app.current_user_id')::int);
```

### Data Encryption

#### Column Encryption
```sql
-- Transparent Data Encryption (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    encrypted_data BYTEA,
    checksum VARCHAR(64)
);

-- Insert encrypted data
INSERT INTO sensitive_data (encrypted_data, checksum)
VALUES (
    pgp_sym_encrypt('Secret message', 'encryption_key'),
    md5('Secret message')
);

-- Decrypt data
SELECT 
    pgp_sym_decrypt(encrypted_data, 'encryption_key') as decrypted_data
FROM sensitive_data;
```

## Database Administration

### Backup and Recovery

#### PostgreSQL Backup
```bash
# Full backup
pg_dump -h localhost -U postgres -d mydb > backup.sql

# Compressed backup
pg_dump -h localhost -U postgres -d mydb | gzip > backup.sql.gz

# Specific tables only
pg_dump -h localhost -U postgres -d mydb -t users -t posts > tables_backup.sql

# Restore database
psql -h localhost -U postgres -d mydb < backup.sql

# Restore from compressed backup
gunzip -c backup.sql.gz | psql -h localhost -U postgres -d mydb
```

#### Point-in-Time Recovery
```bash
# Enable WAL archiving
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'

# Restore to specific point
pg_basebackup -h localhost -D /backup/base -U postgres -v -P
```

### Monitoring

#### Performance Monitoring
```sql
-- Database statistics
SELECT 
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted
FROM pg_stat_database;

-- Table statistics
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables;
```

## Database Design Patterns

### Common Patterns

#### Soft Deletes
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    deleted_at TIMESTAMP NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Query for active users
SELECT * FROM users WHERE is_deleted = FALSE;

-- Soft delete
UPDATE users 
SET deleted_at = NOW(), is_deleted = TRUE 
WHERE id = 1;
```

#### Audit Trail
```sql
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_values JSON,
    new_values JSON,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger for audit trail
DELIMITER //
CREATE TRIGGER users_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_values, changed_by)
        VALUES ('users', NEW.id, 'INSERT', JSON_OBJECT(
            'username', NEW.username,
            'email', NEW.email
        ), USER());
    ELSEIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by)
        VALUES ('users', NEW.id, 'UPDATE', JSON_OBJECT(
            'username', OLD.username,
            'email', OLD.email
        ), JSON_OBJECT(
            'username', NEW.username,
            'email', NEW.email
        ), USER());
    ELSEIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, changed_by)
        VALUES ('users', OLD.id, 'DELETE', JSON_OBJECT(
            'username', OLD.username,
            'email', OLD.email
        ), USER());
    END IF;
END//
DELIMITER ;
```

#### Polymorphic Associations
```sql
-- Base table for comments
CREATE TABLE comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    content TEXT NOT NULL,
    user_id INT NOT NULL,
    commentable_type ENUM('post', 'video', 'photo') NOT NULL,
    commentable_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Query comments for posts
SELECT c.*, p.title as post_title
FROM comments c
JOIN posts p ON c.commentable_id = p.id AND c.commentable_type = 'post'
WHERE c.commentable_type = 'post';
```

## Scaling Databases

### Vertical Scaling
- Increase server resources (CPU, RAM, SSD)
- Simplifies architecture
- Limited by single server capacity

### Horizontal Scaling

#### Read Replicas
```sql
-- PostgreSQL replica setup
-- postgresql.conf (master)
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64

-- Create replication user
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';

-- pg_hba.conf (master)
host replication replicator 192.168.1.0/24 md5
```

#### Sharding
```python
# Example sharding logic
class ShardManager:
    def __init__(self, num_shards):
        self.num_shards = num_shards
        self.shards = [create_connection(i) for i in range(num_shards)]
    
    def get_shard(self, user_id):
        return self.shards[user_id % self.num_shards]
    
    def get_user(self, user_id):
        shard = self.get_shard(user_id)
        return shard.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

## Database Migration

#### Migration with Alembic
```python
# migrations/versions/001_create_users_table.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')
```

## Best Practices

### Design Principles
1. **Normalization**: Normalize to 3NF, denormalize when necessary
2. **Indexing**: Index frequently queried columns
3. **Constraints**: Use foreign keys and check constraints
4. **Naming**: Use consistent naming conventions
5. **Documentation**: Document schema and business rules

### Performance Tips
1. **Query optimization**: Use EXPLAIN ANALYZE
2. **Connection pooling**: Reuse database connections
3. **Caching**: Cache frequently accessed data
4. **Bulk operations**: Use bulk inserts/updates
5. **Monitoring**: Regularly monitor performance metrics

### Security Practices
1. **Least privilege**: Grant minimal necessary permissions
2. **Encryption**: Encrypt sensitive data at rest and in transit
3. **Auditing**: Log all data modifications
4. **Regular updates**: Keep database software updated
5. **Backups**: Regular, tested backup procedures

## Common Issues and Solutions

### Performance Issues
- **Slow queries**: Missing indexes, poor query structure
- **Locking**: Long-running transactions, deadlocks
- **Memory issues**: Insufficient memory, memory leaks

### Data Integrity
- **Orphaned records**: Missing foreign key constraints
- **Duplicate data**: Lack of unique constraints
- **Inconsistent data**: Poor transaction handling

## Exercises

### Beginner
1. Design a simple blog database schema
2. Write basic SQL queries (SELECT, INSERT, UPDATE, DELETE)
3. Create appropriate indexes for common queries
4. Normalize a denormalized table to 3NF

### Intermediate
1. Implement stored procedures and functions
2. Design and implement triggers for audit trails
3. Create materialized views for reporting
4. Set up database replication

### Advanced
1. Design a sharding strategy for a large application
2. Implement database connection pooling
3. Create database migration scripts
4. Set up database monitoring and alerting

## Resources

### Documentation
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Neo4j Documentation](https://neo4j.com/docs/)

### Books
- "Database System Concepts" by Silberschatz, Korth, and Sudarshan
- "SQL Antipatterns" by Bill Karwin
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "High Performance MySQL" by Baron Schwartz et al.

### Online Courses
- Coursera: Database Systems by University of Illinois
- edX: Introduction to Databases by Stanford University
- MongoDB University: MongoDB courses

## See Also

- [Data Structures](data-structures.md) - Foundation for understanding database internals
- [Algorithms](algorithms.md) - Query optimization and indexing algorithms
- [System Design](../sysadmin/system-design.md) - Database design in large systems

---

*This guide is part of the Computer Science coursework series. For more information, see the [CS Coursework Index](index.md).*
