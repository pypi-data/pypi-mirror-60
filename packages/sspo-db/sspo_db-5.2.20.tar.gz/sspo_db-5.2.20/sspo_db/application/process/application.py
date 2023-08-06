from sspo_db.application.abstract_application import AbstractApplication
from sspo_db.model.process.models import Sprint, ScrumAtomicProject, ScrumComplexProject, ScrumProcess, ProductBacklogDefinition
from sspo_db.model.artifact.models import ProductBacklog
from sspo_db.model.organization.models import ScrumTeam, DevelopmentTeam
from sspo_db.application.core.application import ApplicationApplicationReference

from sspo_db.service.process.service import SprintService, ScrumComplexProjectService, ScrumAtomicProjectService, ScrumProjectService, ScrumAtomicProjectService, ScrumProcessService, ProductBacklogDefinitionService
from sspo_db.service.artifact.service import ProductBacklogService
from sspo_db.service.organization.service import ScrumTeamService, DevelopmentTeamService


class ApplicationSprint(AbstractApplication):

    def __init__(self):
        super().__init__(SprintService())
        
    def retrive_by_name_and_project_name(self, sprint_name, project_name):
        return self.service.retrive_by_name_and_project_name(sprint_name, project_name)

class ApplicationScrumComplexProject(AbstractApplication):

    def __init__(self):
        super().__init__(ScrumComplexProjectService())
        self.application_application_reference = ApplicationApplicationReference()
    
    def retrive_by_external_uuid(self, external_uuid):
        application_reference = self.application_application_reference.get_by_external_uuid_and_seon_entity_name(external_uuid)
        if application_reference:
            return self.scrum_atomic_project_service.get_by_uuid(application_reference.internal_uuid)
        return None

class ApplicationScrumAtomicProject(AbstractApplication):

    def __init__(self):
        super().__init__(ScrumAtomicProjectService())
        self.application_application_reference = ApplicationApplicationReference()
    
    def retrive_by_external_uuid(self, external_uuid):
        application_reference = self.application_application_reference.get_by_external_uuid_and_seon_entity_name(external_uuid)
        if application_reference:
            return self.scrum_atomic_project_service.get_by_uuid(application_reference.internal_uuid)
        return None

class ApplicationScrumProject(AbstractApplication):

    def __init__(self):
        super().__init__(ScrumProjectService())
# comentario
class ApplicationScrumProcess(AbstractApplication):
    
    def __init__(self):
        super().__init__(ScrumProcessService())

class ApplicationProductBacklogDefinition(AbstractApplication):
    
    def __init__(self):
        super().__init__(ProductBacklogDefinitionService())
    
    def retrive_scrum_team_by_external_uuid(self, external_uuid):
        application_reference = self.application_application_reference.get_by_external_uuid_and_seon_entity_name(external_uuid, "scrum_team")
        if application_reference:
            return self.scrum_team_service.get_by_uuid(application_reference.internal_uuid)
        return None


