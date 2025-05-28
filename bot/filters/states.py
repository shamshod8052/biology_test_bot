from aiogram.fsm.state import State, StatesGroup


class TestState(StatesGroup):
    check_answers = State()

class Keyboard(StatesGroup):
    attestation = State()
    certificate = State()
