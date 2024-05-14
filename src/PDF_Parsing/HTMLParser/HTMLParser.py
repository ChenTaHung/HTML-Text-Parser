#%%
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd

class HTMLParser:
    def __init__(self, html_content, using_url=False):
        self.html_content = html_content
        # check if html_content is a url
        if using_url:
            if 'http' in html_content and '://' in html_content and '.com' in html_content:
                import requests
                response = requests.get(html_content)
                self.html_content = response.text
        else:
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
            self.parsed_data = df
            
            return df
    
    def output_whole_text(self, output_file = None):
        """
        Returns the extracted text content from the HTML document.

        Returns:
            str: The extracted text content.
        """
        if output_file: # write text to text file
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(' '.join([row['text_content'] for _, row in self.self.parsed_data.iterrows()]))
        else:
            return ' '.join([row['text_content'] for _, row in self.self.parsed_data.iterrows()])
