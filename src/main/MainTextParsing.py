#%%
import os
os.chdir('/Users/chentahung/Desktop/git/HTML-Text-Parser')
from src.main.TextParsing.HTMLParser import HTMLParser
from src.main.TextParsing.TextChunker import TextChunker
# %%

with open('data/FASB_2022_html/ASU_2022-01.html', 'r') as html_file:
    html_content = html_file.read()
parser = HTMLParser(html_content)
text_info_df = parser.parse()
chunker = TextChunker(text_info_df)
text_info_df
# %%
"""
output_text_only = True
"""

result_chunks_list_otT = chunker.chunk_text(cutoff = 7, auto_adjust_cutoff=True)
result_chunks_list_otT[5]
# %%
"""
output_text_only = False
"""
result_chunks_list_otF = chunker.chunk_text(cutoff = 7, auto_adjust_cutoff=True, keep_text_only = False)
result_chunks_list_otF[3]
# %%
"""
output_text_only = False
refine = False
"""
result_chunks_list_otF_rF = chunker.chunk_text(cutoff = 7, keep_text_only = False, refine=False)
print(result_chunks_list_otF_rF[1])
# %%


"""
Get all the text
"""
allText = parser.get_text()
# %%
