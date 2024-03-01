from src.snippets.memory import VectorStoreSummaryBufferMemory
import pytest


@pytest.fixture
def memory():
    return VectorStoreSummaryBufferMemory(session="test_session", buffer_size=5)


def test_assign_multiple_roles_to_messages():
    pass
    
def test_assign_role_to_message():
    pass

def test_get_file_path():
    pass

def test_read_summary_buffer_logs():
    pass

def test_write_summary_buffer_logs():
    pass

def test_truncate_file():
    pass

def test_save_context_on_disk():
    pass

def test_save_buffer_on_disk():
    pass

def test_load_context_from_disk():
    pass

def test_load_buffer_from_disk():
    pass

def test_reset_buffer_on_disk():
    pass

def test_create_initial_summary_buffer_prompt():
    pass

def test_update_initial_buffer():
    pass

def test_create_summary_buffer_prompt():
    pass

def test_update_summary_buffer():
    pass