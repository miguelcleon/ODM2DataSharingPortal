from dataloaderinterface.models import SiteRegistration
from leafpack.models import LeafPackBug, LeafPackType, LeafPack, Macroinvertebrate
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):

    def handle(self, *args, **options):
        leafpack_types = ['Beech', 'Birch', 'Cherry', 'Elm', 'Grasses', 'Gum', 'Maple', 'Oak', 'Pine', 'Sycamore', 'Tulip polar']

        macroinvertebrates = {
            'Ephemeroptera': {'common_name': 'mayflies', 'pollution_tolerance': 3.6},
            'Plecoptera': {'common_name': 'stoneflies', 'pollution_tolerance': 1.0},
            'Tricoptera': {
                'common_name': 'all caddisflies', 'pollution_tolerance': 2.8,
                'families': {'Hydropsychidae': {'common_name': 'common netspinner caddisflies', 'pollution_tolerance': 5.0}}
            },
            'Anisoptera': {'common_name': 'dragonflies', 'pollution_tolerance': 4.0},
            'Zygoptera': {'common_name': 'damselflies', 'pollution_tolerance': 7.0},
            'Megaloptera': {
                'common_name': 'alderly, dobsonfly, fishfly', 'pollution_tolerance': 4.0,
                'families': {
                    'Corydalidae': {
                        'common_name': 'Dobsonfly/Fishfly', 'pollution_tolerance': 3.0
                    },
                    'Sialidae': {
                        'common_name': 'Alderfly', 'pollution_tolerance': 4.0
                    }
                }
            },
            'Diptera': {
                'common_name': 'all true flies', 'pollution_tolerance': 6.0,
                'families': {'Athericidae': {'common_name': 'watersnipe flies', 'pollution_tolerance': 2.0},
                             'Chironomidae': {'common_name': 'midges', 'pollution_tolerance': 6.0},
                             'Simuliidae': {'common_name': 'black flies', 'pollution_tolerance': 6.0},
                             'Tipulidae': {'common_name': 'crane flies', 'pollution_tolerance': 3.0}}
            },
            'Coleoptera': {
                'common_name': 'all beetles', 'pollution_tolerance': 4.6,
                'families': {'Psephenidae': {'common_name': 'water-penny beetles', 'pollution_tolerance': 4.6},
                             'Elmidae': {'common_name': 'riffle bettles', 'pollution_tolerance': 4.6}}
            },
            'Amphipoda': {'common_name': 'Scud', 'pollution_tolerance': 6.0},
            'Isopoda': {'common_name': 'aquatic sow bugs', 'pollution_tolerance': 8.0},
            'Decapoda': {'common_name': 'crayfish', 'pollution_tolerance': 5.0},
            'Oligochaeta': {'common_name': 'aquatic worms', 'pollution_tolerance': 8.0},
            'Hirudinea': {'common_name': 'leeches', 'pollution_tolerance': 8.0},
            'Turbellaria': {'common_name': 'planarians', 'pollution_tolerance': 8.0},
            'Gastropoda': {
                'common_name': 'all gastropods', 'pollution_tolerance': 7.0,
                'families': {
                    'Prosobranchia': {'common_name': 'Right - handed / gilled snail', 'pollution_tolerance': 7.0},
                    'Archaeopulmonata': {'common_name': 'Left - handed / lunged snail', 'pollution_tolerance': 7.0}}
            },
            'Bivalvia': {'common_name': 'all clams & mussels', 'pollution_tolerance': 8.0},
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
                bug = self.create_macroinvertebrate(name, value['common_name'], value['pollution_tolerance'])

            if value.get('families', None):
                for family_name, family_value in value.get('families').iteritems():
                    self.create_macroinvertebrate(family_name, family_value['common_name'],
                                                  family_value['pollution_tolerance'], family_of=bug)

    def create_macroinvertebrate(self, scientific_name, common_name, pollution, family_of=None):
        try:
            bug = Macroinvertebrate.objects.get(scientific_name=scientific_name, common_name=common_name)
        except ObjectDoesNotExist:
            bug = Macroinvertebrate()
        bug.scientific_name = scientific_name
        bug.common_name = common_name
        bug.pollution_tolerance = pollution
        if family_of:
            bug.family_of = family_of
        bug.save()
        return bug

    def create_leafpack_type(self, name):
        LeafPackType.objects.create(name=name)
