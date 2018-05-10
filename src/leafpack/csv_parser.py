import csv
import os
from tempfile import mkstemp
from leafpack.models import LeafPack, LeafPackBug, LeafPackType, Macroinvertebrate
from uuid import UUID


def parse(writer, leafpack):  # writer = csv.writer(fout)
    data = {}
    lpgs = LeafPackBug.objects.filter(leaf_pack=leafpack)

    lp_fields = LeafPack._meta.get_fields()
    for field in lp_fields:
        if field.is_relation:
            continue

        field_name = " ".join(field.name.split("_"))
        field_value = getattr(leafpack, field.name, None)

        if field_value is not None:
            data[" ".join(field_name.split("_"))] = field_value

    ignore_fields = ('id', 'uuid')
    # fieldnames = [key for key in data.keys() if key not in ignore_fields]

    for field in ignore_fields:
        del data[field]

    # fd, path = mkstemp(suffix=suffix)
    # path = os.path.join(os.getcwd(), 'leafpack.csv')
    writer.writerow(['Leaf Pack Experiment Details'])
    # writer.writerow(['http://data.wikiwatershed.org/sites/SITE_CODE/{0}'.format(leafpack.uuid)])

    writer.writerow([])

    for key, value in data.iteritems():
        writer.writerow([key, value])

    writer.writerow([])

    for lpg in lpgs:
        writer.writerow([lpg.bug.common_name, str(lpg.bug_count)])
    writer.writerow([])
    writer.writerow(['Water Quality Index Values'])
    writer.writerow(['Total number of individuals found', str(leafpack.total_bug_count())])
    biotic_index = leafpack.biotic_index()
    writer.writerow(['Biotic Index', round(biotic_index, 2)])
    writer.writerow(['Water Quality Category', leafpack.water_quality(biotic_index=biotic_index)])
    writer.writerow(['Percent EPT', round(leafpack.percent_EPT(), 2)])

    # os.close(fd)
    # os.remove(path)

