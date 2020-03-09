import argparse

import hashlib
import random
import re

from pymongo import MongoClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="User name", default="")
    parser.add_argument("-n", "--realname", help="Real name", default="")
    parser.add_argument("-p", "--password", help="A difficult password", default='')
    parser.add_argument("-e", "--email", help="User email", default='')
    parser.add_argument("-l", "--language", help="User language", default='en')
    args = parser.parse_args()
    print("%s %s %s (%s)" % (args.username, args.password, args.email, args.realname))

    email_re = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

    error = False
    # Check input format
    if re.match(r"^[-_|~0-9A-Z]{4,}$", args.username, re.IGNORECASE) is None:
        error = True
        msg = "Invalid username format."
    elif email_re.match(args.email) is None:
        error = True
        msg = "Invalid email format."
    elif len(args.password) < 6:
        error = True
        msg = "Password too short."
    elif len(args.realname) < 1:
        error = True
        msg = "Real name must be provided."

    myclient = MongoClient("mongodb://localhost:27017/")
    mydb = myclient["INGInious"]
    mycol = mydb["users"]


    if not error:
        existing_user = mycol.find_one(
            {"$or": [{"username": args.username}, {"email": args.email}]})
        if existing_user is not None:
            error = True
            if existing_user["username"] == args.username:
                msg = _("This username is already taken !")
            else:
                msg = _("This email address is already in use !")
        else:
            passwd_hash = hashlib.sha512(args.password.encode("utf-8")).hexdigest()
            obj = {"username": args.username,
                  "realname": args.realname,
                  "email": args.email,
                  "password": passwd_hash,
                  "bindings": {},
                  "language": args.language}
            mycol.insert(obj)
            print("Inserted! %s " % (obj))
    if error:
        print("Error! %s" % (msg))