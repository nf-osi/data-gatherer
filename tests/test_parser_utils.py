import re
import pandas as pd
from data_gatherer.parser.base_parser import LLMParser
from data_gatherer.parser.xml_parser import XMLParser
from data_gatherer.parser.html_parser import HTMLParser
from data_gatherer.parser.pdf_parser import PDFParser
from data_gatherer.logger_setup import setup_logging
from conftest import get_test_data_path
from lxml import etree

import os
from dotenv import load_dotenv

load_dotenv()

# To see logs in the test output, configure the logger to also log to the console (StreamHandler), or set log_file=None in setup_logging.

def test_get_data_availability_elements_from_HTML(get_test_data_path):
    logger = setup_logging("test_logger", log_file="logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_extract_1.html'), 'rb') as f:
        raw_html = f.read()
    preprocessed_data = parser.normalize_HTML(raw_html)
    DAS_elements = parser.retriever.get_data_availability_elements_from_webpage(preprocessed_data)
    assert isinstance(DAS_elements, list)
    assert len(DAS_elements) == 5
    assert all(isinstance(sm, dict) for sm in DAS_elements)
    print('\n')

def test_extract_href_from_supplementary_material_html(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_extract_2.html'), 'rb') as f:
        raw_html = f.read()
    parser.publisher = "PMC"
    hrefs = parser.extract_href_from_supplementary_material(raw_html,
                                                                 "https://pmc.ncbi.nlm.nih.gov/articles/PMC8628860/")
    print(f"hrefs: \n\n{hrefs.columns}\n\n")
    for col in hrefs.columns:
        if col == 'description':
            print(f"{col}: {hrefs[col].tolist()}")

    assert isinstance(hrefs, pd.DataFrame)
    assert len(hrefs) == 58
    print('\n')

def test_extract_supplementary_material_refs_html(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_extract_2.html'), 'rb') as f:
        raw_html = f.read()
    parser.publisher = "PMC"
    hrefs = parser.extract_href_from_supplementary_material(raw_html,
                                                                 "https://pmc.ncbi.nlm.nih.gov/articles/PMC8628860/")
    metadata = parser.extract_supplementary_material_refs(raw_html, hrefs)

    expected_len_descriptions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23665, 1287, 554, 1636, 287, 0, 572, 185, 317, 481,
                                 880, 834, 341, 504, 1412, 615, 630, 440, 491, 1084, 576, 0, 0, 576, 286, 181, 2202, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33]

    len_descriptions = [len(desc) for desc in metadata['context_description'].tolist()]

    assert isinstance(metadata, pd.DataFrame)
    assert len(metadata) == 58
    assert len_descriptions == expected_len_descriptions

    print('\n')
def test_extract_href_from_supplementary_material_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_2.xml'), 'rb') as f:
        api_xml = f.read()
    parser.publisher = "PMC"
    api_xml = etree.fromstring(api_xml)
    hrefs = parser.extract_href_from_supplementary_material(api_xml,
                                                                 "https://pmc.ncbi.nlm.nih.gov/articles/PMC11129317/")
    print(f"hrefs: \n\n{hrefs.columns}\n\n")
    print(f"hrefs: \n\n{hrefs['description'].tolist()}\n\n")

    assert isinstance(hrefs, pd.DataFrame)
    assert len(hrefs) == 10
    print('\n')

def test_extract_supplementary_material_refs_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_2.xml'), 'rb') as f:
        api_xml = f.read()
    parser.publisher = "PMC"
    api_xml = etree.fromstring(api_xml)

    hrefs = parser.extract_href_from_supplementary_material(api_xml,
                                                                 "https://pmc.ncbi.nlm.nih.gov/articles/PMC11129317/")
    metadata = parser.extract_supplementary_material_refs(api_xml, hrefs)

    expected_len_descriptions = [9086, 728, 163, 389, 400, 177, 405, 209, 147, 0]

    len_descriptions = [len(desc) for desc in metadata['context_description'].tolist()]

    assert isinstance(metadata, pd.DataFrame)
    assert len(metadata) == 10
    assert len_descriptions == expected_len_descriptions

    print('\n')

def test_extract_paragraphs_from_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_1.xml'), 'rb') as f:  # ✅ open in binary mode
        xml_root = etree.fromstring(f.read())
    paragraphs = parser.extract_paragraphs_from_xml(xml_root)
    assert isinstance(paragraphs, list)
    assert len(paragraphs) > 0
    assert all(isinstance(p, dict) for p in paragraphs)
    print('\n')

def test_extract_sections_from_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_1.xml'), 'rb') as f:  # ✅ open in binary mode
        xml_root = etree.fromstring(f.read())
    section = parser.extract_sections_from_xml(xml_root)
    assert isinstance(section, list)
    assert len(section) > 0
    assert all(isinstance(s, dict) for s in section)
    print('\n')

def test_extract_sections_from_text(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = PDFParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    text = parser.extract_text_from_pdf(get_test_data_path('test_pdf_extract_1.pdf'))
    normalized_text = parser.normalize_extracted_text(text)
    sections = parser.extract_sections_from_text(normalized_text)
    assert isinstance(sections, list)
    assert len(sections) > 0 and len(sections) < 200
    assert all(isinstance(s, dict) for s in sections)
    print('\n')

def test_resolve_data_repository():
    logger = setup_logging("test_logger", log_file="../logs/scraper.log", level="INFO",
                                    clear_previous_logs=True)
    parser = XMLParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    test_cases = [
        {
            "extracted_name": "NCBI GEO",
            "target_name": "GEO",
            "extracted_id": "GSE123456"
        },
        {
            "extracted_name": "NCBI Gene Expression Omnibus (GEO)",
            "target_name": "GEO",
            "extracted_id": "GSE923456"
        }
    ]
    for obj in test_cases:
        repo, tgt, extracted_id = obj["extracted_name"], obj["target_name"], obj["extracted_id"]
        print(f"Testing URL: {repo}")
        data_repo = parser.resolve_data_repository(repo, identifier=extracted_id)
        assert isinstance(data_repo, str)
        assert data_repo.lower() == tgt.lower()
        print('\n')

def test_extract_title_from_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_1.xml'), 'rb') as f:  # ✅ open in binary mode
        xml_root = etree.fromstring(f.read())
    title = parser.extract_publication_title(xml_root)
    assert isinstance(title, str)
    assert len(title) > 0
    assert title == "Dual molecule targeting HDAC6 leads to intratumoral CD4+ cytotoxic lymphocytes recruitment through MHC-II upregulation on lung cancer cells"
    print('\n')

def test_extract_title_from_html_PMC(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_extract_1.html'), 'rb') as f:
        raw_html = f.read()
    title = parser.extract_publication_title(raw_html)
    assert isinstance(title, str)
    assert len(title) > 0
    assert "Proteogenomic insights suggest druggable pathways in endometrial carcinoma" in title
    print('\n')

def test_extract_title_from_html_nature(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('Webscraper_fetch_1.html'), 'rb') as f:
        raw_html = f.read()
    title = parser.extract_publication_title(raw_html)
    assert isinstance(title, str)
    assert "Defective N-glycosylation of IL6 induces metastasis and tyrosine kinase inhibitor resistance" in title
    print('\n')

def test_semantic_retrieve_from_corpus(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('Webscraper_fetch_1.html'), 'rb') as f:
        raw_html = f.read()
    corpus = parser.extract_sections_from_html(raw_html)
    top_k_sections = parser.semantic_retrieve_from_corpus(corpus, topk_docs_to_retrieve=3)
    accession_ids = ['GSE269782', 'GSE31210', 'GSE106765', 'GSE60189', 'GSE59239', 'GSE122005', 'GSE38121', 'GSE71587',
                     'GSE37699', 'PXD051771']
    scores = [ 0.9393497109413147, 1.3575516939163208, 1.4186346530914307]
    DAS_text = ".\n".join([item['text'] for item in top_k_sections])
    assert isinstance(top_k_sections, list)
    assert len(top_k_sections) == 3
    assert all(isinstance(res, dict) for res in top_k_sections)
    for acc_id in accession_ids:
        assert acc_id in DAS_text
    for sect_i, sect in enumerate(top_k_sections):
        assert abs(sect['L2_distance'] - scores[sect_i]) < 0.02
    print('\n')

def test_normalize_text_from_pdf(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = PDFParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    raw_text = parser.extract_text_from_pdf(get_test_data_path('test_pdf_extract_1.pdf'))
    normalized_text = parser.normalize_extracted_text(raw_text)
    assert isinstance(normalized_text, str)
    assert len(normalized_text) > 0
    assert len(normalized_text) < 178720
    assert not re.search('\nPage\s+\d+\s*', normalized_text)
    assert not re.search('\nNewpage\s+\d+\s*', normalized_text)
    print('\n')