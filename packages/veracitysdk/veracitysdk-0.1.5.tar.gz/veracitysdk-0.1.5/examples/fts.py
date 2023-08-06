import os
import sys

from veracitysdk import Client, MetadataType, SimpleCache

def catch_err(err):
	if err:
		print(err.data)
		sys.exit()


# Create client
client = Client(
	key = os.environ["VERACITY_KEY"],
	secret = os.environ["VERACITY_SECRET"],
)

# Perform a search
results, err = client.articles.fulltext_search("disinformation -france")
catch_err(err)
print(results)
