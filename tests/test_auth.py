"""
Unit & Integration Tests for User Authentication and Registration.
"""

import json


def test_register_success(client):
    """Test standard valid user registration."""
    response = client.post('/api/register', json={
        'name': 'Cloud Beginner',
        'email': 'cloud@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['user']['email'] == 'cloud@example.com'


def test_register_duplicate_email(client, auth_user):
    """Test that duplicate email registration is rejected."""
    response = client.post('/api/register', json={
        'name': 'Duplicate User',
        'email': auth_user.email,
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert "already exists" in data['error']


def test_register_password_mismatch(client):
    """Test validation when passwords do not match."""
    response = client.post('/api/register', json={
        'name': 'Mismatch User',
        'email': 'mismatch@example.com',
        'password': 'password123',
        'confirm_password': 'different_password'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert "Passwords do not match" in data['error']


def test_login_success(client, auth_user):
    """Test successful user login."""
    response = client.post('/api/login', json={
        'email': auth_user.email,
        'password': 'SecurePass123!'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['user']['name'] == auth_user.name


def test_login_invalid_password(client, auth_user):
    """Test login failure with wrong password."""
    response = client.post('/api/login', json={
        'email': auth_user.email,
        'password': 'WrongPassword999'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['success'] is False
    assert "Invalid email or password" in data['error']


def test_logout(client, auth_user):
    """Test user logout."""
    client.post('/api/login', json={
        'email': auth_user.email,
        'password': 'SecurePass123!'
    })
    response = client.post('/api/logout')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
