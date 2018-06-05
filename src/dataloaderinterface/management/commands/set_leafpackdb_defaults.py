from leafpack.models import LeafPackType, Macroinvertebrate
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError


class Command(BaseCommand):

    def handle(self, *args, **options):
        leafpack_types = ['Beech', 'Birch', 'Cherry', 'Elm', 'Grasses', 'Gum', 'Maple', 'Oak', 'Pine', 'Sycamore', 'Tulip polar']

        """  [scientific_name,    common_name,     pollution_tolerance,     parent_taxon] """
        taxons = [
            ['Ephemeroptera', 'Mayflies', 3.6, None],
            ['Plecoptera', 'stoneflies', 1.0, None],
            ['Tricoptera', 'all caddisflies', 2.8, None],
            ['Hydropsychidae', 'Common netspinner caddisflies', 5.0, 'Tricoptera'],
            ['Anisoptera', 'Dragonflies', 4.0, None],
            ['Zygoptera', 'Damselflies', 7.0, None],
            ['Corydalidae', 'Hellgrammites', 3.0, None],
            ['Sialidae', 'Alderflies', 4.0, None],
            ['Coleoptera', 'Beetles', 4.6, None],
            ['Psephenidae', 'Water-penny beetles', 4.6, None],
            ['Elmidae', '', 4.6, None],
            ['Diptera', 'True flies', 6.0, None],
            ['Eristalinae', 'Rat-tailed maggot', 6.0, 'Diptera'],
            ['Athericidae', 'Watersnipe flies', 2.0, 'Diptera'],
            ['Chironomidae', 'Midges', 6.0, 'Diptera'],
            ['Simuliidae', 'Black flies', 6.0, 'Diptera'],
            ['Tipulidae', 'Crane flies', 3.0, 'Diptera'],
            ['Amphipoda', 'Scuds', 6.0, None],
            ['Isopoda', 'Aquatic sowbugs', 8.0, None],
            ['Decapoda', 'Crayfish', 5.0, None],
            ['Oligochaeta', 'Aquatic worms', 8.0, None],
            ['Hirudinea', 'Leeches', 8.0, None],
            ['Turbellaria', 'Planarians', 8.0, None],
            ['Gastropoda', 'Snails', 7.0, None],
            ['Prosobranchia', 'Right-handed/gilled snail', 7.0, 'Gastropoda'],
            ['Archaeopulmonata', 'Left-handed/lunged snail', 7.0, 'Gastropoda'],
            ['Bivalvia', 'Clam/Mussel', 8.0, None],
            ['Sphaeriidae', 'Fingernail clams', 8.0, 'Bivalvia']
        ]

        for leafpack_type in leafpack_types:
            try:
                LeafPackType.objects.create(name=leafpack_type)
            except IntegrityError:
                continue

        for taxon_data in taxons:
            self.update_or_create_taxon(*taxon_data)

    def update_or_create_taxon(self, scientific_name, common_name, pollution, family_of=None):
        try:
            bug = Macroinvertebrate.objects.get(scientific_name=scientific_name)
        except ObjectDoesNotExist:
            bug = Macroinvertebrate()

        bug.common_name = common_name
        bug.pollution_tolerance = pollution

        if family_of:
            try:
                bug.family_of = Macroinvertebrate.objects.get(scientific_name=family_of)
            except ObjectDoesNotExist:
                pass

        bug.save()

        return bug

    def create_leafpack_type(self, name):
        LeafPackType.objects.create(name=name)
