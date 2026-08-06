"""Multi-tenant registry.

Design principle for isolation: tenancy is not a filter bolted on at query
time — it is a structural boundary. Each tenant gets its own VectorStore
instance (app/rag/vector_store.py) with its own dict of chunks, so there is
no shared index a bug could accidentally query across. `TenantRegistry` is
the only place a tenant_id is resolved to its store/users, and every lookup
requires the caller to already know the tenant_id (it is never inferred
from the query text).
"""
from __future__ import annotations

from app.models import Role, Tenant, User


class TenantRegistry:
    def __init__(self) -> None:
        self._tenants: dict[str, Tenant] = {}
        self._users: dict[str, User] = {}  # user_id -> User

    def register_tenant(self, tenant: Tenant) -> None:
        self._tenants[tenant.tenant_id] = tenant

    def register_user(self, user: User) -> None:
        if user.tenant_id not in self._tenants:
            raise ValueError(f"Unknown tenant '{user.tenant_id}' for user '{user.user_id}'")
        self._users[user.user_id] = user

    def get_tenant(self, tenant_id: str) -> Tenant:
        if tenant_id not in self._tenants:
            raise KeyError(f"Unknown tenant_id: {tenant_id}")
        return self._tenants[tenant_id]

    def get_user(self, user_id: str) -> User:
        if user_id not in self._users:
            raise KeyError(f"Unknown user_id: {user_id}")
        return self._users[user_id]

    def authorize(self, user_id: str, claimed_tenant_id: str) -> User:
        """Reject a request outright if the caller's tenant claim doesn't
        match the user's actual tenant membership. This is what stops a
        compromised or buggy client from asking Tenant A's vector store a
        question while presenting a Tenant B user_id, and vice versa.
        """
        user = self.get_user(user_id)
        if user.tenant_id != claimed_tenant_id:
            raise PermissionError(
                f"user '{user_id}' belongs to tenant '{user.tenant_id}', "
                f"not '{claimed_tenant_id}' — cross-tenant access denied"
            )
        return user

    def tenants(self) -> list[Tenant]:
        return list(self._tenants.values())


def build_demo_registry() -> TenantRegistry:
    """Seeds the two demo scenarios' tenants and a handful of users."""
    reg = TenantRegistry()

    reg.register_tenant(Tenant("northstar_bank", "NorthStar Bank (white-label brand)", "white_label_brand"))
    reg.register_tenant(Tenant("meridian_bank", "Meridian Bank (white-label brand)", "white_label_brand"))
    reg.register_tenant(Tenant("retail_banking_dept", "Retail Banking Dept (internal)", "internal_department"))
    reg.register_tenant(Tenant("risk_compliance_dept", "Risk & Compliance Dept (internal)", "internal_department"))

    reg.register_user(User("cust_ns_01", "northstar_bank", Role.CUSTOMER, "Alex (NorthStar customer)"))
    reg.register_user(User("cust_mb_01", "meridian_bank", Role.CUSTOMER, "Jamie (Meridian customer)"))

    reg.register_user(User("teller_rb_01", "retail_banking_dept", Role.TELLER, "Sam (Retail teller)"))
    reg.register_user(User("risk_rb_01", "retail_banking_dept", Role.RISK_ANALYST, "Dana (Retail risk analyst)"))
    reg.register_user(User("risk_rc_01", "risk_compliance_dept", Role.RISK_ANALYST, "Priya (Risk analyst)"))
    reg.register_user(
        User("compliance_rc_01", "risk_compliance_dept", Role.COMPLIANCE_OFFICER, "Morgan (Compliance officer)")
    )

    return reg
