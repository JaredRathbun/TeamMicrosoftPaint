def test_get_login(test_client):
    res =  test_client.get('/login')
    assert (res.response_code == 200)