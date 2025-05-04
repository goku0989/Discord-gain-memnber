import threading
import requests
import time
import base64
import json
import sys
import os
from colorama import Fore, init

# Initialize colorama with autoreset
init(autoreset=True)

# Dictionary to track replied users for each token
token_replied_users = {}
active_threads = []
stop_flag = False

# Encrypted server check function
def _sv_chk_(tkn):
    try:
        # Encrypted server ID check (1342814979513909405)
        enc_srv = "MTM0MjgxNDk3OTUxMzkwOTQwNQ=="
        srv_id = base64.b64decode(enc_srv).decode('utf-8')
        
        headers = {"authorization": tkn}
        print(f"{Fore.CYAN}[*] Checking server membership...")
        r = requests.get(f"https://discord.com/api/v9/users/@me/guilds", headers=headers)
        
        if r.status_code == 200:
            guilds = r.json()
            for guild in guilds:
                if guild['id'] == srv_id:
                    return True
        
        print(f"{Fore.RED}[!] You must join the following server for this bot to work:")
        print(f"{Fore.YELLOW}https://discord.gg/bjezt6T7Px")
        return False
    except Exception as e:
        print(f"{Fore.RED}[!] Error checking server membership: {e}")
        return False

# Send messages to channels
def spam_to_channels(token, channel, message, delay_time):
    global stop_flag
    url = f'https://discord.com/api/v9/channels/{channel}/messages'
    headers = {"authorization": token}
    data = {"content": message}

    print(f"{Fore.BLUE}[*] Starting channel message thread for {channel}")
    
    while not stop_flag:  # Check the stop flag
        try:
            r = requests.post(url, json=data, headers=headers)
            if r.status_code == 200:
                print(f"{Fore.GREEN}[+] Message Sent | Channel ID: {channel} | Token: {token[:7]}...")
            else:
                print(f"{Fore.RED}[-] Failed to send message | Channel ID: {channel} | Error: {r.status_code}")
                if r.status_code == 429:  # Rate limit
                    try:
                        retry_after = r.json().get('retry_after', 5)
                        print(f"{Fore.YELLOW}[!] Rate limited. Waiting {retry_after} seconds...")
                        time.sleep(float(retry_after))
                        continue  # Skip the regular delay
                    except:
                        pass
        except Exception as e:
            print(f"{Fore.RED}[-] An error occurred (channel message): {e}")
        
        try:
            # Use the delay value, with a fallback
            time.sleep(int(delay_time))
        except ValueError:
            time.sleep(5)

# Check and reply to new DMs
def listen_and_reply_to_new_dms(token, reply_message):
    global stop_flag
    url = "https://discord.com/api/v9/users/@me/channels"
    headers = {"authorization": token}

    # Initialize set for this token if not exists
    if token not in token_replied_users:
        token_replied_users[token] = set()
    
    # First, let's collect all DM channels and their last messages to build our initial state
    print(f"{Fore.BLUE}[*] Initializing DM history...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            dm_channels = response.json()
            for channel in dm_channels:
                try:
                    if 'recipients' not in channel or len(channel['recipients']) == 0:
                        continue
                        
                    channel_id = channel['id']
                    user_id = channel['recipients'][0]['id']
                    
                    # Get message history to identify pre-existing conversations
                    messages_url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=10"
                    messages_response = requests.get(messages_url, headers=headers)
                    if messages_response.status_code == 200:
                        messages = messages_response.json()
                        if messages and len(messages) > 0:
                            # If there are any messages in the history, mark this user as already contacted
                            token_replied_users[token].add(user_id)
                            print(f"{Fore.YELLOW}[*] Marked user {user_id} as previously contacted")
                except Exception as e:
                    print(f"{Fore.RED}[-] Error during DM history initialization: {e}")
    except Exception as e:
        print(f"{Fore.RED}[-] Error initializing DM history: {e}")
    
    print(f"{Fore.BLUE}[*] Starting DM listener thread")
    print(f"{Fore.YELLOW}[*] Initial contact list has {len(token_replied_users[token])} users")

    while not stop_flag:  # Check the stop flag
        try:
            # Get DM channels
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                dm_channels = response.json()
                for channel in dm_channels:
                    try:
                        # Ensure the channel has recipients
                        if 'recipients' not in channel or len(channel['recipients']) == 0:
                            continue
                            
                        channel_id = channel['id']
                        user_id = channel['recipients'][0]['id']

                        # Skip if already replied to this user
                        if user_id in token_replied_users[token]:
                            continue

                        # Check for new messages
                        messages_url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"
                        messages_response = requests.get(messages_url, headers=headers)
                        if messages_response.status_code == 200:
                            messages = messages_response.json()
                            if messages and len(messages) > 0:
                                latest_message = messages[0]
                                if 'author' in latest_message and 'id' in latest_message['author']:
                                    # Check if message is from another user (not the bot itself)
                                    if latest_message['author']['id'] == user_id:
                                        print(f"{Fore.CYAN}[*] New message from {user_id}")
                                        # Reply to this user
                                        data = {"content": reply_message}
                                        send_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
                                        send_message = requests.post(send_url, headers=headers, json=data)
                                        
                                        if send_message.status_code == 200:
                                            print(f"{Fore.GREEN}[+] Reply Sent | User ID: {user_id} | Token: {token[:7]}...")
                                            token_replied_users[token].add(user_id)  # Mark as replied
                                        else:
                                            print(f"{Fore.RED}[-] Failed to send reply | User ID: {user_id} | Error: {send_message.status_code}")
                                            if send_message.status_code == 429:  # Rate limit
                                                retry_after = send_message.json().get('retry_after', 5)
                                                print(f"{Fore.YELLOW}[!] Rate limited. Waiting {retry_after} seconds...")
                                                time.sleep(float(retry_after))
                    except Exception as e:
                        print(f"{Fore.RED}[-] Error processing DM channel: {e}")
            elif response.status_code == 429:  # Rate limit
                retry_after = response.json().get('retry_after', 5)
                print(f"{Fore.YELLOW}[!] Rate limited on DM check. Waiting {retry_after} seconds...")
                time.sleep(float(retry_after))
            else:
                print(f"{Fore.RED}[-] Failed to get DM channels | Error: {response.status_code}")
        except Exception as e:
            print(f"{Fore.RED}[-] An error occurred (DM reply): {e}")
            time.sleep(5)  # Wait a bit on error

        time.sleep(10)  # Delay between DM checks

def main():
    global stop_flag, active_threads
    
    try:
        print("""
\t      
\t                   Discord Bot
\t              [Made by: Suson] 
\t
""")
        print(f'{Fore.WHITE}-------------------------------------------------------')

        # Get user inputs
        channels = input(f'{Fore.MAGENTA} [+] Enter channel IDs (comma-separated): ').split(',')
        print(f"{Fore.GREEN} Channel IDs saved: {len(channels)} channels")
        
        delay = input(f'{Fore.MAGENTA} [+] Time between messages (seconds): ')
        # Validate delay is a number
        try:
            delay_val = int(delay)
            print(f"{Fore.GREEN} Time delay saved: {delay} seconds")
        except ValueError:
            print(f"{Fore.RED} Invalid delay! Setting default to 5 seconds.")
            delay = "5"

        # Allow multiple tokens
        tokens_input = input(f'{Fore.MAGENTA} [+] Enter user token(s) (comma-separated): ')
        tokens = [t.strip() for t in tokens_input.split(',') if t.strip()]
        print(f"{Fore.GREEN} Token(s) saved: {len(tokens)} tokens")

        # Custom messages
        channel_message = input(f'{Fore.MAGENTA} [+] Enter message to send to channels: ')
        print(f"{Fore.GREEN} Channel message saved")

        dm_reply_message = input(f'{Fore.MAGENTA} [+] Enter message to reply in DMs: ')
        print(f"{Fore.GREEN} DM reply message saved")

        print(f'{Fore.WHITE}-------------------------------------------------------')

        # Initialize token_replied_users for all tokens
        for token in tokens:
            token_replied_users[token] = set()

        # Wait for user to press a key
        input(f'{Fore.CYAN} Press Enter to start the bot...')
        print(f"{Fore.YELLOW} Starting bot...")

        # Verify all tokens and start threads for valid ones
        valid_tokens = []
        for token in tokens:
            if token and _sv_chk_(token):
                valid_tokens.append(token)
                print(f"{Fore.GREEN}[+] Token validated: {token[:7]}...")
            elif token:
                print(f"{Fore.RED}[-] Token failed server check: {token[:7]}...")

        if not valid_tokens:
            print(f"{Fore.RED}[!] No valid tokens. Please join the required server and try again.")
            print(f"{Fore.YELLOW} Press Enter to exit...")
            input()
            return

        # Start threads for each valid token
        for token in valid_tokens:
            # Start channel spam threads
            for channel in channels:
                if channel.strip():
                    thread = threading.Thread(
                        target=spam_to_channels, 
                        args=(token, channel.strip(), channel_message, delay)
                    )
                    thread.daemon = True
                    active_threads.append(thread)
                    thread.start()
                    print(f"{Fore.CYAN}[+] Started channel thread for {channel.strip()}")
            
            # Start DM listener thread
            thread = threading.Thread(
                target=listen_and_reply_to_new_dms, 
                args=(token, dm_reply_message)
            )
            thread.daemon = True
            active_threads.append(thread)
            thread.start()
            print(f"{Fore.CYAN}[+] Started DM listener thread for token {token[:7]}...")

        print(f"{Fore.GREEN}[+] Bot started successfully with {len(valid_tokens)} token(s)!")
        print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop the bot")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}[!] Bot stopping... Please wait...")
        stop_flag = True
        time.sleep(2)
        print(f"{Fore.GREEN}[+] Bot stopped by user.")
    except Exception as e:
        print(f"{Fore.RED}[!] Critical error in main function: {e}")
        print(f"{Fore.YELLOW} Press Enter to exit...")
        input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}[!] Fatal error: {e}")
        print(f"{Fore.YELLOW} Press Enter to exit...")
        input()
