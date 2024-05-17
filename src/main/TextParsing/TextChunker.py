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
    
    def chunk_text(self, cutoff, keep_text_only = True, refine = True, sel_metric='words', lower_bound = 100, upper_bound = 650) -> list:
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

        # if the total score is greater than or equal to the cutoff, set 'is_cutoff' to 1
        self.df['is_cutoff'] = np.where(self.df['total_score'] >= cutoff, 1, 0)
        self.df['Chunk'] = self.df['is_cutoff'].cumsum()

        # Split the DataFrame into chunks based on 'chunk' id
        chunk_list = []
        
        for _, group in self.df.groupby('Chunk'):
            chunk_list.append(group)
        
        
        if refine:
            refiner = ChunkRefiner(chunk_list)
                
            res = refiner.refine(lower_bound=lower_bound, upper_bound=upper_bound, sel_metric = sel_metric)
        else:
            res = chunk_list
            
        if keep_text_only:
            return [chunk['text_content'].str.cat(sep = ' ') for chunk in res]
        else:
            return res
    
    
    