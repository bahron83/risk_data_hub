# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from optparse import make_option
from dateutil.parser import parse as parse_date

from django.core.management.base import BaseCommand, CommandError

#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from geonode.layers.models import Layer
from risks.models.user import RdhUser
from risks.models import DamageAssessment, Hazard, RiskApp
from risks.models import AnalysisType, DamageType
from risks.models import DamageTypeValue, SendaiTarget

from django.db import IntegrityError, transaction

import ConfigParser

Config = ConfigParser.ConfigParser()

RISK_APPS = [a[0] for a in RiskApp.APPS]
RISK_APP_DEFAULT = RiskApp.APP_DATA_EXTRACTION

class Command(BaseCommand):
    """
    Allows to define a new Risk Analysis along with Dymentions descriptors.

    The command needs an 'ini' file defined as follows (just an example):

        [DEFAULT]
        # optional, if not provided, data_extraction will be used 
        # (or any other provided in -r cli switch)
        app = data_extraction|cost_benefit_analysis

        # unique and less than 30 characters
        name = future_projections_Hospital

        # can be 'impact' or 'loss_impact'
        analysis_type = impact

        # must use mnemonics
        hazard_type = EQ

        # must exists on GeoNode and you have to use its native 'name'
        # **not** the title
        layer = test

        [DIM1]
        # can be 'Scenario' or 'Round Period' for now
        dymensioninfo = Scenario

        # the first one must be always the baseline; the order is important
        values =
            Hospital
            SSP1
            SSP2
            SSP3
            SSP4
            SSP5

        # can be 'x', 'y', 'z', 't', 'e'; the order is important
        #  - layer 'x' always corresponds to the XLSX sheets
        #  - layer 'y' always corresponds to the XLSX columns
        axis = x

        # corresponding attribute name of the 'layer'
        layer_attribute = dim1

        [DIM2]
        # can be 'Scenario' or 'Round Period' for now
        dymensioninfo = Round Period

        # the first one must be always the baseline; the order is important
        values =
            10
            20
            50
            100
            250
            500
            1000
            2500

        # can be 'x', 'y', 'z', 't', 'e'; the order is important
        #  - layer 'x' always corresponds to the XLSX sheets
        #  - layer 'y' always corresponds to the XLSX columns
        axis = y

        # corresponding attribute name of the 'layer'
        layer_attribute = dim2

    Example Usage:
    $> python manage.py createriskanalysis \
            -f WP6__Impact_analysis_results_future_projections_Hospital.ini
    $> python manage.py createriskanalysis \
            -f WP6__Impact_analysis_results_future_projections_Population.ini
    $> python manage.py createriskanalysis \
            -f WP6\ -\ 2050\ Scenarios\ -\ ...\ Afghanistan\ PML\ Split.ini

    """

    help = 'Creates a new Risk Analysis descriptor: \
Loss Impact and Impact Analysis Types.'


    def add_arguments(self, parser):
        parser.add_argument('-f',
                            '--descriptor-file',
                            dest='descriptor_file',
                            type=str,
                            help='Input Risk Analysis Descriptor INI File.')
        parser.add_argument('-a',
                            '--risk-app',
                            dest='risk_app',
                            default=RISK_APP_DEFAULT,
                            help="Risk application name, available: {}, default: {}. Note that app config value has precedense over cli switch.".format(', '.join(RISK_APPS), RISK_APP_DEFAULT)
                            )
        parser.add_argument('-u',
                            '--current-user',
                            dest='current_user',
                            type=str,
                            help='Current user ID.')

        return parser
    
    @transaction.atomic
    def create_relation(self, value, damage_type, damage_assessment, order, axis, layer_attribute, sendai_indicator):
        res = None
        try:
            with transaction.atomic():
                rd, created = DamageTypeValue.objects.update_or_create(
                    value=value,
                    damage_type = damage_type,
                    damage_assessment = damage_assessment,
                    order = order,
                    axis = axis,
                    layer_attribute = layer_attribute,
                    sendai_indicator=sendai_indicator
                )  
                res = rd              
        except IntegrityError:
            pass
        return res
    
    def handle(self, **options):
        descriptor_file = options.get('descriptor_file')
        user_id = options.get('current_user')

        if not descriptor_file or len(descriptor_file) == 0:
            raise CommandError("Input Risk Analysis Descriptor INI File \
'--descriptor_file' is mandatory")

        Config.read(descriptor_file)
        da_name = Config.get('DEFAULT', 'name')        
        analysis_type_name = Config.get('DEFAULT', 'analysis_type')
        hazard_type_name = Config.get('DEFAULT', 'hazard_type')
        
        assessment_date_str = Config.get('DEFAULT', 'assessment_date')
        tags = Config.get('DEFAULT', 'tags')
        try:
            app_name = Config.get('DEFAULT', 'app')
        except ConfigParser.NoOptionError:
            app_name = options['risk_app']

        try:
            assessment_date = parse_date(assessment_date_str)
        except ValueError:
            raise CommandError("Invalid date format {}".format(assessment_date_str))

        app = RiskApp.objects.get(name=app_name)

        if DamageAssessment.objects.filter(name=da_name, app=app).exists():
            raise CommandError("A Risk Analysis with name '" + da_name +
                               "' already exists on DB!")

        if not Hazard.objects.filter(mnemonic=hazard_type_name, app=app).exists():
            raise CommandError("An Hazard Type with mnemonic '" +
                               hazard_type_name+"' does not exist on DB!")

        if not AnalysisType.objects.filter(name=analysis_type_name, app=app).exists():
            raise CommandError("An Analysis Type with name '" +
                               analysis_type_name + "' does not exist on DB!")

        

        hazard = Hazard.objects.get(mnemonic=hazard_type_name, app=app)
        analysis = AnalysisType.objects.get(name=analysis_type_name, app=app)
        
        matched_user = User.objects.get(id=user_id)
        owner = RdhUser.objects.get(id=user_id)

        if not owner.region:
            raise CommandError("Current user must be assigned to a Region to upload data!")

        print ("before transaction")
        da, created = DamageAssessment.objects.update_or_create(
            owner=owner,
            name=da_name,
            app=app,            
            analysis_type = analysis,
            hazard = hazard,
            region = owner.region,            
            assessment_date = assessment_date
        ) 

        if tags:
            DamageAssessment.objects.filter(pk=da.id).update(tags=tags)

        if created:
            print ("Created Risk Analysis [%s] (%s) - %s" %
                (da_name, hazard, analysis))

            for section in Config.sections():            
                damage_type_values = ConfigSectionMap(section)

                values = list(filter(None,
                                    (x.strip() for x in
                                    damage_type_values['values'].splitlines())))

                if 'sendai_indicators' in damage_type_values:
                    sendai_indicators = list(filter(None,
                                        (x.strip() for x in
                                        damage_type_values['sendai_indicators'].splitlines())))

                dim_name = damage_type_values['damagetype']
                i = 0
                for counter, dim_value in enumerate(values):                        
                    damage_type = DamageType.objects.get(name=dim_name)  
                    sendai_target = None
                    try:
                        sendai_indicator = SendaiTarget.objects.get(code=sendai_indicators[i])
                    except:
                        sendai_indicator = None
                    rd = self.create_relation(dim_value, damage_type, da, counter, damage_type_values['axis'], damage_type_values['layer_attribute'], sendai_indicator)                       
                    if rd is not None:
                        print ("Created Risk Analysis Dym %s [%s] (%s) - axis %s" %
                        (rd.order, dim_value, dim_name, rd.axis))            
                    i += 1

        return da_name    

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

