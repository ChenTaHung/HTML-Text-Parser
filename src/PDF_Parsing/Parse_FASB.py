#%%
import os
# TODO: change the working directory
# os.chdir('/Users/shenfengyuan/Desktop/BU-MSSP/MA676/Partner_Projects/Fidelity-Fall_2023')
os.chdir('/Users/chentahung/Desktop/MSSP/Fall2023/MA675-StatisticsPracticum-1/Partner-Project/RemoteGit')
from src.PDF_Parsing.HTMLParser.HTMLParser import HTMLParser
#%%
# Store into doc > FASB > FASB_parsed_output

for files in os.listdir('doc/FASB/FASB_2022_html'):
    print('Processing:', files)
    with open(f'doc/FASB/FASB_2022_html/{files}', 'r') as html_file:
        html_content = html_file.read()
    try:
        parser = HTMLParser(html_content)
        text_info_df = parser.parse()
        file_name = '-'.join(files.split('-')[:3])
        old_df = parser.output_parsed_text_doc('old', output_file = f'doc/FASB/FASB_parsed_output/{file_name}_old.txt', text_info_df = text_info_df)
        new_df = parser.output_parsed_text_doc('new', output_file = f'doc/FASB/FASB_parsed_output/{file_name}_new.txt', text_info_df = text_info_df)
        print('Done:', files)
    except:
        print('Error:', files)

# %%

# Unit Test: Using single file

with open('doc/FASB/FASB_html/FASB_2023_html/ASU-2023-09-740.html', 'r') as html_file:
    html_content = html_file.read()
parser = HTMLParser(html_content)
text_info_df = parser.parse()
# file_name = '-'.join(files.split('-')[:3])
# old_df = parser.output_parsed_text_doc('old', output_file = f'doc/FASB/FASB_parsed_output/{file_name}_old.txt', text_info_df = text_info_df)
# new_df = parser.output_parsed_text_doc('new', output_file = f'doc/FASB/FASB_parsed_output/{file_name}_new.txt', text_info_df = text_info_df)
# %%
