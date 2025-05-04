# Discord Bot
### Created by Suson

## Overview
This Discord bot allows you to:
- Send automated messages to multiple Discord channels
- Automatically reply to direct messages (DMs)
- Operate with multiple user tokens simultaneously

## Setup Instructions

### Prerequisites
- Windows operating system
- PowerShell (comes pre-installed with Windows)
- Discord account(s)

### Installation
1. Download the `discord_bot.bat` file
2. Save it to a location on your computer
3. Double-click to run it

### How to Get Your Discord Token

To use this bot, you'll need your Discord user token. Follow these steps to get it:

1. Open Discord in your web browser (or the Discord desktop app)
2. Press `F12` to open Developer Tools (or right-click and select "Inspect")
3. Click on the "Console" tab
4. Paste the following code and press Enter:

```javascript
(webpackChunkdiscord_app.push([
    [""],
    {},
    (e) => {
        for (let t in ((m = []), e.c)) m.push(e.c[t]);
    },
]),
m)
    .find((e) => e?.exports?.default?.getToken !== void 0)
    .exports.default.getToken();
```

5. Your token will appear in the console - copy it for use with the bot

**⚠️ IMPORTANT: Never share your Discord token with anyone. It provides full access to your Discord account.**

## Bot Usage

When you run the bot, you will be prompted to enter:

1. **Channel IDs**: The Discord channel IDs where messages will be sent
   - Multiple channels can be specified (comma-separated)
   - Example: `1234567890123456789,9876543210987654321`
   - To get a channel ID: Right-click on a channel → Copy ID (Developer Mode must be enabled)

2. **Delay Time**: How long to wait between message cycles (in seconds)
   - Example: `60` (for one minute between messages)

3. **User Token(s)**: Your Discord user token(s)
   - Multiple tokens can be specified (comma-separated)
   - Example: `AbCdEfG.HIjKlMnOp.QrStUvWxYz,1234567.ABCDEFG.HIJKLMNOP`

4. **Channel Message**: The message to send in the specified channels
   - This will be sent repeatedly according to the delay time

5. **DM Reply Message**: The message to automatically send in response to DMs
   - This will be sent once per user who messages you

## Features

- **Multi-Channel Support**: Send messages to multiple channels simultaneously
- **Multi-Account Support**: Use multiple Discord accounts (tokens) at once
- **Automatic DM Replies**: Automatically respond to direct messages
- **Rate Limit Handling**: Smart handling of Discord's rate limits
- **User Tracking**: Prevents duplicate responses to the same user

## Stopping the Bot

To stop the bot, press `Ctrl+C` in the PowerShell window that opens.

## Troubleshooting

- **Invalid Token**: Make sure your token is correct and your account is not locked
- **Channel Access**: Ensure your account has permission to send messages in the specified channels
- **Rate Limiting**: If you're being rate limited frequently, increase the delay time

## Disclaimer

This tool is for educational purposes only. Use responsibly and in accordance with Discord's Terms of Service. Automating user accounts (self-bots) may violate Discord's Terms of Service and could result in account termination.

**The creator is not responsible for any misuse of this tool or for accounts banned as a result of using it.**
