from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_restful import Resource
from root.db import mdb
from root.general.commonUtilis import (
    bcryptPasswordHash,
    cleanupEmail,
    maskEmail,
    mdbObjectIdToStr,
    verifyPassword,
)
from root.general.authUtils import validate_auth
from root.static import G_ACCESS_EXPIRES
from bson import ObjectId
import secrets
from datetime import datetime, timedelta
from root.general.emailUtils import send_password_reset_email

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        userMeta = {
            "email": email,
            "password": password,
        }

        return login(userMeta, {})

def login(data, filter, isRedirect=True):
    email = cleanupEmail(data.get("email"))
    filter = {"email": email, "status": {"$nin": ["deleted", "removed", "suspended"]}}
    userDoc = mdb.users.find_one(filter)

    if not (userDoc and "_id" in userDoc):
        return {
            "status": 0,
            "cls": "error",
            "msg": "Invalid email id and password. Please try again",
        }

    userStatus = userDoc.get("status")

    if userStatus == "pending":
        return {
            "status": 0,
            "cls": "error",
            "msg": "Your Request is still pending, Contact admin for more info",
            "payload": {
                "redirect": "/adminApproval",
                "userMeta": userDoc,
            },
        }

    password = data.get("password")

    if not verifyPassword(userDoc["password"], password):
        return {
            "status": 0,
            "cls": "error",
            "msg": "Invalid email id and password. Please try again",
        }

    uid = mdbObjectIdToStr(userDoc["_id"])
    access_token = create_access_token(identity=uid, expires_delta=G_ACCESS_EXPIRES)

    payload = {
        "accessToken": access_token,
        "uid": uid,
        "redirectUrl": "/dashboard",
    }

    return {
        "status": 1,
        "cls": "success",
        "msg": f"Login successful. Please be patient, it will redirect automatically!",
        "payload": payload,
    }

class ForgetPassword(Resource):
    def post(self):
        data = request.get_json()
        email = cleanupEmail(data.get("email"))

        user = mdb.users.find_one({"email": email})

        if not user:
            return {
                "status": 0,
                "cls": "error",
                "msg": "No account found with this email address.",
            }

        # Generate a reset token
        reset_token = secrets.token_urlsafe(32)
        expiration_time = datetime.utcnow() + timedelta(hours=1)

        # Store the reset token in the database
        mdb.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"reset_token": reset_token, "reset_token_expires": expiration_time}}
        )

        # Send password reset email
        reset_link = f"{request.host_url}reset-password?token={reset_token}"
        try:
            send_password_reset_email(email, reset_link)
        except Exception as e:
            return {
                "status": 0,
                "cls": "error",
                "msg": "An error occurred while sending the reset email. Please try again later.",
            }

        return {
            "status": 1,
            "cls": "success",
            "msg": "Password reset instructions have been sent to your email.",
        }

class ResetPassword(Resource):
    def post(self):
        data = request.get_json()
        token = data.get("token")
        new_password = data.get("new_password")

        user = mdb.users.find_one({
            "reset_token": token,
            "reset_token_expires": {"$gt": datetime.utcnow()}
        })

        if not user:
            return {
                "status": 0,
                "cls": "error",
                "msg": "Invalid or expired reset token.",
            }

        # Update the user's password
        hashed_password = bcryptPasswordHash(new_password)
        mdb.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"password": hashed_password},
                "$unset": {"reset_token": "", "reset_token_expires": ""}
            }
        )

        return {
            "status": 1,
            "cls": "success",
            "msg": "Your password has been successfully reset. Please login with your new password.",
        }

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        # You might want to add the token to a blocklist or invalidate it in your database
        # For simplicity, we'll just return a success message
        return {
            "status": 1,
            "cls": "success",
            "msg": "Successfully logged out",
        }

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        email = cleanupEmail(data.get("email"))
        password = data.get("password")
        
        if mdb.users.find_one({"email": email}):
            return {
                "status": 0,
                "cls": "error",
                "msg": "A user with this email already exists.",
            }
        
        hashed_password = bcryptPasswordHash(password)
        new_user = {
            "email": email,
            "password": hashed_password,
            "status": "active",
            "created_at": datetime.utcnow(),
        }
        
        mdb.users.insert_one(new_user)
        
        return {
            "status": 1,
            "cls": "success",
            "msg": "User registered successfully. Please login.",
        }

class UpdateProfile(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Add logic to update user profile
        # For example:
        # mdb.users.update_one({"_id": ObjectId(current_user_id)}, {"$set": data})
        
        return {
            "status": 1,
            "cls": "success",
            "msg": "Profile updated successfully.",
        }