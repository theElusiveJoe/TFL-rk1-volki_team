import uuid

def gen_unique_node():
        return f"[{uuid.uuid4().hex[:3].upper()}]"