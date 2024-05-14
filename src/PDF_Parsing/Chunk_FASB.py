#%%
# Code for Vincent's Macbook Pro
# Output to txt file
import os
import pandas as pd
import glob
# os.chdir('/Users/chentahung/Desktop/MSSP/Fall2023/MA675-StatisticsPracticum-1/Partner-Project/RemoteGit')
os.chdir('/Users/shenfengyuan/Desktop/BU-MSSP/MA676/Partner_Projects/Fidelity-Fall_2023')
from src.PDF_Parsing.HTMLChunker.HTMLChunker import HTMLChunker
from src.PDF_Parsing.HTMLChunker.Score import Score
from src.PDF_Parsing.HTMLParser.HTMLParser import HTMLParser
from src.PDF_Parsing.HTMLChunker.ChunkRefiner import ChunkRefiner    
#%%
# Set cutoff score
cutoff = 6
start_year = 2019
end_year = 2024
#%%
for year in range(start_year, end_year):
    for filename in os.listdir(f'doc/FASB/FASB_html/FASB_{year}_html'):
        if filename == '.DS_Store':
            continue
        print('Processing:', filename)
        with open(f'doc/FASB/FASB_html/FASB_{year}_html/{filename}', 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()
        try:
            parser = HTMLParser(html_content)
            text_info_df = parser.parse()
            
            # # Only extract the amendment part df
            # start_i, end_i  = parser._locate_FASB_amendment_part(text_info_df)
            # amendment_df = text_info_df.loc[start_i:end_i]

            # Chunker
            chunker = HTMLChunker(text_info_df, score_dict=Score.ScoreDict)
            chunks = chunker.chunk_by_score(cutoff)
            
            # Chunk refiner
            #refiner = ChunkRefiner(chunks)
            #refined_chunks = refiner.refine(lower_bound=100, upper_bound=650, sel_metric='words')
            
            # # For each refined chunk, output to new/old version df, and output the txt of each version df
            # for c in chunks:
            #     old = parser.output_parsed_text_doc(version = 'old', text_info_df = c, return_only_amendment_part = False)
            #     new = parser.output_parsed_text_doc(version = 'new', text_info_df = c, return_only_amendment_part = False)

            #     # TXT filename for the output
            #     txt_filename_old = f'doc/FASB/FASB_chunked_output/{filename.replace(".html", "_old.txt")}'
            #     txt_filename_new = f'doc/FASB/FASB_chunked_output/{filename.replace(".html", "_new.txt")}'
                
            #     # Write old_df and new_df to txt
            #     HTMLChunker.process_and_output_to_txt(old, txt_filename_old)
            #     HTMLChunker.process_and_output_to_txt(new, txt_filename_new)

            # Create an empty DataFrame for all chunks data
            all_chunks_data = pd.DataFrame()
            
            # Process each chunk and append its data to the all_chunks_data DataFrame
            for i, chunk_df in enumerate(chunks):
                # # Add a column with the chunk number
                # chunk_df['Chunk'] = f'Chunk {i+1}'
                # Append the chunk DataFrame to the all chunks DataFrame
                all_chunks_data = pd.concat([all_chunks_data, chunk_df], ignore_index=True)
            
            # Merge the chunks based on the cutoff score
            merged_chunks = HTMLChunker.merge_chunks_by_cutoff(all_chunks_data)

            # Output the all_chunks_data DataFrame to old and new version
            old_df = parser.output_parsed_text_doc(version = 'old', text_info_df = merged_chunks, return_only_amendment_part = True)
            new_df = parser.output_parsed_text_doc(version = 'new', text_info_df = merged_chunks, return_only_amendment_part = True)

            # TXT filename for the output
            txt_filename_old = f'doc/FASB/FASB_chunked_output/{filename.replace(".html", "_old.txt")}'
            txt_filename_new = f'doc/FASB/FASB_chunked_output/{filename.replace(".html", "_new.txt")}'

            # # Write old_df and new_df to txt
            # HTMLChunker.process_and_output_to_txt(old_df, txt_filename_old)
            # HTMLChunker.process_and_output_to_txt(new_df, txt_filename_new)
            
            # Write old_df and new_df to txt
            HTMLChunker.dataframe_to_text_file(old_df, txt_filename_old)
            HTMLChunker.dataframe_to_text_file(new_df, txt_filename_new)

            print(f'Done: {filename}')
        except Exception as e:
            print(f'Error processing {filename}: {str(e)}')
#%%
# Remove certain text from the txt files
def process_files(input_directory, output_directory):
    # Fetch all txt files in the directory
    txt_file_paths = glob.glob(os.path.join(input_directory, "*.txt"))
    
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for file_path in txt_file_paths:
        file_name = os.path.basename(file_path)
        
        # Read the content of the file
        with open(file_path, "r", encoding='utf-8') as file:
            content = file.read()

        # Determine if the file is 'old' or 'new' and replace the respective text
        if 'old' in file_name:
            content = content.replace("Terms from the Master Glossary are in bold type. Added text is , and deleted text is struck out .", "")
            content = content.replace("Terms from the Master Glossary are in bold type. Added text is .", "")        
        elif 'new' in file_name:
            content = content.replace("Terms from the Master Glossary are in bold type. Added text is underlined , and deleted text is .", "")
            content = content.replace("Terms from the Master Glossary are in bold type. Added text is underlined .", "")
        
        # Write the modified content to the new file in the output directory
        output_file_path = os.path.join(output_directory, file_name)
        with open(output_file_path, "w", encoding='utf-8') as file:
            file.write(content)

# Paths to the input and output directories
input_directory = "doc/FASB/FASB_chunked_output"
output_directory = "doc/FASB/FASB_chunked_output"
process_files(input_directory, output_directory)
#%%