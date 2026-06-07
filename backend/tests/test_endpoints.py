import time


def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json['status'] == 'healthy'


def test_auth_flow(client):
    reg = client.post('/auth/register', json={"email": "test2@eval.ac.uk", "password": "Pass123!", "full_name": "Test"})
    assert reg.status_code == 201
    login = client.post('/auth/login', json={"email": "test2@eval.ac.uk", "password": "Pass123!"})
    assert login.status_code == 200
    assert 'access_token' in login.json


def test_recommendations(client, auth_headers):
    res = client.post('/ai/recommend', json={"skills": ["Python", "ML", "SQL"], "industry": "Technology"}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json
    assert data['success']
    assert len(data['recommendations']) > 0
    assert 'match_score' in data['recommendations'][0]
    assert 'algorithm' in data['recommendations'][0]


def test_phishing_detection(client, auth_headers):
    res = client.post('/cybersecurity/check-url', json={"url": "https://example-job.tk/login"}, headers=auth_headers)
    assert res.status_code == 200
    assert 'risk_level' in res.json['result']


def test_reserved_tld_and_urgent_keywords_are_flagged(client, auth_headers):
    res = client.post(
        '/cybersecurity/check-url',
        json={"url": "http://job-offer-urgent.invalid/claim-now"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    result = res.json['result']
    assert result['risk_level'] in {'medium', 'high', 'critical'}
    assert result['is_safe'] is False
    assert result['overall_score'] >= 30


def test_user_accuracy_shape(client, auth_headers):
    feedback_res = client.post('/ai/feedback', json={"role": "Data Scientist", "rating": 5}, headers=auth_headers)
    assert feedback_res.status_code == 200

    accuracy_res = client.get('/evaluation/accuracy/1?days=30', headers=auth_headers)
    assert accuracy_res.status_code == 200
    data = accuracy_res.json['data']
    assert data['total_feedback'] >= 1
    assert 'rating_distribution' in data
    assert '5_star' in data['rating_distribution']


def test_security_engagement_tracking(client, auth_headers):
    client.post('/cybersecurity/check-url', json={"url": "https://example-job.tk/login"}, headers=auth_headers)
    engagement_res = client.get('/evaluation/security-engagement?user_id=1&days=30', headers=auth_headers)
    assert engagement_res.status_code == 200
    assert engagement_res.json['data']['total_url_checks'] >= 1


def test_performance_tracking(client):
    start = time.time()
    client.get('/health')
    latency = time.time() - start
    assert latency < 0.5, f"Health endpoint too slow: {latency:.3f}s"
