class Score:
    ScoreDict = {
        "tags_scores":{
            # Headers
            'header1': 6, 'header2': 5, 'header3': 4, 'header4': 3, 'header5': 2, 'header6': 1, 
            # text styles
            'bold': 2, 'strong importance': 2, 'italic': 0, 'emphasis': 1, 
            # other styles
            'highlighted': 0, 
            'underline': 0,
            'line-through':0,
            # other notations of text
            'small' : 0, 'citation': 0, 'blockquote': 0,
            'superscript': 0, 'subscript': 0,
            # table elements
            'table': 0, 'table row': 0, 'table cell': 0, 'table header': 0, 'table body': 0, 'table head': 0, 'table foot': 0,
            
        }, 
        "font_size_scores":{
            '6pt': 0,
            '6.5pt': 0,
            '7pt': 0,
            '9pt': 1,
            '9.5pt': 1,
            '10pt': 2,
            '10.5pt': 2,
            '11pt': 2,
            '11.5pt': 3,
            '12pt': 4,
            '12.5pt': 5,
            '13pt': 7,
            '14pt': 6,
            '15pt': 7,
            '16pt': 8,
            '18pt': 9,
            '20pt': 10
        },
        "text_decoration_scores":{
            'underline': 1, 'none': 0
        },
        "font_weight_scores":{
            'bold': 1, 'normal': 0
        }
    }   
        
