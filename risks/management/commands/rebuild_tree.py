import traceback

from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from risks.models import Region, AdministrativeDivision, Event, RiskAnalysis
from risks.models import HazardType, RiskApp
from risks.models import RiskAnalysisDymensionInfoAssociation
from risks.models import RiskAnalysisAdministrativeDivisionAssociation
from risks.models import EventAdministrativeDivisionAssociation


class Command(BaseCommand):
    help = 'Rebuild tree for selected table.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--commit',
            action='store_true',
            dest='commit',
            default=True,
            help='Commits Changes to the storage.')
        parser.add_argument(
            '-m',
            '--model',
            dest='model',
            type=str,
            help='Destination Model')        
        return parser

    def handle(self, **options):
        commit = options.get('commit')
        model = options.get('model')

        models_available = ['AdministrativeDivision']
        
        if model in models_available:
            print("Start rebuilding {}...".format(model))
            if model == 'AdministrativeDivision':
                AdministrativeDivision.objects.rebuild()
            print("Finished rebuilding {}!".format(model))
        
    