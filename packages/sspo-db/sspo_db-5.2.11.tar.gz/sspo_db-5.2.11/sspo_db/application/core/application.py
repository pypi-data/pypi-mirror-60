from sspo_db.model.core.models import ApplicationReference
from sspo_db.service.core.service import ApplicationReferenceService, ApplicationService
from sspo_db.application.abstract_application import AbstractApplication

class ApplicationApplicationReference(AbstractApplication):
    
    def __init__(self):
        super().__init__(ApplicationReferenceService())
        
    #name, description, application, external_id, external_type_entity, external_url,internal_uuid, entity_name 
    
    '''
    application_reference = ApplicationReference()
        application_reference.name = entity_name+ " - "+name
        application_reference.description = description
        application_reference.application = application.id
        application_reference.external_id = external_id
        application_reference.external_url = external_url
        application_reference.external_type_entity = external_type_entity
        application_reference.internal_uuid = internal_uuid
        application_reference.entity_name = entity_name

    '''
    
    def get_by_external_uuid(self,external_id):
        return self.service.retrive_by_external_id(external_id)

    def get_by_external_uuid_and_seon_entity_name(self,external_id,seon_entity_name):
        return self.service.retrive_by_external_id_and_seon_entity_name(external_id, seon_entity_name)
                    
                    