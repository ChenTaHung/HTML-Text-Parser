import pandas as pd
from .Score import Score

class TextChunker:
    def __init__(self, df, score_dict=Score.ScoreDict):
        self.df = df
        # cols: 'text_content', 'font_family', 'font_size', 'font_weight', 'text_decoration', 'font_color', 'tags'
        
        # Define the scoring system for different tags
        self.tags_scores = score_dict.get('tags_scores', {})
        # Define the scoring system for different font sizes
        self.font_size_scores = score_dict.get('font_size_scores', {})
        # Define the scoring system for different text decorations
        self.text_decoration_scores = score_dict.get('text_decoration_scores', {})
        #  Define the scoring system for different font weights
        self.font_weight_scores = score_dict.get('font_weight_scores', {})

    def _calculate_score(self, tags, font_size, text_decoration, font_weight):
        """
        Calculates the score for a given set of tags, font size, text decoration, and font weight.

        Parameters:
        - tags (str): A comma-separated string of tags.
        - font_size (str): The font size.
        - text_decoration (str): The text decoration.
        - font_weight (str): The font weight.

        Returns:
        - score (int): The calculated score based on the tags, font size, text decoration, and font weight.
        """
        # Starting with tag-based scores
        score = sum(self.tags_scores.get(tag.strip(), 0) for tag in tags.split(','))
        # Adding font size scores
        score += self.font_size_scores.get(font_size, 0)
        # Adding text decoration scores
        score += self.text_decoration_scores.get(text_decoration, 0)
        # Adding font weight scores
        score += self.font_weight_scores.get(font_weight, 0)
        return score
    
    def chunk_by_score(self, cutoff) -> list:
        """
        Chunk the DataFrame rows based on a cutoff score and add 'is_cutoff' column.

        Args:
            cutoff (float): The cutoff score. Rows with a total_score greater than or equal to the cutoff will be considered as a new chunk and marked with 'is_cutoff' = 1.

        Returns:
            list: A list of DataFrames, where each DataFrame represents a chunk of rows with an 'is_cutoff' column indicating the start of a new chunk.
        """
        # Calculate the total score for each row
        self.df['total_score'] = self.df.apply(
            lambda row: self._calculate_score(
                row['tags'], str(row['font_size']), row['text_decoration'], row['font_weight']
            ), axis=1
        )

        # Add 'is_cutoff' column with default value 0
        self.df['is_cutoff'] = 0

        # Update 'is_cutoff' based on the 'total_score' and cutoff
        self.df.loc[self.df['total_score'] >= cutoff, 'is_cutoff'] = 1

        # List to store chunks
        chunks = []
        # Temporary list to store current chunk rows
        current_chunk = []
        # Flag to indicate whether we are within a valid chunk (based on cutoff)
        in_chunk = False

        for _, row in self.df.iterrows():
            if row['total_score'] >= cutoff:
                # Found a new chunk start
                if in_chunk:
                    # If we were already in a chunk, save it before starting a new one
                    chunks.append(pd.DataFrame(current_chunk))
                    current_chunk = []  # Reset for the new chunk
                in_chunk = True  # Mark that we are now in a chunk

            if in_chunk:
                # Add rows to the current chunk
                current_chunk.append(row)

        # Save the last chunk if it exists
        if current_chunk:
            chunks.append(pd.DataFrame(current_chunk))

        return chunks
    
    # Function to write DataFrame to txt
    @staticmethod
    def process_and_output_to_txt(df, output_filename) -> None:
        """
        Process the DataFrame and output the chunks to a text file based on 'is_cutoff' column.

        Args:
            df (pandas.DataFrame): The DataFrame containing the chunks.
            output_filename (str): The name of the output text file.

        Returns: 
            None
        """
        with open(output_filename, 'w', encoding='utf-8') as file:
            current_chunk_text = []
            current_chunk_number = 1
            previous_is_cutoff = None

            for index, row in df.iterrows():
                if row['is_cutoff'] == 1:
                    # If it's the first row or if the previous row's is_cutoff was 0, start a new chunk
                    if previous_is_cutoff is None or previous_is_cutoff == 0:
                        # Write the current chunk before starting a new one
                        if current_chunk_text:
                            file.write(f"Chunk {current_chunk_number}\n")
                            file.write(' '.join(current_chunk_text) + '\n\n')  # Add empty line between chunks
                            current_chunk_number += 1  # Prepare the chunk number for the next chunk
                            current_chunk_text = []  # Reset the text for the new chunk
                        
                    # Add the text to the current chunk
                    current_chunk_text.append(row['text_content'])
                    
                else:
                    # If is_cutoff is 0, simply continue adding text to the current chunk
                    current_chunk_text.append(row['text_content'])
                
                # Update the previous_is_cutoff
                previous_is_cutoff = row['is_cutoff']

            # Write out the last chunk
            if current_chunk_text:
                file.write(f"Chunk {current_chunk_number}\n")
                file.write(' '.join(current_chunk_text) + '\n')

    # Function to merge chunks based on cutoff
    @staticmethod
    def merge_chunks_by_cutoff(df) -> pd.DataFrame:
        """
        Merges rows into chunks based on 'is_cutoff' value and assigns a chunk number.

        Args:
            df (pandas.DataFrame): The DataFrame to process.
            cutoff (int): The cutoff flag value that triggers a new chunk.

        Returns:
            pandas.DataFrame: The DataFrame with merged text content and chunk numbers.
        """
        current_chunk_number = 1
        previous_is_cutoff = None
        df['Chunk'] = current_chunk_number  # Initialize the 'Chunk' column

        for index, row in df.iterrows():
            # If it's the first row or if the previous row's 'is_cutoff' was 0, start a new chunk
            if row['is_cutoff'] == 1 and (previous_is_cutoff is None or previous_is_cutoff == 0):
                if index != 0:  # Avoid incrementing the chunk number for the first row
                    current_chunk_number += 1  # Increment chunk number
            df.at[index, 'Chunk'] = current_chunk_number  # Assign the current chunk number
            previous_is_cutoff = row['is_cutoff']  # Update the previous_is_cutoff

        return df
    
    # Function to write DataFrame to txt
    @staticmethod
    def dataframe_to_text_file(df, output_filename) -> None:
        """
        Writes a DataFrame to a text file, with each chunk separated by a newline.

        Args:
            df (pandas.DataFrame): The DataFrame containing the chunks with a 'Chunk' column.
            output_filename (str): The name of the output text file.
        """
        with open(output_filename, 'w', encoding='utf-8') as file:
            for chunk_id, chunk_group in df.groupby('Chunk'):
                file.write(f"Chunk {chunk_id}\n")
                chunk_text = ' '.join(chunk_group['text_content'].astype(str))
                file.write(chunk_text + '\n\n')  # Add empty line between chunks