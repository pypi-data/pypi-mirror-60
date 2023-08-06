from abc import ABC
from sqlalchemy import update
from pprint import pprint

class AbstractApplication(ABC):

    def __init__(self, service):
        self.service = service
        
    def create(self, object):
        self.service.create (object)
    
    def retrive_by_external_uuid(self, external_uuid):
        
        application_reference = self.application_application_reference.get_by_external_uuid_and_seon_entity_name(external_uuid, self.service.type)
        if application_reference:
            return self.service.get_by_uuid(application_reference.internal_uuid)
        return None
    
    def update (self, object):
        self.service.update(object)
    
    def retrive_by_name (self, name):
        return self.service.retrive_by_name(name)
    
    def get_by_uuid (self, uuid):
        return self.service.get_by_uuid(uuid)
    
