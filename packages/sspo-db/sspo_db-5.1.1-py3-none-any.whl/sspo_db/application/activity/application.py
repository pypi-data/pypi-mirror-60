from sspo_db.service.activity.service import ScrumIntentedDevelopmentTaskService, RiskService, PriorityService, DevelopmentTaskTypeService
from sspo_db.application.abstract_application import AbstractApplication


class ApplicationScrumIntentedDevelopmentTask(AbstractApplication):
    
    def __init__(self):
        super().__init__(ScrumIntentedDevelopmentTaskService())
    
class ApplicationDevelopmentTaskType(AbstractApplication):

    def __init__(self):
        super().__init__(DevelopmentTaskTypeService())
    
    def retrive_by_name (self, name):
        return self.service.retrive_by_name(name)

class ApplicationPriority(AbstractApplication):

    def __init__(self):
        super().__init__(PriorityService())
    
    def retrive_by_name (self, name):
        return self.service.retrive_by_name(name)

class ApplicationRisk(AbstractApplication):

    def __init__(self):
        super().__init__(RiskService())
    
    def retrive_by_name (self, name):
        return self.service.retrive_by_name(name)