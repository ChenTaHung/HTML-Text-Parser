#%%
import unittest
import pandas as pd

class TestDataFrameOperations(unittest.TestCase):
    def setUp(self):
        # Setup DataFrame
        self.df = pd.DataFrame({
            'total_score': [10, 20, 15, 5, 25, 30],
            'is_cutoff': [0] * 6  # Initialize 'is_cutoff' with 0
        })

    def test_cutoff_and_chunk_creation(self):
        # Define the cutoff
        cutoff = 15

        # Update 'is_cutoff' based on 'total_score' and cutoff
        self.df.loc[self.df['total_score'] >= cutoff, 'is_cutoff'] = 1

        # Assert that 'is_cutoff' is correctly set
        expected_is_cutoff = [0, 1, 1, 0, 1, 1]
        self.assertListEqual(self.df['is_cutoff'].tolist(), expected_is_cutoff)

        # Split the DataFrame into chunks based on 'is_cutoff'
        chunks = []
        for _, group in self.df.groupby((self.df['is_cutoff'] == 1).cumsum()):
            chunks.append(group)

        # Verify the correct number of chunks and their contents
        self.assertEqual(len(chunks), 4)  # Should split into 4 chunks
        self.assertTrue((chunks[1]['total_score'] == [20, 15]).all())  # Second chunk check
        self.assertTrue((chunks[3]['total_score'] == [25, 30]).all())  # Fourth chunk check

if __name__ == '__main__':
    unittest.main()

# %%
