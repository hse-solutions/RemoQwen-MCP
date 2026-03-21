import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config
from src.ui.dashboard import Dashboard as db

# Initialize internal logging for v7.0 stability
logger = logging.getLogger("remotion_bridge")

class RemoteCommander:
    """
    v7.0 REMOTE COMMANDER: The ultimate Gateway Engine.
    Features: Silent Task Sync, Hybrid Permission Gates, and Real-time Notification.
    """
    _app: Application = None
    _permission_event = asyncio.Event()
    _last_permission_result = False

    @classmethod
    async def start_bot(cls):
        """Initializes the Telegram polling loop within the server's lifecycle."""
        if not config.TELEGRAM_ENABLED or not config.TELEGRAM_TOKEN:
            return

        db.log("SERVER", "Booting Telegram Remote Gateway...")
        
        try:
            # Build Application
            cls._app = Application.builder().token(config.TELEGRAM_TOKEN).build()

            # Register Core Handlers
            cls._app.add_handler(CommandHandler("start", cls._cmd_start))
            cls._app.add_handler(CommandHandler("help", cls._cmd_help))
            cls._app.add_handler(CommandHandler("status", cls._cmd_status))
            cls._app.add_handler(CallbackQueryHandler(cls._handle_permission_callback))
            cls._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cls._handle_remote_prompt))

            # Async Warm-up
            await cls._app.initialize()
            await cls._app.start()
            await cls._app.updater.start_polling(drop_pending_updates=True)
            
            db.log("SUCCESS", "Remote Commander linked and encrypted.")
            
            # Welcome message to the user
            await cls._app.bot.send_message(
                chat_id=config.AUTHORIZED_CHAT_ID,
                text="🦁 *SENTINEL LION ONLINE*\nI am connected to your PC. Send a prompt to start building.",
                parse_mode="Markdown"
            )

        except Exception as e:
            db.log("ERROR", f"Gateway failure: {str(e)}")

    @staticmethod
    async def _cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        await update.message.reply_text(f"👋 Greetings Boss!\nRemoQwen-MCP v7.0 is standing by.\nMode: {config.SELECTED_MODE}")

    @staticmethod
    async def _cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_msg = "🚀 *REMOTE COMMANDS*\n\n💬 *Just Text* - Injects a new mission\n📊 /status - Real-time radar\n🛡️ /help - This guide"
        await update.message.reply_markdown(help_msg)

    @staticmethod
    async def _cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        status_card = (
            "📡 *MISSION CONTROL RADAR*\n"
            "───────────────────\n"
            f"✅ *State:* Immortal Online\n"
            f"⚙️ *Mode:* {config.SELECTED_MODE}\n"
            f"📍 *Project:* `{os.path.basename(config.PROJECT_ROOT)}`"
        )
        await update.message.reply_markdown(status_card)

    @classmethod
    async def _handle_remote_prompt(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        THE SILENT SYNC: Intercepts Telegram text and writes it directly to the 
        project's src folder so the AI can read it via 'initialize_task'.
        """
        if str(update.effective_user.id) != str(config.AUTHORIZED_CHAT_ID): return
        
        prompt = update.message.text
        db.log("REMOTE", f"Capturing remote instruction: {prompt[:30]}...")

        try:
            # 🛡️ BULLETPROOF PATHING: Ensure the directory exists
            os.makedirs(os.path.dirname(config.REMOTE_TASK_FILE), exist_ok=True)
            
            # ATOMIC WRITE: Overwrite existing task to keep AI focused
            with open(config.REMOTE_TASK_FILE, "w", encoding="utf-8") as f:
                f.write(f"# 🚨 REMOTE MISSION RECEIVED\n\n{prompt}\n\n---\n*Source: Telegram Remote Commander*")
            
            db.log("SUCCESS", "Remote task synchronized with AI brain.")
            await update.message.reply_text("⚡ *TASK SYNCED ✅*\nQwen is being notified. Watch the terminal or wait for updates.")
            
        except Exception as e:
            db.log("ERROR", f"Silent sync failed: {str(e)}")
            await update.message.reply_text(f"❌ *SYNC ERROR:* {e}")

    @classmethod
    async def send_notification(cls, message: str):
        """Utility to push instant terminal updates to the phone."""
        if cls._app and config.TELEGRAM_ENABLED:
            try:
                await cls._app.bot.send_message(chat_id=config.AUTHORIZED_CHAT_ID, text=message)
            except: pass

    @classmethod
    async def ask_hybrid_permission(cls, tool_name: str, target: str) -> bool:
        """
        HYBRID GATE v7.0: Decides where to ask for permission based on active mode.
        If Telegram is ON, it sends buttons to the phone and blocks locally until clicked.
        """
        if not cls._app or not config.TELEGRAM_ENABLED:
            # Fallback to Terminal UI if remote is disabled
            return await db.ask_permission(tool_name, target)

        db.log("GUARD", f"Awaiting remote authorization for '{tool_name}'...", style="bold magenta")
        
        keyboard = [[
            InlineKeyboardButton("✅ APPROVE", callback_data="perm_yes"),
            InlineKeyboardButton("❌ DENY", callback_data="perm_no")
        ]]
        
        cls._permission_event.clear()
        
        msg = f"⚠️ *AUTHORIZATION REQUIRED*\n\nAI wants to: `{tool_name}`\nTarget: `{target}`"
        await cls._app.bot.send_message(
            chat_id=config.AUTHORIZED_CHAT_ID, 
            text=msg, 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
        # ASYNC BLOCK: Wait for phone input without hanging the server heartbeat
        await cls._permission_event.wait()
        return cls._last_permission_result

    @classmethod
    async def _handle_permission_callback(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the button response from Telegram."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "perm_yes":
            cls._last_permission_result = True
            await query.edit_message_text(text="✅ *PERMISSION GRANTED* (Executing on PC...)")
            db.log("SUCCESS", "Remote approval received.")
        else:
            cls._last_permission_result = False
            await query.edit_message_text(text="❌ *PERMISSION DENIED* (Aborted locally.)")
            db.log("ERROR", "Remote rejection received.")
        
        # UNBLOCK: Release the server task
        cls._permission_event.set()