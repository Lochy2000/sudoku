from typing import Any

from django.test import Client


def test_signup_login_logout_and_protected_profile(db: Any) -> None:
    client = Client()

    # Profile should require login
    resp = client.get("/accounts/profile")
    assert resp.status_code in (301, 302)

    # Sign up a new user
    resp = client.post(
        "/accounts/signup",
        {
            "username": "alice",
            "password1": "a-Strong_pass1",
            "password2": "a-Strong_pass1",
        },
        follow=True,
    )
    assert resp.status_code == 200

    # Now profile should work and show username
    resp = client.get("/accounts/profile")
    assert resp.status_code == 200
    assert b"user:alice" in resp.content

    # Logout
    resp = client.get("/accounts/logout", follow=True)
    assert resp.status_code == 200

    # Login again
    resp = client.post(
        "/accounts/login",
        {
            "username": "alice",
            "password": "a-Strong_pass1",
        },
        follow=True,
    )
    assert resp.status_code == 200

    # Access profile again
    resp = client.get("/accounts/profile")
    assert resp.status_code == 200
    assert b"user:alice" in resp.content
