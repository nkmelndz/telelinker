
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import SessionRevokedError, AuthKeyUnregisteredError
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor


class TelegramService:
    def __init__(self, session_path, api_id, api_hash):
        try:
            self.session_path = session_path
            self.api_id = api_id
            self.api_hash = api_hash
            self.client = None
            self._loop = None
            self._thread = None
        except (SessionRevokedError, AuthKeyUnregisteredError):
            pass  # Silenciar completamente el error

    def _run_in_thread(self):
        """Ejecutar el event loop en un hilo separado"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _ensure_loop(self):
        """Asegurar que el event loop esté corriendo en un hilo separado"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run_in_thread, daemon=True)
            self._thread.start()
            # Esperar un poco para que el loop se inicialice
            import time
            time.sleep(0.1)

    async def _ensure_client(self):
        """Asegurar que el cliente esté inicializado y conectado"""
        if self.client is None:
            self.client = TelegramClient(self.session_path, self.api_id, self.api_hash)
            
        # Conectar si no está conectado
        if not self.client.is_connected():
            await self.client.connect()
            
        # Verificar si ya está autorizado antes de intentar start()
        if await self.client.is_user_authorized():
            # Eliminar mensaje para evitar duplicados en consola
            return
            
        # Solo hacer start() si no está autorizado
        print("🔐 Authentication required...")
        await self.client.start()

    def start(self):
        try:
            self._ensure_loop()
            future = asyncio.run_coroutine_threadsafe(self._ensure_client(), self._loop)
            # Aumentar timeout para permitir autenticación manual (5 minutos)
            future.result(timeout=300)
            return True
        except (SessionRevokedError, AuthKeyUnregisteredError):
            print("❌ Session expired. Please run 'telelinker login' to authenticate again.")
            return False
        except Exception as e:
            # Solo mostrar error si realmente hay un problema, no por timeout de input
            if "timeout" not in str(e).lower() and "input" not in str(e).lower():
                print(f"❌ Authentication failed: {str(e)}")
            return False

    async def _iter_group_messages_async(self, group_username):
        """Versión asíncrona de iter_group_messages"""
        try:
            await self._ensure_client()
            messages = []
            async for message in self.client.iter_messages(group_username):
                messages.append(message)
            return messages
        except (SessionRevokedError, AuthKeyUnregisteredError):
            return []  # Silenciar completamente el error

    def iter_group_messages(self, group_username):
        try:
            self._ensure_loop()
            future = asyncio.run_coroutine_threadsafe(
                self._iter_group_messages_async(group_username), 
                self._loop
            )
            return future.result(timeout=30)
        except (SessionRevokedError, AuthKeyUnregisteredError):
            return []  # Silenciar completamente el error
        except Exception:
            return []
    
    async def _iter_user_dialogs_async(self):
        """Versión asíncrona de iter_user_dialogs"""
        try:
            await self._ensure_client()
            dialogs = []
            async for dialog in self.client.iter_dialogs():
                dialogs.append(dialog)
            return dialogs
        except (SessionRevokedError, AuthKeyUnregisteredError):
            return []  # Silenciar completamente el error

    def iter_user_dialogs(self):
        try:
            self._ensure_loop()
            future = asyncio.run_coroutine_threadsafe(
                self._iter_user_dialogs_async(), 
                self._loop
            )
            return future.result(timeout=30)
        except (SessionRevokedError, AuthKeyUnregisteredError):
            return []  # Silenciar completamente el error
        except Exception:
            return []

    def disconnect(self):
        try:
            if self.client and self._loop:
                async def _disconnect():
                    await self.client.disconnect()
                
                future = asyncio.run_coroutine_threadsafe(_disconnect(), self._loop)
                future.result(timeout=5)
        except Exception:
            pass
        
        try:
            if self._loop:
                self._loop.call_soon_threadsafe(self._loop.stop)
        except Exception:
            pass
