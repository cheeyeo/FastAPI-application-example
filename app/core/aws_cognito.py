import base64
import hashlib
import hmac
import os

import boto3
import httpx
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field

AWS_REGION = os.getenv("AWS_REGION")
AWS_COGNITO_APP_CLIENT_ID = os.getenv("AWS_COGNITO_APP_CLIENT_ID")
# Since we enabled client secret we need to create secret hash for each api call
AWS_COGNITO_APP_CLIENT_SECRET = os.getenv("AWS_COGNITO_APP_CLIENT_SECRET")
AWS_USER_POOL_ID = os.getenv("AWS_USER_POOL_ID")


class UserSignup(BaseModel):
    username: str = Field(max_length=50)
    email: EmailStr
    password: str


class UserSignin(BaseModel):
    username: str
    password: str


class UserVerify(BaseModel):
    username: str
    confirmation_code: str


class UserResendCode(BaseModel):
    username: str


class AWSCognito:
    def __init__(self, client, region, client_id, client_secret, user_pool_id):
        self.client = client
        self.region = region
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_pool_id = user_pool_id

    def user_signup(self, user: UserSignup):
        secret_hash = base64.b64encode(
            hmac.new(
                bytes(self.client_secret, "utf-8"),
                bytes(user.username + self.client_id, "utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()

        response = self.client.sign_up(
            ClientId=self.client_id,
            SecretHash=secret_hash,
            Username=user.username,
            Password=user.password,
            UserAttributes=[
                {"Name": "name", "Value": user.username},
                {"Name": "email", "Value": user.email},
            ],
        )

        return response

    def verify_account(self, data: UserVerify):
        secret_hash = base64.b64encode(
            hmac.new(
                bytes(self.client_secret, "utf-8"),
                bytes(data.username + self.client_id, "utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()

        response = self.client.confirm_sign_up(
            ClientId=self.client_id,
            Username=data.username,
            ConfirmationCode=data.confirmation_code,
            SecretHash=secret_hash,
        )

        return response

    def resend_confirmation_code(self, data: UserResendCode):
        """Sends the confirmation code"""

        secret_hash = base64.b64encode(
            hmac.new(
                bytes(self.client_secret, "utf-8"),
                bytes(data.username + self.client_id, "utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()

        response = self.client.resend_confirmation_code(
            ClientId=self.client_id,
            Username=data.username,
            SecretHash=secret_hash,
        )

        return response

    def user_signin(self, data: UserSignin):
        secret_hash = base64.b64encode(
            hmac.new(
                bytes(self.client_secret, "utf-8"),
                bytes(data.username + self.client_id, "utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()

        response = self.client.initiate_auth(
            ClientId=self.client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": data.username,
                "PASSWORD": data.password,
                "SECRET_HASH": secret_hash,
            },
        )

        return response

    def logout(self, access_token: str):
        response = self.client.global_sign_out(AccessToken=access_token)
        return response

    def get_jwks(self):
        """Fetches the JSON Web Key Set (JWKS) from Cognito."""
        jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        response = httpx.get(jwks_url)
        return response.json()

    def decode_token(self, token: str):
        jwks = self.get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}

        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }

        if not rsa_key:
            raise Exception("Unable to find appropriate key")

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=self.client_id,
                options={"verify_aud": True},
            )

            return payload
        except JWTError:
            raise JWTError
