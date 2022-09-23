def test_get_login(test_client):
    res =  test_client.get('/login')
    
    assert (res.status_code == 200)

