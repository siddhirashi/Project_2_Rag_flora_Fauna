
BASE_URL = "http://localhost:1234"      


EMBED_MODEL = "text-embedding-nomic-embed-text-v1.5"
CHAT_MODEL = "qwen2.5-7b-instruct"


DOC_PREFIX = "text-embedding-nomic-embed-text-v1.5:2 "
QUERY_PREFIX = "qwen2.5-vl-3b-instruct"

CORPUS_DIR = "corpus"
INDEX_DIR = "index"
RESULTS_DIR = "results"

CHUNK_CHARS = 1200
CHUNK_OVERLAP = 200
TOP_K = 6          # chunks retrieved per query

# What we search for. Each query is embedded and matched against the chunks.
FLORA_QUERIES = {
    "Trees":   ["trees, groves and forests", "mango, banyan, ashoka, sandalwood or other tree"],
    "Plants":  ["plants, creepers, vines and grass", "lotus, reeds, bamboo or other water plants"],
    "Flowers": ["flowers, blossoms and garlands", "lotus, jasmine, champak, lily or other flower"],
    "Herbs":   ["herbs, medicinal plants and spices", "basil, tulsi, turmeric, ginger or other herb"],
    "Crops":   ["crops, rice, barley, harvest and fields", "paddy, wheat, sugarcane, sesame or other crop"],
}
FAUNA_QUERIES = {
    "Mammals":  ["wild animals, elephants, deer, tigers and monkeys", "cow, horse, lion, jackal or other mammal"],
    "Birds":    ["birds, peacocks, swans, parrots and cuckoos", "crane, goose, crow, owl or other bird"],
    "Reptiles": ["snakes, serpents, lizards and tortoises", "cobra, crocodile, turtle or other reptile"],
    "Fish":     ["fish, rivers and ponds with fishes", "fish, fisherman, net or other water creature"],
    "Insects":  ["bees, ants, flies, locusts and insects", "bee, butterfly, firefly, mosquito or other insect"],
}
