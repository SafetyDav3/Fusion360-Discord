# DiscordPresence.py

import adsk.core
import adsk.fusion
import traceback
import threading
import time

# Import the local pypresence module (must reside in a "pypresence" subfolder)
from pypresence import Presence

# === Configuration ===
DISCORD_CLIENT_ID = 'YOUR_DISCORD_CLIENT_ID'  # <-- Replace with your real Client ID
UPDATE_INTERVAL = 15  # seconds between automatic updates

# === Global Handles ===
app: adsk.core.Application = None
ui: adsk.core.UserInterface = None
handlers = []            # Keep event handlers alive
rpc_client: Presence = None
rpc_thread: threading.Thread = None
stop_thread = False

# === Helper: Build Presence Payload ===
def build_presence_payload():
    """
    Returns a dict for Discord Rich Presence:
      - details: "Editing: [document name]"
      - state:   "In Fusion 360"
      - large_image: 'fusion_logo' (if you uploaded this asset)
      - timestamps: start time
    """
    now = int(time.time())
    doc = app.activeDocument
    doc_name = doc.name if doc else "No Document"
    payload = {
        'details': f"Editing: {doc_name}",
        'state': "In Fusion 360",
        'start': now,
        # If you uploaded an Art Asset named 'fusion_logo' in Discord Dev Portal:
        'large_image': 'fusion_logo',
        'large_text': 'Autodesk Fusion 360'
    }
    return payload

# === Discord RPC Thread ===
def rpc_update_loop():
    """
    Periodically refresh Rich Presence so Discord doesn’t time out.
    """
    global stop_thread, rpc_client
    while not stop_thread:
        try:
            payload = build_presence_payload()
            rpc_client.update(**payload)
        except Exception:
            ui.messageBox(f"Error updating Discord presence:\n{traceback.format_exc()}")
        time.sleep(UPDATE_INTERVAL)

# === Fusion Event Handler: Document Activated ===
class DocumentActivatedHandler(adsk.core.DocumentEventHandler):
    def notify(self, args):
        try:
            payload = build_presence_payload()
            rpc_client.update(**payload)
        except:
            ui.messageBox(f"Error in DocumentActivatedHandler:\n{traceback.format_exc()}")

# === Fusion Event Handler: Application Closing ===
class StopEventHandler(adsk.core.ApplicationEventHandler):
    def notify(self, args):
        """
        Fusion is closing—tear down the RPC connection cleanly.
        """
        global stop_thread, rpc_client
        stop_thread = True
        if rpc_client:
            try:
                rpc_client.clear()
                rpc_client.close()
            except:
                pass

# === Command Class (invoked by our toolbar button) ===
class DiscordPresenceCommand(adsk.core.CommandEventHandler):
    def notify(self, args):
        """
        When “Start Discord Presence” is clicked:
          1. Connect to Discord IPC via pypresence.
          2. Hook documentActivated and applicationClosing events.
          3. Start the background thread to refresh presence every UPDATE_INTERVAL seconds.
        """
        try:
            global rpc_client, rpc_thread, stop_thread

            # If already running, do nothing
            if rpc_client:
                ui.messageBox("Discord Presence is already running.")
                return

            # Initialize and connect RPC client
            rpc_client = Presence(DISCORD_CLIENT_ID)
            rpc_client.connect()

            # Send an initial presence immediately
            payload = build_presence_payload()
            rpc_client.update(**payload)

            # Attach event: document switched → update presence instantly
            doc_activated_ev = app.documentActivated
            doc_handler = DocumentActivatedHandler()
            doc_activated_ev.add(doc_handler)
            handlers.append(doc_handler)

            # Attach Fusion closing event → clean up RPC on exit
            app_close_ev = app.applicationClosing
            close_handler = StopEventHandler()
            app_close_ev.add(close_handler)
            handlers.append(close_handler)

            # Start background thread to keep refreshing Presence
            stop_thread = False
            rpc_thread = threading.Thread(target=rpc_update_loop)
            rpc_thread.daemon = True
            rpc_thread.start()

            ui.messageBox("Discord Rich Presence started successfully.")
        except Exception:
            ui.messageBox(f"Failed to start Discord Presence:\n{traceback.format_exc()}")

# === Standard run() and stop() Entry Points ===
def run(context):
    """
    Fusion calls this when the add-in is launched. We register our command here.
    """
    global app, ui
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Find or create the command definition defined in DiscordPresence.manifest
        cmdDefs = ui.commandDefinitions
        cmdDef = cmdDefs.itemById('startDiscordPresence')
        if not cmdDef:
            ui.messageBox("Command definition not found. Check DiscordPresence.manifest.")
            return

        # Hook commandCreated event so our DiscordPresenceCommand runs on click
        onCommandCreated = DiscordPresenceCommand()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

    except Exception:
        if ui:
            ui.messageBox(f"Add-in start failed:\n{traceback.format_exc()}")

def stop(context):
    """
    Fusion calls this when the user stops the add-in in the Scripts & Add-Ins dialog.
    We must:
      1. Remove the command from the UI.
      2. Stop the RPC thread and close the Discord IPC socket.
      3. Remove any attached event handlers.
    """
    global stop_thread, rpc_client, rpc_thread
    try:
        # Remove the command definition so the toolbar icon disappears
        ui = adsk.core.Application.get().userInterface
        cmdDef = ui.commandDefinitions.itemById('startDiscordPresence')
        if cmdDef:
            cmdDef.deleteMe()

        # Signal the background thread to stop, then join briefly
        stop_thread = True
        if rpc_thread and rpc_thread.is_alive():
            rpc_thread.join(timeout=2.0)

        # Disconnect from Discord
        if rpc_client:
            try:
                rpc_client.clear()
                rpc_client.close()
            except:
                pass
            rpc_client = None

        # Detach any event handlers we registered
        for h in handlers:
            try:
                h.remove()
            except:
                pass
        handlers.clear()

    except Exception:
        if ui:
            ui.messageBox(f"Add-in stop failed:\n{traceback.format_exc()}")
