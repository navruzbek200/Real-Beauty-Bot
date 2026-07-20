"""
What a seller is allowed to do.

Permissions are what actually gates the admin, so the role radio on the staff
page has to map onto a real permission set. Keeping that set here — rather than
in whatever state the group happens to be in the database — means the answer to
"what can a seller see?" is readable, and a migration can enforce it.
"""

from __future__ import annotations

from django.contrib.auth.models import Group, Permission

SELLER_GROUP = "Seller"

# (app_label, codename) — a seller runs the counter: they add customers, record
# what those customers bought, and answer them. Everything that changes how the
# bot behaves (settings, templates, discounts) is deliberately absent.
SELLER_PERMISSIONS: list[tuple[str, str]] = [
    ("users", "view_telegramuser"),
    ("users", "add_telegramuser"),
    ("users", "change_telegramuser"),
    ("users", "view_userproduct"),
    ("users", "add_userproduct"),
    ("users", "change_userproduct"),
    ("users", "delete_userproduct"),
    ("products", "view_product"),
    ("analytics", "view_userfeedback"),
    ("analytics", "change_userfeedback"),
    ("analytics", "view_progressphoto"),
    ("support", "view_supportthread"),
    ("support", "change_supportthread"),
    ("support", "view_supportmessage"),
    ("support", "add_supportmessage"),
]


def sync_seller_group(group_model=Group, permission_model=Permission) -> Group:
    """
    Make the Seller group match SELLER_PERMISSIONS exactly.

    Model classes are injectable so migrations can pass their historical
    versions instead of the live ones.
    """
    group, _ = group_model.objects.get_or_create(name=SELLER_GROUP)
    wanted = permission_model.objects.filter(
        content_type__app_label__in={app for app, _ in SELLER_PERMISSIONS},
        codename__in={codename for _, codename in SELLER_PERMISSIONS},
    )
    # The filter above is a coarse cross-product; keep only real pairs.
    wanted = [
        p
        for p in wanted.select_related("content_type")
        if (p.content_type.app_label, p.codename) in set(SELLER_PERMISSIONS)
    ]
    group.permissions.set(wanted)
    return group
