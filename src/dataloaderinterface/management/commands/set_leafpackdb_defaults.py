from dataloaderinterface.models import SiteRegistration
from leafpack.models import LeafPackBug, LeafPackType, LeafPack, Macroinvertebrate
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        leafpack_types = ['Beech', 'Birch', 'Cherry', 'Elm', 'Grasses', 'Gum', 'Maple', 'Oak', 'Pine', 'Sycamore', 'Tulip polar']

        macroinvertebrates = {
            'Ephemeroptera': {'common_name': 'mayflies'},
            'Plecoptera': {'common_name': 'stoneflies'},
            'Tricoptera': {
                'common_name': 'all caddisflies',
                'families': {'Hydropsychidae': {'common_name': 'common netspinner caddisflies'}}
            },
            'Anisoptera': {'common_name': 'dragonflies'},
            'Zygoptera': {'common_name': 'damselflies'},
            'Corydalidae': {'common_name': 'dobsonflies, fishflies, hellgrammites'},
            'Sialidae': {'common_name': 'alderflies'},
            'Diptera': {
                'common_name': 'all true flies',
                'families': {'Athericidae': {'common_name': 'watersnipe flies'},
                             'Chironomidae': {'common_name': 'midges'},
                             'Simuliidae': {'common_name': 'black flies'},
                             'Tipulidae': {'common_name': 'crane flies'},
                             'Eristalinae': {'common_name': 'rat-tailed maggot'}}
            },
            'Coleoptera': {
                'common_name': 'all beetles',
                'families': {'Psephenidae': {'common_name': 'water-penny beetles'},
                             'Elmidae': {'common_name': 'riffle bettles'}}
            },
            'Crustacea': {
                'common_name': 'all crustaceans',
                'families': {
                    'Amphipoda': {'common_name': 'scuds'},
                    'Isopoda': {'common_name': 'aquatic sow bugs'},
                    'Decapoda': {'common_name': 'crayfish'}}
            },
            'Oligochaeta': {'common_name': 'aquatic worms'},
            'Hirudinea': {'common_name': 'leeches'},
            'Turbellaria': {'common_name': 'planarians'},
            'Gastropoda': {
                'common_name': 'all gastropods',
                'families': {
                    'Prosobranchia': {'common_name': 'Right - handed / gilled snail'},
                    'Archaeopulmonata': {'common_name': 'Left - handed / lunged snail'}}
            },
            'Bivalvia': {
                'common_name': 'all clams & mussels',
                'families': {'Sphaeriidae': {'common_name': 'fingernail clams'}}
            },
        }

        for leafpack_type in leafpack_types:
            types = LeafPackType.objects.filter(name=leafpack_type)
            if not len(types):
                self.create_leafpack_type(leafpack_type)

        for name, value in macroinvertebrates.iteritems():

            bugs = Macroinvertebrate.objects.filter(scientific_name=name)

            if len(bugs) > 0:
                bug = bugs.first()
            else:
                bug = self.create_macroinvertebrate(name, value['common_name'])

            if value.get('families', None):
                for family_name, family_value in value.get('families').iteritems():
                    self.create_macroinvertebrate(scientific_name=family_name, common_name=family_value['common_name'],
                                                  family_of=bug)

    def create_macroinvertebrate(self, scientific_name, common_name, family_of=None):
        bug = Macroinvertebrate()
        bug.scientific_name = scientific_name
        bug.common_name = common_name
        if family_of:
            bug.family_of = family_of
        bug.save()
        return bug

    def create_leafpack_type(self, name):
        LeafPackType.objects.create(name=name)
