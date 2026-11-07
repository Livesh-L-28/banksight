"""
BankSight Enterprise PII Masking Engine
Implements role-based dynamic data masking in compliance with GDPR, CCPA, and GLBA standards.
"""

from typing import Any, Dict, Optional


class PIIMasker:
    """
    Applies dynamic field-level masking according to the caller's authorized role and data scope.
    """

    UNMASKED_ROLES = {"Admin", "ComplianceOfficer"}

    @staticmethod
    def mask_name(name: Optional[str], role: str = "DataAnalyst") -> str:
        """Masks full name (e.g., 'Eleanor Vance' -> 'E****** V****')."""
        if not name or role in PIIMasker.UNMASKED_ROLES:
            return name or ""
        parts = name.strip().split()
        masked_parts = []
        for p in parts:
            if len(p) <= 2:
                masked_parts.append(p[0] + "*")
            else:
                masked_parts.append(p[0] + "*" * (len(p) - 1))
        return " ".join(masked_parts)

    @staticmethod
    def mask_email(email: Optional[str], role: str = "DataAnalyst") -> str:
        """Masks email address (e.g., 'eleanor.vance@example.com' -> 'e***e@example.com')."""
        if not email or role in PIIMasker.UNMASKED_ROLES:
            return email or ""
        if "@" not in email:
            return "***"
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "*"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: Optional[str], role: str = "DataAnalyst") -> str:
        """Masks phone number (e.g., '+1-555-123-4567' -> '+1-***-***-4567')."""
        if not phone or role in PIIMasker.UNMASKED_ROLES:
            return phone or ""
        digits = [c for c in phone if c.isdigit()]
        if len(digits) < 4:
            return "******"
        last_four = "".join(digits[-4:])
        return f"***-***-{last_four}"

    @staticmethod
    def mask_account_number(account_id: Optional[str], role: str = "DataAnalyst") -> str:
        """Masks financial account identifier (e.g., 'ACC-0001234' -> 'ACC-****1234')."""
        if not account_id or role in PIIMasker.UNMASKED_ROLES:
            return account_id or ""
        if len(account_id) <= 4:
            return "****"
        return account_id[:4] + "****" + account_id[-4:]

    @classmethod
    def mask_customer_dossier(cls, customer_dict: Dict[str, Any], role: str = "DataAnalyst") -> Dict[str, Any]:
        """
        Applies comprehensive dynamic masking over a customer dictionary dossier.
        """
        if role in cls.UNMASKED_ROLES:
            return customer_dict.copy()

        dossier = customer_dict.copy()
        if "first_name" in dossier:
            dossier["first_name"] = cls.mask_name(dossier["first_name"], role)
        if "last_name" in dossier:
            dossier["last_name"] = cls.mask_name(dossier["last_name"], role)
        if "full_name" in dossier:
            dossier["full_name"] = cls.mask_name(dossier["full_name"], role)
        if "email" in dossier:
            dossier["email"] = cls.mask_email(dossier["email"], role)
        if "phone" in dossier:
            dossier["phone"] = cls.mask_phone(dossier["phone"], role)
        if "address" in dossier:
            dossier["address"] = "REDACTED [Confidential Address]"
        if "postal_code" in dossier:
            # Mask last 2 digits for geographic privacy
            pc = str(dossier["postal_code"])
            dossier["postal_code"] = pc[:3] + "**" if len(pc) >= 3 else "***"

        # Mask account IDs if present in accounts list
        if "accounts" in dossier and isinstance(dossier["accounts"], list):
            masked_accounts = []
            for acc in dossier["accounts"]:
                acc_copy = acc.copy() if isinstance(acc, dict) else acc
                if isinstance(acc_copy, dict) and "account_id" in acc_copy:
                    acc_copy["account_id"] = cls.mask_account_number(acc_copy["account_id"], role)
                masked_accounts.append(acc_copy)
            dossier["accounts"] = masked_accounts

        return dossier
