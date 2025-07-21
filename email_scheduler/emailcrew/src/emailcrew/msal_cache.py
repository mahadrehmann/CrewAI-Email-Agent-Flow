# msal_cache.py
# import os, sys
# from msal_extensions import (
#     FilePersistenceWithDataProtection,
#     KeychainPersistence,
#     LibsecretPersistence,
#     build_encrypted_persistence,
#     PersistedTokenCache
# )

# def build_persistence(cache_path="msal_token_cache.bin"):
#     if sys.platform.startswith("win"):
#         persistence = FilePersistenceWithDataProtection(cache_path)
#     elif sys.platform.startswith("darwin"):
#         persistence = KeychainPersistence(cache_path, "email_scheduler", "user")
#     else:
#         try:
#             persistence = LibsecretPersistence(cache_path, "email_scheduler", {"app": "email_scheduler"})
#         except:
#             persistence = build_encrypted_persistence(cache_path)
#     return PersistedTokenCache(persistence)


# def build_persistence(cache_path="msal_token_cache.bin"):
#     try:
#         from msal_extensions import LibsecretPersistence
#         return PersistedTokenCache(
#             LibsecretPersistence(cache_path, "email_scheduler", {"app": "email_scheduler"})
#         )
#     except ImportError:
#         # No `gi`/libsecret → fall back to unencrypted file
#         from msal_extensions import FilePersistence
#         return PersistedTokenCache(FilePersistence(cache_path))


from msal_extensions import PersistedTokenCache, FilePersistence

def build_persistence(cache_path="msal_token_cache.bin"):
    persistence = FilePersistence(cache_path)
    return PersistedTokenCache(persistence)
