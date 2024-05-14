#%%
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd

class HTMLParser:
    def __init__(self, html_content):
        self.html_content = html_content
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        self.data = []
        self.processed_texts = set()  # To avoid duplicates
        self.styles = self._extract_styles()
        self.body = self.soup.find('body') if self.soup.find('body') else self.soup
        self.tag_types = {
            'h1': 'header1', 'h2': 'header2', 'h3': 'header3', 'h4': 'header4', 'h5': 'header5', 'h6': 'header6', 
            'data-list-text': 'header2',
            'strong': 'strong importance', 'b': 'bold', 'em': 'emphasis', 'i': 'italic', 
            'mark': 'highlighted',
            'u': 'underline', 
            'del': 'line-through', 's': 'line-through', 'strike': 'line-through',
            'small': 'small', 'cite': 'citation', 'blockquote': 'blockquote',
            'sup': 'superscript', 'sub': 'subscript', 
            'table': 'table', 'tr': 'table row', 'td': 'table cell', 'th': 'table header', 'tbody': 'table body', 'thead': 'table head', 'tfoot': 'table foot'
        }

    def _extract_styles(self):
        """
        Extracts and returns the CSS styles from the HTML document.

        Returns:
            dict: A dictionary containing CSS styles. The keys are CSS selectors and the values are dictionaries
                  representing the CSS properties and their corresponding values.
        """
        styles = {}
        for style in self.soup.find_all("style"):
            css_text = style.string if style.string else ''
            css_rules = [rule.strip() for rule in css_text.split('}') if rule.strip()]
            for rule in css_rules:
                selector, properties_str = rule.split('{', 1)
                selector = selector.strip().lstrip('.')
                properties = {}
                for prop in properties_str.split(';'):
                    if ':' in prop.strip():
                        key, value = prop.split(':', 1)
                        properties[key.strip()] = value.strip()
                styles[selector] = properties
        return styles

    def _extract_inline_styles(self, tag_styles):
        """
        Extracts inline styles from a string of tag styles.

        Args:
            tag_styles (str): A string containing tag styles separated by semicolons.

        Returns:
            dict: A dictionary containing the extracted inline styles, where the keys are style properties and the values are the corresponding values.

        """
        inline_styles = {}
        for style in tag_styles.split(';'):
            if ':' in style.strip():
                key, value = style.split(':', 1)
                inline_styles[key.strip()] = value.strip()
        return inline_styles


    def _extract_text_with_style(self, tag, inherited_styles={}, tags=[]):
        """
        Extracts text content from HTML tags along with their associated styles.

        Args:
            tag (Tag or NavigableString): The HTML tag or string to extract text from.
            inherited_styles (dict, optional): The inherited styles from parent tags. Defaults to an empty dictionary.
            tags (list, optional): The list of tag names representing the hierarchy of the current tag. Defaults to an empty list.

        Returns:
            None

        Notes:
            - This method appends extracted text content along with associated styles to the `data` list attribute of the class.
            - The extracted information includes text content, font family, font size, font weight, text decoration, font color, and tags.
            - The `inherited_styles` parameter is used to pass the cumulative styles inherited from parent tags.
            - The `tags` parameter is used to keep track of the hierarchy of tags.

        """
        if isinstance(tag, NavigableString):
            text = tag.strip()
            if text:
                self.data.append({
                    'text_content': text,
                    'font_family': inherited_styles.get('font-family', ''),
                    'font_size': inherited_styles.get('font-size', ''),
                    'font_weight': inherited_styles.get('font-weight', ''),
                    'text_decoration': inherited_styles.get('text-decoration', ''),
                    'font_color': inherited_styles.get('color', ''),
                    'tags': ', '.join(tags)
                })
        elif isinstance(tag, Tag):
            current_styles = inherited_styles.copy()

            if tag.has_attr('class'):
                class_styles = {}
                class_list = tag['class']
                for cls in class_list:
                    if cls in self.styles:
                        class_styles.update(self.styles[cls])
                current_styles.update(class_styles)

            if tag.has_attr('style'):
                inline_styles = self._extract_inline_styles(tag['style'])
                current_styles.update(inline_styles)

            current_tags = tags + [tag.name]

            # Extract and add data-list-text content if available
            if tag.has_attr('data-list-text'):
                self.data.append({
                    'text_content': tag['data-list-text'],
                    'font_family': '',
                    'font_size': '',
                    'font_weight': '',
                    'text_decoration': '',
                    'font_color': '',
                    'tags': ', '.join(current_tags) + ', data-list-text'
                })

            for child in tag.contents:
                self._extract_text_with_style(child, current_styles, current_tags)


        
    def parse(self):
            """
            Parses the HTML body and returns a DataFrame with extracted data.
            
            Returns:
                df (pandas.DataFrame): DataFrame containing the extracted data.
            """
            
            self._extract_text_with_style(self.body)
            df = pd.DataFrame(self.data)
            
            # update tags to simplified tags
            return_tags_list = []
            for tags in df['tags']:
                
                return_tags = []    
                for t in tags.split(','):
                    return_tags.append(self.tag_types.get(t.strip(), ''))
                
                return_tags  = list(set(return_tags))
                return_tags.remove('')
                return_tags_list.append(return_tags)
            
            df['tags'] = pd.Series([', '.join(x) for x in return_tags_list])
            
            return df

    def _locate_FASB_amendment_part(self, df):
        """
        Locates the FASB amendment part in the given DataFrame.

        Args:
            df (DataFrame): The DataFrame containing the text content.

        Returns:
            tuple: A tuple containing the start index and end index of the FASB amendment part.

        Raises:
            ValueError: If there are multiple occurrences of "Amendments to the" in the text.
            IndexError: If the next text after "Amendments to the" is not "FASB Accounting Standards Codification".
        """
        start_index = df[(df['text_content'] == 'Amendments to the') & ((df['font_size'] == '20pt') | (df['font_size'] == '16pt'))].index[0]
        if len([start_index]) != 1 : # multiple index
            raise ValueError('There are multiple "Amendments to the" in the text')
            
        # check that the next text is " FASB Accounting Standards Codification®" or not
        if df.loc[start_index+1, 'text_content'] == 'FASB Accounting Standards Codification' :
            filtered_df = df[df['text_content'].str.contains('The amendments in this Update were adopted by')]
            if not filtered_df.empty:
                end_index = filtered_df.index[0]
            else:
                end_index = df.index[-1]
            df = df.loc[start_index:end_index]
            self.ammedment_df = df
        else :
            raise IndexError('The next text after "Amendments to the" is not "FASB Accounting Standards Codification"')
            
        return start_index, end_index
    
    def _create_old_new_df(self, df, version):
        """
        Create a new DataFrame based on the given version.

        Args:
            df (pandas.DataFrame): The original DataFrame.
            version (str): The version to be used for filtering the DataFrame. 
                           Acceptable values are 'old' or 'new'.

        Returns:
            pandas.DataFrame: The filtered DataFrame based on the given version.

        Raises:
            ValueError: If an invalid version is provided.

        """
        if version == 'old':
            # remove df with text_decoration = underline or tags contains underline
            output_df = df[~((df['text_decoration'].str.contains('underline', case=False)) | (df['tags'].str.contains('underline', case=False)))]
        elif version == 'new':
            # remove df with text_decoration = line-through or tags = line-through
            output_df = df[~((df['text_decoration'].str.contains('line-through', case=False)) | (df['tags'].str.contains('line-through', case=False)))]
        else:
            raise ValueError(f'Invalid version input: {version}, acceptable values are [old, new]')

        return output_df
    
    def output_parsed_text_doc(self, version, output_file = None, text_info_df=None, return_only_amendment_part=True) -> pd.DataFrame:
        """
        Outputs the parsed text to a file and returns a DataFrame containing the parsed information.

        Args:
            version (str): The version of the parsed text.
            output_file (str): The path to the output file where the parsed text will be saved.
            text_info_df (pd.DataFrame, optional): A DataFrame containing the parsed text information. If not provided, the method will parse the text.
            return_only_amendment_part (bool, optional): Whether to return only the amendment part of the parsed text. Defaults to True.

        Returns:
            pd.DataFrame: A DataFrame containing the parsed information.

        """
        if text_info_df is None:
            df = self.parse()
        else:
            df = text_info_df

        if return_only_amendment_part:
            start_index, end_index = self._locate_FASB_amendment_part(df)
            df = df.loc[start_index:end_index]

        output_df = self._create_old_new_df(df=df, version=version)

        str_list_output = output_df['text_content'].str.cat(sep='  ').split('.  ')

        if output_file:
            with open(output_file, 'w') as f:
                for line in str_list_output:
                    f.write(line + '\n')
        
        return output_df
