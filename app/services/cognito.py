from botocore.exceptions import ClientError
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.core.aws_cognito import AWSCognito, UserSignin, UserSignup, UserVerify
from app.dependencies import logger


class AuthService:
    @staticmethod
    def user_signup(user: UserSignup, cognito: AWSCognito):
        try:
            response = cognito.user_signup(user)
        except ClientError as e:
            logger.info(f"ERROR FROM COGNNITO: {e}")
            if e.response["Error"]["Code"] == "UsernameExistsException":
                raise HTTPException(status_code=409, detail="Account with email exists")
            else:
                raise HTTPException(status_code=500, detail="Internal server error")
        else:
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                content = {
                    "message": "User created successfully",
                    "sub": response["UserSub"],
                }
                return JSONResponse(content=content, status_code=201)

    @staticmethod
    def user_signin(user: UserSignin, cognito: AWSCognito):
        try:
            response = cognito.user_signin(user)
        except ClientError as e:
            logger.info(f"ERROR USER SIGNIN - {e}")
            if e.response["Error"]["Code"] == "UserNotFoundException":
                raise HTTPException(status_code=404, detail="User does not exist")
            elif e.response["Error"]["Code"] == "UserNotConfirmedException":
                raise HTTPException(status_code=403, detail="Verify your account")
            elif e.response["Error"]["Code"] == "NotAuthorizedException":
                raise HTTPException(
                    status_code=401, detail="Incorrect username or password"
                )
            else:
                raise HTTPException(status_code=500, detail="Internal server error")
        else:
            content = {
                "message": "User signed in successfully",
                "AccessToken": response["AuthenticationResult"]["AccessToken"],
                "RefreshToken": response["AuthenticationResult"]["RefreshToken"],
            }

            return JSONResponse(content, status_code=200)

    @staticmethod
    def logout(access_token: str, cognito: AWSCognito):
        try:
            cognito.logout(access_token)
        except ClientError as e:
            logger.info(f"ERROR USER LOGOUT - {e}")
            if e.response["Error"]["Code"] == "InvalidParameterException":
                raise HTTPException(
                    status_code=400, detail="Access token provided has wrong format"
                )
            elif e.response["Error"]["Code"] == "NotAuthorizedException":
                raise HTTPException(
                    status_code=401, detail="Invalid access token provided"
                )
            elif e.response["Error"]["Code"] == "TooManyRequestsException":
                raise HTTPException(status_code=429, detail="Too many requests")
            else:
                raise HTTPException(status_code=500, detail="Internal server error")
        else:
            return JSONResponse(
                content={"message": "Logged out successfully"}, status_code=200
            )

    @staticmethod
    def verify_account(data: UserVerify, cognito: AWSCognito):
        try:
            cognito.verify_account(data)
        except ClientError as e:
            if e.response["Error"]["Code"] == "CodeMismatchException":
                raise HTTPException(
                    status_code=400,
                    detail="The provided code does not match the expected value.",
                )
            elif e.response["Error"]["Code"] == "ExpiredCodeException":
                raise HTTPException(
                    status_code=400, detail="The provided code has expired."
                )
            elif e.response["Error"]["Code"] == "UserNotFoundException":
                raise HTTPException(status_code=404, detail="User not found")
            elif e.response["Error"]["Code"] == "NotAuthorizedException":
                raise HTTPException(status_code=200, detail="User already verified.")
            else:
                raise HTTPException(status_code=500, detail="Internal server error")
        else:
            return JSONResponse(
                content={"message": "Account verification successful"}, status_code=200
            )

    @staticmethod
    def resend_confirmation(username: str, cognito: AWSCognito):
        try:
            cognito.resend_confirmation_code(username)
        except ClientError as e:
            if e.response["Error"]["Code"] == "UserNotFoundException":
                raise HTTPException(status_code=404, detail="User not found")
            elif e.response["Error"]["Code"] == "LimitExceededException":
                raise HTTPException(status_code=429, detail="Limit exceeded")
            else:
                raise HTTPException(status_code=500, detail="Internal Server")
        else:
            return JSONResponse(
                content={"message": "Confirmation code sent successfully"},
                status_code=200,
            )
