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

        self.scrum_atomic_project_service = ScrumAtomicProjectService()
        
        self.scrum_team_service = ScrumTeamService()
        self.development_team_service = DevelopmentTeamService()
        self.application_application_reference = ApplicationApplicationReference()
    
    def retrive_by_external_id(self, external_id):
        return self.service.retrive_by_external_id(external_id)
    
    def create_atomic_project (self, name, description, organization, scrum_complex_project=None):
        #Persistindo a classe no banco
        scrum_atomic_project = ScrumAtomicProject()
        scrum_atomic_project.name = name
        scrum_atomic_project.description = description
        scrum_atomic_project.organization = organization
        
        if scrum_complex_project:
            scrum_atomic_project.scrum_complex_project_id = scrum_complex_project.id
        
        #criando o projeto atomico
        self.scrum_atomic_project_service.create(scrum_atomic_project)
        
        return scrum_atomic_project

    def create_atomic_project_process_and_team(self, name, description, organization, scrum_complex_project=None):
        
        #criando o projeto atomico
        scrum_atomic_project = self.create_atomic_project(name, description, organization, scrum_complex_project)
        #Criando o processo
        scrum_process = self.create_scrum_process(name, description,scrum_atomic_project)
        #criando o team
        scrum_team = self.create_scrum_team(name, description, scrum_atomic_project, organization)

        return scrum_atomic_project, scrum_process, scrum_team

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


'''    
    def create(self, name, description, scrum_project):
        
        scrum_process = ScrumProcess()
        
        scrum_process.name = name
        scrum_process.description = description
        scrum_process.scrum_project = scrum_project
        self.service.create(scrum_project)

        #Criando o product backlog definition
        product_backlog_definition = ProductBacklogDefinition()
        product_backlog_definition.name = name
        product_backlog_definition.description = description
        product_backlog_definition.scrum_process = scrum_process
                    
        self.product_backlog_definition_service.create(product_backlog_definition)
                    
        # Criando o backlog do projeto
        product_backlog = ProductBacklog()
        product_backlog.name = name
        product_backlog.description = description
        product_backlog.product_backlog_definition = product_backlog_definition.id
                    
        self.product_backlog_service.create(product_backlog)

        return scrum_process
    
    def create_scrum_team(self, name, description, scrum_project, organization):
        
        #criando o scrum team
        scrum_team = ScrumTeam()
        scrum_team.name = name
        scrum_team.description = description
        scrum_team.organization = organization
        scrum_team.scrum_project = scrum_project.id
                    
        self.scrum_team_service.create(scrum_team)

        development_team = DevelopmentTeam()
        development_team.name = name
        development_team.description = description
        development_team.scrum_team_id = scrum_team.id
        
        self.development_team_service.create (development_team)
        
        return scrum_team
    '''
    