class InstitutionScopedQuerysetMixin:
    """Scope moderator querysets to the institution on their Admin profile."""

    institution_lookup = "institution_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        admin_profile = getattr(self.request, "admin_profile", None)
        if admin_profile and admin_profile.role == "moderator":
            return queryset.filter(**{self.institution_lookup: admin_profile.institution_id})
        return queryset
