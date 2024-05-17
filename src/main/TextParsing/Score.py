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
        # Font size scoring using bins with the following ranges:
        "font_size_scores":{
            '':0, # No specified font size
            '6pt': 0,
            '8pt': 0.5,
            '9pt': 1,
            '10pt': 2,
            '11pt': 2.5,
            '12pt': 4,
            '13pt': 7,
            '15pt': 7.5,
            '16pt': 8,
            '18pt': 9,
            '20pt': 10,
            '24pt': 12,
            '28pt': 14,
            '36pt': 18,
            '48pt': 24,
            '72pt': 36
        },
        "font_size_bins":[
            6, 8, 9, 10, 11, 12, 13, 15, 16, 18, 20, 24, 28, 36, 48, 72
            ],
        "font_size_labels":[
            '6pt', '8pt', '9pt', '10pt', '11pt', '12pt', '13pt', '15pt', '16pt', '18pt', '20pt', '24pt', '28pt', '36pt', '48pt', '72pt'
        ],
        "text_decoration_scores":{
            'underline': 1, 
            'none': 0,
            'line-through': 0,
            'overline': 0
        },
        "font_weight_scores":{
            'bold': 1, 'normal': 0
        }
    }   

