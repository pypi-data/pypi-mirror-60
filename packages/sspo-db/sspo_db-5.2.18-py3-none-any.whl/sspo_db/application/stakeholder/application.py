from sspo_db.model.stakeholder.models import Person, Developer, ScrumMaster
from sspo_db.service.stakeholder.service import PersonService, DeveloperService, ScrumMasterService, TeamMemberService
from sspo_db.application.core.application import ApplicationApplicationReference
from sspo_db.application.abstract_application import AbstractApplication
from pprint import pprint

class ApplicationPerson(AbstractApplication):
    
    def __init__(self):
        super().__init__(PersonService())
        self.application_reference_service = ApplicationApplicationReference()
    
    def retrive_by_uuid(self, uuid):
        return self.service.get_by_uuid(uuid)
        
class ApplicationTeamMember(AbstractApplication):
    
    def __init__(self):
        super().__init__(TeamMemberService())
        
    def retrive_by_external_id_and_project_name(self, external_id, project_name):
        return self.service.retrive_by_external_id_and_project_name(external_id,project_name)

class ApplicationDeveloper(AbstractApplication):

    def __init__(self):
        super().__init__(DeveloperService())
    '''    
    def create_developer(self, person, team, team_role = ""):
        
        developer = Developer()
        developer.name = team.name+" - "+person.name
        developer.description = person.description
        developer.person = person
        developer.team = team 
        developer.team_role = team_role

        self.service.create(developer)
    '''
    def create_with_project_name(self, external_id, project_name):
        application_person = ApplicationPerson()
        person = application_person.retrive_by_external_uuid(external_id, "person")
        if person is not None:
            return self.service.create_with_project_name(person, project_name)
        return None
        
    '''
    def create_scrum_master(self, person, team, team_role = ""):
        
        scrum_master = ScrumMaster()
        scrum_master.name = person.name
        scrum_master.description = person.description
        scrum_master.person = person
        scrum_master.team = team 
        scrum_master.team_role = team_role

        self.scrum_master_service.create(scrum_master)
    '''
    
    class ApplicationScrumMaster(AbstractApplication):
        super().__init__(ScrumMasterService())
        
    