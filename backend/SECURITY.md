# 🔐 Security Documentation

Complete security documentation for the backend application.

## Overview

Security is a top priority. The backend implements multiple layers of security to protect against common vulnerabilities and attacks.

## Security Features

### 1. Authentication

#### JWT Tokens

- **Access Tokens**: Short-lived (30 minutes)
- **Refresh Tokens**: Long-lived (7 days)
- **Algorithm**: HS256
- **Storage**: Redis for token revocation

#### Password Security

- **Hashing**: bcrypt with salt rounds (12)
- **Validation**: Minimum 8 characters, complexity requirements
- **Storage**: Never stored in plain text

#### Multi-Factor Authentication (MFA)

- **TOTP**: Time-based one-time passwords
- **QR Code**: For authenticator apps
- **Backup Codes**: For account recovery

### 2. Authorization

#### Role-Based Access Control (RBAC)

**Roles**:
- **Guest**: Read-only access, basic chat (rate-limited)
- **User**: Full chat, history, favorites, itinerary creation
- **Moderator**: Content moderation, limited user management
- **Admin**: Full system access, analytics, user/role management

#### Permission Checks

```python
from backend.app.core.auth import require_role

@router.get("/admin/users")
@require_role("admin")
async def get_users():
    pass
```

### 3. Input Validation

#### Pydantic Validation

All inputs are validated using Pydantic models:

```python
from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
```

#### Sanitization

- **HTML Sanitization**: Bleach library for XSS prevention
- **SQL Injection**: MongoDB parameterized queries
- **NoSQL Injection**: Input validation and sanitization

### 4. Rate Limiting

#### Limits

- **Default**: 100 requests/minute per IP
- **Authenticated**: 200 requests/minute per user
- **Admin**: 1000 requests/minute
- **Chat**: 50 requests/minute
- **Auth**: 10 requests/minute

#### Implementation

- **Redis-backed**: Distributed rate limiting
- **In-memory fallback**: If Redis unavailable
- **Headers**: Rate limit info in response headers

### 5. CORS Protection

#### Configuration

```python
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

#### Features

- Whitelist-based origin validation
- Credential support for authenticated requests
- Preflight request handling

### 6. Security Headers

#### Headers Added

- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - XSS protection
- `Strict-Transport-Security` - HSTS (HTTPS only)
- `Content-Security-Policy` - CSP policy
- `Referrer-Policy: strict-origin-when-cross-origin`

### 7. HTTPS/TLS

#### Configuration

- **Production**: HTTPS required
- **TLS Version**: TLS 1.2+
- **Certificate**: Let's Encrypt or commercial certificate

### 8. Error Handling

#### Security

- **Error Messages**: Don't expose sensitive information
- **Stack Traces**: Hidden in production
- **Logging**: Security events logged

### 9. Session Management

#### Features

- **Token Storage**: Redis for token revocation
- **Session Timeout**: Automatic expiration
- **Concurrent Sessions**: Limited per user

### 10. Audit Logging

#### Logged Events

- Authentication attempts
- Authorization failures
- Sensitive operations (user deletion, role changes)
- Security events (rate limit exceeded, suspicious activity)

## Security Best Practices

### 1. Secrets Management

#### Environment Variables

```bash
# Never commit secrets
SECRET_KEY=<generate-secure-key>
MONGODB_URL=mongodb://user:password@host:27017/db
REDIS_URL=redis://password@host:6379
```

#### Secret Generation

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Password Security

#### Requirements

- Minimum 8 characters
- Mix of uppercase, lowercase, numbers, special characters
- Not in common password lists
- Hashed with bcrypt (12 rounds)

#### Implementation

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 3. API Security

#### API Keys

- **Optional**: For external integrations
- **Rotation**: Regular key rotation
- **Storage**: Encrypted in database

#### Rate Limiting

- Prevents abuse and DoS attacks
- Configurable per endpoint
- Distributed rate limiting with Redis

### 4. Database Security

#### Authentication

- **MongoDB**: Username/password authentication
- **Connection String**: Encrypted credentials
- **Network**: Restrict network access

#### Data Encryption

- **At Rest**: Database encryption
- **In Transit**: TLS/SSL connections
- **Backup**: Encrypted backups

### 5. Dependency Security

#### Updates

- Regular dependency updates
- Security patch monitoring
- Vulnerability scanning

#### Tools

```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip install --upgrade package-name
```

## Vulnerability Prevention

### 1. OWASP Top 10

#### A01: Broken Access Control

- **Prevention**: Role-based access control, permission checks
- **Testing**: Authorization tests

#### A02: Cryptographic Failures

- **Prevention**: Strong encryption, secure key management
- **Testing**: Encryption validation

#### A03: Injection

- **Prevention**: Input validation, parameterized queries
- **Testing**: Injection tests

#### A04: Insecure Design

- **Prevention**: Security by design, threat modeling
- **Testing**: Security architecture review

#### A05: Security Misconfiguration

- **Prevention**: Secure defaults, configuration review
- **Testing**: Configuration audits

#### A06: Vulnerable Components

- **Prevention**: Dependency updates, vulnerability scanning
- **Testing**: Dependency scanning

#### A07: Authentication Failures

- **Prevention**: Strong authentication, MFA
- **Testing**: Authentication tests

#### A08: Software and Data Integrity

- **Prevention**: Code signing, integrity checks
- **Testing**: Integrity validation

#### A09: Security Logging Failures

- **Prevention**: Comprehensive logging, audit trails
- **Testing**: Logging tests

#### A10: Server-Side Request Forgery

- **Prevention**: URL validation, allowlist
- **Testing**: SSRF tests

### 2. Common Attacks

#### SQL/NoSQL Injection

**Prevention**:
- Parameterized queries
- Input validation
- ORM/ODM usage (Beanie)

#### XSS (Cross-Site Scripting)

**Prevention**:
- Input sanitization (Bleach)
- Output encoding
- Content Security Policy

#### CSRF (Cross-Site Request Forgery)

**Prevention**:
- CSRF tokens
- SameSite cookies
- Origin validation

#### DoS (Denial of Service)

**Prevention**:
- Rate limiting
- Request timeout
- Resource limits

#### Brute Force

**Prevention**:
- Rate limiting on auth endpoints
- Account lockout after failed attempts
- CAPTCHA (future)

## Security Testing

### 1. Security Tests

**Location**: `backend/tests/security_tests/`

```python
def test_rate_limiting():
    """Test rate limiting"""
    for _ in range(101):
        response = client.get("/api/v1/attractions")
    assert response.status_code == 429

def test_authentication_required():
    """Test authentication requirement"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_authorization():
    """Test authorization"""
    # Test user cannot access admin endpoints
    response = client.get("/api/v1/admin/users", headers=user_headers)
    assert response.status_code == 403
```

### 2. Penetration Testing

- Regular penetration testing
- Vulnerability scanning
- Security audits

### 3. Dependency Scanning

```bash
# Scan for vulnerabilities
pip-audit

# Check for outdated packages
pip list --outdated
```

## Security Monitoring

### 1. Logging

#### Security Events

- Authentication attempts (success/failure)
- Authorization failures
- Rate limit exceeded
- Suspicious activity
- Security violations

#### Log Format

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "WARNING",
  "event": "rate_limit_exceeded",
  "ip": "192.168.1.1",
  "user_id": "user123",
  "request_id": "req-123"
}
```

### 2. Alerting

#### Alerts

- Multiple failed login attempts
- Unusual API usage patterns
- Security violations
- System anomalies

### 3. Incident Response

#### Process

1. **Detection**: Identify security incident
2. **Containment**: Isolate affected systems
3. **Investigation**: Analyze incident
4. **Remediation**: Fix vulnerabilities
5. **Recovery**: Restore services
6. **Post-Mortem**: Document and learn

## Security Checklist

### Pre-Production

- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Set DEBUG=false
- [ ] Configure firewall rules
- [ ] Enable database authentication
- [ ] Review CORS settings
- [ ] Set up rate limiting
- [ ] Configure security headers
- [ ] Enable audit logging
- [ ] Set up monitoring
- [ ] Run security tests
- [ ] Dependency vulnerability scan
- [ ] Security audit
- [ ] Penetration testing

### Ongoing

- [ ] Regular dependency updates
- [ ] Security patch monitoring
- [ ] Log review
- [ ] Security incident response
- [ ] Regular security audits
- [ ] User access review
- [ ] Backup verification

## Compliance

### GDPR

- **Right to Access**: User data export
- **Right to Erasure**: User data deletion
- **Data Portability**: Data export in standard format
- **Privacy by Design**: Privacy built into system

### Data Protection

- **Encryption**: Data encryption at rest and in transit
- **Access Control**: Role-based access control
- **Audit Logging**: Comprehensive audit trails
- **Data Retention**: Configurable data retention policies

## Security Resources

### Tools

- **pip-audit**: Dependency vulnerability scanning
- **bandit**: Security linter for Python
- **safety**: Check dependencies for known vulnerabilities

### References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

## Future Enhancements

1. **CAPTCHA**: For rate-limited endpoints
2. **IP Whitelisting**: For admin endpoints
3. **Web Application Firewall (WAF)**: Additional protection layer
4. **Security Information and Event Management (SIEM)**: Advanced monitoring
5. **Bug Bounty Program**: Community security testing

