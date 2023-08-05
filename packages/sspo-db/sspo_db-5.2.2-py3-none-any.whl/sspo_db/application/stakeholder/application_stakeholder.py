from sspo_db.model.stakeholder.models import Person, Developer, ScrumMaster
from sspo_db.service.stakeholder.service import PersonService, DeveloperService, ScrumMasterService, TeamMemberService
from sspo_db.service.organization.service import ScrumTeamService
from sspo_db.application.core.application_application_reference import ApplicationApplicationReference


class ApplicationPerson():
    
    def __init__(self):
        self.person_service = PersonService()
        self.application_reference_service = ApplicationApplicationReference()
    
    def retrive_by_uuid(self, uuid):
        return self.person_service.get_by_uuid(uuid)
    
    def retrive_person_by_external_uuid (self, external_id):
        return self.person_service.retrive_by_external_id(external_id)
        
    def create_person(self, name, email, organization, description = ""):
        
        person = Person()
        person.name = name
        person.description = description
        person.email = email 
        person.organization = organization

        self.person_service.create(person)
        return person
        
class ApplicationTeamMember():
    
    def __init__(self):
        self.service = TeamMemberService()
    
    def retrive_by_external_id_and_project_name(self, external_id, project_name):
        return self.service.retrive_by_external_id_and_project_name(external_id,project_name)

class ApplicationStakeholder():

    def __init__(self):
        self.developer_service = DeveloperService()
        self.scrum_master_service = ScrumMasterService()
    
    def create_developer(self, person, team, team_role = ""):
        
        developer = Developer()
        developer.name = team.name+" - "+person.name
        developer.description = person.description
        developer.person = person
        developer.team = team 
        developer.team_role = team_role

        self.developer_service.create(developer)

    def create_scrum_master(self, person, team, team_role = ""):
        
        scrum_master = ScrumMaster()
        scrum_master.name = team.name+" - "+person.name
        scrum_master.description = person.description
        scrum_master.person = person
        scrum_master.team = team 
        scrum_master.team_role = team_role

        self.scrum_master_service.create(scrum_master)
    
    class ApplicationScrumTeam():
        def __init__(self):
            self.service = ScrumTeamService()
        
        def create(self, scrum_team):
            self.service.create(scrum_team)
        
        
        
        
            

    
    