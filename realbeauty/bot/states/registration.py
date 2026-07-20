from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class SelfReg(StatesGroup):
    """FSM for user self-registration."""

    full_name = State()
    birth_date = State()
    phone = State()
    face_condition = State()
    photo = State()


class AdminAssistedReg(StatesGroup):
    """FSM for admin-assisted registration."""

    full_name = State()
    birth_date = State()
    phone = State()
    face_condition = State()
    photo = State()


class FeedbackState(StatesGroup):
    """FSM for week-1 feedback collection."""

    text = State()
    rating = State()


class ProgressState(StatesGroup):
    """FSM for week-2 before/after photo collection."""

    before_photo = State()
    after_photo = State()


class SupportState(StatesGroup):
    """FSM for free-form questions/messages to the shop."""

    message = State()
