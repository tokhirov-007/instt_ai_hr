# --- TORCH MONKEY-PATCH ---
try:
    import torch.utils._pytree
    if not hasattr(torch.utils._pytree, "register_pytree_node"):
        torch.utils._pytree.register_pytree_node = getattr(torch.utils._pytree, "_register_pytree_node", lambda *args, **kwargs: None)
    if not hasattr(torch.utils._pytree, "serialized_type_name"):
        torch.utils._pytree.serialized_type_name = lambda *args, **kwargs: "unknown"
except ImportError:
    pass
# -------------------------
