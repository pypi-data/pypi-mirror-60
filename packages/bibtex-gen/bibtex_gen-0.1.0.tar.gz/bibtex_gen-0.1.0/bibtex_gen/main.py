from typing import List, Dict, Sequence, Optional
from mendeley2 import Mendeley
from mendeley2.auth import MendeleySession
from pyexlatex.models.references.bibtex.base import BibTexEntryBase
from pyexlatex.texparser.references.bibtex.extract import extract_bibtex_str
from bibtex_gen.mendeley import bib_tex_from_mendeley_doc


class BibTexGenerator:

    def __init__(self, mendeley_client_id: str, mendeley_client_secret: str):
        mendeley = Mendeley(mendeley_client_id, mendeley_client_secret)
        self.session = mendeley.start_client_credentials_flow().authenticate()

    def generate(self, doi: str, item_accessor: str) -> BibTexEntryBase:
        return bib_tex_from_doi(self.session, doi, item_accessor)


def _item_accessor_doi_dict_to_bib_tex(item_doi_dict: Dict[str, str], mendeley_client_id: str,
                                       mendeley_client_secret: str) -> List[BibTexEntryBase]:
    btg = BibTexGenerator(
        mendeley_client_id,
        mendeley_client_secret
    )
    bib_texs = [btg.generate(doi, item_accessor) for item_accessor, doi in item_doi_dict.items()]
    return bib_texs


def bib_tex_from_doi(mendeley_session: MendeleySession, doi: str, item_accessor: str) -> BibTexEntryBase:
    mendeley_doc = mendeley_session.catalog.by_identifier(doi=doi, view='bib')
    return bib_tex_from_mendeley_doc(mendeley_doc, item_accessor)


def item_accessor_doi_dict_to_bib_tex(item_doi_dict: Dict[str, str], mendeley_client_id: str,
                                      mendeley_client_secret: str,
                                      extra_bibtex_objs: Optional[Sequence[BibTexEntryBase]] = None,
                                      extract_from_str: Optional[str] = None
                                      ) -> List[BibTexEntryBase]:
    bib_texs = _item_accessor_doi_dict_to_bib_tex(
        item_doi_dict,
        mendeley_client_id,
        mendeley_client_secret
    )
    if extra_bibtex_objs:
        bib_texs.extend(extra_bibtex_objs)
    if extract_from_str:
        bib_texs.extend(extract_bibtex_str(extract_from_str))
    return bib_texs
