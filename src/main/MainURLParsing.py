#%%
import os
os.chdir('/Users/chentahung/Desktop/git/HTML-Text-Parser')
from src.main.TextParsing.HTMLParser import HTMLParser
from src.main.TextParsing.TextChunker import TextChunker
# %%
"""
Using URL
"""

parser = HTMLParser('https://medium.com/@eldatero/web-scraping-with-chatgpt-code-interpreter-using-only-01-prompt-step-by-step-tutorial-cd6b2fb06c90', using_url=True)
text_info_df = parser.parse()
chunker = TextChunker(text_info_df)
text_info_df
#%%
"""
output_text_only = True
"""

result_chunks_list_otT = chunker.chunk_text(cutoff = 7)
result_chunks_list_otT[1]
# %%
"""
output_text_only = False
"""
result_chunks_list_otF = chunker.chunk_text(cutoff = 7, keep_text_only = False)
result_chunks_list_otF[2]
# %%
"""
output_text_only = False
refine = False
"""
result_chunks_list_otF_rF = chunker.chunk_text(cutoff = 7, keep_text_only = False, refine=False)
result_chunks_list_otF_rF[8]
# %%

# %%
