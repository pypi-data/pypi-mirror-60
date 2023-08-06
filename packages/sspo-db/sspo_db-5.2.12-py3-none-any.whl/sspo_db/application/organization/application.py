from sspo_db.application.abstract_application import AbstractApplication
from sspo_db.service.organization.service import OrganizationService

class OrganizationSprint(AbstractApplication):

    def __init__(self):
        super().__init__(OrganizationService())