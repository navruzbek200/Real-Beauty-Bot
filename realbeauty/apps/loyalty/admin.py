"""
No admin registrations: the points program is retired.

The models and their rows are kept so historical balances stay readable in
the database, but nothing in the product writes to them any more, and an
admin screen that still edits a dead system is worse than no screen.
"""

from __future__ import annotations
