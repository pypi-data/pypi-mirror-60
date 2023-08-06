from sspo_db.application.activity.application import *
from sspo_db.application.artifact.application import *
from sspo_db.application.core.application import *
from sspo_db.application.organization.application import *
from sspo_db.application.process.application import *
from sspo_db.application.stakeholder.application import *
import factory

# stakeholders
class PersonFactory(factory.Factory):
    class Meta:
        model = ApplicationPerson

class TeamMemberFactory(factory.Factory):
    class Meta:
        model = ApplicationTeamMember

class DeveloperFactory(factory.Factory):
    class Meta:
        model = ApplicationDeveloper

class ScrumMasterFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumMaster

class ProductOwnerFactory(factory.Factory):
    class Meta:
        model = ApplicationProductOwner

class ClientFactory(factory.Factory):
    class Meta:
        model = ApplicationClient

# Process
class ScrumProjectFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumProject

class ScrumComplexProjectFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumComplexProject

class ScrumAtomicProjectFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumAtomicProject

class ScrumProcessFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumProcess

class ProductBacklogDefinitionFactory(factory.Factory):
    class Meta:
        model = ApplicationProductBacklogDefinition

class SprintFactory(factory.Factory):
    class Meta:
        model = ApplicationSprint

class CerimonyFactory(factory.Factory):
    class Meta:
        model = ApplicationCerimony

class PlanningMeetingFactory(factory.Factory):
    class Meta:
        model = ApplicationPlanningMeeting

class DailyStandupMeetingFactory(factory.Factory):
    class Meta:
        model = ApplicationDailyStandupMeeting

class ReviewMeetingFactory(factory.Factory):
    class Meta:
        model = ApplicationReviewMeeting

class RetrospectiveMeetingFactory(factory.Factory):
    class Meta:
        model = ApplicationRetrospectiveMeeting

# Organization
class OrganizationFactory(factory.Factory):
    class Meta:
        model = ApplicationOrganization

class TeamFactory(factory.Factory):
    class Meta:
        model = ApplicationTeam

class ScrumTeamFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumTeam

class DevelopmentTeamFactory(factory.Factory):
    class Meta:
        model = ApplicationDevelopmentTeam


## Core
class ApplicationTypeFactory(factory.Factory):
    class Meta:
        model = ApplicationApplicationType

class ApplicationFactory(factory.Factory):
    class Meta:
        model = ApplicationApplication

class ConfigurationFactory(factory.Factory):
    class Meta:
        model = ApplicationConfiguration

class ApplicationReferenceFactory(factory.Factory):
    class Meta:
        model = ApplicationApplicationReference


## Artifact

class ProductBacklogFactory(factory.Factory):
    class Meta:
        model = ApplicationProductBacklog

class UserStoryFactory(factory.Factory):
    class Meta:
        model = ApplicationUserStory

class EpicFactory(factory.Factory):
    class Meta:
        model = ApplicationEpic

class AtomicUserStoryFactory(factory.Factory):
    class Meta:
        model = ApplicationAtomicUserStory

class SprintBacklogFactory(factory.Factory):
    class Meta:
        model = ApplicationSprintBacklog

class AcceptanceCriterionFactory(factory.Factory):
    class Meta:
        model = ApplicationAcceptanceCriterion

class NonFunctionalAcceptanceCriterionFactory(factory.Factory):
    class Meta:
        model = ApplicationNonFunctionalAcceptanceCriterion

class FunctionalAcceptanceCriterionFactory(factory.Factory):
    class Meta:
        model = ApplicationFunctionalAcceptanceCriterion

### Activiy ####
class ScrumDevelopmentTaskFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumDevelopmentTask

class DevelopmentTaskTypeFactory(factory.Factory):
    class Meta:
        model = ApplicationDevelopmentTaskType

class PriorityFactory(factory.Factory):
    class Meta:
        model = ApplicationPriority

class RiskFactory(factory.Factory):
    class Meta:
        model = ApplicationRisk

class ScrumIntentedDevelopmentTaskFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumIntentedDevelopmentTask

class ScrumPerformedDevelopmentTaskFactory(factory.Factory):
    class Meta:
        model = ApplicationScrumPerformedDevelopmentTask