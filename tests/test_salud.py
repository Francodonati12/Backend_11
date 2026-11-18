def test_salud_responde_con_la_base(client):
    response = client.get("/salud")
    assert response.status_code == 200
    assert response.json() == {"estado": "ok", "base": "ok"}
