# Fusion 360 Discord Presence Add-In

This repository contains a simple Fusion 360 add-in that updates your Discord Rich Presence. The folder, Python script, and manifest all share the same base name (`DiscordPresence`) to satisfy Fusion 360's add-in naming rules.

## Folder Structure

```
DiscordPresence/
├── DiscordPresence.manifest
├── DiscordPresence.py
└── pypresence/
    ├── __init__.py
    ├── baseclient.py
    ├── client.py
    ├── exceptions.py
    ├── payloads.py
    ├── presence.py
    └── utils.py
```

## Usage

1. Copy the `DiscordPresence` folder into your Fusion 360 add-ins directory:
   - **Windows:** `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns`
   - **macOS:** `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns`
2. Replace `YOUR_DISCORD_CLIENT_ID` in `DiscordPresence.py` with the Client ID of your Discord application.
3. Restart Fusion 360, open **Tools → Add-Ins**, and run **Discord Presence**.

Once running, a new button named **Start Discord Presence** appears in the SOLID workspace. Clicking it connects to Discord and keeps your status up to date with the current document name.
## Troubleshooting
If Fusion 360 reports that a script cannot be identified or that the script and manifest names do not match, verify the following:

- The folder is named `DiscordPresence`.
- The main script is `DiscordPresence.py` (no hidden `.txt` extension).
- The manifest file is `DiscordPresence.manifest` and not `.json` or `.txt`.
- All three names use the exact same capitalization.
- On Windows, disable "Hide extensions for known file types" so you can confirm the file extensions.

## Avoiding Merge Conflicts when Updating this Add-In

When modifying the code or documentation, keep your changes small and focused to reduce the chance of merge conflicts. Update your local branch with `git pull --rebase` before editing and commit frequently. If multiple people are collaborating, work on short-lived branches so that edits rarely overlap.
