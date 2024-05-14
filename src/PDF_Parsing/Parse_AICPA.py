#%%
import os
# TODO: change the working directory
os.chdir('/Users/chentahung/Desktop/MSSP/Fall2023/MA675-StatisticsPracticum-1/Partner-Project/RemoteGit')

from src.PDF_Parsing.HTMLParser.HTMLParser import HTMLParser
#%%

with open('doc/AICPA/IPSAS 2021 html/2021-IPSASB-Handbook_ENG_Web_Secure.html', 'r') as html_file:
    AICPA2021 = html_file.read()
parser = HTMLParser(AICPA2021)
text_info_df = parser.parse()

old_df = parser.output_parsed_text_doc('old', output_file = f'doc/AICPA/AICPA_parsed_output/AICPA_2021_old.txt', text_info_df = text_info_df,  return_only_amendment_part=False)
new_df = parser.output_parsed_text_doc('new', output_file = f'doc/AICPA/AICPA_parsed_output/AICPA_2021_new.txt', text_info_df = text_info_df, return_only_amendment_part=False)

# %%

with open('doc/AICPA/IPSAS 2022 html/2022-IPSASB-Handbook_ENG_Web_Secure.html', 'r') as html_file:
    AICPA2021 = html_file.read()
parser = HTMLParser(AICPA2021)
text_info_df = parser.parse()

old_df = parser.output_parsed_text_doc('old', output_file = f'doc/AICPA/AICPA_parsed_output/AICPA_2022_old.txt', text_info_df = text_info_df, return_only_amendment_part=False)
new_df = parser.output_parsed_text_doc('new', output_file = f'doc/AICPA/AICPA_parsed_output/AICPA_2022_new.txt', text_info_df = text_info_df, return_only_amendment_part=False)

# %%
