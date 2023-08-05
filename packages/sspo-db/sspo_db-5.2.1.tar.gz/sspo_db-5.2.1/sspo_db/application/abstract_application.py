from abc import ABC
from sspo_db.application.core.application_application_reference import ApplicationApplicationReference

class AbstractApplication(ABC):

    def __init__(self, service):
        self.service = service
        self.application_application_reference = ApplicationApplicationReference()
    
    def create(self, object):
        self.service.create (object)
    
    def retrive_by_external_uuid(self, external_uuid, type):
        application_reference = self.application_application_reference.get_by_external_uuid_and_seon_entity_name(external_uuid, type)
        if application_reference:
            return self.service.get_by_uuid(application_reference.internal_uuid)
        return None
    
