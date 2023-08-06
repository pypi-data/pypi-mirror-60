from .base import BaseTest


class JWTTest(BaseTest):
    def test_jwt(self):
        response = self.get_jwt_tokens(email=self.email, password=self.password)
        self.assertStatus(response)

        tokens = response.json()

        response = self.refresh_jwt_access_token(tokens["refresh"])
        self.assertStatus(response)

        response = self.verify_jwt_access_token(tokens["access"])
        self.assertStatus(response)
