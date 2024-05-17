import pandas as pd

class Node:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.next = None
    
    def __fulltext__(self):
        """
        concatenate all text content in the chunk
        """
        return self.data['text_content'].str.cat(sep=' ')
    
    def __charlen__(self):
        """
        length of the concatenated text content
        """
        return len(self.__fulltext__())
    
    def __wordscnt__(self):
        """
        number of words in the concatenated text content
        """
        return len(self.__fulltext__().split(' '))
    
    def mergechunks(self, nextNode) -> None:
        """
        Merge the data from the current node with the data from the next node.

        Parameters:
        - nextNode: The next node containing data to be merged.

        Returns: Void
        None
        """
        self.data = pd.concat([self.data, nextNode.data], axis=0, ignore_index=True)
    def mergechunks(self, nextNode):
        
        self.data = pd.concat([self.data, nextNode.data], axis = 0, ignore_index=True)

class ChunkRefiner:
    def __init__(self, chunks: list):
        self.chunks = chunks

    def refine(self, lower_bound: int, upper_bound: int, sel_metric='words'):
        """
        Refines the chunks based on the specified lower and upper bounds and selected metric.

        Args:
            lower_bound (int): The lower bound for the chunk length.
            upper_bound (int): The upper bound for the chunk length.
            sel_metric (str, optional): The selected metric for refining the chunks. 
                Acceptable values are 'words' or 'characters'. Defaults to 'words'.

        Returns:
            list: A list of refined chunks.

        Raises:
            ValueError: If an invalid metric input is provided.

        """

        root: Node = Node(self.chunks[0])
        cur: Node = root

        # construct linked list
        for i in range(1, len(self.chunks)):
            cur.next = Node(self.chunks[i])
            cur = cur.next

        # refine chunks length
        cur = root

        if sel_metric == 'words':

            while cur.next is not None:

                if cur.__wordscnt__() < lower_bound:

                    if cur.__wordscnt__() + cur.next.__wordscnt__() <= upper_bound:
                        cur.mergechunks(cur.next)
                        cur.next = cur.next.next  # next node is merged into cur, so we skip the next node
                    else:
                        cur = cur.next
                else:
                    cur = cur.next

        elif sel_metric == 'characters':

            while cur.next is not None:
                if cur.__charlen__() < lower_bound:
                    if cur.__charlen__() + cur.next.__charlen__() <= upper_bound:
                        cur.mergechunks(cur.next)
                        cur.next = cur.next.next  # next node is merged into cur, so we skip the next node
                    else:
                        cur = cur.next
                else:
                    cur = cur.next

        else:
            raise ValueError(f'Invalid metric input: {sel_metric}, acceptable values are [words, characters]')

        # output the refined chunks
        cur = root
        refined_chunks = []
        while cur is not None:
            refined_chunks.append(cur.data)
            cur = cur.next

        return refined_chunks
    
