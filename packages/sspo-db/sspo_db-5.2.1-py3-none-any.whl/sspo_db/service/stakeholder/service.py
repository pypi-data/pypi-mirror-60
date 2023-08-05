from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sspo_db.model.stakeholder.models import *
from sspo_db.model.organization.models import ScrumTeam, DevelopmentTeam
from sspo_db.model.process.models import ScrumProject
from sspo_db.service.core.service import ApplicationReferenceService
from pprint import pprint
from sspo_db.service.base_service import BaseService

class PersonService(BaseService):
    
    def __init__(self):
        super(PersonService,self).__init__(Person)
       
        self.application_reference_service = ApplicationReferenceService()

    def retrive_by_external_id(self, external_id):
        application_reference = self.application_reference_service.retrive_by_external_id(external_id)
        if application_reference:
            return self.get_by_uuid(application_reference.internal_uuid)
        return None

    
class TeamMemberService(BaseService):
    def __init__(self):
        super(TeamMemberService,self).__init__(TeamMember)
        self.person_service = PersonService()

    def retrive_by_external_id_and_project_name (self, external_id, project_name):
        
        person = self.person_service.retrive_by_external_id(external_id)
        scrum_team = self.session.query(ScrumTeam).join(ScrumProject).filter(ScrumProject.name.like (project_name)).first()
        team_member = self.session.query(TeamMember).filter(TeamMember.person == person, TeamMember.team == scrum_team).first()
        
        if team_member is None: 
            team_member = self.session.query(TeamMember).join(DevelopmentTeam).filter(TeamMember.team_id == developmen_team.id, TeamMember.person == person, DevelopmentTeam.scrum_team_id == scrum_team.id).first()
        
        return team_member

class DeveloperService(BaseService):
    def __init__(self):
        super(DeveloperService,self).__init__(Developer)

class ScrumMasterService(BaseService):
    def __init__(self):
        super(ScrumMasterService,self).__init__(ScrumMaster)

class ProductOwnerService(BaseService):
    def __init__(self):
        super(ProductOwnerService,self).__init__(ProductOwner)

class ClientService(BaseService):
    def __init__(self):
        super(ClientService,self).__init__(Client)