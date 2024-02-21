from src.llm_dnd_dm.memory import MessagesMemory

memory = MessagesMemory()


def test_assign_role_to_message():
    role = "user"
    message = "Hi there"
    assert memory.assign_role_to_message(role=role, message=message) == {
        "role": role,
        "message": message,
    }
