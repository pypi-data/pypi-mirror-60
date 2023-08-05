from sspo_db.application.abstract_application import AbstractApplication
from sspo_db.model.process.models import Sprint
from sspo_db.service.process.service import SprintService, ScrumAtomicProjectService
from sspo_db.application.core.application_application_reference import ApplicationApplicationReference

class ApplicationSprint(AbstractApplication):

    def __init__(self):
        super().__init__(SprintService())
        
    def retrive_by_name_and_project_name(self, sprint_name, project_name):
        return self.service.retrive_by_name_and_project_name(sprint_name, project_name)

class ApplicationScrumAtomic():
    
    def __init__(self):
        self.scrum_atomic_project_service = ScrumAtomicProjectService()
        self.application_application_reference = ApplicationApplicationReference()
    
    def retrive_by_external_uuid(self, external_uuid):
        application_reference = self.application_application_reference.get_by_external_uuid_and_seon_entity_name(external_uuid, "scrum_atomic_project")
        if application_reference:
            return self.scrum_atomic_project_service.get_by_uuid(application_reference.internal_uuid)
        return None
