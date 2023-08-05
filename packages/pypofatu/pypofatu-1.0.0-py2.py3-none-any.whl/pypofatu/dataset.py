import sqlite3
import itertools
import contextlib
import collections

import attr
from clldutils.apilib import API
from clldutils.source import Source
from csvw.dsv import reader, UnicodeWriter
import xlrd
from pybtex.database import parse_file

from pypofatu.models import *  # noqa: F403
from pypofatu import util
from pypofatu import errata

SD_VALUE_SUFFIX = ' SD value'
SD_SIGMA_SUFFIX = ' SD sigma'
SHEETS = collections.OrderedDict([(n.split()[0], n) for n in [
    '1 Data source',
    '2 Sample metadata',
    '3 Compositional data',
    '4 Methodological metadata',
    '5 Vocabularies',
]])


@contextlib.contextmanager
def dbcursor(fname):
    conn = sqlite3.connect(str(fname))
    try:
        yield conn.cursor()
    finally:
        conn.rollback()


class Pofatu(API):
    def __init__(self, repos):
        super().__init__(repos)
        self.raw_dir = self.repos / 'raw'
        self.csv_dir = self.repos / 'csv'
        self.dist_dir = self.repos / 'dist'
        self.db_path = self.dist_dir / 'pofatu.sqlite'

    def query(self, sql):
        with dbcursor(self.db_path) as cu:
            cu.execute(sql)
            return cu

    @staticmethod
    def clean_bib_key(s):
        key = s.replace('{', '').replace('}', '')
        return errata.KEYS_IN_BIB.get(key, key)

    def fname_for_sheet(self, sheetname):
        for number, name in SHEETS.items():
            if sheetname[0] == number:
                return '{0}.csv'.format(name.replace(' ', '_'))
        else:
            raise ValueError(sheetname)

    def dump_sheets(self, fname=None):
        wb = xlrd.open_workbook(fname or str(self.raw_dir / 'pofatu.xlsx'))
        for name in wb.sheet_names():
            sheet = wb.sheet_by_name(name)
            with UnicodeWriter(self.csv_dir / self.fname_for_sheet(name)) as writer:
                for i in range(sheet.nrows):
                    row = [sheet.cell(i, j).value for j in range(sheet.ncols)]
                    if len(set(row)) == 1:
                        assert row.pop() in ('', '*')
                        continue
                    writer.writerow([s.strip() if isinstance(s, str) else s for s in row])

    def iterbib(self):
        for entry in parse_file(
                str(self.raw_dir / 'pofatu-references.bib'), bib_format='bibtex').entries.values():
            yield Source.from_entry(self.clean_bib_key(entry.fields['annotation']), entry)

    def iterrows(self, number_or_name):
        """
        Pofatu sheets are of the form

        Title
        First-level header
        Second-level header
        data rows
        ...
        """
        csv_path = self.csv_dir / self.fname_for_sheet(number_or_name)
        if not csv_path.exists():
            self.dump_sheets()

        head = [None, None]
        for i, row in enumerate(reader(csv_path)):
            row = [None if c == 'NA' else c for c in row]
            if i == 1:
                head[0] = row
            if i == 2:
                head[1] = row
            elif i >= 3:
                yield util.Row(i, head, row)

    def itermethods(self):
        for key, rows in itertools.groupby(
            sorted(self.iterrows('4'), key=lambda r: r.values[:2]),
            lambda r: r.values[:2],
        ):
            for k, row in enumerate(rows):
                if k == 0:
                    m = Method(*(row.values[:8] + row.values[13:17]))
                assert attr.astuple(m)[8:12] == tuple(row.values[13:17])
                m.references.append(MethodReference(
                    sample_name=row.values[8],
                    sample_measured_value=row.values[9],
                    uncertainty=row.values[10],
                    uncertainty_unit=row.values[11],
                    number_of_measurements=row.values[12],
                ))
            yield m

    def itercontributions(self):
        for cid, rows in itertools.groupby(
                sorted(self.iterrows('1'), key=lambda r: r.values[0]), lambda r: r.values[0]):
            kw = {'id': cid, 'source_ids': set()}
            for row in rows:
                row = row.values
                kw['source_ids'].add(row[7])
                for i, key in [
                    (1, 'name'),
                    (2, 'description'),
                    (3, 'authors'),
                    (4, 'affiliation'),
                    (5, 'contributors'),
                    (6, 'contact_email'),
                ]:
                    if row[i]:
                        assert (key not in kw) or (kw[key] == row[i])
                        kw[key] = row[i]
            yield Contribution(**kw)

    def iter_compositional_data(self):
        """
        return a `dict`, grouping anlyses of samples by sample id
        """
        # Note: We already sort by Method ID, too, since we want to group by it in _iter_merged!
        for sample_id, rows in itertools.groupby(
            sorted(self.iterrows('3'), key=lambda r_: (r_.values[1], r_.values[2])),
            lambda r_: r_.values[1]
        ):
            rows = list(rows)
            assert len(set(r.values[2] for r in rows)) == len(rows), \
                'multiple measurements with same method ID'
            yield errata.SAMPLE_IDS.get(sample_id, sample_id), rows

    def itersamples(self):
        sids = {}
        for r in self.iterrows('2'):
            d = r.dict
            if d['Sample ID'] in sids:
                assert sids[d['Sample ID']] == r.values, 'different samples with same ID'
                # Ignore true duplicates.
                continue
            sids[d['Sample ID']] = r.values
            yield Sample(
                id=d['Sample ID'],
                category=d['Sample category'],
                comment=d['Sample comment'],
                location=Location(
                    loc1=d['Location 1'],
                    loc2=d['Location 2'],
                    loc3=d['Location 3'],
                    comment=d['Location comment'],
                    latitude=d['Latitude'],
                    longitude=d['Longitude'],
                    elevation=d['Elevation'],
                ),
                petrography=d['Petrography'],
                source_id=d['Source ID 1'],
                analyzed_material_1=d['Analyzed material 1'],
                analyzed_material_2=d['Analyzed material 2'],
                artefact=Artefact(
                    id=d['Artefact ID'],
                    name=d['Artefact name'],
                    category=d['Artefact category'],
                    attributes=d['Artefact attributes'],
                    comment=d['Artefact comments'],
                    source_ids=d['Source ID 2'],
                    collector=d['Collector'],
                    collection_type=d['Fieldwork'],
                    fieldwork_date=d['Fieldwork date'],
                    collection_location=d['Collection storage location'],
                    collection_comment=d['Collection comment'],
                ),
                site=Site(
                    name=d['Site name'],
                    code=d['Site code'],
                    context=d['Site context'],  # sample sepcific
                    comment=d['Site comments'],  # sample sepcific
                    stratigraphic_position=d['Stratigraphic position'],  # sample sepcific
                    stratigraphy_comment=d['Stratigraphy comments'],
                    source_ids=d['Source ID 3'],
                ),
            )

    def iterdata(self):
        params = None
        cd = collections.OrderedDict(self.iter_compositional_data())
        methods = {(m.code, m.parameter): m for m in self.itermethods()}
        aids = {}

        for sample in self.itersamples():
            rows = cd[sample.id]
            if not params:
                params, in_params = collections.OrderedDict(), False
                for j, (name, unit) in enumerate(list(zip(*rows[0].keys))):
                    if in_params:
                        param = name
                        if unit:
                            param += ' [{0}]'.format(unit)
                        assert param not in params, 'duplicate parameter'
                        assert param
                        params[param] = j
                    if name == 'PARAMETER':
                        # The Level-1 header "PARAMETER" signals the start of measurements.
                        in_params = True

            for k, row in enumerate(rows):
                d = row.dict
                analysis = Analysis('{0}-{1}'.format(sample.id, d['Method ID']), sample=sample)
                assert analysis.id not in aids, 'duplicate analysis id'
                aids[analysis.id] = row.values
                for p, j in params.items():
                    if p.endswith(SD_VALUE_SUFFIX) or p.endswith(SD_SIGMA_SUFFIX):
                        continue
                    v, less = util.parse_value(row.values[j])
                    if v is not None:
                        sd_value_key = '{0}{1}'.format(p, SD_VALUE_SUFFIX)
                        sd_sigma_key = '{0}{1}'.format(p, SD_SIGMA_SUFFIX)
                        m = methods.get((d['Method ID'], p.split()[0]))
                        analysis.measurements.append(Measurement(
                            parameter=p,
                            method=m,
                            value=v,
                            less=less,
                            precision=row.values[params[sd_value_key]]
                            if sd_value_key in params else None,
                            sigma=row.values[params[sd_sigma_key]]
                            if sd_sigma_key in params else None,
                        ))
                yield analysis

    @util.callcount
    def log_or_raise(self, log, msg):
        if log:
            log.warning(msg)
        else:
            raise ValueError(msg)

    def validate(self, log=None, bib=None):
        from tqdm import tqdm

        missed_methods = collections.Counter()
        bib = bib if bib is not None else {rec.id: rec for rec in self.iterbib()}

        aids = set()
        for dp in tqdm(self.iterdata()):
            assert dp.id not in aids, dp.id
            aids.add(dp.id)
            for m in dp.measurements:
                missed_methods.update([not m.method])
            if dp.sample.source_id not in bib:
                self.log_or_raise(
                    log, '{0}: sample source missing in bib'.format(dp.sample.source_id))
            for sid in dp.sample.artefact.source_ids:
                if sid not in bib:
                    self.log_or_raise(log, '{0}: artefact source missing in bib'.format(sid))
            for sid in dp.sample.site.source_ids:
                if sid not in bib:
                    self.log_or_raise(log, '{0}: artefact source missing in bib'.format(sid))

        all_sources = set()
        for contrib in self.itercontributions():
            if bib and contrib.id not in bib:
                self.log_or_raise(log, 'Missing source in bib: {0}'.format(contrib.id))
            # We relate samples to contributions by matching Sample.source_id with
            # Contribution.source_ids. Thus, the latter must be disjoint sets!
            assert not all_sources.intersection(contrib.source_ids)
            all_sources = all_sources | set(contrib.source_ids)

        if missed_methods[True]:
            self.log_or_raise(log, 'Missing methods: {0} of {1} measurements'.format(
                missed_methods[True], missed_methods[False]))
        return self.log_or_raise.callcount
