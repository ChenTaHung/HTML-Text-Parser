import pandas as pd
import numpy as np
from .Score import Score
from .ChunkRefiner import ChunkRefiner
import regex as re

class TextChunker:
    def __init__(self, df, score_dict=Score.ScoreDict):
        self.df = df
        # cols: 'text_content', 'font_family', 'font_size', 'font_weight', 'text_decoration', 'font_color', 'tags'
        
        # Define the scoring system for different tags
        self.tags_scores = score_dict.get('tags_scores', {})
        # Define the scoring system for different font sizes
        self.font_size_scores = score_dict.get('font_size_scores', {})
        self.font_size_bins = score_dict.get('font_size_bins', [])
        self.font_size_labels = score_dict.get('font_size_labels', [])
        # Define the scoring system for different text decorations
        self.text_decoration_scores = score_dict.get('text_decoration_scores', {})
        #  Define the scoring system for different font weights
        self.font_weight_scores = score_dict.get('font_weight_scores', {})

    def _assign_font_size_label(self, font_size):
        """
        Assigns a label to a given font size based on the font size bins.

        Parameters:
        - font_size (str): The font size extract from the parsed text dataframe.

        Returns:
        - label (str): The label assigned to the font size.
        """
        if font_size == '':
            return ''
        else:
            if 'pt' in font_size:
                font_size = float(font_size.replace('pt', ''))
            elif 'px' in font_size:
                font_size = float(font_size.replace('px', '')) * 0.75
            else:
                digit_part = re.sub(r'[^\d.]', '', font_size)
                if digit_part == '':
                    return ''
                else:
                    font_size = float(digit_part) # remove all non-numeric characters
            
            # values that exceed the value range, use the smallest or the largest label instead
            if font_size <= self.font_size_bins[0]:
                return self.font_size_labels[0]
            if font_size >= self.font_size_bins[-1]:
                return self.font_size_labels[-1]
            
            
            for i in range(len(self.font_size_bins)):
                # match the label with the smaller value of the bin
                if font_size >= self.font_size_bins[i-1] and font_size < self.font_size_bins[i] :
                    return self.font_size_labels[i-1]
            

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
        score = 0
        # Starting with tag-based scores
        score += sum(self.tags_scores.get(tag.strip(), 0) for tag in tags.split(','))
        # Adding font size scores
        score += self.font_size_scores.get(self._assign_font_size_label(font_size), 0)
        # Adding text decoration scores
        score += sum(self.text_decoration_scores.get(decoration.strip(), 0) for decoration in text_decoration.split(','))
        # Adding font weight scores
        score += sum(self.font_weight_scores.get(weight.strip(), 0)  for weight in font_weight.split(','))
        
        return score
    
    def chunk_text(self, cutoff = 7, auto_adjust_cutoff=False, keep_text_only=True, refine=True, sel_metric='words', lower_bound=100, upper_bound=650) -> list:
        """
        Chunk the text based on specified criteria.

        Parameters:
        - cutoff (int): The cutoff value for determining whether a row should be included in a chunk. Defaults to 7.
        - auto_adjust_cutoff (bool, optional): Whether to automatically adjust the cutoff value. Defaults to False.
        - keep_text_only (bool, optional): Whether to return only the concatenated text content of each chunk. Defaults to True.
        - refine (bool, optional): Whether to refine the chunks based on the selected metric. Defaults to True.
        - sel_metric (str, optional): The metric used for refining the chunks. Defaults to 'words'.
        - lower_bound (int, optional): The lower bound for the refined chunk size. Defaults to 100.
        - upper_bound (int, optional): The upper bound for the refined chunk size. Defaults to 650.

        Returns:
            list: A list of chunks, either as concatenated text content or as DataFrames.

        """
        # Calculate the total score for each row
        self.df['total_score'] = self.df.apply(
            lambda row: self._calculate_score(
                row['tags'], str(row['font_size']), row['text_decoration'], row['font_weight']
            ), axis=1
        )

        # if the total score is greater than or equal to the cutoff, set 'is_cutoff' to 1
        if auto_adjust_cutoff:
            # On average the title and subtitle contains 6% of the contents
            # cutoff set as quantile 94% of the total score
            cut_off = int(self.df['total_score'].quantile(0.94))
        else:
            cut_off = cutoff

        # cut_off new defined variable to avoid conflict with the cutoff parameter
        self.df['is_cutoff'] = np.where(self.df['total_score'] >= cut_off, 1, 0)
        self.df['Chunk'] = self.df['is_cutoff'].cumsum()

        # Split the DataFrame into chunks based on 'chunk' id
        chunk_list = []

        for _, group in self.df.groupby('Chunk'):
            chunk_list.append(group)

        # Refine the chunks based on the selected metric
        if refine:
            refiner = ChunkRefiner(chunk_list)

            res = refiner.refine(lower_bound=lower_bound, upper_bound=upper_bound, sel_metric=sel_metric)
        else:
            res = chunk_list

        if keep_text_only:
            # Return the chunks as a list of concatenated text content
            return [chunk['text_content'].str.cat(sep=' ') for chunk in res]
        else:
            # Return the chunks as a list of DataFrames
            return res
    
    
    